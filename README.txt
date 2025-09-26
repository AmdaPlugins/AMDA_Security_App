# 🏗️ AmdaOps — Plataforma Modular de Operaciones

**AmdaOps** es una arquitectura operativa diseñada para gestionar múltiples sitios (**ShoppingCenter**, **Warehouse**, **Parking**, etc.)
de forma **segura, escalable y colaborativa**. Su estructura modular permite reutilizar componentes, mantener trazabilidad y
facilitar el despliegue en entornos reales.

---

## 📂 Estructura del proyecto

```plaintext
AmdaOps/
├── shared/              # Módulos comunes reutilizables
│   ├── loader.py
│   ├── registry.py
│   └── phrase.py
├── ShoppingCenter/      # Módulo operativo actual
│   ├── formulario/
│   ├── data/
│   ├── streamlit_app/
│   └── tests/
├── Idea/                # Prototipos y exploraciones
├── docs/                # Documentación técnica
├── venv/                # Entorno virtual (excluido del repo)
└── README.md

🧩 Componentes Compartidos (shared/)

loader.py → Carga y validación de estructuras de datos

registry.py → Registro de módulos y configuración dinámica

phrase.py → Gestión de frases y textos bilingües

Estos módulos se comparten entre todos los sitios operativos, garantizando coherencia y mantenimiento centralizado.

🏬 Módulo ShoppingCenter

Contiene:

formulario/ → Formularios principales

data/ → Datos simulados

streamlit_app/ → Interfaz visual

tests/ → Pruebas unitarias

Está diseñado para ser el primer sitio operativo y servir como plantilla para futuros módulos:

AmdaOps/
├── Warehouse/
├── Parking/
├── DeliveryHub/

Cada sitio puede tener su propio formulario/, data/, tests/, y reutilizar los módulos de shared/.

🚀 Objetivos

Consolidar la base modular con componentes compartidos

Validar la estructura de datos antes de avanzar

Preparar el sistema para producción y uso real por equipos operativos

📄 Documentación

Toda decisión arquitectónica, convenciones de nombres y estructura de carpetas se documenta en:

docs/estructura.md