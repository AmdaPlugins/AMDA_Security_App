import streamlit as st
from pathlib import Path
import sys

# Añadir carpeta shared al path
sys.path.append(str(Path(__file__).resolve().parent / "shared"))

# Importar funciones desde módulos compartidos
from loader import load_phrases
from registry import load_registry, get_prefixes, get_site_by_prefix
from phrase import filter_phrases_by_site, get_categories, get_hotwords

# Rutas de archivos
PHRASES_PATH = Path("data/181_line__bank_Shoping_Center_en_es.json")
REGISTRY_PATH = Path("data/site_registry.json")

st.set_page_config(page_title="AmdaOps Viewer", layout="wide")
st.title("🛡️ AmdaOps - Visualizador de frases operativas")

# Cargar datos
phrases = load_phrases(PHRASES_PATH)
registry = load_registry(REGISTRY_PATH)

# Selector de prefijo
prefixes = get_prefixes(registry)
selected_prefix = st.sidebar.selectbox("🏷️ Seleccionar sitio por prefijo", prefixes)

# Obtener datos del sitio
site_info = get_site_by_prefix(registry, selected_prefix)
if site_info:
    st.subheader("📍 Información del sitio seleccionado")
    st.markdown(f"""
    **Prefijo:** `{selected_prefix}`  
    **Tipo de sitio:** {site_info['site']}  
    **Nombre:** {site_info['name']}  
    **Dirección:** {site_info['address']}  
    **Ciudad:** {site_info['city']}  
    **Estado:** {site_info['state']}  
    **Código postal:** {site_info['zip']}
    """)
else:
    st.warning("No se encontró información para ese prefijo.")
    st.stop()

# Filtrar frases por sitio
filtered_phrases = filter_phrases_by_site(phrases, site_info)

# Filtros
categories = get_categories(filtered_phrases)
category = st.selectbox("📂 Categoría", [""] + categories)

hotwords = get_hotwords(filtered_phrases)
hotword = st.selectbox("🔍 Palabra clave (hotword)", [""] + hotwords)
custom_hotword = st.text_input("✏️ O escribe una palabra clave personalizada")
final_hotword = custom_hotword if custom_hotword else hotword

limit = st.slider("🔢 Cantidad de frases", 1, 20, 5)

# Buscar frases
if st.button("🔎 Buscar frases"):
    resultados = []
    for p in filtered_phrases:
        if category and p.get("cat") != category:
            continue
        if final_hotword:
            hw = final_hotword.lower()
            if hw not in p.get("en", "").lower() and hw not in p.get("es", "").lower() and hw not in [h.lower() for h in p.get("hotwords", [])]:
                continue
        resultados.append(p)
        if len(resultados) >= limit:
            break

    st.subheader("🧠 Frases encontradas")
    if resultados:
        for p in resultados:
            st.markdown(f"✅ **[{p['cat']}]** {p['en']}  \n🌐 *{p['es']}*")
    else:
        st.warning("No se encontraron frases con esos filtros.")

# Mostrar todas las frases
st.markdown("---")
st.subheader("📋 Todas las frases en esta hoja")

for p in filtered_phrases:
    if p.get("en") and p.get("es"):
        st.markdown(f"- **[{p['cat']}]** {p['en']}  \n🌐 *{p['es']}*")
