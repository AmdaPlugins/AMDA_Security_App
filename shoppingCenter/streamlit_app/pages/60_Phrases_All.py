# -*- coding: utf-8 -*-
import streamlit as st
from modules.core import ctx

st.set_page_config(page_title="All Phrases", page_icon="📖")
C = ctx(); DM, SH = C["DM"], C["SH"]

st.header("📖 All Phrases")
prefix = st.session_state.get("selected_prefix","")
site = SH["get_site_by_prefix"](DM.registry, prefix) if prefix else {}
filt = SH["filter_phrases_by_site"](DM.phrases, site)
st.write(f"**Total phrases:** {len(filt)}")

cats = [""] + SH["get_categories"](filt)
sel = st.selectbox("Filter by category:", cats)

items = [p for p in filt if not sel or p.get("cat")==sel]
if not items:
    st.info("No phrases to display.")
else:
    per=20; pages=(len(items)+per-1)//per
    page=st.number_input("Page", min_value=1, max_value=max(pages,1), value=1)
    a=(page-1)*per; b=min(a+per, len(items))
    st.caption(f"Showing {a+1}-{b} of {len(items)}")
    for i,p in enumerate(items[a:b], a+1):
        st.markdown(f"**#{i} [{p.get('cat','—')}]** {p.get('en','—')}  \n🌐 *{p.get('es','—')}*")
