#!/bin/bash

# Ir al directorio donde está el script
cd "$(dirname "$0")"

echo "Detectando IP local de tu red..."

# Intentar obtener la IP (compatible con Windows Git Bash, Linux y Mac)
if command -v ipconfig.exe >/dev/null 2>&1; then
    # Windows
    LOCAL_IP=$(ipconfig.exe | grep IPv4 | grep -v "127.0.0.1" | awk '{print $NF}' | tr -d '\r' | head -n 1)
else
    # Linux/Mac
    LOCAL_IP=$(hostname -I | awk '{print $1}')
fi

if [ -z "$LOCAL_IP" ]; then
    echo "No se pudo detectar la IP. Se usará 10.0.2.2 (emulador Android)."
    LOCAL_IP="10.0.2.2"
fi

echo "======================================"
echo "IP detectada: $LOCAL_IP"
echo "======================================"

PROPERTIES_FILE="animoon/local.properties"
GRADLE_FILE="animoon/app/build.gradle.kts"

# Actualizar local.properties
if [ -f "$PROPERTIES_FILE" ]; then
    # Eliminar cualquier linea previa con API_BASE_URL
    sed -i.bak '/^API_BASE_URL=/d' "$PROPERTIES_FILE"
    # Agregar la nueva IP
    echo "API_BASE_URL=http://$LOCAL_IP:8000/" >> "$PROPERTIES_FILE"
    echo "✓ local.properties actualizado"
else
    echo "x No se encontró $PROPERTIES_FILE"
fi

# Opcional: Actualizar la IP por defecto en build.gradle.kts si hace falta
if [ -f "$GRADLE_FILE" ]; then
    # Busca la IP actual en el fallback (sea cual sea) y la cambia
    sed -i.bak -E "s|http://[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:8000/|http://$LOCAL_IP:8000/|g" "$GRADLE_FILE"
    echo "✓ build.gradle.kts actualizado"
fi

echo "Limpiando contenedores anteriores y levantando Docker..."
docker-compose down -v
docker-compose up -d --build

echo "======================================"
echo "¡Listo! El backend está corriendo localmente."
echo "La app en Kotlin ya debería apuntar a http://$LOCAL_IP:8000/"
echo "======================================"
