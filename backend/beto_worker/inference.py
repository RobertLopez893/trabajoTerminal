"""
=============================================================================
MÓDULO DE INFERENCIA: ANALIZADOR BETO ONNX (MICROSERVICIO BETO_WORKER)
=============================================================================
Este módulo encapsula el motor de inferencia ONNX y el tokenizador de BETO
para evaluar conversaciones en tiempo real mediante ventanas deslizantes
y atribución semántica rigurosa de autoría.
=============================================================================
"""

import os
import sys
import logging
import numpy as np
import onnxruntime as ort
from transformers import AutoTokenizer

logger = logging.getLogger("BETOInference")
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# Configuración de rutas por defecto
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR))

DEFAULT_MODEL_DIR = os.path.join(
    PROJECT_ROOT,
    "proyecto_pln",
    "output",
    "training_results_v5",
    "mejor_modelo",
    "modelo_comprimido"
)

# Nombres legibles de las clases entrenadas
ETIQUETAS_RIESGO = {
    0: "NIVEL_0_SEGURO",
    1: "NIVEL_1_SOSPECHOSO",
    2: "NIVEL_2_GROOMING"
}


class AnalizadorBETO:
    """
    Carga el modelo BETO exportado en formato ONNX y ejecuta inferencia
    sobre ventanas de mensajes utilizando ONNX Runtime con mapeo de alias
    y atribución semántica de culpabilidad.
    """

    def __init__(self, model_dir: str = None, ventana_tam: int = 5, umbral_grooming: float = None):
        self.model_dir = model_dir or os.getenv("BETO_MODEL_DIR", DEFAULT_MODEL_DIR)
        self.ventana_tam = ventana_tam
        if umbral_grooming is not None:
            self.umbral_grooming = umbral_grooming
        else:
            # Umbral calibrado a 0.82 para evitar falsos positivos por ruido o bromas
            self.umbral_grooming = float(os.getenv("BETO_UMBRAL_GROOMING", "0.82"))

        onnx_model_path = os.path.join(self.model_dir, "model.onnx")
        if not os.path.exists(onnx_model_path):
            raise FileNotFoundError(f"No se encontró el archivo model.onnx en: {self.model_dir}")

        logger.info(f"Cargando tokenizador desde: {self.model_dir}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_dir)

        logger.info(f"Cargando sesión ONNX Runtime desde: {onnx_model_path}")
        opts = ort.SessionOptions()
        opts.intra_op_num_threads = max(1, os.cpu_count() or 1)
        opts.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        self.session = ort.InferenceSession(onnx_model_path, sess_options=opts, providers=["CPUExecutionProvider"])

        logger.info(f"AnalizadorBETO inicializado correctamente (Umbral Grooming={self.umbral_grooming:.2%}).")

    def generar_alias_map(self, mensajes: list, usuario_a_id: str = None, usuario_b_id: str = None) -> dict:
        """
        Mapea los IDs reales (UUIDs de 36 caracteres) a etiquetas limpias ('Usuario A', 'Usuario B')
        para que coincidan exactamente con el formato con el que fue entrenado BETO,
        evitando saturar el límite de 128 tokens con identificadores hexadecimales.
        """
        alias_map = {}
        if usuario_a_id:
            alias_map[usuario_a_id] = "Usuario A"
        if usuario_b_id:
            alias_map[usuario_b_id] = "Usuario B"

        etiquetas_disponibles = ["Usuario A", "Usuario B", "Usuario C"]
        for m in mensajes:
            emisor = m.get("emisor_id")
            if emisor and emisor not in alias_map:
                for eti in etiquetas_disponibles:
                    if eti not in alias_map.values():
                        alias_map[emisor] = eti
                        break
                if emisor not in alias_map:
                    alias_map[emisor] = f"Usuario {len(alias_map) + 1}"

        return alias_map

    def construir_ventanas(self, mensajes: list, alias_map: dict = None) -> list:
        """
        Construye ventanas deslizantes de tamaño N siguiendo exactamente
        la estructura con la que fue entrenado el modelo:
        'Usuario A: texto | Usuario B: texto | ...'
        """
        ventanas = []
        n = len(mensajes)
        if n == 0:
            return ventanas

        if alias_map is None:
            alias_map = self.generar_alias_map(mensajes)

        for i in range(n):
            inicio = max(0, i - self.ventana_tam + 1)
            fragmentos = []
            emisores_en_ventana = []
            for j in range(inicio, i + 1):
                emisor_real = mensajes[j].get("emisor_id", "DESCONOCIDO")
                alias = alias_map.get(emisor_real, "Usuario A")
                texto = mensajes[j].get("texto", "").strip()
                fragmentos.append(f"{alias}: {texto}")
                emisores_en_ventana.append(emisor_real)

            texto_ventana = " | ".join(fragmentos)
            ventanas.append({
                "indice_final": i,
                "texto_ventana": texto_ventana,
                "ultimo_emisor": emisores_en_ventana[-1] if emisores_en_ventana else None,
                "emisores": list(set(emisores_en_ventana))
            })

        return ventanas

    def evaluar_texto(self, texto_ventana: str) -> dict:
        """
        Ejecuta la inferencia sobre una ventana de texto y retorna
        probabilidades softmax para cada una de las 3 clases.
        """
        inputs = self.tokenizer(
            texto_ventana,
            padding=True,
            truncation=True,
            max_length=128,
            return_tensors="np"
        )

        ort_inputs = {
            "input_ids": inputs["input_ids"].astype(np.int64),
            "attention_mask": inputs["attention_mask"].astype(np.int64)
        }
        if "token_type_ids" in inputs:
            ort_inputs["token_type_ids"] = inputs["token_type_ids"].astype(np.int64)

        outputs = self.session.run(None, ort_inputs)
        logits = outputs[0][0]

        # Softmax numéricamente estable
        e_x = np.exp(logits - np.max(logits))
        probs = e_x / e_x.sum()

        clase_predicha = int(np.argmax(probs))
        prob_grooming = float(probs[2])  # Clase 2: Nivel 2 Grooming

        return {
            "clase": clase_predicha,
            "fase": ETIQUETAS_RIESGO.get(clase_predicha, "DESCONOCIDO"),
            "prob_nivel_0": float(probs[0]),
            "prob_nivel_1": float(probs[1]),
            "prob_nivel_2": prob_grooming,
            "score_confianza": float(probs[clase_predicha])
        }

    def analizar_bloque(self, mensajes: list, usuario_a_id: str = None, usuario_b_id: str = None) -> dict:
        """
        Analiza el bloque completo de mensajes procesando todas las ventanas deslizantes
        utilizando alias ('Usuario A' / 'Usuario B') y aplicando atribución de autoría por
        discurso aislado para garantizar que jamás se confunda a la víctima con el agresor.
        """
        if not mensajes:
            return {
                "grooming_detectado": False,
                "nivel_riesgo_max": 0,
                "fase_detectada": "NIVEL_0_SEGURO",
                "confidence_score": 0.0,
                "agresor_id": None,
                "victima_id": None,
                "ventana_evidencia": None,
                "total_ventanas": 0
            }

        alias_map = self.generar_alias_map(mensajes, usuario_a_id, usuario_b_id)
        ventanas = self.construir_ventanas(mensajes, alias_map)
        total_v = len(ventanas)

        max_nivel = 0
        max_prob_grooming = 0.0
        mejor_confianza = 0.0
        ventana_critica = None

        logger.info(f"🔍 [BETO INFERENCIA] Evaluando {len(mensajes)} mensajes en {total_v} ventanas (Umbral Grooming={self.umbral_grooming:.2%}):")

        for idx, vent in enumerate(ventanas, 1):
            pred = self.evaluar_texto(vent["texto_ventana"])
            clase = pred["clase"]
            conf = pred["score_confianza"]
            p0, p1, p2 = pred["prob_nivel_0"], pred["prob_nivel_1"], pred["prob_nivel_2"]

            tag_clase = "GROOMING" if clase == 2 else ("SOSPECHOSO" if clase == 1 else "SEGURO")
            ultimo_txt = vent["texto_ventana"].split(" | ")[-1] if " | " in vent["texto_ventana"] else vent["texto_ventana"]

            logger.info(
                f"  [{idx:02d}/{total_v:02d}] {tag_clase:<10} | Conf: {conf:.1%} (Seg: {p0:.1%}, Sosp: {p1:.1%}, Groom: {p2:.1%}) | Msg: \"{ultimo_txt}\""
            )

            if p2 > max_prob_grooming:
                max_prob_grooming = p2
                mejor_confianza = conf
                ventana_critica = vent
                if clase > max_nivel:
                    max_nivel = clase
            elif clase > max_nivel:
                max_nivel = clase
                mejor_confianza = conf

        # 1. Determinación de Grooming en la conversación
        es_grooming = (max_prob_grooming >= self.umbral_grooming)

        # 2. Atribución Categórica de Culpabilidad (Aislamiento Semántico de Autor)
        agresor_id = None
        victima_id = None

        if es_grooming:
            participantes = list(alias_map.keys())
            if len(participantes) >= 2:
                u1, u2 = participantes[0], participantes[1]

                # Extraer mensajes con contenido real emitidos por cada participante en el bloque
                msgs_u1 = [m["texto"].strip() for m in mensajes if m.get("emisor_id") == u1 and len(m.get("texto", "").strip()) > 1]
                msgs_u2 = [m["texto"].strip() for m in mensajes if m.get("emisor_id") == u2 and len(m.get("texto", "").strip()) > 1]

                # Construir el discurso aislado de cada participante
                sub_1 = " | ".join([f"{alias_map[u1]}: {t}" for t in msgs_u1[-8:]])
                sub_2 = " | ".join([f"{alias_map[u2]}: {t}" for t in msgs_u2[-8:]])

                pred_1 = self.evaluar_texto(sub_1) if sub_1 else {"prob_nivel_2": 0.0}
                pred_2 = self.evaluar_texto(sub_2) if sub_2 else {"prob_nivel_2": 0.0}

                score_1 = pred_1["prob_nivel_2"]
                score_2 = pred_2["prob_nivel_2"]

                logger.info(
                    f"⚖️ [ATRIBUCIÓN DE CULPABILIDAD POR DISCURSO AISLADO]:\n"
                    f"   - {alias_map[u1]} ('{u1}'): Score Grooming = {score_1:.2%}\n"
                    f"   - {alias_map[u2]} ('{u2}'): Score Grooming = {score_2:.2%}"
                )

                # El agresor es quien tiene carga semántica depredadora dominante y significativa
                if score_1 > score_2 and score_1 >= 0.65:
                    agresor_id = u1
                    victima_id = u2
                elif score_2 > score_1 and score_2 >= 0.65:
                    agresor_id = u2
                    victima_id = u1
                else:
                    logger.warning(
                        f"⚠️ [ATRIBUCIÓN AMBIGUA] Ningún participante superó de forma aislada el umbral de certeza (U1={score_1:.1%}, U2={score_2:.1%}). "
                        f"Descartando sanción automática para evitar falso positivo contra inocentes."
                    )
                    es_grooming = False
            elif len(participantes) == 1:
                agresor_id = participantes[0]

        fase_final = "NIVEL_2_GROOMING" if es_grooming else ETIQUETAS_RIESGO.get(max_nivel, "NIVEL_0_SEGURO")

        if es_grooming:
            evid_txt = ventana_critica['texto_ventana'] if ventana_critica else 'N/A'
            logger.warning(
                f"🚨 [DECISIÓN FINAL]: GROOMING CONFIRMADO (P={max_prob_grooming:.2%} >= Umbral {self.umbral_grooming:.2%}).\n"
                f"   - Agresor culpable: '{agresor_id}' ({alias_map.get(agresor_id, 'Desconocido')})\n"
                f"   - Víctima protegida: '{victima_id}' ({alias_map.get(victima_id, 'Desconocido')})\n"
                f"   - Ventana crítica de evidencia: \"{evid_txt}\""
            )
        else:
            logger.info(
                f"✅ [DECISIÓN FINAL]: Bloque {fase_final} (Confianza: {mejor_confianza:.2%}). No se sanciona."
            )

        return {
            "grooming_detectado": es_grooming,
            "nivel_riesgo_max": 2 if es_grooming else max_nivel,
            "fase_detectada": fase_final,
            "confidence_score": round(max_prob_grooming, 4),
            "agresor_id": agresor_id,
            "victima_id": victima_id,
            "ventana_evidencia": ventana_critica["texto_ventana"] if ventana_critica else None,
            "total_ventanas": total_v
        }
