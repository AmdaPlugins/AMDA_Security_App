@echo off
REM 🚀 Lanzador directo de AmdaOps

cd /d "C:\AmdaOps"
python -m streamlit run "C:\AmdaOps\shoppingCenter\app.py"

echo.
echo 🟢 Streamlit finalizado o detenido. Presiona una tecla para cerrar...
pause >nul
