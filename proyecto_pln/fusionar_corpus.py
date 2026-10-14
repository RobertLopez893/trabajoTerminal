import pandas as pd
from pathlib import Path

# --- RUTAS DINÁMICAS ---
DIRECTORIO_SCRIPT = Path(__file__).resolve().parent

# Tu corpus anterior
RUTA_DEFINITIVO_ANT = DIRECTORIO_SCRIPT / "output" / "corpus_definitivo_v2.csv"

# El archivo que acabamos de generar con los riesgos de grooming
RUTA_NUEVO_RIESGO = DIRECTORIO_SCRIPT / "corpus_sintetico_casos_borde.csv"

# El nuevo archivo resultante
RUTA_SALIDA = DIRECTORIO_SCRIPT / "output" / "corpus_definitivo_v3.csv"

def main():
    print("1. Cargando datasets...")
    try:
        # Dejamos que Pandas infiera los tipos de datos automáticamente
        df_def = pd.read_csv(RUTA_DEFINITIVO_ANT, encoding="utf-8-sig")
        df_nuevo = pd.read_csv(RUTA_NUEVO_RIESGO, encoding="utf-8-sig")
    except FileNotFoundError as e:
        print(f"Error: No se encontró el archivo en:\n{e.filename}\nRevisa que las rutas sean correctas.")
        return

    print(f" -> Corpus definitivo anterior cargado con {len(df_def)} filas.")
    print(f" -> Corpus nuevo de riesgo cargado con {len(df_nuevo)} filas.")

    print("\n2. Normalizando y limpiando etiquetas...")
    # Convertimos la columna a número. Si hay texto basura, lo vuelve NaN
    df_def['nivel_riesgo'] = pd.to_numeric(df_def['nivel_riesgo'], errors='coerce')
    df_nuevo['nivel_riesgo'] = pd.to_numeric(df_nuevo['nivel_riesgo'], errors='coerce')

    # Filtramos para quedarnos solo con 0, 1 y 2
    df_def = df_def[df_def['nivel_riesgo'].isin([0, 1, 2])].copy()
    df_nuevo = df_nuevo[df_nuevo['nivel_riesgo'].isin([0, 1, 2])].copy()

    print(f" -> Tras limpiar, el corpus anterior conservó {len(df_def)} filas.")
    print(f" -> Tras limpiar, el corpus nuevo conservó {len(df_nuevo)} filas.")

    print("\n3. Protegiendo IDs de conversación...")
    # Aseguramos que el id_bloque sea string antes de concatenar
    df_nuevo['id_bloque'] = 'ext_' + df_nuevo['id_bloque'].astype(str)

    print("4. Fusionando datasets...")
    df_final = pd.concat([df_def, df_nuevo], ignore_index=True)
    
    # Convertimos el riesgo a entero puro para quitar cualquier ".0" visual
    df_final['nivel_riesgo'] = df_final['nivel_riesgo'].astype(int)

    print("5. Guardando el Corpus Definitivo V3...")
    RUTA_SALIDA.parent.mkdir(parents=True, exist_ok=True)
    df_final.to_csv(RUTA_SALIDA, index=False, encoding="utf-8-sig")

    print(f"\n¡Corpus fusionado con éxito en:\n{RUTA_SALIDA}")
    print("\nEstadísticas finales de nivel_riesgo:")
    print(df_final['nivel_riesgo'].value_counts())

if __name__ == "__main__":
    main()