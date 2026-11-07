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
import re
import sys
import unicodedata
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

# Expresiones regulares direccionales para desambiguar Agresor vs Víctima
PATRONES_AGRESOR = [
    r"\b(secreto|secretito)\b",
    r"\bno\s+le(s)?\s+diga(s|z)?\b",
    r"\bno\s+diga(s|z)?\s+nada\b",
    r"\bnadie\s+(sepa|nos\s+vea|se\s+entere)\b",
    r"\b(tus\s+papas|tus\s+jefes|tu\s+mama|tu\s+papa)\s+no\b",
    r"\b(mandame|pasa|pasame|enviame)\s+(una\s+)?(foto|fotos|pack|tu\s+whats|tu\s+numero|tu\s+insta)\b",
    r"\b(foto|fotos)\s+(intima|privada|sin\s+ropa|desnud|tuya)\b",
    r"\b(whatsapp|whats|insta|instagram|telegram)\b",
    r"\b(otro\s+lado|mas\s+privado|a\s+solas|tu\s+cuarto)\b",
    r"\b(donde\s+vives|cuantos\s+anos\s+tienes|cual\s+es\s+tu\s+edad)\b",
    r"\b(borra|borralos)\b",
    r"\b(prende\s+la\s+camara|verte\s+en\s+persona|nos\s+vemos)\b",
]

PATRONES_VICTIMA_DEFENSIVOS = [
    r"\bno\s+quiero\b",
    r"\bno\s+puedo\b",
    r"\b(me\s+da|dando)\s+(miedo|pena)\b",
    r"\bdejame\s+en\s+paz\b",
    r"\bno\s+te\s+conozco\b",
    r"\bquien\s+eres\b",
    r"\b(decirle|contarle|dire)\s+a\s+(mis\s+papas|mi\s+mama|mi\s+papa|mis\s+jefes)\b",
    r"\b(mi\s+mama|mi\s+papa|mis\s+papas)\s+(dice|dicen|no\s+me\s+deja|me\s+regana)\b",
    r"\btengo\s+(6|7|8|9|10|11|12|13)\s+anos\b",
]


def _normalizar_texto(texto: str) -> str:
    """Convierte a minúsculas y elimina acentos para evaluación léxica auxiliar."""
    texto_norm = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in texto_norm if unicodedata.category(c) != "Mn")


def _contar_patrones(texto: str, lista_patrones: list) -> int:
    t = _normalizar_texto(texto)
    return sum(1 for pat in lista_patrones if re.search(pat, t))


class AnalizadorBETO:
    """
    Carga el modelo BETO exportado en formato ONNX y ejecuta inferencia
    sobre ventanas de mensajes utilizando ONNX Runtime con mapeo de alias
    simétrico y atribución semántica híbrida de culpabilidad.
    """

    def __init__(self, model_dir: str = None, ventana_tam: int = 5, umbral_grooming: float = None):
        self.model_dir = model_dir or os.getenv("BETO_MODEL_DIR", DEFAULT_MODEL_DIR)
        self.ventana_tam = ventana_tam
        if umbral_grooming is not None:
            self.umbral_grooming = umbral_grooming
        else:
            # Umbral calibrado a 0.68 para detectar grooming en bloques de 10 mensajes sin falsos positivos
            self.umbral_grooming = float(os.getenv("BETO_UMBRAL_GROOMING", "0.68"))

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
            fragmentos_canonicos = []
            emisores_en_ventana = []
            ultimo_emisor = mensajes[i].get("emisor_id", "DESCONOCIDO")
            ultimo_texto = mensajes[i].get("texto", "").strip()

            for j in range(inicio, i + 1):
                emisor_real = mensajes[j].get("emisor_id", "DESCONOCIDO")
                alias = alias_map.get(emisor_real, "Usuario A")
                # En la vista canónica el autor del mensaje evaluado (i) siempre asume el rol 'Usuario A'
                # para eliminar el sesgo posicional del corpus hacia 'Usuario A' como agresor.
                alias_canon = "Usuario A" if emisor_real == ultimo_emisor else "Usuario B"
                texto = mensajes[j].get("texto", "").strip()
                fragmentos.append(f"{alias}: {texto}")
                fragmentos_canonicos.append(f"{alias_canon}: {texto}")
                emisores_en_ventana.append(emisor_real)

            texto_ventana = " | ".join(fragmentos)
            texto_ventana_canonico = " | ".join(fragmentos_canonicos)
            ventanas.append({
                "indice_final": i,
                "texto_ventana": texto_ventana,
                "texto_ventana_canonico": texto_ventana_canonico,
                "ultimo_emisor": ultimo_emisor,
                "ultimo_texto": ultimo_texto,
                "longitudes_textos": [len(mensajes[j].get("texto", "").strip()) for j in range(inicio, i + 1)],
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

    def evaluar_discurso_aislado(self, textos_autor: list) -> float:
        """
        Evalúa los mensajes propios de un autor mediante sub-ventanas deslizantes
        de tamaño 2 a 4 bajo la etiqueta canónica 'Usuario A', filtrando respuestas
        puramente defensivas de víctima y caracteres sueltos para evitar dilución
        y sesgo posicional.
        """
        filtrados = []
        for t in textos_autor:
            t_clean = t.strip()
            if len(t_clean) <= 1:
                continue
            es_defensivo = (
                _contar_patrones(t_clean, PATRONES_VICTIMA_DEFENSIVOS) > 0
                and _contar_patrones(t_clean, PATRONES_AGRESOR) == 0
            )
            if not es_defensivo:
                filtrados.append(t_clean)

        if not filtrados:
            return 0.0

        max_prob = 0.0
        tamanos = sorted(set([min(len(filtrados), k) for k in (2, 3, 4) if min(len(filtrados), k) > 0]))
        for tam in tamanos:
            for i in range(len(filtrados)):
                ini = max(0, i - tam + 1)
                sub = " | ".join([f"Usuario A: {m}" for m in filtrados[ini:i + 1]])
                pred = self.evaluar_texto(sub)
                if pred["prob_nivel_2"] > max_prob:
                    max_prob = pred["prob_nivel_2"]

        return max_prob

    def analizar_bloque(self, mensajes: list, usuario_a_id: str = None, usuario_b_id: str = None) -> dict:
        """
        Analiza el bloque completo de mensajes procesando todas las ventanas deslizantes
        de forma simétrica ('Usuario A' / 'Usuario B') y aplicando atribución híbrida de
        autoría (discurso aislado en sub-ventanas + incremento marginal de riesgo + patrones
        direccionales) para identificar con precisión al agresor y proteger a la víctima.
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

        impulso_riesgo = {u: 0.0 for u in alias_map}
        marcadores_agr = {u: 0 for u in alias_map}
        marcadores_vic = {u: 0 for u in alias_map}

        for m in mensajes:
            em = m.get("emisor_id")
            txt = m.get("texto", "").strip()
            if em:
                impulso_riesgo.setdefault(em, 0.0)
                marcadores_agr[em] = marcadores_agr.get(em, 0) + _contar_patrones(txt, PATRONES_AGRESOR)
                marcadores_vic[em] = marcadores_vic.get(em, 0) + _contar_patrones(txt, PATRONES_VICTIMA_DEFENSIVOS)

        logger.info(f"🔍 [BETO INFERENCIA] Evaluando {len(mensajes)} mensajes en {total_v} ventanas (Umbral Grooming={self.umbral_grooming:.2%}):")

        prev_p2 = 0.0
        for idx, vent in enumerate(ventanas, 1):
            # Ignorar spam artificial de mensajes de 1 solo carácter (ej. 'N | D | W | E')
            ultimos_largos = vent["longitudes_textos"][-3:]
            es_spam_un_caracter = (len(vent["ultimo_texto"]) <= 1 and max(ultimos_largos) <= 2)

            pred_base = self.evaluar_texto(vent["texto_ventana"])
            if vent["texto_ventana_canonico"] != vent["texto_ventana"]:
                pred_canon = self.evaluar_texto(vent["texto_ventana_canonico"])
                pred = pred_canon if pred_canon["prob_nivel_2"] > pred_base["prob_nivel_2"] else pred_base
            else:
                pred = pred_base

            if es_spam_un_caracter:
                pred = {
                    "clase": 0,
                    "fase": "NIVEL_0_SEGURO",
                    "prob_nivel_0": 0.95,
                    "prob_nivel_1": 0.03,
                    "prob_nivel_2": 0.02,
                    "score_confianza": 0.95
                }

            clase = pred["clase"]
            conf = pred["score_confianza"]
            p0, p1, p2 = pred["prob_nivel_0"], pred["prob_nivel_1"], pred["prob_nivel_2"]

            emisor_act = vent["ultimo_emisor"]
            txt_act = vent["ultimo_texto"]
            es_msg_defensivo = (
                _contar_patrones(txt_act, PATRONES_VICTIMA_DEFENSIVOS) > 0
                and _contar_patrones(txt_act, PATRONES_AGRESOR) == 0
            )
            delta_p2 = p2 - prev_p2
            if emisor_act and delta_p2 > 0 and not es_msg_defensivo:
                impulso_riesgo[emisor_act] = impulso_riesgo.get(emisor_act, 0.0) + delta_p2
            prev_p2 = p2

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

        # 2. Atribución Híbrida de Culpabilidad (Sub-ventanas Aisladas + Impulso Marginal + Patrones)
        agresor_id = None
        victima_id = None

        if es_grooming:
            participantes = list(alias_map.keys())
            if len(participantes) >= 2:
                u1, u2 = participantes[0], participantes[1]

                msgs_u1 = [m["texto"].strip() for m in mensajes if m.get("emisor_id") == u1 and len(m.get("texto", "").strip()) > 1]
                msgs_u2 = [m["texto"].strip() for m in mensajes if m.get("emisor_id") == u2 and len(m.get("texto", "").strip()) > 1]

                aislado_1 = self.evaluar_discurso_aislado(msgs_u1)
                aislado_2 = self.evaluar_discurso_aislado(msgs_u2)

                imp_1 = impulso_riesgo.get(u1, 0.0)
                imp_2 = impulso_riesgo.get(u2, 0.0)

                score_1 = (aislado_1 * 0.50) + (min(1.0, imp_1) * 0.35) + (min(1.0, marcadores_agr.get(u1, 0) * 0.20)) - (min(0.4, marcadores_vic.get(u1, 0) * 0.15))
                score_2 = (aislado_2 * 0.50) + (min(1.0, imp_2) * 0.35) + (min(1.0, marcadores_agr.get(u2, 0) * 0.20)) - (min(0.4, marcadores_vic.get(u2, 0) * 0.15))

                logger.info(
                    f"⚖️ [ATRIBUCIÓN DE CULPABILIDAD HÍBRIDA]:\n"
                    f"   - {alias_map[u1]} ('{u1}'): Score Final={score_1:.2%} (Aislado={aislado_1:.2%}, Impulso={imp_1:.2%}, PatronesAgr={marcadores_agr.get(u1, 0)}, PatronesVic={marcadores_vic.get(u1, 0)})\n"
                    f"   - {alias_map[u2]} ('{u2}'): Score Final={score_2:.2%} (Aislado={aislado_2:.2%}, Impulso={imp_2:.2%}, PatronesAgr={marcadores_agr.get(u2, 0)}, PatronesVic={marcadores_vic.get(u2, 0)})"
                )

                if score_1 > score_2:
                    agresor_id = u1
                    victima_id = u2
                elif score_2 > score_1:
                    agresor_id = u2
                    victima_id = u1
                else:
                    agresor_id = ventana_critica["ultimo_emisor"] if (ventana_critica and ventana_critica.get("ultimo_emisor")) else u1
                    victima_id = u2 if agresor_id == u1 else u1
            elif len(participantes) == 1:
                agresor_id = participantes[0]
                if usuario_a_id and usuario_b_id:
                    victima_id = usuario_b_id if agresor_id == usuario_a_id else usuario_a_id

        if es_grooming:
            fase_final = "NIVEL_2_GROOMING"
        elif max_nivel >= 1 or max_prob_grooming >= 0.35:
            fase_final = "NIVEL_1_SOSPECHOSO"
        else:
            fase_final = "NIVEL_0_SEGURO"

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
                f"✅ [DECISIÓN FINAL]: Bloque {fase_final} (Confianza: {mejor_confianza:.2%}, MaxGroom: {max_prob_grooming:.2%}). No se sanciona."
            )

        return {
            "grooming_detectado": es_grooming,
            "nivel_riesgo_max": 2 if es_grooming else (1 if fase_final == "NIVEL_1_SOSPECHOSO" else 0),
            "fase_detectada": fase_final,
            "confidence_score": round(max_prob_grooming, 4),
            "agresor_id": agresor_id,
            "victima_id": victima_id,
            "ventana_evidencia": ventana_critica["texto_ventana"] if ventana_critica else None,
            "total_ventanas": total_v
        }
