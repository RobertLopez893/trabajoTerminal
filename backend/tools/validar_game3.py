import json
import sys
from pathlib import Path

RUTA = Path(__file__).resolve().parent.parent / "data" / "game3_conversaciones.json"
MIN_MENSAJES = 6
MAX_MENSAJES = 10
EMISORES = {"yo", "otro"}


def validar(ruta: Path) -> int:
    errores = []

    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
    except (OSError, json.JSONDecodeError) as e:
        print(f"[ERROR] No se pudo leer {ruta}: {e}")
        return 1

    conversaciones = datos.get("conversaciones")
    if not isinstance(conversaciones, list) or not conversaciones:
        print("[ERROR] Falta la lista 'conversaciones' o está vacía.")
        return 1

    ids = set()
    con_riesgo = 0

    for indice, conv in enumerate(conversaciones, start=1):
        etiqueta = conv.get("id", f"#{indice}")

        for campo in ("id", "contacto", "riesgo", "mensajes", "retroalimentacion"):
            if campo not in conv:
                errores.append(f"{etiqueta}: falta el campo '{campo}'")

        if conv.get("id") in ids:
            errores.append(f"{etiqueta}: id repetido")
        ids.add(conv.get("id"))

        if not isinstance(conv.get("riesgo"), bool):
            errores.append(f"{etiqueta}: 'riesgo' debe ser true o false")
        elif conv["riesgo"]:
            con_riesgo += 1

        mensajes = conv.get("mensajes", [])
        if not (MIN_MENSAJES <= len(mensajes) <= MAX_MENSAJES):
            errores.append(f"{etiqueta}: tiene {len(mensajes)} mensajes (debe tener entre {MIN_MENSAJES} y {MAX_MENSAJES})")

        for n, msg in enumerate(mensajes, start=1):
            if msg.get("emisor") not in EMISORES:
                errores.append(f"{etiqueta}: mensaje {n} con emisor inválido (usa 'yo' u 'otro')")
            if not str(msg.get("texto", "")).strip():
                errores.append(f"{etiqueta}: mensaje {n} sin texto")

        if not any(m.get("emisor") == "otro" for m in mensajes):
            errores.append(f"{etiqueta}: no tiene mensajes del contacto ('otro')")

    seguras = len(conversaciones) - con_riesgo
    print(f"Conversaciones: {len(conversaciones)} (seguras: {seguras}, con riesgo: {con_riesgo})")

    if con_riesgo < 3:
        errores.append("Se necesitan al menos 3 conversaciones con riesgo para armar partidas balanceadas")
    if seguras < 3:
        errores.append("Se necesitan al menos 3 conversaciones seguras para armar partidas balanceadas")

    if errores:
        print("\nProblemas encontrados:")
        for error in errores:
            print(f" - {error}")
        return 1

    print("Todo en orden.")
    return 0


if __name__ == "__main__":
    ruta = Path(sys.argv[1]) if len(sys.argv) > 1 else RUTA
    sys.exit(validar(ruta))
