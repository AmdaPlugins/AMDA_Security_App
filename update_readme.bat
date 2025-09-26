@echo off
REM === Ir al proyecto ===
cd /d C:\AmdaOps

REM === Crear/Actualizar README.md con contenido ===
(
echo # 🏗️ AmdaOps — Plataforma Modular de Operaciones
echo.
echo **AmdaOps** es una arquitectura operativa diseñada para gestionar múltiples sitios (^**ShoppingCenter^**, ^**Warehouse^**, ^**Parking^**, etc.)  
echo de forma **segura, escalable y colaborativa**. Su estructura modular permite reutilizar componentes, mantener trazabilidad y  
echo facilitar el despliegue en entornos reales.
echo.
echo ---
echo.
echo ## 📂 Estructura del proyecto
echo.
echo ^```plaintext
echo AmdaOps/
echo ├── shared/              # Módulos comunes reutilizables
echo │   ├── loader.py
echo │   ├── registry.py
echo │   └── phrase.py
echo ├── ShoppingCenter/      # Módulo operativo actual
echo │   ├── formulario/
echo │   ├── data/
echo │   ├── streamlit_app/
echo │   └── tests/
echo ├── Idea/                # Prototipos y exploraciones
echo ├── docs/                # Documentación técnica
echo ├── venv/                # Entorno virtual (excluido del repo)
echo └── README.md
echo ^```
echo.
echo ---
echo.
echo ## 🧩 Componentes Compartidos (^`shared/^`)
echo.
echo - **loader.py** → Carga y validación de estructuras de datos  
echo - **registry.py** → Registro de módulos y configuración dinámica  
echo - **phrase.py** → Gestión de frases y textos bilingües  
echo.
echo Estos módulos se comparten entre todos los sitios operativos, garantizando **coherencia** y **mantenimiento centralizado**.
echo.
echo ---
echo.
echo ## 🏬 Módulo ^`ShoppingCenter^`
echo.
echo Contiene:  
echo - **formulario/** → Formularios principales  
echo - **data/** → Datos simulados  
echo - **streamlit_app/** → Interfaz visual  
echo - **tests/** → Pruebas unitarias  
echo.
echo Está diseñado para ser el **primer sitio operativo** y servir como **plantilla** para futuros módulos:
echo.
echo ^```plaintext
echo AmdaOps/
echo ├── Warehouse/
echo ├── Parking/
echo ├── DeliveryHub/
echo ^```
echo.
echo Cada sitio puede tener su propio ^`formulario/^`, ^`data/^`, ^`tests/^`, y reutilizar los módulos de ^`shared/^`.
echo.
echo ---
echo.
echo ## 🚀 Objetivos
echo.
echo - Consolidar la **base modular** con componentes compartidos  
echo - Validar la **estructura de datos** antes de avanzar  
echo - Preparar el sistema para **producción** y uso real por equipos operativos  
echo.
echo ---
echo.
echo ## 📄 Documentación
echo.
echo Toda decisión arquitectónica, convenciones de nombres y estructura de carpetas se documenta en:  
echo.
echo ^`docs/estructura.md^`
echo.
echo ---
echo.
echo ## ⚡ Instalación rápida
echo.
echo Clona el repositorio e instala las dependencias en un entorno virtual:
echo.
echo ^```bash
echo # Clonar el repositorio
echo git clone https://github.com/AmdaPlugins/AmdaOps.git
echo cd AmdaOps
echo.
echo # Crear y activar un entorno virtual
echo python -m venv venv
echo # En Linux/Mac
echo source venv/bin/activate
echo # En Windows (PowerShell)
echo venv\Scripts\Activate.ps1
echo.
echo # Instalar dependencias
echo pip install -r requirements.txt
echo ^```
echo.
echo Ejecutar la aplicación principal (ejemplo con Streamlit):
echo.
echo ^```bash
echo streamlit run ShoppingCenter/streamlit_app/app.py
echo ^```
echo.
echo ---
echo.
echo ## 🤝 Colaboración
echo.
echo Este proyecto está abierto a **mejoras, sugerencias y extensiones**.  
echo Se prioriza la **claridad**, la **modularidad** y la **experiencia de usuario sin fricciones**.
) > README.md

REM === Subir cambios a GitHub ===
git add README.md
git commit -m "Actualización automática README.md"
git push

echo.
echo ✅ README.md actualizado y subido a GitHub
pause
