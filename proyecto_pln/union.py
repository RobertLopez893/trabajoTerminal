import os
import pandas as pd

CORPUS_ORIGINAL = "./output/corpus_final.csv"
SINTETICOS      = "./output/synthetic_grooming.csv"

def main():
    print("=" * 50)
    print("  ANIMOON — Fusión de corpus")
    print("=" * 50)

    if not os.path.exists(CORPUS_ORIGINAL):
        print(f"\nERROR: no se encontró {CORPUS_ORIGINAL}")
        return

    if not os.path.exists(SINTETICOS):
        print(f"\nERROR: no se encontró {SINTETICOS}")
        return

    original  = pd.read_csv(CORPUS_ORIGINAL, encoding="utf-8-sig")
    sintetico = pd.read_csv(SINTETICOS,      encoding="utf-8-sig")

    original["nivel_riesgo"]  = original["nivel_riesgo"].astype(int)
    sintetico["nivel_riesgo"] = sintetico["nivel_riesgo"].astype(int)

    print(f"\n  Corpus original  : {len(original):,} mensajes")
    for nivel, nombre in [(0, "Bajo  "), (1, "Medio "), (2, "Alto  ")]:
        n = (original.nivel_riesgo == nivel).sum()
        print(f"  Clase {nivel} {nombre}: {n:,}")

    print(f"\n  Sintéticos       : {len(sintetico):,} mensajes")
    for nivel, nombre in [(1, "Medio "), (2, "Alto  ")]:
        n = (sintetico.nivel_riesgo == nivel).sum()
        print(f"  Clase {nivel} {nombre}: {n:,}")

    combinado = pd.concat([original, sintetico]).reset_index(drop=True)
    combinado.to_csv(CORPUS_ORIGINAL, index=False, encoding="utf-8-sig")

    print(f"\n  Corpus actualizado: {len(combinado):,} mensajes")
    print(f"\n  Distribución final:")
    for nivel, nombre in [(0, "Bajo  "), (1, "Medio "), (2, "Alto  ")]:
        n   = (combinado.nivel_riesgo == nivel).sum()
        pct = n / len(combinado) * 100
        print(f"  Clase {nivel} {nombre}: {n:>8,}  ({pct:.1f}%)")

    print(f"\n  Mensajes por fuente:")
    fuentes = combinado["id_bloque"].str.split("_").str[0].value_counts()
    for fuente, count in fuentes.items():
        print(f"  {fuente:15}: {count:,}")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()