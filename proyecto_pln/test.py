import torch
from transformers import BertTokenizer, BertForSequenceClassification
from peft import PeftModel

RUTA_MODELO = "./output/training_results/mejor_modelo"
MAX_LEN      = 128
VENTANA      = 5
device       = torch.device("cuda" if torch.cuda.is_available() else "cpu")

niveles = {
    0: "Bajo riesgo",
    1: "Riesgo medio",
    2: "Alto riesgo"
}

print("Cargando modelo...")
tokenizer   = BertTokenizer.from_pretrained(RUTA_MODELO)
modelo_base = BertForSequenceClassification.from_pretrained(
    "bert-base-multilingual-cased",
    num_labels=3
)
modelo = PeftModel.from_pretrained(modelo_base, RUTA_MODELO)
modelo.to(device)
modelo.eval()
print("Listo.\n")


def clasificar_ventana(textos_ventana):
    texto = " | ".join(textos_ventana)
    tokens = tokenizer(
        texto,
        max_length=MAX_LEN,
        padding="max_length",
        truncation=True,
        return_tensors="pt"
    )
    ids     = tokens["input_ids"].to(device)
    mascara = tokens["attention_mask"].to(device)

    with torch.no_grad():
        salida = modelo(input_ids=ids, attention_mask=mascara)
        probs  = torch.softmax(salida.logits, dim=1).squeeze()
        pred   = torch.argmax(probs).item()

    return pred, probs


def analizar_conversacion(mensajes):
    print(f"\n{'─'*50}")
    print(f"  Analizando conversacion ({len(mensajes)} mensajes)")
    print(f"  Ventana de contexto: {VENTANA} mensajes")
    print(f"{'─'*50}")

    riesgo_max = 0
    alertas    = []
    historial  = []

    for i, msg in enumerate(mensajes):
        historial.append(f"{msg['emisor']}: {msg['texto']}")
        ventana_actual = historial[max(0, len(historial) - VENTANA):]

        pred, probs = clasificar_ventana(ventana_actual)

        print(f"  [{i+1}] {msg['emisor']}: {msg['texto'][:55]}...")
        print(f"       {niveles[pred]} | "
              f"B:{probs[0]*100:.1f}% M:{probs[1]*100:.1f}% A:{probs[2]*100:.1f}%")

        if pred > riesgo_max:
            riesgo_max = pred

        if pred >= 1:
            alertas.append(i + 1)

    print(f"\n  Resultado final: {niveles[riesgo_max]}")
    if alertas:
        print(f"  Mensajes en alerta: {alertas}")
    print(f"{'─'*50}\n")


def modo_interactivo():
    print("=" * 50)
    print("  ANIMOON — prueba de modelo (LoRA + Ventana)")
    print("  'salir' para terminar")
    print("  'conv'  para probar conversacion de ejemplo")
    print("=" * 50)

    historial_interactivo = []

    while True:
        entrada = input("\nEmisor (A/B) y mensaje, separados por ':'\n> ").strip()

        if entrada.lower() == "salir":
            break

        elif entrada.lower() == "conv":
            historial_interactivo = []
            ejemplo = [
                {"emisor": "Usuario A", "texto": "hey do you want to play roblox?"},
                {"emisor": "Usuario B", "texto": "sure, what's your username?"},
                {"emisor": "Usuario A", "texto": "how old are you by the way?"},
                {"emisor": "Usuario B", "texto": "i'm 12"},
                {"emisor": "Usuario A", "texto": "are you home alone right now?"},
                {"emisor": "Usuario A", "texto": "want to meet up sometime?"},
            ]
            analizar_conversacion(ejemplo)

        elif entrada.lower() == "reset":
            historial_interactivo = []
            print("  Historial limpiado — nueva conversacion")

        elif ":" in entrada:
            partes = entrada.split(":", 1)
            emisor = partes[0].strip()
            texto  = partes[1].strip()

            historial_interactivo.append(f"{emisor}: {texto}")
            ventana_actual = historial_interactivo[max(0, len(historial_interactivo) - VENTANA):]

            pred, probs = clasificar_ventana(ventana_actual)
            print(f"  {niveles[pred]}")
            print(f"  Bajo: {probs[0]*100:.1f}% | Medio: {probs[1]*100:.1f}% | Alto: {probs[2]*100:.1f}%")
            print(f"  Contexto usado: {len(ventana_actual)} mensaje(s)")

        else:
            print("  Formato: EmisorA: mensaje  o  EmisorB: mensaje")
            print("  Comandos: 'conv', 'reset', 'salir'")


if __name__ == "__main__":
    modo_interactivo()