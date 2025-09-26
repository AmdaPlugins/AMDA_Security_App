import streamlit as st
from pathlib import Path
from shared.loader import load_phrases, save_phrase
from shared.registry import load_registry, get_prefixes, get_site_by_prefix

# Rutas de archivos
PHRASES_PATH = Path("data/181_line__bank_Shoping_Center_en_es.json")
REGISTRY_PATH = Path("data/site_registry.json")

st.set_page_config(page_title="Agregar frase operativa", layout="centered")
st.title("🧠 Inserción de frases operativas")

# Cargar datos
phrases = load_phrases(PHRASES_PATH)
registry = load_registry(REGISTRY_PATH)

# Selector de prefijo
prefixes = get_prefixes(registry)
selected_prefix = st.selectbox("🏷️ Seleccionar sitio por prefijo", prefixes)

# Obtener datos del sitio
site_info = get_site_by_prefix(registry, selected_prefix)
if site_info:
    st.markdown(f"📍 **{site_info['name']}**")
    st.caption(f"📫 {site_info['address']} ({site_info['city']}, {site_info['state']} {site_info['zip']})")
else:
    st.warning("No se encontró información para ese prefijo.")
    st.stop()

# Formulario para agregar frase
st.markdown("### ✏️ Nueva frase operativa")
with st.form("add_phrase_form"):
    phrase_cat = st.selectbox("Categoría", [
        "Patrol", "Access", "Incident", "Safety", "Loss Prevention",
        "Parking", "Person", "Training", "Report"
    ])
    phrase_hotwords = st.text_input("Palabras calientes (separadas por coma)")
    phrase_en = st.text_area("Frase en inglés")
    phrase_es = st.text_area("Frase en español")
    save = st.form_submit_button("Guardar frase")

    if save:
        if not phrase_en or not phrase_es or not phrase_cat:
            st.error("❌ Todos los campos son obligatorios.")
        else:
            new_phrase = {
                "site": site_info["site"],
                "name": site_info["name"],
                "address": site_info["address"],
                "cat": phrase_cat,
                "hotwords": [w.strip().lower() for w in phrase_hotwords.split(",") if w.strip()],
                "en": phrase_en.strip(),
                "es": phrase_es.strip()
            }
            save_phrase(PHRASES_PATH, phrases, new_phrase)
            st.success("✅ Frase guardada correctamente.")
