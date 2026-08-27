# corpus_builder.py — ANIMOON v4
# Fuentes: PAN12 (test corpus) + PJZC (JsonData/PJZC.txt)
# Sin traducción — corpus en inglés
# Formato: id_bloque | orden_mensaje | emisor | texto_mensaje | nivel_riesgo

import os
import re
import json
import xml.etree.ElementTree as ET
import pandas as pd
from tqdm import tqdm

# ─────────────────────────────────────────────
# RUTAS — ajustadas a tu estructura exacta
# ─────────────────────────────────────────────
RAW_DIR    = "./raw_data"
DICT_DIR   = "./dictionaries"
OUTPUT_DIR = "./output"

# PAN12 — corpus de test (el que tienes descargado)
PAN12_DIR  = os.path.join(RAW_DIR, "pan12",
             "pan12-sexual-predator-identification-test-corpus-2012-05-21")
PAN12_XML  = os.path.join(PAN12_DIR,
             "pan12-sexual-predator-identification-test-corpus-2012-05-17.xml")
# Ground truth problema 1 (identificación de predadores) — el que necesitamos
PAN12_GT   = os.path.join(PAN12_DIR,
             "pan12-sexual-predator-identification-groundtruth-problem1.txt")

# PJZC — usamos el JSON completo (mejor que los CSV para mantener estructura de conversación)
PJZC_JSON  = os.path.join(RAW_DIR, "pjzc", "BF-PSR-Framework-main",
             "JsonData", "PJZC.txt")

# Diccionario de slang
SLANG_JSON = os.path.join(DICT_DIR, "slang_dict.json")

# Salida
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "corpus_final.csv")

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ─────────────────────────────────────────────
# PASO A — Cargar diccionario de slang
# ─────────────────────────────────────────────
def load_slang():
    with open(SLANG_JSON, "r", encoding="utf-8") as f:
        slang = json.load(f)
    combined = {**slang.get("en_slang", {}), **slang.get("es_slang", {})}
    print(f"  Diccionario cargado: {len(combined)} entradas")
    return combined


# ─────────────────────────────────────────────
# PASO B — Limpieza y preprocesamiento de texto
# ─────────────────────────────────────────────
def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = re.sub(r'<[^>]+>', '', text)                         # HTML tags
    text = re.sub(r'http\S+|www\.\S+', '', text)                # URLs
    text = re.sub(r'\S+@\S+', '', text)                         # correos
    text = re.sub(r'&amp;|&lt;|&gt;|&apos;|&quot;', ' ', text) # HTML entities
    text = re.sub(r'[\r\n\t]+', ' ', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()

def expand_slang(text, slang_dict):
    tokens = text.lower().split()
    return ' '.join([slang_dict.get(t, t) for t in tokens])

def preprocess(text, slang_dict):
    text = clean_text(text)
    text = expand_slang(text, slang_dict)
    return text


# ─────────────────────────────────────────────
# PASO C — Etiquetado por palabras clave (inglés)
# ─────────────────────────────────────────────
KEYWORDS_HIGH = [
    "when are your parents", "when will you be alone", "home alone",
    "what time do your parents", "when do your parents leave",
    "send me a pic", "send me a photo", "send me a picture",
    "send me a video", "nude", "naked", "without clothes",
    "take off your", "touch yourself", "on webcam", "on camera",
    "come to my place", "come over", "meet in person", "meet up",
    "don't tell anyone", "keep it secret", "our little secret",
    "don't tell your parents", "just between us",
    "have sex", "sexual", "make love", "sleep with me",
]

KEYWORDS_MEDIUM = [
    "how old are you", "what's your name", "where do you live",
    "what school do you go", "phone number", "give me your number",
    "your address", "are you alone", "are you home alone",
    "do you have a boyfriend", "do you have a girlfriend",
    "you're so mature", "you seem older than", "you're special",
    "only you understand", "no one understands you like",
    "add me on", "message me on", "text me on", "find me on",
    "kik me", "snap me", "hit me up on",
    "you're pretty", "you're beautiful", "you're cute", "you're hot",
    "i really like you", "i think i love you",
    "can i see you", "want to meet",
    "your parents don't understand", "your friends don't get it",
    "trust me", "i would never hurt you",
]

def label_risk(text):
    """
    0 = Bajo riesgo  (conversación normal)
    1 = Riesgo medio (solicitud de datos personales, elogios excesivos, intento de cambio de plataforma)
    2 = Alto riesgo  (solicitud de imágenes, encuentro físico, lenguaje sexual, aislamiento)
    """
    t = text.lower()
    for kw in KEYWORDS_HIGH:
        if kw in t:
            return 2
    for kw in KEYWORDS_MEDIUM:
        if kw in t:
            return 1
    return 0


# ─────────────────────────────────────────────
# PASO D — Parser PAN12
# Ground truth problem1.txt: una línea = un ID de conversación predatoria
# ─────────────────────────────────────────────
def parse_pan12(xml_path, gt_path, slang_dict):
    print("  Parseando PAN12...")

    # Ground truth problem1.txt — cada línea es un ID de autor predador
    predators = set()
    with open(gt_path, 'r', encoding='utf-8') as f:
        for line in f:
            pid = line.strip()
            if pid:
                predators.add(pid)
    print(f"  IDs de predadores en ground truth: {len(predators)}")

    # Parsear XML — iterparse para manejar el archivo de 394MB eficientemente
    print("  Cargando XML (394MB, puede tardar ~1 min)...")
    context = ET.iterparse(xml_path, events=('start', 'end'))

    rows      = []
    usadas    = 0
    omitidas  = 0
    conv_id   = None
    messages  = []
    in_conv   = False

    for event, elem in tqdm(context, desc="  Procesando XML", mininterval=2.0):

        if event == 'start' and elem.tag == 'conversation':
            conv_id  = elem.get('id', 'unknown')
            messages = []
            in_conv  = True

        elif event == 'end' and elem.tag == 'message' and in_conv:
            author_elem = elem.find('author')
            text_elem   = elem.find('text')
            author = author_elem.text.strip() if author_elem is not None and author_elem.text else ""
            text   = text_elem.text           if text_elem   is not None and text_elem.text   else ""
            messages.append({'author': author, 'text': text})
            elem.clear()  # liberar memoria

        elif event == 'end' and elem.tag == 'conversation' and in_conv:
            in_conv = False

            if not messages:
                omitidas += 1
                elem.clear()
                continue

            # Identificar predador en esta conversación
            authors_in_conv = list(dict.fromkeys([m['author'] for m in messages]))
            predator_author = next((a for a in authors_in_conv if a in predators), None)

            if predator_author is None:
                omitidas += 1
                elem.clear()
                continue

            usadas += 1
            for i, msg in enumerate(messages):
                emisor = "Usuario A" if msg['author'] == predator_author else "Usuario B"
                texto  = preprocess(msg['text'], slang_dict)

                if not texto or len(texto.split()) < 2:
                    continue

                rows.append({
                    'id_bloque':     f"pan12_{conv_id}",
                    'orden_mensaje': i + 1,
                    'emisor':        emisor,
                    'texto_mensaje': texto,
                    'nivel_riesgo':  label_risk(texto)
                })

            elem.clear()

    print(f"  Conversaciones usadas: {usadas} | Omitidas (sin predador): {omitidas}")
    print(f"  Mensajes extraídos de PAN12: {len(rows):,}")
    return rows


# ─────────────────────────────────────────────
# PASO E — Parser PJZC (JsonData/PJZC.txt)
# Estructura JSON: {"conversation": [{id, source, label, messages:[{author,time,text}]}]}
# label: "1"=grooming, "0"=no grooming
# author: "decoy"=víctima, cualquier otro=predador
# ─────────────────────────────────────────────
def parse_pjzc(json_path, slang_dict):
    print(f"  Parseando PJZC desde {os.path.basename(json_path)}...")

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # El JSON tiene clave 'conversation' según el README del repo
    conversations = data.get('conversation', [])
    if not conversations:
        # Intentar si es lista directamente
        conversations = data if isinstance(data, list) else []

    print(f"  Conversaciones encontradas: {len(conversations):,}")

    grooming     = 0
    no_grooming  = 0
    rows         = []

    for conv in tqdm(conversations, desc="  Conversaciones PJZC"):
        conv_id  = conv.get('id', 'unknown')
        label    = str(conv.get('label', '0'))   # '1'=grooming, '0'=no grooming
        messages = conv.get('messages', [])

        if label == '1':
            grooming += 1
        else:
            no_grooming += 1

        if not messages:
            continue

        for i, msg in enumerate(messages):
            autor = str(msg.get('author', '')).lower().strip()
            texto = preprocess(msg.get('text', ''), slang_dict)

            if not texto or len(texto.split()) < 2:
                continue

            # 'decoy' = voluntario que simula ser menor → víctima → Usuario B
            # cualquier otro autor = predador → Usuario A
            emisor = "Usuario B" if autor == 'decoy' else "Usuario A"

            rows.append({
                'id_bloque':     f"pjzc_{conv_id}",
                'orden_mensaje': i + 1,
                'emisor':        emisor,
                'texto_mensaje': texto,
                # Si es grooming aplicamos keywords; si no, nivel 0 siempre
                'nivel_riesgo':  label_risk(texto) if label == '1' else 0
            })

    print(f"  Conversaciones grooming: {grooming:,} | No grooming: {no_grooming:,}")
    print(f"  Mensajes extraídos de PJZC: {len(rows):,}")
    return rows


# ─────────────────────────────────────────────
# PASO F — Main
# ─────────────────────────────────────────────
def main():
    print("=" * 57)
    print("  ANIMOON — Corpus Builder v4")
    print("  Fuentes: PAN12 (test) + PJZC | Inglés | Sin traducción")
    print("=" * 57)
    print()

    # Verificar archivos antes de empezar
    print("[0/4] Verificando archivos...")
    archivos = {
        "PAN12 XML"  : PAN12_XML,
        "PAN12 GT"   : PAN12_GT,
        "PJZC JSON"  : PJZC_JSON,
        "Slang dict" : SLANG_JSON,
    }
    todo_ok = True
    for nombre, ruta in archivos.items():
        existe = os.path.exists(ruta)
        estado = "✓" if existe else "✗ NO ENCONTRADO"
        print(f"  {estado}  {nombre}: {ruta}")
        if not existe:
            todo_ok = False

    if not todo_ok:
        print("\n  ADVERTENCIA: Algunos archivos no se encontraron.")
        print("  El script continuará pero puede generar un corpus incompleto.\n")

    # 1. Diccionario
    print("\n[1/4] Cargando diccionario de slang...")
    slang_dict = load_slang()

    all_rows = []

    # 2. PAN12
    print("\n[2/4] Procesando PAN12...")
    if os.path.exists(PAN12_XML) and os.path.exists(PAN12_GT):
        pan12_rows = parse_pan12(PAN12_XML, PAN12_GT, slang_dict)
        all_rows.extend(pan12_rows)
    else:
        print("  PAN12 no disponible — se omite.")

    # 3. PJZC
    print("\n[3/4] Procesando PJZC...")
    if os.path.exists(PJZC_JSON):
        pjzc_rows = parse_pjzc(PJZC_JSON, slang_dict)
        all_rows.extend(pjzc_rows)
    else:
        print(f"  PJZC no disponible — se omite.")
        print(f"  Esperado en: {PJZC_JSON}")

    # 4. Guardar
    print(f"\n[4/4] Guardando corpus final...")
    if not all_rows:
        print("  ERROR: No se extrajeron mensajes. Revisa las rutas y archivos.")
        return

    df = pd.DataFrame(all_rows, columns=[
        'id_bloque', 'orden_mensaje', 'emisor', 'texto_mensaje', 'nivel_riesgo'
    ])
    df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')

    # Estadísticas finales
    print(f"\n{'=' * 57}")
    print(f"  ✓ Corpus guardado en: {OUTPUT_CSV}")
    print(f"  Total mensajes      : {len(df):,}")
    print(f"\n  Distribución de clases (nivel_riesgo):")
    etiquetas = {0: "Bajo  ", 1: "Medio ", 2: "Alto  "}
    dist = df['nivel_riesgo'].value_counts().sort_index()
    for nivel, count in dist.items():
        pct = count / len(df) * 100
        print(f"    {nivel} — {etiquetas[nivel]}: {count:,}  ({pct:.1f}%)")
    print(f"\n  Mensajes por fuente:")
    fuentes = df['id_bloque'].str.split('_').str[0].value_counts()
    for fuente, count in fuentes.items():
        print(f"    {fuente:10}: {count:,}")
    print(f"{'=' * 57}")


if __name__ == "__main__":
    main()