#!/bin/bash

# Ir al directorio donde estǭ el script
cd "$(dirname "$0")"

echo "======================================"
echo "   CONFIGURACI"N DE ENTORNO ANIMOON"
echo "======================================"

# Intentar obtener la IP (compatible con Windows Git Bash, Linux y Mac)
if command -v ipconfig.exe >/dev/null 2>&1; then
    AUTO_IP=$(ipconfig.exe | grep IPv4 | grep -v "127.0.0.1" | awk '{print $NF}' | tr -d '\r' | head -n 1)
else
    AUTO_IP=$(hostname -I | awk '{print $1}')
fi

if [ -z "$AUTO_IP" ]; then
    AUTO_IP="10.0.2.2"
fi

echo "1) Correr backend en esta computadora (IP detectada: $AUTO_IP)"
echo "2) El backend corre en OTRA computadora (Configurar Android manualmente)"
read -p "Elige una opcin [1]: " OP
OP=${OP:-1}

if [ "$OP" == "1" ]; then
    LOCAL_IP=$AUTO_IP
    INICIAR_DOCKER=true
elif [ "$OP" == "2" ]; then
    read -p "Ingresa la IP de la otra computadora (ej. 192.168.0.100): " LOCAL_IP
    if [ -z "$LOCAL_IP" ]; then
        echo "IP invǭlida. Saliendo..."
        exit 1
    fi
    INICIAR_DOCKER=false
else
    echo "Opcin invǭlida."
    exit 1
fi

echo -e "\nAplicando configuracin para la IP: $LOCAL_IP"

PROPERTIES_FILE="animoon/local.properties"
GRADLE_FILE="animoon/app/build.gradle.kts"

# Actualizar local.properties
if [ -f "$PROPERTIES_FILE" ]; then
    sed -i.bak '/^API_BASE_URL=/d' "$PROPERTIES_FILE"
    echo "API_BASE_URL=http://$LOCAL_IP:8000/" >> "$PROPERTIES_FILE"
    echo "[x] local.properties actualizado"
else
    echo "API_BASE_URL=http://$LOCAL_IP:8000/" > "$PROPERTIES_FILE"
    echo "[x] local.properties creado y actualizado"
fi

# Actualizar build.gradle.kts
if [ -f "$GRADLE_FILE" ]; then
    sed -i.bak -E "s|http://[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:8000/|http://$LOCAL_IP:8000/|g" "$GRADLE_FILE"
    echo "[x] build.gradle.kts actualizado"
fi

if [ "$INICIAR_DOCKER" = true ]; then
    echo -e "\nLimpiando contenedores y levantando Docker..."
    docker-compose down -v
    docker-compose up -d --build
    echo "======================================"
    echo "Listo! El backend estǭ corriendo localmente."
else
    echo "======================================"
    echo "Listo! Frontend configurado. No se inici Docker."
fi

echo "La app de Android apunta a http://$LOCAL_IP:8000/"
echo "======================================"
