# -*- coding: utf-8 -*-
import streamlit as st
from modules.core import ctx

st.set_page_config(page_title="AmdaOps — Security Management", page_icon="🛡️", layout="wide")
st.title("🛡️ AmdaOps — Security Management")

C = ctx(); DM, SH = C["DM"], C["SH"]

def _prefixes(reg):
    if isinstance(reg, list) and reg and isinstance(reg[0], dict):
        return [r.get("prefix") for r in reg if r.get("prefix")]
    return []

# ---- Sidebar: SOLO selección de sitio + info (sin radio extra) ----
st.sidebar.header("🏷️ Site Selection")
prefixes = SH["get_prefixes"](DM.registry) or _prefixes(DM.registry) or ["DEFAULT"]
default_idx = 0
if "selected_prefix" in st.session_state and st.session_state["selected_prefix"] in prefixes:
    default_idx = prefixes.index(st.session_state["selected_prefix"])

selected = st.sidebar.selectbox("Select Site", prefixes, index=default_idx)
st.session_state["selected_prefix"] = selected

site = SH["get_site_by_prefix"](DM.registry, selected) if selected else {}
st.sidebar.divider()
st.sidebar.subheader("📍 Selected Site")
if site:
    st.sidebar.write(f"**Name:** {site.get('name','—')}")
    st.sidebar.write(f"**Type:** {site.get('site','—')}")
    st.sidebar.write(f"**Status:** {site.get('status','—')}")
    st.sidebar.write(f"**Address:** {site.get('address','—')}")
    if site.get("maps_link"):
        st.sidebar.markdown(f"🌍 [Google Maps]({site['maps_link']})")

# ---- Contenido principal: métricas y guía ----
st.subheader("📊 Overview")
c1,c2,c3 = st.columns(3)
with c1: st.metric("Prefix", selected or "—")
with c2: st.metric("Officers (total)", len(DM.officers))
with c3: st.metric("Shifts (total)", len(DM.schedules))

st.info(
    "Usa el menú automático de Streamlit (arriba en el sidebar) para navegar: "
    "**Site Manager**, **Officers**, **Schedule**, **Time Tracking**, **Search Phrases**, **All Phrases**."
)
