@echo off
setlocal enabledelayedexpansion

REM === 1) Ir al proyecto ===
cd /d C:\AmdaOps

REM Asegurar que Python vea la raíz del proyecto (para imports tipo "from Shared...")
set "PYTHONPATH=%CD%;%PYTHONPATH%"

echo.
echo ==== AMDA_Security_App :: Lanzador ====
echo Carpeta: %CD%
echo.

REM === 2) Detectar/crear entorno virtual (.venv o venv) ===
set "VENV_DIR="
if exist ".venv\Scripts\activate.bat" set "VENV_DIR=.venv"
if not defined VENV_DIR if exist "venv\Scripts\activate.bat" set "VENV_DIR=venv"

if not defined VENV_DIR (
  echo [INFO] No se encontro entorno virtual. Creando ".venv"...
  python -m venv .venv
  if errorlevel 1 (
    echo [ERROR] No se pudo crear el entorno virtual. ¿Tienes Python en PATH?
    pause
    exit /b 1
  )
  set "VENV_DIR=.venv"
)

echo [OK] Usando entorno: %VENV_DIR%
call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
  echo [ERROR] No se pudo activar el entorno virtual.
  pause
  exit /b 1
)

REM === 3) Asegurar pip y dependencias ===
echo.
echo [INFO] Actualizando pip...
python -m pip install --upgrade pip

if exist "requirements.txt" (
  echo [INFO] Instalando dependencias desde requirements.txt ...
  pip install -r requirements.txt
) else (
  echo [WARN] No hay requirements.txt en %CD% (continuando de todos modos) 
)

REM === 4) Detectar el entrypoint de Streamlit ===
set "APP_PATH="

if exist "shoppingCenter\streamlit_app\Home.py" set "APP_PATH=shoppingCenter\streamlit_app\Home.py"
if not defined APP_PATH if exist "ShoppingCenter\streamlit_app\Home.py" set "APP_PATH=ShoppingCenter\streamlit_app\Home.py"
if not defined APP_PATH if exist "shoppingCenter\streamlit_app\app.py" set "APP_PATH=shoppingCenter\streamlit_app\app.py"
if not defined APP_PATH if exist "ShoppingCenter\streamlit_app\app.py" set "APP_PATH=ShoppingCenter\streamlit_app\app.py"

if not defined APP_PATH (
  echo.
  echo [ERROR] No encontre el archivo principal de Streamlit.
  echo Busca uno de estos y ajusta el script:
  echo   shoppingCenter\streamlit_app\Home.py
  echo   ShoppingCenter\streamlit_app\Home.py
  echo   shoppingCenter\streamlit_app\app.py
  echo   ShoppingCenter\streamlit_app\app.py
  if exist "shoppingCenter\streamlit_app" start "" "shoppingCenter\streamlit_app"
  if exist "ShoppingCenter\streamlit_app" start "" "ShoppingCenter\streamlit_app"
  pause
  exit /b 1
)

echo.
echo [OK] Lanzando Streamlit con: %APP_PATH%
echo (Si no abre el navegador, copia la URL que aparezca abajo)
echo.

REM === 5) Ejecutar Streamlit usando Python del venv ===
python -m streamlit run "%APP_PATH%"
if errorlevel 1 (
  echo.
  echo [ERROR] Streamlit fallo al iniciar.
  echo Prueba manualmente:
  echo   python -m streamlit run "%APP_PATH%"
  pause
  exit /b 1
)

echo.
echo [OK] Streamlit finalizo.
pause
