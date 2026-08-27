import torch
from transformers import BertTokenizer, BertForSequenceClassification

RUTA_MODELO = "./output/training_results/mejor_modelo"
MAX_LEN     = 128
device      = torch.device("cuda" if torch.cuda.is_available() else "cpu")

niveles = {
    0: "Bajo riesgo",
    1: "Riesgo medio",
    2: "Alto riesgo"
}

print("Cargando modelo...")
tokenizer = BertTokenizer.from_pretrained(RUTA_MODELO)
modelo    = BertForSequenceClassification.from_pretrained(RUTA_MODELO)
modelo.to(device)
modelo.eval()
print("Listo.\n")


def clasificar(texto):
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
    riesgo_max = 0
    alertas    = []

    for i, msg in enumerate(mensajes):
        pred, probs = clasificar(msg["texto"])

        print(f"  [{i+1}] {msg['emisor']}: {msg['texto'][:55]}...")
        print(f"       {niveles[pred]} | "
              f"B:{probs[0]*100:.1f}% M:{probs[1]*100:.1f}% A:{probs[2]*100:.1f}%")

        if pred > riesgo_max:
            riesgo_max = pred

        if pred >= 1:
            alertas.append(i + 1)

    print(f"\n  Resultado: {niveles[riesgo_max]}")
    if alertas:
        print(f"  Mensajes en alerta: {alertas}")
    print(f"{'─'*50}\n")


def modo_interactivo():
    print("=" * 50)
    print("  ANIMOON — prueba de modelo")
    print("  'salir' para terminar")
    print("  'conv'  para probar conversacion de ejemplo")
    print("=" * 50)

    while True:
        texto = input("\nMensaje: ").strip()

        if texto.lower() == "salir":
            break

        elif texto.lower() == "conv":
            ejemplo = [
                {"emisor": "Usuario A", "texto": "hey do you want to play roblox?"},
                {"emisor": "Usuario B", "texto": "sure, what's your username?"},
                {"emisor": "Usuario A", "texto": "how old are you by the way?"},
                {"emisor": "Usuario B", "texto": "i'm 12"},
                {"emisor": "Usuario A", "texto": "are you home alone right now?"},
                {"emisor": "Usuario A", "texto": "want to meet up sometime?"},
            ]
            analizar_conversacion(ejemplo)

        elif texto:
            pred, probs = clasificar(texto)
            print(f"  {niveles[pred]}")
            print(f"  Bajo: {probs[0]*100:.1f}% | Medio: {probs[1]*100:.1f}% | Alto: {probs[2]*100:.1f}%")


if __name__ == "__main__":
    modo_interactivo()