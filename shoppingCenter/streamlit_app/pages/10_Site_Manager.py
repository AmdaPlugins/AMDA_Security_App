# -*- coding: utf-8 -*-
import streamlit as st
from modules.core import ctx

st.set_page_config(page_title="Site Manager", page_icon="🏢")
C = ctx(); DM, SH = C["DM"], C["SH"]

st.header("🏢 Site Manager")
prefix = st.session_state.get("selected_prefix", "")
site = SH["get_site_by_prefix"](DM.registry, prefix) if prefix else {}
if not site:
    st.warning("Selecciona un sitio desde Home.")
else:
    c1,c2 = st.columns(2)
    with c1:
        st.subheader("🧭 Básico")
        st.write(f"**Prefijo:** `{site.get('prefix','—')}`")
        st.write(f"**Tipo:** {site.get('site','—')}")
        st.write(f"**Nombre:** {site.get('name','—')}")
        st.write(f"**Estado:** {site.get('status','—')}")
    with c2:
        st.subheader("📍 Dirección")
        st.write(f"{site.get('address','—')}, {site.get('city','—')}, {site.get('state','—')} {site.get('zip','—')}")
        if site.get("maps_link"):
            st.markdown(f"🌍 [Google Maps]({site['maps_link']})")
