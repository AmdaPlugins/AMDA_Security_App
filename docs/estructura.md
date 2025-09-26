# 📂 Estructura del proyecto (Checklist)

C:\\AmdaOps
├─ Shared  
│  ├─ loader.py
│  ├─ registry.py
│  └─ phrase.py
├─ shoppingCenter  
│  ├─ data  
│  │  ├─ 181\_line\_\_bank\_Shoping\_Center\_en\_es.json
│  │  ├─ site\_registry.json
│  │  ├─ security\_officers.json
│  │  ├─ work\_schedules.json
│  │  ├─ time\_logs.json
│  │  └─ officers\_photos  
│  └─ streamlit\_app  
│     ├─ Home.py
│     ├─ modules  
│     │  └─ core.py
│     └─ pages  
│        ├─ 10\_Site\_Manager.py
│        ├─ 20\_Officers.py
│        ├─ 30\_Schedule.py
│        ├─ 40\_Time\_Tracking.py
│        ├─ 50\_Phrases\_Search.py
│        └─ 60\_Phrases\_All.py
├─ requirements.txt
└─ run\_app.bat

✅ Claves:

* Usar **shoppingCenter** (minúsculas) como carpeta del sitio.
* Los módulos compartidos van en **Shared/** (S mayúscula).
* Entrada de Streamlit: **shoppingCenter/streamlit\_app/Home.py** (el .bat ya lo lanza).
* Páginas en **streamlit\_app/pages/** (Streamlit las detecta automáticamente).
