# -*- coding: utf-8 -*-
# 📦 Imports
import streamlit as st
from pathlib import Path
import sys
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import re
import uuid
import base64, hashlib, io
try:
    from PIL import Image
except Exception:
    Image = None

# 🔧 Rutas de proyecto (robustas)
# Este archivo está en: .../AmdaOps/shoppingCenter/streamlit_app/Home.py
APP_DIR  = Path(__file__).resolve().parent
SITE_DIR = APP_DIR.parent                # .../AmdaOps/shoppingCenter
ROOT_DIR = SITE_DIR.parent               # .../AmdaOps

# Asegura import de módulos: from Shared.xxx import ...
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# 🧠 Módulos compartidos (con fallback si faltan)
def load_shared_modules():
    try:
        from Shared.loader import load_phrases
        from Shared.registry import load_registry, get_prefixes, get_site_by_prefix
        from Shared.phrase import filter_phrases_by_site, get_categories, get_hotwords
        return {
            'load_phrases': load_phrases,
            'load_registry': load_registry,
            'get_prefixes': get_prefixes,
            'get_site_by_prefix': get_site_by_prefix,
            'filter_phrases_by_site': filter_phrases_by_site,
            'get_categories': get_categories,
            'get_hotwords': get_hotwords
        }
    except ImportError as e:
        st.error(f"❌ Error importando módulos Shared: {e}")

        # Fallback suaves para no romper la app
        def _no_op(*args, **kwargs): return []
        def _get_prefixes(reg):
            if isinstance(reg, list):
                if reg and isinstance(reg[0], dict):
                    return [r.get('prefix') for r in reg if r.get('prefix')]
                if reg and isinstance(reg[0], str):
                    return [s for s in reg if s.strip()]
            return []
        def _get_site_by_prefix(reg, pref):
            if isinstance(reg, list):
                if reg and isinstance(reg[0], dict):
                    return next((r for r in reg if r.get('prefix') == pref), {})
                if reg and isinstance(reg[0], str) and pref in reg:
                    return {"prefix": pref, "site": "ShoppingCenter", "name": f"Site {pref}"}
            return {}

        return {
            'load_phrases': _no_op,
            'load_registry': _no_op,
            'get_prefixes': _get_prefixes,
            'get_site_by_prefix': _get_site_by_prefix,
            'filter_phrases_by_site': lambda x, y: x,
            'get_categories': lambda x: sorted({p.get('cat') for p in x if p.get('cat')}),
            'get_hotwords': lambda x: sorted({h for p in x for h in (p.get('hotwords') or [])})
        }

modules = load_shared_modules()

# ⚙️ Config
class Config:
    """Gestión centralizada de paths y archivos."""
    def __init__(self):
        # Datos reales en .../shoppingCenter/data
        self.DATA_DIR       = SITE_DIR / "data"
        self.PHOTOS_DIR     = self.DATA_DIR / "officers_photos"
        self.PHRASES_PATH   = self.DATA_DIR / "181_line__bank_Shoping_Center_en_es.json"
        self.REGISTRY_PATH  = self.DATA_DIR / "site_registry.json"
        self.OFFICERS_PATH  = self.DATA_DIR / "security_officers.json"
        self.SCHEDULES_PATH = self.DATA_DIR / "work_schedules.json"
        self.TIME_LOGS_PATH = self.DATA_DIR / "time_logs.json"
        self._ensure_files()

    def _ensure_files(self):
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
        defaults = {
            self.OFFICERS_PATH: [],
            self.SCHEDULES_PATH: [],
            self.TIME_LOGS_PATH: []
        }
        for fp, dv in defaults.items():
            if not fp.exists():
                fp.write_text(json.dumps(dv, ensure_ascii=False, indent=2), encoding="utf-8")
        if not self.REGISTRY_PATH.exists():
            default_registry = [{
                "prefix": "DEFAULT",
                "site": "ShoppingCenter",
                "name": "Default Shopping Center",
                "status": "Active",
                "address": "123 Main Street",
                "city": "Anytown",
                "state": "CA",
                "zip": "12345",
                "country": "USA",
                "maps_link": "https://maps.google.com"
            }]
            self.REGISTRY_PATH.write_text(json.dumps(default_registry, ensure_ascii=False, indent=2), encoding="utf-8")

    def validate_core_paths(self) -> List[str]:
        missing = []
        if not self.PHRASES_PATH.exists():  missing.append(f"Phrases: `{self.PHRASES_PATH}`")
        if not self.REGISTRY_PATH.exists(): missing.append(f"Registry: `{self.REGISTRY_PATH}`")
        return missing

# 📚 Data Manager
class DataManager:
    def __init__(self, config: Config, modules: Dict):
        self.cfg = config
        self.m   = modules or {}
        self._phrases = self._registry = self._officers = self._schedules = self._time_logs = None

    @property
    def phrases(self):
        if self._phrases is None:
            fn = self.m.get('load_phrases'); self._phrases = fn(self.cfg.PHRASES_PATH) if callable(fn) else []
        return self._phrases

    @property
    def registry(self):
        if self._registry is None:
            fn = self.m.get('load_registry'); raw = fn(self.cfg.REGISTRY_PATH) if callable(fn) else []
            self._registry = self._normalize_registry(raw)
        return self._registry

    def _normalize_registry(self, r):
        if not r: return [{
            "prefix":"DEFAULT","site":"ShoppingCenter","name":"Default Site","status":"Active",
            "address":"123 Main St","city":"Anytown","state":"CA","zip":"12345","country":"USA"
        }]
        if isinstance(r, dict): r = [r]
        out = []
        for i, it in enumerate(r):
            if isinstance(it, dict) and it.get("prefix"):
                base = {
                    "prefix": it.get("prefix"),
                    "site": it.get("site","ShoppingCenter"),
                    "name": it.get("name", f"Site {it.get('prefix')}"),
                    "status": it.get("status","Active"),
                    "address": it.get("address", f"{i+1} Example St"),
                    "city": it.get("city","City"),
                    "state": it.get("state","ST"),
                    "zip": it.get("zip","12345"),
                    "country": it.get("country","USA")
                }
                base.update({k:v for k,v in it.items() if k not in base})
                out.append(base)
            elif isinstance(it, str) and it.strip():
                out.append({
                    "prefix": it.strip(),"site":"ShoppingCenter","name":f"Site {it.strip()}",
                    "status":"Active","address":f"{i+1} Example St","city":"City","state":"ST","zip":"12345","country":"USA"
                })
        return out or [{
            "prefix":"DEFAULT","site":"ShoppingCenter","name":"Default Site","status":"Active",
            "address":"123 Main St","city":"Anytown","state":"CA","zip":"12345","country":"USA"
        }]

    @property
    def officers(self):
        if self._officers is None:
            self._officers = json.loads(self.cfg.OFFICERS_PATH.read_text(encoding="utf-8"))
        return self._officers

    @property
    def schedules(self):
        if self._schedules is None:
            self._schedules = json.loads(self.cfg.SCHEDULES_PATH.read_text(encoding="utf-8"))
        return self._schedules

    @property
    def time_logs(self):
        if self._time_logs is None:
            self._time_logs = json.loads(self.cfg.TIME_LOGS_PATH.read_text(encoding="utf-8"))
        return self._time_logs

    def save_officers(self, data): self.cfg.OFFICERS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"); self._officers = data; return True
    def save_schedules(self, data): self.cfg.SCHEDULES_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"); self._schedules = data; return True
    def save_time_logs(self, data): self.cfg.TIME_LOGS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"); self._time_logs = data; return True
    def save_registry(self, data):  self.cfg.REGISTRY_PATH.write_text(json.dumps(data,  ensure_ascii=False, indent=2), encoding="utf-8"); self._registry  = data; return True

# 🎛️ UI helpers (avatares/fotos)
def _initials(name:str)->str:
    parts = [p for p in re.split(r"\s+", (name or "").strip()) if p]
    if not parts: return "?"
    return (parts[0][0] + (parts[-1][0] if len(parts)>1 else (parts[0][1] if len(parts[0])>1 else ""))).upper()

def _palette(name:str)->str:
    pal = ["#E3F2FD","#E8F5E9","#FFF3E0","#F3E5F5","#E0F7FA","#FCE4EC","#FFFDE7","#EDE7F6"]
    h = hashlib.sha256((name or "").encode("utf-8")).hexdigest()
    return pal[int(h[:2],16)%len(pal)]

def _avatar_html(txt:str, size:int=48, bg:str="#EEE")->str:
    return f"""
    <div style="width:{size}px;height:{size}px;border-radius:50%;background:{bg};
    display:flex;align-items:center;justify-content:center;font-weight:700;color:#333;
    border:1px solid rgba(0,0,0,.08);font-family:system-ui,Segoe UI,Roboto;line-height:1;">{txt}</div>"""

def _img_tag(path:str,size:int=48)->str:
    try:
        with open(path,"rb") as f: b64 = base64.b64encode(f.read()).decode("ascii")
        return f'<img src="data:image/*;base64,{b64}" style="width:{size}px;height:{size}px;border-radius:50%;object-fit:cover;border:1px solid rgba(0,0,0,.1);" />'
    except Exception: return ""

def _ensure_photos_dir(cfg:Config)->Path:
    p = cfg.PHOTOS_DIR; p.mkdir(parents=True, exist_ok=True); return p

def _save_uploaded_image(uploaded_file, dest:Path):
    try:
        data = uploaded_file.read()
        if Image is not None:
            img = Image.open(io.BytesIO(data))
            if img.mode in ("RGBA","P"): img = img.convert("RGB")
            img.save(dest, format="PNG", optimize=True)
        else:
            dest.write_bytes(data)
        return True
    except Exception as e:
        st.error(f"Error guardando imagen: {e}"); return False

# 🖥️ Config de página
st.set_page_config(page_title="AmdaOps - Security Management", layout="wide", page_icon="🛡️", initial_sidebar_state="expanded")
st.title("🛡️ AmdaOps - Security Management System")

# ⚡ Carga y validaciones
cfg = Config()
missing = cfg.validate_core_paths()
if missing:
    st.error("❌ **Faltan archivos requeridos:**")
    for m in missing: st.write(f"- {m}")
    st.stop()

dm = DataManager(cfg, modules)

# 🧭 Sidebar: selección de sitio
def _safe_prefixes(reg)->List[str]:
    if not reg: return []
    if isinstance(reg, list) and reg:
        if isinstance(reg[0], dict): return [r.get("prefix") for r in reg if r.get("prefix")]
        if isinstance(reg[0], str):  return [s for s in reg if s.strip()]
    return []

try:
    prefixes = modules['get_prefixes'](dm.registry)
    if not prefixes: prefixes = _safe_prefixes(dm.registry)
except Exception:
    prefixes = _safe_prefixes(dm.registry)

if not prefixes:
    prefixes = ["DEFAULT"]
    dm.save_registry([{
        "prefix":"DEFAULT","site":"ShoppingCenter","name":"Default Site","status":"Active",
        "address":"123 Main St","city":"Anytown","state":"CA","zip":"12345","country":"USA"
    }])

st.sidebar.title("🧭 AmdaOps Navigation")
st.sidebar.subheader("🏷️ Site Selection")
options = ["➕ Add new site…"] + prefixes
last_sel = st.session_state.get("last_selected_prefix")
idx = 1 + prefixes.index(last_sel) if last_sel in prefixes else 1 if len(options)>1 else 0
choice = st.sidebar.selectbox("Select Site", options, index=min(idx, len(options)-1), key="site_selector")

adding = (choice == "➕ Add new site…")
st.session_state["adding_site"] = adding
selected_prefix = "" if adding else choice

# Info sitio en sidebar
try:
    site_info = modules['get_site_by_prefix'](dm.registry, selected_prefix) if selected_prefix else {}
except Exception:
    site_info = next((r for r in dm.registry if isinstance(r, dict) and r.get("prefix")==selected_prefix), {}) if selected_prefix else {}

if site_info:
    st.sidebar.divider()
    st.sidebar.subheader("📍 Selected Site")
    st.sidebar.write(f"**Name:** {site_info.get('name','N/A')}")
    st.sidebar.write(f"**Type:** {site_info.get('site','N/A')}")
    st.sidebar.write(f"**Status:** {site_info.get('status','Active')}")
    st.sidebar.write(f"**Address:** {site_info.get('address','N/A')}")
    if site_info.get("maps_link"):
        st.sidebar.markdown(f"🌍 [Google Maps]({site_info['maps_link']})")

# 🔗 Menú
st.sidebar.divider()
st.sidebar.subheader("📚 Application Pages")
menu = st.sidebar.radio("Go to", ["Home", "Work Scheduling", "Time Tracking", "Search phrases", "View all"], key="nav_menu")

# ===== Home: Site Management + Officers (compacto) =====
def render_home(selected_prefix:str):
    st.subheader("🏢 Site Management")
    # Lectura simple (dejar CRUD avanzado para después)
    c1,c2,c3 = st.columns(3)
    with c1:
        st.markdown(f"**Prefix:** `{selected_prefix or '—'}`")
        st.markdown(f"**Type:** {site_info.get('site','—') if site_info else '—'}")
        st.markdown(f"**Name:** {site_info.get('name','—') if site_info else '—'}")
    with c2:
        st.markdown(f"**Address:** {site_info.get('address','—') if site_info else '—'}")
        st.markdown(f"**City:** {site_info.get('city','—') if site_info else '—'}")
    with c3:
        st.markdown(f"**State:** {site_info.get('state','—') if site_info else '—'}")
        st.markdown(f"**ZIP:** {site_info.get('zip','—') if site_info else '—'}")

    st.divider()
    st.subheader("👮 Officers Roster")

    # Alta rápida
    with st.expander("➕ Add new officer", expanded=False):
        with st.form("officer_add"):
            col1,col2 = st.columns([1.5,1])
            with col1:
                name  = st.text_input("Full name *")
                email = st.text_input("Email", placeholder="name@company.com")
                phone = st.text_input("Phone", placeholder="+1 555 123 4567")
            with col2:
                photo = st.file_uploader("Photo (jpg/png/webp)", type=["jpg","jpeg","png","webp"])
            ok = st.form_submit_button("Add officer", type="primary")
            if ok:
                if not name.strip() or (not email.strip() and not phone.strip()):
                    st.error("Name is required and at least one contact (email or phone).")
                else:
                    oid = str(uuid.uuid4())
                    ppath = ""
                    if photo is not None:
                        dest = _ensure_photos_dir(cfg) / f"{oid}.png"
                        if _save_uploaded_image(photo, dest): ppath = str(dest)
                    offs = list(dm.officers or [])
                    offs.append({"id":oid,"name":name.strip(),"email":email.strip(),"phone":phone.strip(),
                                 "status":"Active","photo_path":ppath,"created_at":datetime.now().isoformat()})
                    if dm.save_officers(offs):
                        st.success(f"Officer **{name.strip()}** added.")
                        st.rerun()

    # Listado
    offs = list(dm.officers or [])
    if not offs:
        st.info("No officers yet. Use **Add new officer** to create one.")
    else:
        for i, off in enumerate(offs):
            with st.container():
                c1,c2,c3,c4 = st.columns([0.12,0.38,0.25,0.25])
                with c1:
                    tag = ""
                    if off.get("photo_path") and Path(off["photo_path"]).exists():
                        tag = _img_tag(off["photo_path"], 48)
                    if not tag:
                        tag = _avatar_html(_initials(off.get("name","")), bg=_palette(off.get("name","")))
                    st.markdown(tag, unsafe_allow_html=True)
                with c2:
                    st.write(f"**{off.get('name','')}**")
                    st.caption(off.get("status","Active"))
                with c3:
                    st.caption(f"📧 {off.get('email','—') or '—'}")
                with c4:
                    st.caption(f"📞 {off.get('phone','—') or '—'}")
            st.markdown("---")

# 🔎 Buscar frases
def render_search(selected_prefix:str):
    st.subheader("🔎 Filter Phrases")
    try:
        s = modules['get_site_by_prefix'](dm.registry, selected_prefix) if selected_prefix else {}
    except Exception:
        s = next((r for r in dm.registry if r.get("prefix")==selected_prefix), {}) if selected_prefix else {}
    filt = modules.get('filter_phrases_by_site', lambda x,y:x)(dm.phrases, s)
    cats = modules.get('get_categories', lambda x:[])(filt)
    hots = modules.get('get_hotwords', lambda x:[])(filt)

    c1,c2,c3,c4 = st.columns([2,2,3,2])
    with c1: cat = st.selectbox("📂 Category", [""]+cats)
    with c2: hot = st.selectbox("🔑 Hotword",  [""]+hots)
    with c3: custom = st.text_input("✍️ Custom hotword")
    with c4: limit = st.slider("🔢 Amount", 1, 50, 10)
    hw = (custom or hot or "").strip().lower()

    if st.button("🔍 Search"):
        res = []
        for p in filt:
            if cat and p.get("cat") != cat: continue
            if hw:
                en = (p.get("en") or "").lower(); es = (p.get("es") or "").lower()
                hotl = [h.lower() for h in (p.get("hotwords") or [])]
                if hw not in en and hw not in es and hw not in hotl: continue
            res.append(p)
            if len(res) >= limit: break
        st.subheader(f"🧠 Results ({len(res)})")
        if not res: st.warning("No phrases found."); return
        for i, p in enumerate(res, 1):
            with st.expander(f"#{i} [{p.get('cat','—')}] {p.get('en','—')}", expanded=False):
                c1,c2 = st.columns(2)
                with c1: st.write("**English**"); st.info(p.get('en','—'))
                with c2: st.write("**Spanish**"); st.success(p.get('es','—'))
                if p.get('hotwords'): st.write("**Hotwords:** " + ", ".join(p['hotwords']))

# 📖 Ver todas
def render_view_all(selected_prefix:str):
    st.subheader("📖 All Phrases")
    try:
        s = modules['get_site_by_prefix'](dm.registry, selected_prefix) if selected_prefix else {}
    except Exception:
        s = next((r for r in dm.registry if r.get("prefix")==selected_prefix), {}) if selected_prefix else {}
    filt = modules.get('filter_phrases_by_site', lambda x,y:x)(dm.phrases, s)
    st.write(f"**Total phrases:** {len(filt)}")
    cats = [""] + modules.get('get_categories', lambda x:[])(filt)
    sel = st.selectbox("Filter by category:", cats)
    items = [p for p in filt if not sel or p.get("cat")==sel]
    if not items: st.info("No phrases to display."); return
    per = 20; pages = (len(items)+per-1)//per
    page = st.number_input("Page", min_value=1, max_value=max(pages,1), value=1)
    a = (page-1)*per; b = min(a+per, len(items))
    st.caption(f"Showing {a+1}-{b} of {len(items)}")
    for i,p in enumerate(items[a:b], a+1):
        st.markdown(f"**#{i} [{p.get('cat','—')}]** {p.get('en','—')}  \n🌐 *{p.get('es','—')}*")
    st.divider()

# 🕒 Placeholders
def render_sched(selected_prefix:str):
    st.subheader("🕒 Work Scheduling")
    st.info("Aquí irá la gestión de turnos/calendario.")

def render_time(selected_prefix:str):
    st.subheader("⏱️ Time Tracking")
    st.info("Aquí irán time logs, métricas y KPIs.")

# 🚦 Router
if menu == "Home":
    render_home(selected_prefix)
elif menu == "Work Scheduling":
    render_sched(selected_prefix)
elif menu == "Time Tracking":
    render_time(selected_prefix)
elif menu == "Search phrases":
    render_search(selected_prefix)
elif menu == "View all":
    render_view_all(selected_prefix)
