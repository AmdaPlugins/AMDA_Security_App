@echo off
cd /d C:\AmdaOps

REM Correcciones en todos los .py bajo shoppingCenter
powershell -NoProfile -Command ^
  "Get-ChildItem -Recurse -Path 'shoppingCenter' -Include *.py | ForEach-Object { $p=$_.FullName; $t=Get-Content $p; $t = $t -replace 'from\s+loader\s+import','from Shared.loader import'; $t = $t -replace '(^|\s)import\s+loader(\s|$)',' from Shared import loader '; $t = $t -replace 'from\s+registry\s+import','from Shared.registry import'; $t = $t -replace '(^|\s)import\s+registry(\s|$)',' from Shared import registry '; $t = $t -replace 'from\s+phrase\s+import','from Shared.phrase import'; $t = $t -replace '(^|\s)import\s+phrase(\s|$)',' from Shared import phrase '; Set-Content -Path $p -Value $t -Encoding UTF8 }"

echo.
echo [OK] Imports actualizados. Subiendo cambios a Git...
git add shoppingCenter
git commit -m "Fix: imports a Shared.loader/registry/phrase"
git push
echo Listo.
pause
