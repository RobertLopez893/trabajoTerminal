import os
import torch
from transformers import BertTokenizer, BertForSequenceClassification
from peft import PeftModel

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_MODELO  = os.path.join(BASE_DIR, "output", "training_results_v4", "mejor_modelo")
MAX_LEN      = 128
VENTANA      = 5
device       = torch.device("cuda" if torch.cuda.is_available() else "cpu")

niveles = {
    0: "Bajo riesgo",
    1: "Riesgo medio",
    2: "Alto riesgo"
}

print("Cargando modelo base y adaptadores LoRA (V3)...")
tokenizer = BertTokenizer.from_pretrained(RUTA_MODELO)

modelo_base = BertForSequenceClassification.from_pretrained(
    "dccuchile/bert-base-spanish-wwm-cased",
    num_labels=3,
    use_safetensors=True
)

modelo = PeftModel.from_pretrained(modelo_base, RUTA_MODELO)
modelo.to(device)
modelo.eval()
print("¡Modelo ensamblado y cargado con éxito!\n")


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

    prob_bajo = probs[0].item()
    prob_alto = probs[2].item()
    
    # Heurística de incertidumbre (Margen 5%)
    diferencia = abs(prob_alto - prob_bajo)
    if diferencia < 0.05:
        pred = 1  

    # NUEVA: Mitigación de vacío contextual
    # Si hay 3 mensajes o menos y el modelo dicta Alto Riesgo...
    if len(textos_ventana) <= 3 and pred == 2:
        # ...pero la certeza matemática no supera el 95%, lo degradamos a Riesgo Medio
        if prob_alto < 0.95:
            pred = 1  

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
    print("  ANIMOON — prueba de modelo (V3 - Heurística Activa)")
    print("  'salir' para terminar")
    print("  'conv'  para probar caso de ofuscación/grooming clásico")
    print("  'conv2' para probar caso de regalos/extracción")
    print("=" * 50)

    historial_interactivo = []

    while True:
        entrada = input("\nEmisor (A/B) y mensaje, separados por ':'\n> ").strip()

        if entrada.lower() == "salir":
            break

        elif entrada.lower() == "conv":
            historial_interactivo = []
            ejemplo = [
                {"emisor": "Usuario A", "texto": "hola, qué juegas?"},
                {"emisor": "Usuario B", "texto": "roblox, tu?"},
                {"emisor": "Usuario A", "texto": "igual. oye nena cuantos años tienes?"},
                {"emisor": "Usuario B", "texto": "tengo 8 años"},
                {"emisor": "Usuario A", "texto": "estas bien chiquita, pasame tu numero de whatsapp"},
                {"emisor": "Usuario B", "texto": "no puedo, mi mama me regaña"},
                {"emisor": "Usuario A", "texto": "no le digas a tu mama, es nuestro secreto. vete a tu cuarto sola"},
                {"emisor": "Usuario B", "texto": "para que?"},
                {"emisor": "Usuario A", "texto": "quiero que te quites toda la ropa y me mandes foto de tu cuerpo"},
                {"emisor": "Usuario A", "texto": "mandame una foto tuya d3snud4 ahorita mismo o voy a ir a tu casa"},
            ]
            analizar_conversacion(ejemplo)

        elif entrada.lower() == "conv2":
            historial_interactivo = []
            ejemplo_2 = [
                {"emisor": "Usuario A", "texto": "oye juegas muy bien, hacemos equipo?"},
                {"emisor": "Usuario B", "texto": "si claro, invita"},
                {"emisor": "Usuario A", "texto": "te voy a regalar unos pavos para que te compres una skin"},
                {"emisor": "Usuario B", "texto": "en serio?? gracias!"},
                {"emisor": "Usuario A", "texto": "de nada. cuantos años tienes? para saber si te puedo mandar el codigo"},
                {"emisor": "Usuario B", "texto": "tengo 10"},
                {"emisor": "Usuario A", "texto": "ah ok, no le vayas a decir a tus papas porque luego no dejan aceptar regalos de internet"},
                {"emisor": "Usuario B", "texto": "bueno, no les digo"},
                {"emisor": "Usuario A", "texto": "pasame tu insta o tu whats para mandarte el codigo por ahi"},
                {"emisor": "Usuario B", "texto": "no tengo celular, solo la tablet"},
                {"emisor": "Usuario A", "texto": "entonces prende la camara un rato para conocerte y te paso el premio"},
            ]
            analizar_conversacion(ejemplo_2)

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
            print("  Comandos: 'conv', 'conv2', 'reset', 'salir'")


if __name__ == "__main__":
    modo_interactivo()