# ðŸ“¦ Imports
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

# ðŸ”— Add shared folder to path
shared_path = Path(__file__).resolve().parent.parent / "shared"
sys.path.append(str(shared_path))

# âš™ï¸ Page config
st.set_page_config(
    page_title="AmdaOps - Security Management",
    layout="wide",
    page_icon="ðŸ›¡ï¸",
    initial_sidebar_state="expanded"
)

# ðŸ§  Load shared modules with better error handling
def load_shared_modules():
    """Dynamically load shared modules with comprehensive error handling"""
    try:
        try:
            from Shared.loader import load_phrases
            from Shared.registry import load_registry, get_prefixes, get_site_by_prefix
            from Shared.phrase import filter_phrases_by_site, get_categories, get_hotwords
        except ImportError as e:
            st.error(f"âŒ **Error importing shared modules**: {e}")

            # Dummies para no romper la app
            def load_phrases(path):
                return []

            def load_registry(path):
                if path.exists():
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            # lista de strings -> lista de dicts
                            if isinstance(data, list) and data and isinstance(data[0], str):
                                corrected_data = [{"prefix": p, "name": f"Site {p}", "site": "ShoppingCenter"} for p in data]
                                with open(path, 'w', encoding='utf-8') as f_out:
                                    json.dump(corrected_data, f_out, indent=2, ensure_ascii=False)
                                return corrected_data
                            # dict suelto -> lista
                            if isinstance(data, dict):
                                return [data]
                            return data
                    except Exception as e2:
                        st.error(f"Error loading registry: {e2}")
                return []

            def get_prefixes(registry):
                if isinstance(registry, list) and registry:
                    if isinstance(registry[0], dict):
                        return [site.get('prefix', '') for site in registry if isinstance(site, dict) and site.get('prefix')]
                    if isinstance(registry[0], str):
                        return [s for s in registry if isinstance(s, str) and s.strip()]
                return []

            def get_site_by_prefix(registry, prefix):
                if isinstance(registry, list):
                    if registry and isinstance(registry[0], dict):
                        return next((site for site in registry if site.get('prefix') == prefix), {})
                    if registry and isinstance(registry[0], str):
                        if prefix in registry:
                            return {"prefix": prefix, "site": "ShoppingCenter", "name": f"Site {prefix}"}
                return {}

            def filter_phrases_by_site(phrases, site_info):
                return phrases

            def get_categories(phrases):
                return sorted({p.get('cat') for p in phrases if p.get('cat')})

            def get_hotwords(phrases):
                hot = set()
                for p in phrases:
                    if p.get('hotwords'):
                        hot.update(p['hotwords'])
                return sorted(hot)

        return {
            'load_phrases': load_phrases,
            'load_registry': load_registry,
            'get_prefixes': get_prefixes,
            'get_site_by_prefix': get_site_by_prefix,
            'filter_phrases_by_site': filter_phrases_by_site,
            'get_categories': get_categories,
            'get_hotwords': get_hotwords
        }
    except Exception as e:
        st.error(f"âŒ **Unexpected error loading modules**: {e}")
        return None


# ðŸ“ Configuration
class Config:
    """Centralized configuration management"""

    def __init__(self):
        self.BASE_DIR = Path(__file__).resolve().parent
        self.DATA_DIR = self.BASE_DIR / "data"
        self.DATA_DIR.mkdir(exist_ok=True)

        # Photos dir for officers
        self.PHOTOS_DIR = self.DATA_DIR / "officers_photos"

        # Core data files
        self.PHRASES_PATH = self.DATA_DIR / "181_line__bank_Shoping_Center_en_es.json"
        self.REGISTRY_PATH = self.DATA_DIR / "site_registry.json"

        # Security officer files
        self.OFFICERS_PATH = self.DATA_DIR / "security_officers.json"
        self.SCHEDULES_PATH = self.DATA_DIR / "work_schedules.json"
        self.TIME_LOGS_PATH = self.DATA_DIR / "time_logs.json"

        self._initialize_json_files()

    def _initialize_json_files(self):
        new_files = {
            self.OFFICERS_PATH: [],
            self.SCHEDULES_PATH: [],
            self.TIME_LOGS_PATH: []
        }
        for file_path, default_data in new_files.items():
            if not file_path.exists():
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(default_data, f, indent=2, ensure_ascii=False)
                except Exception as e:
                    st.error(f"Error creating {file_path}: {e}")

        # Crear carpeta de fotos
        try:
            self.PHOTOS_DIR.mkdir(exist_ok=True, parents=True)
        except Exception as e:
            st.error(f"Error creating photos folder: {e}")

        # Inicializar site_registry.json con formato correcto si no existe
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
            try:
                with open(self.REGISTRY_PATH, 'w', encoding='utf-8') as f:
                    json.dump(default_registry, f, indent=2, ensure_ascii=False)
            except Exception as e:
                st.error(f"Error creating default registry: {e}")

    def validate_core_paths(self) -> List[str]:
        missing_files = []
        for path, name in [(self.PHRASES_PATH, "Phrases"), (self.REGISTRY_PATH, "Registry")]:
            if not path.exists():
                missing_files.append(f"{name}: `{str(path)}`")
        return missing_files


# ðŸ“Š Data Manager
class DataManager:
    """Manage data loading and caching"""

    def __init__(self, config: Config, modules: Dict):
        self.config = config
        self.modules = modules or {}
        self._phrases = None
        self._registry = None
        self._officers = None
        self._schedules = None
        self._time_logs = None

    @property
    def phrases(self) -> List[Dict]:
        if self._phrases is None:
            self._phrases = self._load_data('phrases')
        return self._phrases

    @property
    def registry(self) -> List[Dict]:
        if self._registry is None:
            self._registry = self._load_data('registry')
            self._registry = self._validate_and_fix_registry(self._registry)
        return self._registry

    def _validate_and_fix_registry(self, registry_data):
        """Normaliza el registry a lista de dicts con campos base y lo guarda."""
        if not registry_data:
            cleaned = [{
                "prefix": "DEFAULT",
                "site": "ShoppingCenter",
                "name": "Default Site",
                "status": "Active",
                "address": "123 Main St",
                "city": "Anytown",
                "state": "CA",
                "zip": "12345",
                "country": "USA"
            }]
            try:
                with open(self.config.REGISTRY_PATH, 'w', encoding='utf-8') as f:
                    json.dump(cleaned, f, indent=2, ensure_ascii=False)
            except Exception as e:
                st.error(f"Error saving corrected registry: {e}")
            return cleaned

        if isinstance(registry_data, dict):
            registry_data = [registry_data]
        if not isinstance(registry_data, list):
            registry_data = []

        cleaned: List[Dict[str, Any]] = []
        for i, item in enumerate(registry_data):
            if isinstance(item, dict) and item.get("prefix"):
                base = {
                    "prefix": item.get("prefix"),
                    "site": item.get("site", "ShoppingCenter"),
                    "name": item.get("name", f"Site {item.get('prefix')}"),
                    "status": item.get("status", "Active"),
                    "address": item.get("address", f"{i+1} Example Street"),
                    "city": item.get("city", "City"),
                    "state": item.get("state", "ST"),
                    "zip": item.get("zip", "12345"),
                    "country": item.get("country", "USA"),
                }
                for k, v in item.items():
                    if k not in base:
                        base[k] = v
                cleaned.append(base)
            elif isinstance(item, str) and item.strip():
                cleaned.append({
                    "prefix": item.strip(),
                    "site": "ShoppingCenter",
                    "name": f"Site {item.strip()}",
                    "status": "Active",
                    "address": f"{i+1} Example Street",
                    "city": "City",
                    "state": "ST",
                    "zip": "12345",
                    "country": "USA"
                })

        if not cleaned:
            cleaned = [{
                "prefix": "DEFAULT",
                "site": "ShoppingCenter",
                "name": "Default Site",
                "status": "Active",
                "address": "123 Main St",
                "city": "Anytown",
                "state": "CA",
                "zip": "12345",
                "country": "USA"
            }]

        try:
            with open(self.config.REGISTRY_PATH, 'w', encoding='utf-8') as f:
                json.dump(cleaned, f, indent=2, ensure_ascii=False)
        except Exception as e:
            st.error(f"Error saving normalized registry: {e}")

        return cleaned

    @property
    def officers(self) -> List[Dict]:
        if self._officers is None:
            self._officers = self._load_data('officers')
        return self._officers

    @property
    def schedules(self) -> List[Dict]:
        if self._schedules is None:
            self._schedules = self._load_data('schedules')
        return self._schedules

    @property
    def time_logs(self) -> List[Dict]:
        if self._time_logs is None:
            self._time_logs = self._load_data('time_logs')
        return self._time_logs

    def _load_data(self, data_type: str) -> Optional[List[Dict]]:
        try:
            if data_type == 'phrases':
                fn = self.modules.get('load_phrases')
                return fn(self.config.PHRASES_PATH) if callable(fn) else []
            elif data_type == 'registry':
                fn = self.modules.get('load_registry')
                return fn(self.config.REGISTRY_PATH) if callable(fn) else []
            elif data_type == 'officers':
                with open(self.config.OFFICERS_PATH, 'r', encoding='utf-8') as f:
                    return json.load(f)
            elif data_type == 'schedules':
                with open(self.config.SCHEDULES_PATH, 'r', encoding='utf-8') as f:
                    return json.load(f)
            elif data_type == 'time_logs':
                with open(self.config.TIME_LOGS_PATH, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            st.error(f"âŒ **Error loading {data_type}**: {e}")
            return []
        return []

    def save_officers(self, officers_data: List[Dict]):
        try:
            with open(self.config.OFFICERS_PATH, "w", encoding="utf-8") as f:
                json.dump(officers_data, f, indent=2, ensure_ascii=False)
            self._officers = officers_data
            return True
        except Exception as e:
            st.error(f"Error saving officers: {e}")
            return False

    def save_schedules(self, schedules_data: List[Dict]):
        try:
            with open(self.config.SCHEDULES_PATH, "w", encoding="utf-8") as f:
                json.dump(schedules_data, f, indent=2, ensure_ascii=False)
            self._schedules = schedules_data
            return True
        except Exception as e:
            st.error(f"Error saving schedules: {e}")
            return False

    def save_time_logs(self, time_logs_data: List[Dict]):
        try:
            with open(self.config.TIME_LOGS_PATH, "w", encoding="utf-8") as f:
                json.dump(time_logs_data, f, indent=2, ensure_ascii=False)
            self._time_logs = time_logs_data
            return True
        except Exception as e:
            st.error(f"Error saving time logs: {e}")
            return False

    def save_registry(self, registry_data: List[Dict]):
        try:
            with open(self.config.REGISTRY_PATH, "w", encoding="utf-8") as f:
                json.dump(registry_data, f, indent=2, ensure_ascii=False)
            self._registry = registry_data
            return True
        except Exception as e:
            st.error(f"Error saving registry: {e}")
            return False


# ðŸŽ›ï¸ UI Components (Site Management + Officers con foto/initiales)
class UIComponents:
    """Reusable UI components with site management + officers roster (photos/initials)."""

    # ===== Helpers =====
    @staticmethod
    def _initials_from_name(name: str) -> str:
        if not name:
            return "?"
        parts = re.split(r"\s+", name.strip())
        initials = [p[0] for p in parts if p]
        return "".join(initials[:2]).upper()

    @staticmethod
    def _color_from_name(name: str) -> str:
        palette = [
            "#E3F2FD", "#E8F5E9", "#FFF3E0", "#F3E5F5",
            "#E0F7FA", "#FCE4EC", "#FFFDE7", "#EDE7F6"
        ]
        h = hashlib.sha256((name or "").encode("utf-8")).hexdigest()
        idx = int(h[:2], 16) % len(palette)
        return palette[idx]

    @staticmethod
    def _avatar_html(initials: str, size: int = 48, bg: str = "#EEE") -> str:
        return f"""
        <div style="
            width:{size}px;height:{size}px;border-radius:50%;
            background:{bg};display:flex;align-items:center;justify-content:center;
            font-weight:700;color:#333;border:1px solid rgba(0,0,0,.08);
            font-family:system-ui, -apple-system, Segoe UI, Roboto;line-height:1;">
            {initials}
        </div>
        """

    @staticmethod
    def _img_tag_from_path(path: str, size: int = 48) -> str:
        try:
            with open(path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("ascii")
            return f'<img src="data:image/*;base64,{b64}" style="width:{size}px;height:{size}px;border-radius:50%;object-fit:cover;border:1px solid rgba(0,0,0,.1);" />'
        except Exception:
            return ""

    @staticmethod
    def _ensure_photos_dir(config) -> Path:
        try:
            photos_dir = getattr(config, "PHOTOS_DIR", None) or (config.DATA_DIR / "officers_photos")
            photos_dir = Path(photos_dir)
            photos_dir.mkdir(parents=True, exist_ok=True)
            return photos_dir
        except Exception:
            fallback = Path("data") / "officers_photos"
            fallback.mkdir(parents=True, exist_ok=True)
            return fallback

    @staticmethod
    def _save_uploaded_image(uploaded_file, dest_path: Path):
        try:
            data = uploaded_file.read()
            if Image is not None:
                img = Image.open(io.BytesIO(data))
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                img.save(dest_path, format="PNG", optimize=True)
            else:
                with open(dest_path, "wb") as f:
                    f.write(data)
            return True
        except Exception as e:
            st.error(f"Error saving image: {e}")
            return False

    @staticmethod
    def _delete_file(path_str: str):
        try:
            p = Path(path_str)
            if p.exists():
                p.unlink()
                return True
        except Exception:
            pass
        return False

    @staticmethod
    def _rerun():
        try:
            st.rerun()
        except Exception:
            st.experimental_rerun()

    # ===== Site Management =====
    @staticmethod
    def show_site_info(site_info: Dict, selected_prefix: str):
        if site_info:
            with st.container():
                st.subheader("ðŸ¢ Site Details")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Prefix", f"`{selected_prefix}`")
                    st.write(f"**Site Type:** {site_info.get('site', 'N/A')}")
                    st.write(f"**Site Name:** {site_info.get('name', 'N/A')}")
                with col2:
                    st.write(f"**Address:** {site_info.get('address', 'N/A')}")
                    st.write(f"**City:** {site_info.get('city', 'N/A')}")
                    st.write(f"**State:** {site_info.get('state', 'N/A')}")
                    st.write(f"**ZIP:** {site_info.get('zip', 'N/A')}")
                    if site_info.get("maps_link"):
                        st.markdown(f"ðŸŒ [View on Google Maps]({site_info['maps_link']})")

    @staticmethod
    def site_management(data_manager: 'DataManager', selected_prefix: str):
        st.subheader("ðŸ¢ Site Management")

        adding = st.session_state.get("adding_site", False)
        key_prefix = selected_prefix if selected_prefix else "__NEW__"

        if adding:
            site_info = {}
            st.session_state[f'edit_mode_{key_prefix}'] = True
        else:
            try:
                site_info = data_manager.modules['get_site_by_prefix'](data_manager.registry, selected_prefix)
            except Exception:
                site_info = next((r for r in data_manager.registry
                                  if isinstance(r, dict) and r.get("prefix") == selected_prefix), {})

        if f'edit_mode_{key_prefix}' not in st.session_state:
            st.session_state[f'edit_mode_{key_prefix}'] = False

        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

        with col1:
            if adding:
                st.info("ðŸ†• Creating a new site")
            elif not st.session_state[f'edit_mode_{key_prefix}']:
                st.info(f"Currently viewing: **{site_info.get('name', 'Unknown Site')}**")
            else:
                st.warning("ðŸ“ Edit Mode Active - Modifying Site Details")

        with col2:
            # BotÃ³n â€œNew Siteâ€ siempre visible
            if not adding:
                if st.button("âž• New Site", key=f"new_{key_prefix}"):
                    st.session_state["adding_site"] = True
                    st.session_state[f'edit_mode_{key_prefix}'] = False
                    UIComponents._rerun()

            if not adding:
                if not st.session_state[f'edit_mode_{key_prefix}']:
                    if st.button("âœï¸ Edit Site", key=f"edit_{key_prefix}"):
                        st.session_state[f'edit_mode_{key_prefix}'] = True
                        UIComponents._rerun()
                else:
                    if st.button("ðŸ’¾ Save", key=f"save_{key_prefix}", type="primary"):
                        if UIComponents._save_site_details(data_manager, key_prefix):
                            st.session_state[f'edit_mode_{key_prefix}'] = False
                            UIComponents._rerun()

        with col3:
            if adding:
                if st.button("âŒ Cancel Add", key=f"cancel_add_{key_prefix}"):
                    st.session_state["adding_site"] = False
                    st.session_state[f'edit_mode_{key_prefix}'] = False
                    UIComponents._rerun()
            elif st.session_state[f'edit_mode_{key_prefix}']:
                if st.button("âŒ Cancel", key=f"cancel_{key_prefix}"):
                    st.session_state[f'edit_mode_{key_prefix}'] = False
                    UIComponents._rerun()

        with col4:
            if (not adding) and site_info and st.button("ðŸ—‘ï¸ Delete", key=f"delete_{key_prefix}"):
                UIComponents._delete_site_confirmation(data_manager, key_prefix)

        if adding or st.session_state[f'edit_mode_{key_prefix}']:
            UIComponents._render_site_edit_form(data_manager, site_info, key_prefix)
        else:
            UIComponents._render_site_display(data_manager, site_info, key_prefix)

    @staticmethod
    def _render_site_display(data_manager: 'DataManager', site_info: Dict, selected_prefix: str):
        if site_info:
            with st.container():
                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("ðŸ“ Basic Information")
                    st.write(f"**Prefix:** `{site_info.get('prefix', 'N/A')}`")
                    st.write(f"**Site Type:** {site_info.get('site', 'N/A')}")
                    st.write(f"**Site Name:** {site_info.get('name', 'N/A')}")
                    st.write(f"**Status:** {site_info.get('status', 'Active')}")
                    if site_info.get('contact_name'):
                        st.write(f"**Contact:** {site_info.get('contact_name')}")
                    if site_info.get('contact_phone'):
                        st.write(f"**Contact Phone:** {site_info.get('contact_phone')}")
                with col2:
                    st.subheader("ðŸ  Address Details")
                    st.write(f"**Address:** {site_info.get('address', 'N/A')}")
                    st.write(f"**City:** {site_info.get('city', 'N/A')}")
                    st.write(f"**State:** {site_info.get('state', 'N/A')}")
                    st.write(f"**ZIP Code:** {site_info.get('zip', 'N/A')}")
                    st.write(f"**Country:** {site_info.get('country', 'USA')}")
                    if site_info.get("maps_link"):
                        st.markdown(f"### ðŸŒ Navigation")
                        st.markdown(f"[Open in Google Maps]({site_info['maps_link']})")
        else:
            st.warning("No site information available. Please add site details using the Edit button.")

    @staticmethod
    def _render_site_edit_form(data_manager: 'DataManager', site_info: Dict, selected_prefix: str):
        with st.form(key=f"site_edit_form_{selected_prefix}"):
            st.subheader("ðŸ“ Edit Site Details")
            tab1, tab2, tab3 = st.tabs(["Basic Info", "Address", "Additional Details"])

            with tab1:
                col1, col2 = st.columns(2)
                with col1:
                    prefix = st.text_input("ðŸ”¢ Site Prefix*", value=site_info.get('prefix', '') if site_info else "")
                    site_type = st.selectbox(
                        "ðŸ¢ Site Type*",
                        options=["ShoppingCenter", "Warehouse", "Parking", "Office", "Residential", "Other"],
                        index=(["ShoppingCenter","Warehouse","Parking","Office","Residential","Other"].index(site_info.get('site','ShoppingCenter'))
                               if site_info and site_info.get('site') in ["ShoppingCenter","Warehouse","Parking","Office","Residential","Other"] else 0)
                    )
                    site_name = st.text_input("ðŸ·ï¸ Site Name*", value=site_info.get('name', '') if site_info else "")
                with col2:
                    status = st.selectbox(
                        "ðŸ“Š Status",
                        options=["Active", "Inactive", "Under Maintenance", "Planned"],
                        index=(["Active","Inactive","Under Maintenance","Planned"].index(site_info.get('status','Active'))
                               if site_info and site_info.get('status') in ["Active","Inactive","Under Maintenance","Planned"] else 0)
                    )
                    contact_name = st.text_input("ðŸ‘¤ Contact Person", value=site_info.get('contact_name', '') if site_info else "")
                    contact_phone = st.text_input("ðŸ“ž Contact Phone", value=site_info.get('contact_phone', '') if site_info else "")

            with tab2:
                col1, col2 = st.columns(2)
                with col1:
                    address = st.text_input("ðŸ“ Street Address*", value=site_info.get('address', '') if site_info else "")
                    city = st.text_input("ðŸŒ† City*", value=site_info.get('city', '') if site_info else "")
                with col2:
                    state = st.text_input("ðŸ—ºï¸ State/Province*", value=site_info.get('state', '') if site_info else "")
                    zip_code = st.text_input("ðŸ“® ZIP/Postal Code*", value=site_info.get('zip', '') if site_info else "")
                country = st.text_input("ðŸ‡ºðŸ‡¸ Country", value=site_info.get('country', 'USA') if site_info else "USA")

            with tab3:
                notes = st.text_area("ðŸ“‹ Notes", value=site_info.get('notes', '') if site_info else "", height=100)
                special_instructions = st.text_area("âš ï¸ Special Instructions", value=site_info.get('special_instructions', '') if site_info else "", height=100)

                st.subheader("ðŸ›¡ï¸ Security Requirements")
                col1, col2 = st.columns(2)
                with col1:
                    required_officers = st.number_input("Minimum Officers Required", min_value=1, max_value=10,
                                                        value=site_info.get('required_officers', 1) if site_info else 1)
                    patrol_frequency = st.selectbox(
                        "Patrol Frequency",
                        options=["30 minutes", "1 hour", "2 hours", "4 hours", "As needed"],
                        index=(["30 minutes","1 hour","2 hours","4 hours","As needed"].index(site_info.get('patrol_frequency','1 hour'))
                               if site_info and site_info.get('patrol_frequency') in ["30 minutes","1 hour","2 hours","4 hours","As needed"] else 1)
                    )
                with col2:
                    has_cctv = st.checkbox("CCTV Available", value=site_info.get('has_cctv', False) if site_info else False)
                    requires_vehicle = st.checkbox("Vehicle Patrol Required", value=site_info.get('requires_vehicle', False) if site_info else False)

            st.markdown("**Note:** Fields marked with * are required")
            submit_button = st.form_submit_button("ðŸ’¾ Save Site Details", type="primary")

            if submit_button:
                if not all([prefix, site_name, address, city, state, zip_code]):
                    st.error("Please fill in all required fields (marked with *)")
                else:
                    full_address = f"{address}, {city}, {state}, {zip_code}, {country}"
                    maps_link = f"https://www.google.com/maps/search/?api=1&query={full_address.replace(' ', '+')}"
                    updated_site = {
                        "prefix": prefix,
                        "site": site_type,
                        "name": site_name,
                        "status": status,
                        "address": address,
                        "city": city,
                        "state": state,
                        "zip": zip_code,
                        "country": country,
                        "contact_name": contact_name,
                        "contact_phone": contact_phone,
                        "maps_link": maps_link,
                        "notes": notes,
                        "special_instructions": special_instructions,
                        "required_officers": required_officers,
                        "patrol_frequency": patrol_frequency,
                        "has_cctv": has_cctv,
                        "requires_vehicle": requires_vehicle,
                        "last_updated": datetime.now().isoformat()
                    }
                    if not site_info:
                        updated_site["created_date"] = datetime.now().isoformat()

                    registry = data_manager.registry.copy()

                    if site_info and site_info.get('prefix') != prefix:
                        registry = [r for r in registry if r.get('prefix') != site_info.get('prefix')]

                    existing_index = next((i for i, r in enumerate(registry) if r.get('prefix') == prefix), -1)
                    if existing_index >= 0:
                        registry[existing_index] = updated_site
                    else:
                        registry.append(updated_site)

                    if data_manager.save_registry(registry):
                        st.success("âœ… Site details saved successfully!")
                        if not site_info or selected_prefix == "__NEW__":
                            st.session_state["adding_site"] = False
                            st.session_state["last_selected_prefix"] = prefix
                            st.session_state[f'edit_mode_{selected_prefix}'] = False
                            UIComponents._rerun()
                        return True
        return False

    @staticmethod
    def _save_site_details(data_manager: 'DataManager', selected_prefix: str) -> bool:
        return True

    @staticmethod
    def _delete_site_confirmation(data_manager: 'DataManager', selected_prefix: str):
        with st.expander("âš ï¸ Confirm Deletion", expanded=True):
            st.error(f"**Danger Zone**: You are about to delete site `{selected_prefix}`")
            st.warning("This action cannot be undone and will remove all associated schedules and data!")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("âœ… Confirm Delete", type="primary"):
                    registry = [r for r in data_manager.registry if r.get('prefix') != selected_prefix]
                    schedules = [s for s in data_manager.schedules if s.get('site_prefix') != selected_prefix]
                    if data_manager.save_registry(registry) and data_manager.save_schedules(schedules):
                        st.success(f"âœ… Site `{selected_prefix}` deleted successfully!")
                        UIComponents._rerun()
            with col2:
                if st.button("âŒ Cancel Deletion"):
                    st.info("Deletion cancelled")

    # ===== Officers Roster =====
    @staticmethod
    def officer_management(data_manager: 'DataManager'):
        st.subheader("ðŸ‘® Officers Roster")

        # Formulario: agregar
        with st.expander("âž• Add new officer", expanded=True):
            with st.form("officer_add_form"):
                col1, col2 = st.columns([1.5, 1])
                with col1:
                    name = st.text_input("Full name *", key="off_add_name")
                    email = st.text_input("Email", key="off_add_email", placeholder="name@company.com")
                    phone = st.text_input("Phone", key="off_add_phone", placeholder="+1 555 123 4567")
                with col2:
                    photo_up = st.file_uploader("Photo (jpg/png/webp)", type=["jpg","jpeg","png","webp"], key="off_add_photo")

                submitted = st.form_submit_button("Add officer", type="primary")
                if submitted:
                    if not name.strip() or (not email.strip() and not phone.strip()):
                        st.error("Name is required and at least one contact (email or phone).")
                    else:
                        new_id = str(uuid.uuid4())
                        photo_path = ""
                        if photo_up is not None:
                            photos_dir = UIComponents._ensure_photos_dir(data_manager.config)
                            dest = photos_dir / f"{new_id}.png"
                            if UIComponents._save_uploaded_image(photo_up, dest):
                                photo_path = str(dest)

                        new_officer = {
                            "id": new_id,
                            "name": name.strip(),
                            "email": email.strip(),
                            "phone": phone.strip(),
                            "status": "Active",
                            "photo_path": photo_path,
                            "created_at": datetime.now().isoformat()
                        }
                        officers = list(data_manager.officers or [])
                        officers.append(new_officer)
                        if data_manager.save_officers(officers):
                            st.success(f"Officer **{new_officer['name']}** added.")
                            UIComponents._rerun()

        st.markdown("---")

        # Lista
        officers = list(data_manager.officers or [])
        if not officers:
            st.info("No officers yet. Use **Add new officer** to create one.")
            return

        for idx, off in enumerate(officers):
            off_id = off.get("id") or f"row-{idx}"
            edit_key = f"officer_edit_{off_id}"
            if edit_key not in st.session_state:
                st.session_state[edit_key] = False

            # Fila compacta con avatar
            with st.container():
                c1, c2, c3, c4, c5 = st.columns([0.12, 0.30, 0.28, 0.20, 0.10])

                # Avatar
                with c1:
                    avatar_html = ""
                    photo_path = off.get("photo_path") or ""
                    if photo_path and Path(photo_path).exists():
                        avatar_html = UIComponents._img_tag_from_path(photo_path, size=48)
                    if not avatar_html:
                        initials = UIComponents._initials_from_name(off.get("name", ""))
                        bg = UIComponents._color_from_name(off.get("name", ""))
                        avatar_html = UIComponents._avatar_html(initials, size=48, bg=bg)
                    st.markdown(avatar_html, unsafe_allow_html=True)

                with c2:
                    st.write(f"**Name:** {off.get('name','')}")
                with c3:
                    st.write(f"**Email:** {off.get('email','â€”') or 'â€”'}")
                with c4:
                    st.write(f"**Phone:** {off.get('phone','â€”') or 'â€”'}")
                with c5:
                    if not st.session_state[edit_key]:
                        if st.button("Edit", key=f"btn_edit_{off_id}"):
                            st.session_state[edit_key] = True
                            UIComponents._rerun()

            # EdiciÃ³n
            if st.session_state[edit_key]:
                with st.form(f"edit_form_{off_id}"):
                    col1, col2, col3 = st.columns([0.35, 0.30, 0.35])
                    with col1:
                        name_e = st.text_input("Full name *", value=off.get("name",""))
                        status_e = st.selectbox("Status", ["Active","Inactive"], index=0 if off.get("status","Active")=="Active" else 1)
                    with col2:
                        email_e = st.text_input("Email", value=off.get("email",""))
                        phone_e = st.text_input("Phone", value=off.get("phone",""))
                    with col3:
                        st.caption("Photo")
                        current_photo = off.get("photo_path") or ""
                        if current_photo and Path(current_photo).exists():
                            st.markdown(UIComponents._img_tag_from_path(current_photo, size=64), unsafe_allow_html=True)
                        photo_new = st.file_uploader("Replace photo", type=["jpg","jpeg","png","webp"], key=f"up_{off_id}")
                        remove_photo = st.checkbox("Remove current photo", value=False, key=f"rm_{off_id}")

                    colA, colB, colC = st.columns([0.2, 0.2, 0.6])
                    with colA:
                        save = st.form_submit_button("Save", type="primary")
                    with colB:
                        cancel = st.form_submit_button("Cancel")
                    with colC:
                        del_click = st.form_submit_button("Delete", help="Delete this officer")

                if save:
                    if not name_e.strip() or (not email_e.strip() and not phone_e.strip()):
                        st.error("Name is required and at least one contact (email or phone).")
                    else:
                        off.update({
                            "name": name_e.strip(),
                            "email": email_e.strip(),
                            "phone": phone_e.strip(),
                            "status": status_e,
                            "updated_at": datetime.now().isoformat()
                        })

                        # Foto
                        if remove_photo and off.get("photo_path"):
                            UIComponents._delete_file(off["photo_path"])
                            off["photo_path"] = ""

                        if photo_new is not None:
                            photos_dir = UIComponents._ensure_photos_dir(data_manager.config)
                            dest = photos_dir / f"{off_id}.png"
                            if UIComponents._save_uploaded_image(photo_new, dest):
                                off["photo_path"] = str(dest)

                        if data_manager.save_officers(officers):
                            st.success("Officer updated.")
                            st.session_state[edit_key] = False
                            UIComponents._rerun()

                if cancel:
                    st.session_state[edit_key] = False
                    UIComponents._rerun()

                if del_click:
                    if off.get("photo_path"):
                        UIComponents._delete_file(off["photo_path"])
                    remaining = [o for o in officers if (o.get("id") or "") != off_id]
                    if data_manager.save_officers(remaining):
                        st.success("Officer deleted.")
                        st.session_state[edit_key] = False
                        UIComponents._rerun()
            st.markdown("---")


# ðŸ  Home: Site Management + Officers
def render_home_page(data_manager: 'DataManager', ui: UIComponents, selected_prefix: str):
    st.title("ðŸ›¡ï¸ AmdaOps - Security Management System")

    # 1) Site Management
    ui.site_management(data_manager, selected_prefix)

    st.divider()

    # 2) Officers Roster
    ui.officer_management(data_manager)


# ðŸ” Search Page
def render_search_page(data_manager: DataManager, selected_prefix: str):
    st.header("ðŸ” Filter Phrases")
    try:
        site_info = data_manager.modules['get_site_by_prefix'](data_manager.registry, selected_prefix)
    except Exception:
        site_info = next((r for r in data_manager.registry if isinstance(r, dict) and r.get("prefix") == selected_prefix), {})
    filter_fn = data_manager.modules.get('filter_phrases_by_site', lambda x, y: x)
    filtered_phrases = filter_fn(data_manager.phrases, site_info)

    col1, col2 = st.columns(2)
    with col1:
        categories = data_manager.modules.get('get_categories', lambda x: [])(filtered_phrases)
        category = st.selectbox("ðŸ“‚ Category", [""] + categories)
        limit = st.slider("ðŸ”¢ Number of phrases", 1, 50, 10)
    with col2:
        hotwords = data_manager.modules.get('get_hotwords', lambda x: [])(filtered_phrases)
        hotword = st.selectbox("ðŸ” Hotword", [""] + hotwords)
        custom_hotword = st.text_input("âœï¸ Or type your own hotword")

    final_hotword = custom_hotword.strip() if custom_hotword.strip() else hotword

    if st.button("ðŸ”Ž Search Phrases", type="primary"):
        with st.spinner("Searching..."):
            results = _search_phrases(filtered_phrases, category, final_hotword, limit)
            _display_search_results(results)


def _search_phrases(phrases: List[Dict], category: str, hotword: str, limit: int) -> List[Dict]:
    results = []
    for phrase in phrases:
        if category and phrase.get("cat") != category:
            continue
        if hotword:
            hw = hotword.lower()
            if not (hw in phrase.get("en", "").lower() or hw in phrase.get("es", "").lower() or hw in [h.lower() for h in phrase.get("hotwords", [])]):
                continue
        results.append(phrase)
        if len(results) >= limit:
            break
    return results


def _display_search_results(results: List[Dict]):
    st.subheader(f"ðŸ§  Search Results ({len(results)} found)")
    if not results:
        st.warning("No phrases found with the selected filters.")
        return
    for i, phrase in enumerate(results, 1):
        with st.expander(f"#{i} [{phrase.get('cat', 'N/A')}] {phrase.get('en', 'No English text')}", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.write("**English:**")
                st.info(phrase.get('en', 'N/A'))
            with col2:
                st.write("**Spanish:**")
                st.success(phrase.get('es', 'N/A'))
            if phrase.get('hotwords'):
                st.write(f"**Hotwords:** {', '.join(phrase['hotwords'])}")


# ðŸ“‹ View All Page
def render_view_all_page(data_manager: DataManager, selected_prefix: str):
    st.header("ðŸ“‹ All Phrases")
    try:
        site_info = data_manager.modules['get_site_by_prefix'](data_manager.registry, selected_prefix)
    except Exception:
        site_info = next((r for r in data_manager.registry if isinstance(r, dict) and r.get("prefix") == selected_prefix), {})
    filter_fn = data_manager.modules.get('filter_phrases_by_site', lambda x, y: x)
    filtered_phrases = filter_fn(data_manager.phrases, site_info)
    st.write(f"**Total phrases:** {len(filtered_phrases)}")

    categories = [""] + data_manager.modules.get('get_categories', lambda x: [])(filtered_phrases)
    selected_category = st.selectbox("Filter by category:", categories, key="view_all_category")

    display_phrases = [p for p in filtered_phrases if not selected_category or p.get("cat") == selected_category]
    if not display_phrases:
        st.info("No phrases to display.")
        return

    phrases_per_page = 20
    total_pages = (len(display_phrases) + phrases_per_page - 1) // phrases_per_page

    start_idx = 0
    if total_pages > 1:
        page = st.number_input("Page", min_value=1, max_value=total_pages, value=1)
        start_idx = (page - 1) * phrases_per_page
        end_idx = min(start_idx + phrases_per_page, len(display_phrases))
        current_phrases = display_phrases[start_idx:end_idx]
        st.write(f"**Showing phrases {start_idx + 1}-{end_idx} of {len(display_phrases)}**")
    else:
        current_phrases = display_phrases

    for i, phrase in enumerate(current_phrases, start_idx + 1):
        cat = phrase.get('cat', 'N/A')
        en = phrase.get('en', 'No English text')
        es = phrase.get('es', 'No Spanish text')
        st.markdown(f"""**#{i} [{cat}]** {en}  
ðŸŒ *{es}*""")
    st.divider()


# ðŸ—“ï¸ Work Scheduling page (placeholder)
def render_work_scheduling_page(data_manager: DataManager, selected_prefix: str):
    st.header("ðŸ—“ï¸ Work Scheduling")
    st.info("This page will host work shifts, assignments and calendars.")
    st.write(f"Selected Site Prefix: `{selected_prefix or 'â€”'}`")


# â±ï¸ Time Tracking page (placeholder)
def render_time_tracking_page(data_manager: DataManager, selected_prefix: str):
    st.header("â±ï¸ Time Tracking Dashboard")
    st.info("This page will host time logs, metrics, and compliance KPIs.")
    st.write(f"Selected Site Prefix: `{selected_prefix or 'â€”'}`")


# ðŸŽ¯ Main Application
def main():
    # Initialize configuration
    config = Config()

    # Validate core file paths
    missing_files = config.validate_core_paths()
    if missing_files:
        st.error("âŒ **Missing required files:**")
        for file_info in missing_files:
            st.write(f"- {file_info}")
        st.info("ðŸ’¡ **Solution**: Please ensure the data folder exists with the required JSON files.")
        st.stop()

    # Load shared modules
    modules = load_shared_modules()
    if not modules:
        st.info("âš ï¸ **Note**: Some features may be limited due to missing shared modules.")

    # Initialize data manager & UI
    data_manager = DataManager(config, modules)
    ui = UIComponents()

    # Sidebar
    st.sidebar.title("ðŸ§­ AmdaOps Navigation")
    st.sidebar.subheader("ðŸ·ï¸ Site Selection")

    # ObtenciÃ³n robusta de prefixes
    def _safe_get_prefixes(reg) -> List[str]:
        if not reg:
            return []
        try:
            if isinstance(reg, list) and reg:
                first = reg[0]
                if isinstance(first, dict):
                    return [r.get("prefix", "") for r in reg if isinstance(r, dict) and r.get("prefix")]
                if isinstance(first, str):
                    return [s for s in reg if isinstance(s, str) and s.strip()]
        except Exception:
            pass
        return []

    try:
        prefixes = modules['get_prefixes'](data_manager.registry) if modules else []
        if not prefixes:
            prefixes = _safe_get_prefixes(data_manager.registry)
    except Exception:
        prefixes = _safe_get_prefixes(data_manager.registry)

    if not prefixes:
        prefixes = ["DEFAULT"]
        default_registry = [{
            "prefix": "DEFAULT",
            "site": "ShoppingCenter",
            "name": "Default Site",
            "status": "Active",
            "address": "123 Main St",
            "city": "Anytown",
            "state": "CA",
            "zip": "12345",
            "country": "USA"
        }]
        data_manager.save_registry(default_registry)

    # OpciÃ³n para crear sitio y recordar Ãºltimo seleccionado
    last_selected = st.session_state.get("last_selected_prefix")
    options = ["âž• Add new siteâ€¦"] + prefixes

    adding_flag = st.session_state.get("adding_site", False)
    if adding_flag:
        default_index = 0
    elif last_selected and last_selected in prefixes:
        default_index = 1 + prefixes.index(last_selected)
    else:
        default_index = 1 if len(options) > 1 else 0

    choice = st.sidebar.selectbox("Select Site", options, index=min(default_index, len(options)-1), key="site_selector")

    add_new = (choice == "âž• Add new siteâ€¦")
    st.session_state["adding_site"] = add_new
    selected_prefix = "" if add_new else choice

    # Info del sitio seleccionado
    try:
        site_info = modules['get_site_by_prefix'](data_manager.registry, selected_prefix) if (modules and selected_prefix) else {}
    except Exception:
        site_info = next((r for r in data_manager.registry if isinstance(r, dict) and r.get("prefix") == selected_prefix), {}) if selected_prefix else {}

    if site_info:
        st.sidebar.divider()
        st.sidebar.subheader("ðŸ“ Selected Site Info")
        st.sidebar.write(f"**Name:** {site_info.get('name', 'N/A')}")
        st.sidebar.write(f"**Type:** {site_info.get('site', 'N/A')}")
        st.sidebar.write(f"**Status:** {site_info.get('status', 'Active')}")
        st.sidebar.write(f"**Address:** {site_info.get('address', 'N/A')}")
        if site_info.get("maps_link"):
            st.sidebar.markdown(f"ðŸŒ [Google Maps]({site_info['maps_link']})")

    # Navigation
    st.sidebar.divider()
    st.sidebar.subheader("ðŸ“‚ Application Pages")
    menu = st.sidebar.radio(
        "Go to",
        ["Home", "Work Scheduling", "Time Tracking", "Search phrases", "View all"],
        key="nav_menu"
    )

    # Quick stats
    if data_manager.officers:
        st.sidebar.divider()
        st.sidebar.subheader("ðŸ“Š Quick Stats")
        active_officers = len([o for o in data_manager.officers if o.get('status') == 'Active'])
        total_schedules = len(data_manager.schedules)
        st.sidebar.write(f"**Active Officers:** {active_officers}")
        st.sidebar.write(f"**Total Schedules:** {total_schedules}")

    # Render selected page
    if menu == "Home":
        render_home_page(data_manager, ui, selected_prefix)
    elif menu == "Work Scheduling":
        render_work_scheduling_page(data_manager, selected_prefix)
    elif menu == "Time Tracking":
        render_time_tracking_page(data_manager, selected_prefix)
    elif menu == "Search phrases":
        render_search_page(data_manager, selected_prefix)
    elif menu == "View all":
        render_view_all_page(data_manager, selected_prefix)


if __name__ == "__main__":
    main()
