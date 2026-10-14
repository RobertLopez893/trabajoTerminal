import os
import torch
from transformers import BertTokenizer, BertForSequenceClassification
from peft import PeftModel

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_ADAPTADORES = os.path.join(BASE_DIR, "output", "training_results", "mejor_modelo")
RUTA_FUSIONADO   = os.path.join(BASE_DIR, "output", "training_results", "modelo_fusionado")

print("1. Cargando el modelo base de BETO...")
modelo_base = BertForSequenceClassification.from_pretrained(
    "dccuchile/bert-base-spanish-wwm-cased",
    num_labels=3,
    use_safetensors=True
)

print("2. Inyectando adaptadores LoRA entrenados...")
modelo_peft = PeftModel.from_pretrained(modelo_base, RUTA_ADAPTADORES)

print("3. Fusionando pesos...")
modelo_fusionado = modelo_peft.merge_and_unload()

print("4. Guardando modelo fusionado...")
os.makedirs(RUTA_FUSIONADO, exist_ok=True)
modelo_fusionado.save_pretrained(RUTA_FUSIONADO)

# También guardamos el tokenizador en la misma carpeta
tokenizer = BertTokenizer.from_pretrained(RUTA_ADAPTADORES)
tokenizer.save_pretrained(RUTA_FUSIONADO)

print(f"\n¡Éxito! El modelo unificado está listo en: {RUTA_FUSIONADO}")