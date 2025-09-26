# -*- coding: utf-8 -*-
import streamlit as st
from modules.core import ctx

st.set_page_config(page_title="Schedule", page_icon="🕒")
C = ctx(); DM = C["DM"]

st.header("🕒 Work Scheduling")
st.info("Aquí irá la gestión de turnos/calendario (placeholder).")
st.write(f"Site prefix: `{st.session_state.get('selected_prefix','—')}`")
