# -*- coding: utf-8 -*-
import streamlit as st
from modules.core import ctx

st.set_page_config(page_title="Search Phrases", page_icon="🔎")
C = ctx(); DM, SH = C["DM"], C["SH"]

st.header("🔎 Filter Phrases")
prefix = st.session_state.get("selected_prefix","")
site = SH["get_site_by_prefix"](DM.registry, prefix) if prefix else {}
filt = SH["filter_phrases_by_site"](DM.phrases, site)

cats = SH["get_categories"](filt)
hots = SH["get_hotwords"](filt)

c1,c2,c3,c4 = st.columns([2,2,3,2])
with c1: cat = st.selectbox("📂 Category", [""]+cats)
with c2: hot = st.selectbox("🔑 Hotword",  [""]+hots)
with c3: custom = st.text_input("✍️ Custom hotword")
with c4: limit = st.slider("🔢 Amount", 1, 50, 10)
hw = (custom or hot or "").strip().lower()

if st.button("🔍 Search"):
    res=[]
    for p in filt:
        if cat and p.get("cat") != cat: continue
        if hw:
            en=(p.get("en") or "").lower(); es=(p.get("es") or "").lower()
            hl=[h.lower() for h in (p.get("hotwords") or [])]
            if hw not in en and hw not in es and hw not in hl: continue
        res.append(p)
        if len(res)>=limit: break
    st.subheader(f"🧠 Results ({len(res)})")
    if not res: st.warning("No phrases found.")
    for i,p in enumerate(res,1):
        with st.expander(f"#{i} [{p.get('cat','—')}] {p.get('en','—')}", expanded=False):
            c1,c2 = st.columns(2)
            with c1: st.write("**English**"); st.info(p.get('en','—'))
            with c2: st.write("**Spanish**"); st.success(p.get('es','—'))
            if p.get('hotwords'): st.write("**Hotwords:** " + ", ".join(p['hotwords']))
