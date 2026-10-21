"""
Monitor de Recursos de Docker para Animoon (AWS EC2 t3.micro Benchmark)
Mide en tiempo real o en intervalos el consumo de CPU, Memoria RAM (MB y %),
PIDs y Network I/O de los 5 contenedores del stack Animoon:
1. animoon_beto_worker
2. animoon_chat
3. animoon_backend
4. animoon_postgres
5. animoon_redis
"""

import sys
import time
import subprocess
import re
import argparse

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

CONTAINERS = [
    "animoon_beto_worker",
    "animoon_chat",
    "animoon_backend",
    "animoon_postgres",
    "animoon_redis"
]

AWS_T3_MICRO_RAM_MB = 1024.0  # 1 GB RAM en t3.micro


def parse_memory_to_mb(mem_str: str) -> float:
    """Convierte cadenas como '755.4MiB' o '1.2GiB' a float en MiB."""
    mem_str = mem_str.strip()
    match = re.match(r"^([0-9.]+)\s*([a-zA-Z]+)$", mem_str)
    if not match:
        return 0.0
    val, unit = float(match.group(1)), match.group(2).lower()
    if "gib" in unit or "gb" in unit:
        return val * 1024.0
    elif "kib" in unit or "kb" in unit:
        return val / 1024.0
    elif "b" == unit:
        return val / (1024.0 * 1024.0)
    return val  # mib o mb


def obtener_metricas_docker():
    """Ejecuta docker stats y retorna diccionario estructurado."""
    cmd = [
        "docker", "stats", "--no-stream",
        "--format", "{{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.PIDs}}"
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    except Exception as e:
        return None, str(e)

    datos = {}
    for linea in res.stdout.strip().split("\n"):
        if not linea.strip():
            continue
        partes = linea.split("\t")
        if len(partes) >= 6:
            c_name = partes[0].strip()
            if c_name in CONTAINERS:
                cpu_raw = partes[1].replace("%", "").strip()
                mem_usage_raw = partes[2].split("/")[0].strip()
                mem_perc_raw = partes[3].replace("%", "").strip()
                net_io = partes[4].strip()
                pids = partes[5].strip()

                datos[c_name] = {
                    "cpu_perc": float(cpu_raw) if cpu_raw.replace(".", "").isdigit() else 0.0,
                    "mem_mb": parse_memory_to_mb(mem_usage_raw),
                    "mem_raw": mem_usage_raw,
                    "mem_perc": float(mem_perc_raw) if mem_perc_raw.replace(".", "").isdigit() else 0.0,
                    "net_io": net_io,
                    "pids": pids
                }
    return datos, None


def imprimir_dashboard(datos):
    """Muestra un dashboard visual en la terminal."""
    total_ram_mb = sum(c["mem_mb"] for c in datos.values())
    total_cpu = sum(c["cpu_perc"] for c in datos.values())
    pct_t3_micro = (total_ram_mb / AWS_T3_MICRO_RAM_MB) * 100.0

    print("\n" + "═" * 85)
    print("📊 DASHBOARD DE RECURSOS EN VIVO — STACK ANIMOON")
    print("═" * 85)
    print(f"{'CONTENEDOR':<25} | {'CPU %':<9} | {'RAM (MB)':<12} | {'RAM HOST %':<10} | {'PIDs':<6} | {'NET I/O'}")
    print("─" * 85)

    for c_name in CONTAINERS:
        if c_name in datos:
            d = datos[c_name]
            print(f"{c_name:<25} | {d['cpu_perc']:>7.2f}% | {d['mem_mb']:>9.2f} MB | {d['mem_perc']:>8.2f}% | {d['pids']:>6} | {d['net_io']}")
        else:
            print(f"{c_name:<25} | {'OFFLINE':<9} | {'0.00 MB':<12} | {'0.00%':<10} | {'0':<6} | -")

    print("─" * 85)
    print(f"  TOTAL STACK RAM:     {total_ram_mb:>.2f} MB  ({pct_t3_micro:>.1f}% del límite de 1 GB en AWS EC2 t3.micro)")
    print(f"  TOTAL CPU STACK:     {total_cpu:>.2f}%")
    
    # Barra de consumo visual
    bar_len = 35
    filled = int((pct_t3_micro / 100.0) * bar_len)
    filled = min(filled, bar_len)
    barra = "█" * filled + "░" * (bar_len - filled)
    estado_ram = "🟢 ÓPTIMO" if pct_t3_micro < 80 else ("🟡 ALERTA" if pct_t3_micro <= 100 else "🔴 SOBREGIRADO")
    print(f"  USO AWS t3.micro:    [{barra}] {pct_t3_micro:>.1f}% {estado_ram}")
    print("═" * 85)


def modo_live(intervalo: float = 2.0):
    print("[*] Iniciando modo Live (presiona Ctrl+C para salir)...")
    try:
        while True:
            datos, err = obtener_metricas_docker()
            if err:
                print(f"[!] Error: {err}")
            elif datos:
                imprimir_dashboard(datos)
            time.sleep(intervalo)
    except KeyboardInterrupt:
        print("\n[*] Monitor finalizado.")


def modo_benchmark(duracion: int = 15, intervalo: float = 1.0):
    print(f"[*] Ejecutando benchmark de recursos durante {duracion} segundos (muestreo cada {intervalo}s)...")
    historial = {c: {"cpu": [], "ram": []} for c in CONTAINERS}
    total_ram_muestras = []

    start = time.time()
    while time.time() - start < duracion:
        datos, _ = obtener_metricas_docker()
        if datos:
            total_inst = 0.0
            for c_name in CONTAINERS:
                if c_name in datos:
                    historial[c_name]["cpu"].append(datos[c_name]["cpu_perc"])
                    historial[c_name]["ram"].append(datos[c_name]["mem_mb"])
                    total_inst += datos[c_name]["mem_mb"]
            total_ram_muestras.append(total_inst)
        time.sleep(intervalo)

    print("\n" + "═" * 85)
    print(f"📈 REPORTE RESUMEN DE CONSUMO — {duracion} SEGUNDOS")
    print("═" * 85)
    print(f"{'CONTENEDOR':<25} | {'RAM PROM':<12} | {'RAM PICO':<12} | {'CPU PROM':<10} | {'CPU PICO'}")
    print("─" * 85)

    for c_name in CONTAINERS:
        rams = historial[c_name]["ram"]
        cpus = historial[c_name]["cpu"]
        if rams:
            avg_ram = sum(rams) / len(rams)
            max_ram = max(rams)
            avg_cpu = sum(cpus) / len(cpus)
            max_cpu = max(cpus)
            print(f"{c_name:<25} | {avg_ram:>9.2f} MB | {max_ram:>9.2f} MB | {avg_cpu:>8.2f}% | {max_cpu:>8.2f}%")
        else:
            print(f"{c_name:<25} | {'N/A':<12} | {'N/A':<12} | {'N/A':<10} | N/A")

    print("─" * 85)
    if total_ram_muestras:
        ram_prom_total = sum(total_ram_muestras) / len(total_ram_muestras)
        ram_pico_total = max(total_ram_muestras)
        pct_prom = (ram_prom_total / AWS_T3_MICRO_RAM_MB) * 100.0
        pct_pico = (ram_pico_total / AWS_T3_MICRO_RAM_MB) * 100.0
        print(f"  STACK RAM PROMEDIO:  {ram_prom_total:>.2f} MB  ({pct_prom:>.1f}% de 1 GB t3.micro)")
        print(f"  STACK RAM PICO:      {ram_pico_total:>.2f} MB  ({pct_pico:>.1f}% de 1 GB t3.micro)")
    print("═" * 85 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor de recursos Docker para Animoon")
    parser.add_argument("--live", action="store_true", help="Modo en vivo continuo")
    parser.add_argument("--benchmark", type=int, default=0, help="Duración en segundos para recolectar métricas y generar reporte")
    parser.add_argument("--interval", type=float, default=2.0, help="Intervalo de muestreo en segundos")
    args = parser.parse_args()

    if args.benchmark > 0:
        modo_benchmark(duracion=args.benchmark, intervalo=args.interval)
    else:
        modo_live(intervalo=args.interval)
