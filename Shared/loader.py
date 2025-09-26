import json
from pathlib import Path
import streamlit as st

def load_phrases(path: Path):
    if not path.exists():
        st.error(f"❌ No se encontró el archivo de frases en {path}")
        st.stop()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("El archivo debe contener una lista.")
        return data
    except Exception as e:
        st.error(f"❌ Error al cargar frases: {e}")
        st.stop()
