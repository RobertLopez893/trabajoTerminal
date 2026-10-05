import os
import json
import pandas as pd
from openai import OpenAI
from tqdm import tqdm

cliente = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

PROMPT_SISTEMA = """
Eres un generador de datos sintéticos experto en ciberseguridad infantil y lingüística forense para México.
Simula bloques de chat (entre 5 y 10 mensajes) entre dos roles:
- "Usuario A": Un adulto depredador haciéndose pasar por menor o joven.
- "Usuario B": Un menor mexicano (entre 6 y 8 años).

Niveles de riesgo a generar (ELIGE SOLO UNO para el bloque principal):
- Nivel 0 (Bajo): Charla normal de videojuegos (Roblox, Free Fire, Minecraft), escuela o memes. Sin malicia.
- Nivel 1 (Medio): El Usuario A sondea. Pregunta edad, de qué estado de México es, intenta aislarlo ("tus papás no te entienden (puedes usar modismos como 'jefes')", "es un secreto"), o pide cambiar de app ("pásame tu whats", "tienes insta?").
- Nivel 2 (Alto): Grooming explícito. El Usuario A pide fotografías privadas ("pasa pack", "manda foto sin ropa"), ubicación exacta, o intenta verse en persona ("nos vemos en la plaza", "no le digas a tus papás", "pásame la dirección de tu escuela", "a qué hora te quedas solo/a?").

CRÍTICO - ESTILO DE LENGUAJE:
- Ocasionalmente, los mensajes deben estar en español con jerga mexicana de internet ("wey", "neta", "chido", "morro", "jefes", "whats", "bro").
- Usa lenguaje altamente informal y simula errores tipográficos comunes en chat (escribir "q" o "k" en vez de "que", omitir tildes, faltas de ortografía leves).

Devuelve ÚNICAMENTE un JSON válido con esta estructura:
{
  "riesgo_objetivo": 1,
  "mensajes": [
    {"orden": 1, "emisor": "Usuario A", "texto": "q onda wey, juegas free fire?", "nivel_riesgo_individual": 0},
    {"orden": 2, "emisor": "Usuario B", "texto": "si, pasa tu id", "nivel_riesgo_individual": 0},
    {"orden": 3, "emisor": "Usuario A", "texto": "va, oye y cuantos años tienes neta?", "nivel_riesgo_individual": 1}
  ]
}
"""

def generar_bloque(id_bloque):
    respuesta = cliente.chat.completions.create(
        model="llama3.1", 
        messages=[
            {"role": "system", "content": PROMPT_SISTEMA},
            {"role": "user", "content": "Genera un nuevo bloque de conversación aleatorio. Varía el tema y el nivel de riesgo."}
        ],
        temperature=0.85,
        response_format={ "type": "json_object" }
    )
    
    datos = json.loads(respuesta.choices[0].message.content)
    filas = []
    
    # Implementación a prueba de fallos usando .get()
    lista_mensajes = datos.get("mensajes", [])
    
    for idx, msg in enumerate(lista_mensajes):
        nivel = msg.get("nivel_riesgo_individual", msg.get("nivel_riesgo", 0))
        orden = msg.get("orden", idx + 1)
        emisor = msg.get("emisor", "Usuario A" if idx % 2 == 0 else "Usuario B")
        texto = msg.get("texto", msg.get("mensaje", ""))
        
        if texto:
            filas.append({
                "id_bloque": id_bloque,
                "orden_mensaje": orden,
                "emisor": emisor,
                "texto_mensaje": texto,
                "nivel_riesgo": nivel
            })
            
    return filas

def crear_corpus(num_bloques=500):
    todas_las_filas = []
    print(f"Generando {num_bloques} bloques de conversación...")
    
    for i in tqdm(range(num_bloques)):
        try:
            bloque = generar_bloque(f"auto_{i}")
            todas_las_filas.extend(bloque)
        except Exception as e:
            print(f"Error crítico en bloque {i}: {e}")
            
    df = pd.DataFrame(todas_las_filas)
    os.makedirs("output", exist_ok=True)
    df.to_csv("output/corpus_sintetico_llm.csv", index=False, encoding="utf-8-sig")
    print(f"Corpus guardado. Total de mensajes: {len(df)}")

if __name__ == "__main__":
    crear_corpus(1500)