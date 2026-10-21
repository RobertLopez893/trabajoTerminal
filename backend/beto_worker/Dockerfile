FROM python:3.12-slim

WORKDIR /app

# Instalar dependencias del sistema para compilar extensiones si son necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY backend/beto_worker/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copiar el código del proyecto
COPY backend /app/backend
COPY security /app/security
COPY proyecto_pln /app/proyecto_pln

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

CMD ["python", "backend/beto_worker/worker.py"]
