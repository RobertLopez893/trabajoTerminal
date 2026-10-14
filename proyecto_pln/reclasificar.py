import pandas as pd
from pathlib import Path

# ---------------- CONFIGURACION ----------------
DIRECTORIO_SCRIPT = Path(__file__).resolve().parent
# Asegúrate de poner el nombre de tu archivo completo aquí
ARCHIVO_ENTRADA = DIRECTORIO_SCRIPT / "corpus_final_otro_es.csv"
ARCHIVO_SALIDA = DIRECTORIO_SCRIPT / "corpus_solo_riesgo2.csv"
# ------------------------------------------------

def main():
    print(f"Cargando el archivo desde:\n{ARCHIVO_ENTRADA}")
    try:
        df = pd.read_csv(ARCHIVO_ENTRADA, encoding="utf-8-sig")
    except UnicodeDecodeError:
        df = pd.read_csv(ARCHIVO_ENTRADA, encoding="latin-1")
        
    print(f"Mensajes totales originales: {len(df)}")
    print(f"Conversaciones (bloques) totales: {df['id_bloque'].nunique()}")
    
    # 1. Asegurarnos de que el nivel de riesgo se lea correctamente como texto
    df['nivel_riesgo'] = df['nivel_riesgo'].astype(str).str.strip()
    
    # 2. Identificar qué bloques tienen AL MENOS UN mensaje con riesgo "2"
    # Esto filtra las filas con '2' y extrae los id_bloque únicos
    bloques_con_riesgo = df[df['nivel_riesgo'] == '2']['id_bloque'].unique()
    
    print(f"\nConversaciones encontradas con riesgo '2': {len(bloques_con_riesgo)}")
    
    if len(bloques_con_riesgo) == 0:
        print("No se encontró ningún mensaje con nivel de riesgo 2.")
        return

    # 3. Filtrar el dataframe original para quedarnos con TODA la conversación de esos bloques
    df_filtrado = df[df['id_bloque'].isin(bloques_con_riesgo)].copy()
    
    # 4. Asegurarnos de mantener el orden secuencial de los mensajes
    df_filtrado['orden_temp'] = pd.to_numeric(df_filtrado['orden_mensaje'], errors='coerce')
    df_filtrado = df_filtrado.sort_values(by=['id_bloque', 'orden_temp'])
    df_filtrado = df_filtrado.drop(columns=['orden_temp'])
    
    print(f"Mensajes totales extraídos (contexto completo): {len(df_filtrado)}")
    
    # Guardar en un nuevo archivo
    df_filtrado.to_csv(ARCHIVO_SALIDA, index=False, encoding="utf-8-sig")
    print(f"\n¡Listo! Archivo guardado en:\n{ARCHIVO_SALIDA}")

if __name__ == "__main__":
    main()