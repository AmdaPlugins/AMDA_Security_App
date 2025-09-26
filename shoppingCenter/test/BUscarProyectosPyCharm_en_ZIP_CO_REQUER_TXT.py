
# ===============================
# Respaldo proyectos PyCharm -> D:\ + ZIP
# Copia carpetas y comprime al final
# ===============================

# --- 1) LISTA DE PROYECTOS (usa esta lista o deja en blanco para autodetectar) ---
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
C:\project software y and PyCharm\old project\Amda_Music_Qwen_IA
C:\project software y and PyCharm\old project\PythonProject
C:\Proyecto viejo
C:\Proyectos\AMDA_AMUSE
C:\PythonProject
C:\RedGuard_Monitor_Pro
C:\RedGuardMonitor_Pro_Scaffold
C:\Users\abapa\Documents\backup_2025-04-21_03-08-08
C:\Users\abapa\Documents\backup_2025-04-21_05-32-52
C:\Users\abapa\Documents\backup_2025-04-21_17-50-25
C:\Users\abapa\Documents\backup_2025-04-22_14-38-40
C:\Users\abapa\Documents\backup_2025-04-22_15-06-48
C:\Users\abapa\Documents\backup_2025-04-23_07-58-22
C:\Users\abapa\Documents\backup_2025-04-23_20-17-10
C:\Users\abapa\Documents\backup_2025-04-24_05-57-15
C:\Users\abapa\Documents\backup_2025-04-24_10-26-44
C:\Users\abapa\Documents\backup_2025-04-25_00-00-18
C:\Users\abapa\Documents\backup_2025-04-25_09-33-34
C:\Users\abapa\Documents\backup_2025-04-25_12-47-35
C:\Users\abapa\Documents\backup_2025-04-26_02-04-34
C:\Users\abapa\Documents\backup_2025-04-26_04-16-51
C:\Users\abapa\Documents\backup_2025-04-26_09-03-29
C:\Users\abapa\Documents\backup_2025-04-26_13-39-14
C:\Users\abapa\Documents\backup_2025-04-26_21-01-49
C:\Users\abapa\Documents\h_backups\backup_2025-04-26_09-00-57\backup_2025-04-21_03-08-08
C:\Users\abapa\Documents\h_backups\backup_2025-04-26_09-00-57\backup_2025-04-21_05-32-52
C:\Users\abapa\Documents\h_backups\backup_2025-04-26_09-00-57\backup_2025-04-21_17-50-25
C:\Users\abapa\Documents\h_backups\backup_2025-04-26_09-00-57\backup_2025-04-22_14-38-40
C:\Users\abapa\Documents\h_backups\backup_2025-04-26_09-00-57\backup_2025-04-22_15-06-48
C:\Users\abapa\Documents\h_backups\backup_2025-04-26_09-00-57\backup_2025-04-23_07-58-22
C:\Users\abapa\Documents\h_backups\backup_2025-04-26_09-00-57\backup_2025-04-23_20-17-10
C:\Users\abapa\Documents\h_backups\backup_2025-04-26_09-00-57\backup_2025-04-24_05-57-15
C:\Users\abapa\Documents\h_backups\backup_2025-04-26_09-00-57\backup_2025-04-24_10-26-44
C:\Users\abapa\Documents\h_backups\backup_2025-04-26_13-37-20\backup_2025-04-21_03-08-08
C:\Users\abapa\OneDrive\Documents\02 python\AmdaSync
C:\Users\abapa\OneDrive\Documents\DtoPY\ESD-USB
C:\Users\abapa\OneDrive\Documents\DtoPY\ESD-USB\backup_2025-05-01_03-39-58
C:\Users\abapa\OneDrive\Documents\DtoPY\ESD-USB\backup_2025-05-01_13-37-19
C:\Users\abapa\OneDrive\Documents\DtoPY\ESD-USB\backup_pro\AMDA_AMUSE_Backup_2025-05-01_17-09-11\Datos_Proyecto
C:\Users\abapa\OneDrive\Documents\DtoPY\ESD-USB\backup_pro\AMDA_AMUSE_Backup_2025-05-01_17-19-46\Proyecto_Completo
C:\Users\abapa\OneDrive\Documents\DtoPY\ESD-USB\RedGuardMonitor_Final
C:\Users\abapa\PycharmProjects\PythonProject
C:\Users\abapa\PycharmProjects\PythonProject2
C:\Users\abapa\RedGuardMonitor_Final
"@ -split "`r?`n" | Where-Object { $_ -and $_.Trim().Length -gt 0 }

# --- 2) Si $projects vacÃ­o, autodetecta en C:\ (padres de carpetas .idea) ---
if (-not $projects -or $projects.Count -eq 0) {
  Write-Host "ðŸ”Ž Autodetectando proyectos en C:\ (carpetas que contienen .idea)..." -ForegroundColor Cyan
  $projects = Get-ChildItem -Path "C:\" -Directory -Recurse -ErrorAction SilentlyContinue |
              Where-Object { $_.Name -eq ".idea" } |
              ForEach-Object { $_.Parent.FullName } |
              Sort-Object -Unique
}

# --- 3) Preparar destino en D:\ ---
$timestamp  = Get-Date -Format "yyyyMMdd_HHmmss"
$backupRoot = "D:\Backup_PyCharm_$timestamp"
if (-not (Test-Path "D:\")) { throw "âŒ La unidad D:\ no existe. Conecta el USB y vuelve a intentar." }
New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null

# --- 4) Copiar proyectos (robusto con ROBOCOPY) ---
# Excluye tÃ­picos directorios pesados que puedes volver a crear: entornos, caches, node_modules, etc.
$excludeDirs = @("venv",".venv","__pycache__",".mypy_cache",".pytest_cache",".tox","node_modules","build","dist",".eggs",".ruff_cache")

$logFile = Join-Path $backupRoot "robocopy.log"
$copied  = 0; $missing = 0

foreach ($proj in $projects) {
  if (Test-Path $proj) {
    $name = Split-Path $proj -Leaf
    $dest = Join-Path $backupRoot $name
    Write-Host "ðŸ“‚ Copiando: $proj -> $dest"

    # Construir parÃ¡metros /XD para excluir directorios
    $xd = @()
    foreach ($d in $excludeDirs) { $xd += @("/XD", (Join-Path $proj $d)) }

    # /E incluye subcarpetas, /R:1 reintentos, /W:1 espera,
    # /NFL /NDL menos ruido, /NP sin porcentaje, /MT multihilo si estÃ¡ disponible
    $args = @($proj, $dest, "/E", "/R:1", "/W:1", "/NFL", "/NDL", "/NP", "/MT:16", "/LOG+:$logFile") + $xd
    $rc = Start-Process -FilePath robocopy.exe -ArgumentList $args -Wait -PassThru
    $copied++
  } else {
    Write-Host "âš ï¸ No encontrado: $proj" -ForegroundColor Yellow
    $missing++
  }
}

Write-Host "`nâœ… Copia terminada. Proyectos copiados: $copied. No encontrados: $missing." -ForegroundColor Green
Write-Host "ðŸ“ Log de copia: $logFile"

# --- 5) Crear ZIP con todo el respaldo ---
$zipFile = "D:\Backup_PyCharm_$timestamp.zip"
Write-Host "ðŸ“¦ Comprimiendo a ZIP: $zipFile (puede tardar)..."
# Nota: Compress-Archive puede tener problemas con rutas muy largas en sistemas antiguos.
Compress-Archive -Path "$backupRoot\*" -DestinationPath $zipFile -CompressionLevel Optimal -Force
Write-Host "ðŸŽ‰ ZIP creado en: $zipFile" -ForegroundColor Yellow

# --- 6) Resumen de tamaÃ±os (Ãºtil para verificar) ---
$sizes = Get-ChildItem -Path $backupRoot -Directory | ForEach-Object {
  $bytes = (Get-ChildItem -Path $_.FullName -Recurse -File | Measure-Object -Sum Length).Sum
  [pscustomobject]@{ Proyecto = $_.Name; MB = [math]::Round($bytes/1MB,2) }
} | Sort-Object -Property MB -Descending

$sizes | Format-Table -AutoSize
$sizes | Out-File -FilePath (Join-Path $backupRoot "sizes_MB.txt") -Encoding UTF8
Write-Host "ðŸ“„ Detalle de tamaÃ±os guardado en: $(Join-Path $backupRoot 'sizes_MB.txt')"
Write-Host "`nâœ… Respaldo COMPLETO: carpeta + ZIP listos en D:\  â€”  Â¡Buen trabajo!" -ForegroundColor Green

Notas rÃ¡pidas

ROBOCOPY es mÃ¡s fiable que Copy-Item para grandes Ã¡rboles de carpetas y rutas largas.

ExcluÃ­ venv, .venv, node_modules, __pycache__, etc. para ahorrar espacio (se pueden recrear con pip install -r requirements.txt).
Si quieres incluirlos, dime y te paso la versiÃ³n sin exclusiones.

TendrÃ¡s:

La carpeta D:\Backup_PyCharm_<fecha>\â€¦ con cada proyecto.

Un ZIP D:\Backup_PyCharm_<fecha>.zip con todo (por si quieres moverlo o subirlo).
