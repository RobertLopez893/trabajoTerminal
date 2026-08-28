FROM python:3.12-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias para psycopg2 y criptografía
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Copiar requirements y instalarlos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código
COPY backend/ ./backend/
COPY security/ ./security/
# Copiamos variables de entorno si existen
COPY .env* ./

EXPOSE 8000

CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
