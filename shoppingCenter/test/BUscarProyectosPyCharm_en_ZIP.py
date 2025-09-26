# ===============================
# Respaldo proyectos PyCharm -> D:\ + ZIP + requirements.txt
# ===============================

# --- 1) LISTA DE PROYECTOS (puedes pegar tu lista aquí o dejar vacío para autodetectar) ---
$projects = @"
C:\00 Master_Security_Corp_East\00 Master_Security_Corp_East
C:\00 MSCE Report
C:\Amda_Boot_Guard
C:\Amda_IMCox
C:\AMDA_Security_AI
C:\AmdaOps
C:\AndroidQuickReporter
C:\IMCox
C:\MUSIC-IA
C:\Proyectos\AMDA_AMUSE
C:\PythonProject
C:\RedGuardMonitor_Final
"@ -split "`r?`n" | Where-Object { $_ -and $_.Trim().Length -gt 0 }

# --- 2) Si $projects está vacío, autodetecta proyectos con .idea ---
if (-not $projects -or $projects.Count -eq 0) {
  Write-Host "🔎 Autodetectando proyectos en C:\ ..." -ForegroundColor Cyan
  $projects = Get-ChildItem -Path "C:\" -Directory -Recurse -ErrorAction SilentlyContinue |
              Where-Object { $_.Name -eq ".idea" } |
              ForEach-Object { $_.Parent.FullName } |
              Sort-Object -Unique
}

# --- 3) Preparar destino en D:\ ---
$timestamp  = Get-Date -Format "yyyyMMdd_HHmmss"
$backupRoot = "D:\Backup_PyCharm_$timestamp"
if (-not (Test-Path "D:\")) { throw "❌ La unidad D:\ no existe. Conecta el USB y vuelve a intentar." }
New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null

# --- 4) Excluir carpetas pesadas ---
$excludeDirs = @("venv",".venv","__pycache__",".mypy_cache",".pytest_cache",".tox","node_modules","build","dist",".eggs",".ruff_cache")

# --- 5) Copiar proyectos + generar requirements.txt ---
$logFile = Join-Path $backupRoot "robocopy.log"
$copied  = 0; $missing = 0

foreach ($proj in $projects) {
  if (Test-Path $proj) {
    $name = Split-Path $proj -Leaf
    $dest = Join-Path $backupRoot $name
    Write-Host "📂 Copiando: $proj -> $dest"

    # Copiar con robocopy (más robusto que Copy-Item)
    $xd = @()
    foreach ($d in $excludeDirs) { $xd += @("/XD", (Join-Path $proj $d)) }
    $args = @($proj, $dest, "/E", "/R:1", "/W:1", "/NFL", "/NDL", "/NP", "/MT:16", "/LOG+:$logFile") + $xd
    Start-Process -FilePath robocopy.exe -ArgumentList $args -Wait -NoNewWindow

    # Generar requirements.txt si no existe
    $reqFile = Join-Path $proj "requirements.txt"
    if (-not (Test-Path $reqFile)) {
      try {
        Write-Host "📝 Generando requirements.txt en $proj ..."
        # Detectar dependencias importadas en los .py (muy básico)
        $imports = Get-ChildItem -Path $proj -Recurse -Include *.py -ErrorAction SilentlyContinue |
                   Select-String -Pattern "^\s*(import|from)\s+([a-zA-Z0-9_]+)" |
                   ForEach-Object { $_.Matches[0].Groups[2].Value } |
                   Sort-Object -Unique
        if ($imports) {
          $imports | Out-File -FilePath $reqFile -Encoding UTF8
        } else {
          "### No se detectaron imports automáticamente" | Out-File -FilePath $reqFile -Encoding UTF8
        }
      } catch {
        Write-Host "⚠️ Error generando requirements.txt en $proj"
      }
    }
    $copied++
  } else {
    Write-Host "⚠️ No encontrado: $proj" -ForegroundColor Yellow
    $missing++
  }
}

Write-Host "`n✅ Copia terminada. Proyectos copiados: $copied. No encontrados: $missing." -ForegroundColor Green
Write-Host "📝 Log de copia: $logFile"

# --- 6) Crear ZIP con todo el respaldo ---
$zipFile = "D:\Backup_PyCharm_$timestamp.zip"
Write-Host "📦 Comprimiendo a ZIP: $zipFile (puede tardar)..."
Compress-Archive -Path "$backupRoot\*" -DestinationPath $zipFile -CompressionLevel Optimal -Force
Write-Host "🎉 ZIP creado en: $zipFile" -ForegroundColor Yellow

# --- 7) Guardar reporte de tamaños ---
$sizes = Get-ChildItem -Path $backupRoot -Directory | ForEach-Object {
  $bytes = (Get-ChildItem -Path $_.FullName -Recurse -File | Measure-Object -Sum Length).Sum
  [pscustomobject]@{ Proyecto = $_.Name; MB = [math]::Round($bytes/1MB,2) }
} | Sort-Object -Property MB -Descending

$sizes | Format-Table -AutoSize
$sizes | Out-File -FilePath (Join-Path $backupRoot "sizes_MB.txt") -Encoding UTF8
Write-Host "📄 Detalle de tamaños guardado en: $(Join-Path $backupRoot 'sizes_MB.txt')"
Write-Host "`n✅ Respaldo COMPLETO: carpeta + ZIP + requirements.txt listos en D:\" -ForegroundColor Green
