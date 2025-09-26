# -*- coding: utf-8 -*-
import streamlit as st
from modules.core import ctx

st.set_page_config(page_title="Time Tracking", page_icon="⏱️")
C = ctx(); DM = C["DM"]

st.header("⏱️ Time Tracking")
st.info("Aquí irán time logs, métricas y KPIs (placeholder).")
st.write(f"Site prefix: `{st.session_state.get('selected_prefix','—')}`")
