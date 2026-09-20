# Detectar IP local
$localIp = (Test-Connection -ComputerName (hostname) -Count 1).IPv4Address.IPAddressToString

if (-not $localIp) {
    Write-Host "No se pudo detectar la IP. Usando 10.0.2.2 por defecto."
    $localIp = "10.0.2.2"
}

Write-Host "======================================"
Write-Host "IP detectada: $localIp"
Write-Host "======================================"

$propertiesFile = "animoon\local.properties"
$gradleFile = "animoon\app\build.gradle.kts"

# Actualizar local.properties
if (Test-Path $propertiesFile) {
    $content = Get-Content $propertiesFile | Where-Object { $_ -notmatch '^API_BASE_URL=' }
    $content += "API_BASE_URL=http://$localIp`:8000/"
    $content | Set-Content $propertiesFile
    Write-Host "✓ local.properties actualizado"
} else {
    Write-Host "x No se encontró $propertiesFile"
}

# Actualizar build.gradle.kts
if (Test-Path $gradleFile) {
    $content = Get-Content $gradleFile
    $content = $content -replace "http://[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:8000/", "http://$localIp`:8000/"
    $content | Set-Content $gradleFile
    Write-Host "✓ build.gradle.kts actualizado"
}

Write-Host "Limpiando contenedores y levantando Docker..."
docker-compose down -v
docker-compose up -d --build

Write-Host "======================================"
Write-Host "¡Listo! El backend está corriendo localmente."
Write-Host "La app en Kotlin ya debe apuntar a http://$localIp`:8000/"
Write-Host "======================================"
