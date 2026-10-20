# 📊 Suite de Benchmarking y Pruebas de Escalabilidad - Animoon

Esta carpeta contiene las herramientas para la evaluación experimental, pruebas de carga y generación de reportes de rendimiento del sistema de chat y buffer de Animoon.

---

## 🚀 ¿Qué hace esta suite?
1. **Pruebas Automatizadas de Escalabilidad:**
   - Ejecuta escenarios de concurrencia progresivos (ej: 5, 10, 25, 50 y 100 salas simultáneas).
   - Simula clientes WebSocket concurrentes sobre TLS 1.3 con cifrado AES-256-GCM.
   - Envía ráfagas completas de 20 mensajes por sala.
   - Dispara eventos de seguridad en caliente vía Redis Pub/Sub (`channel:grooming_alerts`) para medir tiempos de reacción.
2. **Generación de Reportes Académicos:**
   - **`reporte_concurrencia.md`**: Reporte en formato Markdown con tablas estructuradas listo para copiar a reportes de Trabajo Terminal, avances o tesis.
   - **`tabla_resultados.csv`**: Tabla en formato CSV para importar en Excel o Google Sheets.
   - **`benchmark_data.json`**: Datos crudos estructurados con todas las métricas por nivel de concurrencia.
3. **Generación de Gráficas de Publicación (300 DPI):**
   - **`grafica_latencia.png`**: Curvas de RTT (Mínima, Promedio, Percentil 95 y Máxima).
   - **`grafica_throughput.png`**: Capacidad de procesamiento (mensajes/segundo) vs concurrencia.
   - **`grafica_tiempo_seguridad.png`**: Latencia de corte quirúrgico (SAFE_EXIT y suspensión 4003).
   - **`dashboard_resumen.png`**: Panel multi-gráfico 2x2 para diapositivas y presentaciones ejecutivas.

---

## 💻 Instrucciones de Uso

Desde la terminal en tu entorno Conda `(entornoGeneral)` o con el intérprete de Python:

### 1. Ejecución estándar completa (5, 10, 25, 50, 100 salas)
```powershell
python backend/tests/benchmarks/benchmark_runner.py
```

### 2. Ejecución rápida de prueba (3, 5, 10 salas)
```powershell
python backend/tests/benchmarks/benchmark_runner.py --quick
```

### 3. Niveles personalizados de concurrencia
```powershell
python backend/tests/benchmarks/benchmark_runner.py --salas 10 20 50
```

### 4. Especificar carpeta de salida personalizada
```powershell
python backend/tests/benchmarks/benchmark_runner.py --output-dir backend/tests/benchmarks/reports/prueba_1
```

---

## 📁 Estructura de Salida
Cada ejecución crea una subcarpeta con marca de tiempo en `reports/`:
```text
backend/tests/benchmarks/reports/run_YYYYMMDD_HHMMSS/
├── benchmark_data.json
├── tabla_resultados.csv
├── reporte_concurrencia.md
├── grafica_latencia.png
├── grafica_throughput.png
├── grafica_tiempo_seguridad.png
└── dashboard_resumen.png
```
