# -*- coding: utf-8 -*-
import uuid, io, base64, hashlib
from pathlib import Path
import streamlit as st
try:
    from PIL import Image
except Exception:
    Image = None
from modules.core import ctx

st.set_page_config(page_title="Officers", page_icon="👮")
C = ctx(); DM, CFG = C["DM"], C["CFG"]
st.header("👮 Officers Roster")

def _ensure_photos_dir():
    CFG.PHOTOS_DIR.mkdir(parents=True, exist_ok=True); return CFG.PHOTOS_DIR

def _save_uploaded_image(uploaded_file, dest:Path):
    data = uploaded_file.read()
    if Image is None:
        with open(dest,"wb") as f: f.write(data); return
    img = Image.open(io.BytesIO(data))
    if img.mode in ("RGBA","P"): img = img.convert("RGB")
    img.save(dest, format="PNG", optimize=True)

with st.expander("➕ Add new officer", expanded=False):
    with st.form("officer_add"):
        c1,c2 = st.columns([2,1])
        with c1:
            name  = st.text_input("Full name *")
            email = st.text_input("Email", placeholder="name@company.com")
            phone = st.text_input("Phone", placeholder="+1 555 123 4567")
        with c2:
            photo = st.file_uploader("Photo (jpg/png/webp)", type=["jpg","jpeg","png","webp"])
        ok = st.form_submit_button("Add officer", type="primary")
        if ok:
            if not name.strip() or (not email.strip() and not phone.strip()):
                st.error("Name is required and at least one contact (email or phone).")
            else:
                oid = str(uuid.uuid4()); photo_path = ""
                if photo is not None:
                    dest = _ensure_photos_dir() / f"{oid}.png"
                    _save_uploaded_image(photo, dest); photo_path = str(dest)
                offs = list(DM.officers or [])
                offs.append({"id":oid,"name":name.strip(),"email":email.strip(),"phone":phone.strip(),"status":"Active","photo_path":photo_path})
                DM.save_officers(offs); st.success(f"Officer **{name.strip()}** added."); st.rerun()

offs = list(DM.officers or [])
if not offs:
    st.info("No officers yet.")
else:
    for o in offs:
        with st.container():
            c1,c2,c3,c4 = st.columns([0.12,0.38,0.25,0.25])
            with c1:
                tag=""
                if o.get("photo_path") and Path(o["photo_path"]).exists():
                    with open(o["photo_path"],"rb") as f: b64=base64.b64encode(f.read()).decode("ascii")
                    tag=f'<img src="data:image/*;base64,{b64}" style="width:48px;height:48px;border-radius:50%;object-fit:cover;border:1px solid rgba(0,0,0,.1);" />'
                if not tag:
                    initials="".join([p[0] for p in (o.get("name","").split())][:2]).upper() or "?"
                    colors=["#E3F2FD","#E8F5E9","#FFF3E0","#F3E5F5","#E0F7FA","#FCE4EC","#FFFDE7","#EDE7F6"]
                    color=colors[int(hashlib.sha256((o.get("name","")).encode()).hexdigest()[:2],16)%8]
                    tag=f'<div style="width:48px;height:48px;border-radius:50%;background:{color};display:flex;align-items:center;justify-content:center;font-weight:700;">{initials}</div>'
                st.markdown(tag, unsafe_allow_html=True)
            with c2: st.write(f"**{o.get('name','')}**"); st.caption(o.get("status","Active"))
            with c3: st.caption(f"📧 {o.get('email','—') or '—'}")
            with c4: st.caption(f"📞 {o.get('phone','—') or '—'}")
        st.markdown("---")
