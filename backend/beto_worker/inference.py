"""
=============================================================================
MÓDULO DE INFERENCIA: ANALIZADOR BETO ONNX (MICROSERVICIO BETO_WORKER)
=============================================================================
Este módulo encapsula el motor de inferencia ONNX y el tokenizador de BETO
para evaluar conversaciones en tiempo real mediante ventanas deslizantes.
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
    sobre ventanas de mensajes utilizando ONNX Runtime.
    """

    def __init__(self, model_dir: str = None, ventana_tam: int = 5, umbral_grooming: float = None):
        self.model_dir = model_dir or os.getenv("BETO_MODEL_DIR", DEFAULT_MODEL_DIR)
        self.ventana_tam = ventana_tam
        if umbral_grooming is not None:
            self.umbral_grooming = umbral_grooming
        else:
            self.umbral_grooming = float(os.getenv("BETO_UMBRAL_GROOMING", "0.65"))

        onnx_model_path = os.path.join(self.model_dir, "model.onnx")
        if not os.path.exists(onnx_model_path):
            raise FileNotFoundError(f"No se encontró el archivo model.onnx en: {self.model_dir}")

        logger.info(f"Cargando tokenizador desde: {self.model_dir}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_dir)

        logger.info(f"Cargando sesión ONNX Runtime desde: {onnx_model_path}")
        # Optimización de ejecución en CPU para EC2 t3.micro
        opts = ort.SessionOptions()
        opts.intra_op_num_threads = max(1, os.cpu_count() or 1)
        opts.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        self.session = ort.InferenceSession(onnx_model_path, sess_options=opts, providers=["CPUExecutionProvider"])

        logger.info("AnalizadorBETO inicializado correctamente.")

    def construir_ventanas(self, mensajes: list) -> list:
        """
        Construye ventanas deslizantes de tamaño N siguiendo exactamente
        la estructura con la que fue entrenado el modelo:
        'emisor_id: texto | emisor_id: texto | ...'
        """
        ventanas = []
        n = len(mensajes)
        if n == 0:
            return ventanas

        for i in range(n):
            inicio = max(0, i - self.ventana_tam + 1)
            fragmentos = []
            emisores_en_ventana = []
            for j in range(inicio, i + 1):
                emisor = mensajes[j].get("emisor_id", "DESCONOCIDO")
                texto = mensajes[j].get("texto", "").strip()
                fragmentos.append(f"{emisor}: {texto}")
                emisores_en_ventana.append(emisor)

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
        Analiza el bloque completo de 20 mensajes procesando todas las ventanas deslizantes.
        Identifica la ventana de mayor riesgo y determina si hay grooming.
        """
        if not mensajes:
            return {
                "grooming_detectado": False,
                "nivel_riesgo_max": 0,
                "fase_detectada": "NIVEL_0_SEGURO",
                "confidence_score": 0.0,
                "agresor_id": None,
                "ventana_evidencia": None,
                "total_ventanas": 0
            }

        ventanas = self.construir_ventanas(mensajes)

        max_nivel = 0
        max_prob_grooming = 0.0
        mejor_confianza = 0.0
        ventana_critica = None
        conteo_sospechas_por_emisor = {}

        for vent in ventanas:
            pred = self.evaluar_texto(vent["texto_ventana"])

            emisor = vent["ultimo_emisor"]
            if emisor:
                conteo_sospechas_por_emisor.setdefault(emisor, 0)
                if pred["clase"] >= 1:
                    conteo_sospechas_por_emisor[emisor] += pred["clase"]

            if pred["clase"] > max_nivel or (pred["clase"] == max_nivel and pred["prob_nivel_2"] > max_prob_grooming):
                max_nivel = pred["clase"]
                max_prob_grooming = pred["prob_nivel_2"]
                mejor_confianza = pred["score_confianza"]
                ventana_critica = vent

        # Determinación de Grooming (Clase 2 predicha con probabilidad superando el umbral calibrado)
        es_grooming = (max_nivel == 2) and (max_prob_grooming >= self.umbral_grooming)

        # Identificar al posible agresor
        agresor_id = None
        if es_grooming:
            if conteo_sospechas_por_emisor:
                agresor_id = max(conteo_sospechas_por_emisor, key=conteo_sospechas_por_emisor.get)
            elif ventana_critica and ventana_critica["ultimo_emisor"]:
                agresor_id = ventana_critica["ultimo_emisor"]
            elif usuario_a_id:
                agresor_id = usuario_a_id

        fase_final = "NIVEL_2_GROOMING" if es_grooming else ETIQUETAS_RIESGO.get(max_nivel, "NIVEL_0_SEGURO")

        return {
            "grooming_detectado": es_grooming,
            "nivel_riesgo_max": 2 if es_grooming else max_nivel,
            "fase_detectada": fase_final,
            "confidence_score": round(max_prob_grooming if es_grooming else mejor_confianza, 4),
            "agresor_id": agresor_id,
            "ventana_evidencia": ventana_critica["texto_ventana"] if ventana_critica else None,
            "total_ventanas": len(ventanas)
        }
