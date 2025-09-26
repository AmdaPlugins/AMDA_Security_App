import streamlit as st
from pathlib import Path
from shared.registry import load_registry, save_registry

# Ruta del registro maestro
REGISTRY_PATH = Path("data/site_registry.json")

st.set_page_config(page_title="Agregar dirección", layout="centered")
st.title("📍 Registro maestro de ubicaciones")

# Cargar registro existente
registry = load_registry(REGISTRY_PATH)

# Formulario para agregar nueva dirección
st.markdown("### ➕ Agregar nueva dirección operativa")
with st.form("add_site_form"):
    new_prefix = st.text_input("Prefijo único (ej. WD 371)")
    new_site = st.text_input("Tipo de sitio (ej. Shopping Center, Warehouse)")
    new_name = st.text_input("Nombre del sitio (ej. Stores, LogiDepot)")
    new_address = st.text_input("Dirección completa (formato USA)")
    new_city = st.text_input("Ciudad")
    new_state = st.text_input("Estado (ej. FL)")
    new_zip = st.text_input("Código postal")
    submitted = st.form_submit_button("Guardar")

    if submitted:
        if not new_prefix or not new_site or not new_name or not new_address:
            st.error("❌ Los campos prefijo, tipo de sitio, nombre y dirección son obligatorios.")
        elif any(s["prefix"] == new_prefix for s in registry):
            st.warning(f"⚠️ Ya existe una dirección con el prefijo '{new_prefix}'. Usa uno diferente.")
        else:
            new_entry = {
                "prefix": new_prefix,
                "site": new_site,
                "name": new_name,
                "address": new_address,
                "city": new_city,
                "state": new_state,
                "zip": new_zip
            }
            registry.append(new_entry)
            save_registry(REGISTRY_PATH, registry)
            st.success(f"✅ Dirección '{new_prefix}' guardada correctamente.")
