# Detectar IP local automǭticamente
$autoIp = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notmatch "vEthernet|WSL" -and $_.InterfaceAlias -notlike "Loopback*" -and $_.IPAddress -notlike "169.254.*" } | Select-Object -First 1).IPAddress

if (-not $autoIp) {
    $autoIp = "10.0.2.2"
}

Write-Host "======================================"
Write-Host "     CONFIGURACION DE ENTORNO ANIMOON"
Write-Host "======================================"
Write-Host "1) Correr backend en esta computadora (IP detectada: $autoIp)"
Write-Host "2) El backend corre en OTRA computadora (Configurar Android manualmente)"
$opcion = Read-Host -Prompt "Elige una opcin [1]"

if ($opcion -eq "" -or $opcion -eq "1") {
    $localIp = $autoIp
    $iniciarDocker = $true
} elseif ($opcion -eq "2") {
    $localIp = Read-Host -Prompt "Ingresa la IP de la otra computadora (ej. 192.168.0.100)"
    if (-not $localIp) {
        Write-Host "IP no invǭlida. Saliendo..."
        exit
    }
    $iniciarDocker = $false
} else {
    Write-Host "Opcin invǭlida."
    exit
}

Write-Host "`nAplicando configuracin para la IP: $localIp"

$propertiesFile = "animoon\local.properties"
$gradleFile = "animoon\app\build.gradle.kts"

# Actualizar local.properties
if (Test-Path $propertiesFile) {
    $content = Get-Content $propertiesFile | Where-Object { $_ -notmatch '^API_BASE_URL=' }
    $content += "API_BASE_URL=http://$localIp`:8000/"
    $content | Set-Content $propertiesFile
    Write-Host "[x] local.properties actualizado"
} else {
    Write-Host "API_BASE_URL=http://$localIp`:8000/" | Out-File -FilePath $propertiesFile -Encoding utf8
    Write-Host "[x] local.properties creado y actualizado"
}

# Actualizar build.gradle.kts
if (Test-Path $gradleFile) {
    $content = Get-Content $gradleFile
    $content = $content -replace "http://[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:8000/", "http://$localIp`:8000/"
    $content | Set-Content $gradleFile
    Write-Host "[x] build.gradle.kts actualizado"
}

if ($iniciarDocker) {
    Write-Host "`nLimpiando contenedores y levantando Docker..."
    docker-compose down -v
    docker-compose up -d --build
    Write-Host "======================================"
    Write-Host "Listo! El backend estǭ corriendo localmente."
} else {
    Write-Host "======================================"
    Write-Host "Listo! Frontend configurado. No se inici Docker."
}

Write-Host "La app de Android apunta a http://$localIp`:8000/"
Write-Host "======================================"
