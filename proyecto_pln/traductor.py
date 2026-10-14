import argparse
import json
import re
from pathlib import Path

import pandas as pd
import torch
from tqdm import tqdm
from transformers import MarianMTModel, MarianTokenizer

# ---------------- CONFIGURACION ----------------
# Ruta dinámica: Busca automáticamente en la misma carpeta donde está guardado traductor.py
DIRECTORIO_SCRIPT = Path(__file__).resolve().parent
RUTA_POR_DEFECTO = DIRECTORIO_SCRIPT / "corpus_final otro.csv"

COL_TEXTO = "texto_mensaje"   # columna con el mensaje
COL_FUENTE = "id_bloque"      # columna para identificar PAN-12
VALOR_FUENTE = None           # None = se detecta con el patron

PATRON_PAN12 = re.compile(r"^\s*pan[\s_\-]*(?:20)?12", re.IGNORECASE)
NOMBRES_TEXTO = ["texto", "text", "mensaje", "message", "msg", "contenido", "content"]

MODELO = "Helsinki-NLP/opus-mt-en-es"
BATCH_SIZE = 64         # Si te da error de memoria de video, bajalo a 32 o 16
MAX_TOKENS = 128
# ------------------------------------------------

def leer_csv(ruta):
    for enc in ("utf-8-sig", "latin-1"):
        try:
            return pd.read_csv(ruta, sep=None, engine="python", encoding=enc, dtype=str, keep_default_na=False)
        except UnicodeDecodeError:
            continue
    raise RuntimeError("No pude leer el CSV por problemas de codificación.")

def detectar_fuente(df):
    """Devuelve una mascara booleana con las filas de PAN-12."""
    columnas = [COL_FUENTE] if COL_FUENTE in df.columns else list(df.columns)
    for col in columnas:
        serie = df[col].astype(str)
        if VALOR_FUENTE is not None:
            mascara = serie.str.strip().str.lower() == VALOR_FUENTE.lower()
        else:
            if COL_FUENTE not in df.columns and serie.nunique() > 200:
                continue
            mascara = serie.str.contains(PATRON_PAN12, na=False)
        if mascara.any():
            print(f"Columna de fuente detectada: '{col}' -> {int(mascara.sum())} filas de PAN-12 (Serán ignoradas)")
            return mascara
    return pd.Series([False] * len(df)) # Si no encuentra, asume que nada es PAN-12

def detectar_texto(df):
    if COL_TEXTO in df.columns:
        return COL_TEXTO
    for nombre in NOMBRES_TEXTO:
        for col in df.columns:
            if col.strip().lower() == nombre:
                return col
    return None

# ---------- CONFIGURACIÓN DE GPU Y MODELO ----------
dispositivo = "cuda" if torch.cuda.is_available() else "cpu"
if dispositivo == "cuda":
    print(f"✅ Tarjeta gráfica detectada: {torch.cuda.get_device_name(0)}")
    tipo_dato = torch.float16  # Acelera enormemente la inferencia
else:
    print("⚠️ No se detectó GPU (CUDA). Usando CPU.")
    tipo_dato = torch.float32

print("Cargando modelo...")
tokenizer = MarianTokenizer.from_pretrained(MODELO)
# Se añadió use_safetensors=True para solucionar el error de seguridad de PyTorch
modelo = MarianMTModel.from_pretrained(MODELO, torch_dtype=tipo_dato, use_safetensors=True).to(dispositivo)
modelo.eval()


def traducir_lote(textos):
    entradas = tokenizer(textos, return_tensors="pt", padding=True, truncation=True,
                         max_length=MAX_TOKENS).to(dispositivo)
    with torch.no_grad():
        salidas = modelo.generate(**entradas, max_length=MAX_TOKENS, num_beams=4)
    return tokenizer.batch_decode(salidas, skip_special_tokens=True)


def traducir_unicos(textos, cache, ruta_cache):
    pendientes = sorted({t for t in textos if t.strip() and t not in cache}, key=len)
    
    if not pendientes:
        print("¡Todos los textos ya estaban en el caché! No hay nada nuevo que traducir.")
        return

    print(f"Textos nuevos a traducir: {len(pendientes)}")
    for i in tqdm(range(0, len(pendientes), BATCH_SIZE), desc="Traduciendo con GPU", unit="lote"):
        lote = pendientes[i:i + BATCH_SIZE]
        for original, traducido in zip(lote, traducir_lote(lote)):
            cache[original] = traducido
        
        if (i // BATCH_SIZE) % 50 == 0:
            ruta_cache.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
            
    ruta_cache.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")


def recolectar(nodo, acc):
    if isinstance(nodo, dict):
        if isinstance(nodo.get("texto"), str):
            acc.append(nodo)
        for v in nodo.values():
            recolectar(v, acc)
    elif isinstance(nodo, list):
        for v in nodo:
            recolectar(v, acc)


def main():
    parser = argparse.ArgumentParser(description="Traduce el CSV ignorando las filas de PAN-12.")
    parser.add_argument("--input", "-i", type=str, default=str(RUTA_POR_DEFECTO))
    parser.add_argument("--output", "-o", type=str, default=None)
    parser.add_argument("--cache", "-c", type=str, default=None)
    
    args = parser.parse_args()

    ruta_csv = Path(args.input).resolve()
    ruta_salida = Path(args.output).resolve() if args.output else ruta_csv.with_name("corpus_final_otro_es.csv")
    ruta_cache = Path(args.cache).resolve() if args.cache else ruta_csv.with_name("cache_traducciones_otros.json")

    if not ruta_csv.exists():
        print(f"\nError: No se encontró el archivo en:\n{ruta_csv}")
        return

    df = leer_csv(ruta_csv)
    print(f"Archivo cargado. Filas totales en el CSV original: {len(df)}")

    # Detectar PAN-12 e invertir la máscara para quedarnos con el RESTO
    mascara_pan12 = detectar_fuente(df)
    sub = df[~mascara_pan12].copy()  
    
    print(f"Filas a traducir (excluyendo PAN-12): {len(sub)}")
    
    if len(sub) == 0:
        print("No hay filas para traducir después de quitar PAN-12.")
        return

    col_texto = detectar_texto(sub)
    if col_texto is None:
        print("No pude detectar la columna de texto. Verifica el nombre en COL_TEXTO.")
        return
    
    # Limpiar columnas vacías basura
    sub = sub.drop(columns=[c for c in sub.columns if c.startswith("Unnamed") and (sub[c].str.strip() == "").all()])

    cache = {}
    if ruta_cache.exists():
        cache = json.loads(ruta_cache.read_text(encoding="utf-8"))
        print(f"Caché cargado: {len(cache)} textos previos.")

    # Caso 1: JSON en las celdas
    primera = next((v for v in sub[col_texto] if str(v).strip()), "")
    if str(primera).lstrip()[:1] in ("[", "{"):
        print("Detectado formato JSON en las celdas.")
        parseados, mensajes = [], []
        for celda in sub[col_texto]:
            try:
                obj = json.loads(celda)
            except (json.JSONDecodeError, TypeError):
                obj = None
            parseados.append(obj)
            if obj is not None:
                recolectar(obj, mensajes)
                
        traducir_unicos([m["texto"] for m in mensajes], cache, ruta_cache)
        
        for m in mensajes:
            m["texto"] = cache.get(m["texto"], m["texto"])
        sub[col_texto] = [
            json.dumps(o, ensure_ascii=False) if o is not None else c
            for o, c in zip(parseados, sub[col_texto])
        ]
    # Caso 2: Texto plano
    else:
        textos_limpios = sub[col_texto].fillna("").astype(str).tolist()
        traducir_unicos(textos_limpios, cache, ruta_cache)
        sub[col_texto] = sub[col_texto].map(lambda t: cache.get(t, t))

    sub.to_csv(ruta_salida, index=False, encoding="utf-8-sig")
    print(f"¡Listo! {len(sub)} filas procesadas (sin PAN-12) y guardadas en:\n{ruta_salida}")

if __name__ == "__main__":
    main()