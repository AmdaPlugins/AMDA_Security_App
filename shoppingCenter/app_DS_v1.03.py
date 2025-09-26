# 📦 Imports
import streamlit as st
from pathlib import Path
import sys
import json
import pandas as pd
from datetime import datetime, timedelta, time
import streamlit.components.v1 as components
from typing import Dict, List, Optional, Any, Tuple
import uuid
import re

# 🔗 Add shared folder to path
shared_path = Path(__file__).resolve().parent.parent / "shared"
sys.path.append(str(shared_path))

# ⚙️ Page config
st.set_page_config(
    page_title="AmdaOps - Security Management",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="expanded"
)


# 🧠 Load shared modules with better error handling
def load_shared_modules():
    """Dynamically load shared modules with comprehensive error handling"""
    try:
        # Importar módulos compartidos con manejo de errores mejorado
        try:
            from loader import load_phrases
            from registry import load_registry, get_prefixes, get_site_by_prefix
            from phrase import filter_phrases_by_site, get_categories, get_hotwords
        except ImportError as e:
            st.error(f"❌ **Error importing shared modules**: {e}")

            # Crear funciones dummy para evitar errores
            def load_phrases(path):
                return []

            def load_registry(path):
                # Si el archivo existe pero tiene formato incorrecto, corregirlo
                if path.exists():
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            # Verificar y corregir el formato si es necesario
                            if isinstance(data, list) and data and isinstance(data[0], str):
                                # Convertir lista de strings a lista de diccionarios
                                corrected_data = [{"prefix": prefix, "name": f"Site {prefix}", "site": "ShoppingCenter"}
                                                  for prefix in data]
                                with open(path, 'w', encoding='utf-8') as f_out:
                                    json.dump(corrected_data, f_out, indent=2, ensure_ascii=False)
                                return corrected_data
                            return data
                    except Exception as e:
                        st.error(f"Error loading registry: {e}")
                return []

            def get_prefixes(registry):
                if registry and isinstance(registry, list):
                    if registry and isinstance(registry[0], dict):
                        return [site.get('prefix', '') for site in registry if site.get('prefix')]
                    elif registry and isinstance(registry[0], str):
                        return registry
                return []

            def get_site_by_prefix(registry, prefix):
                if registry and isinstance(registry, list) and registry and isinstance(registry[0], dict):
                    return next((site for site in registry if site.get('prefix') == prefix), {})
                return {}

            def filter_phrases_by_site(phrases, site_info):
                return phrases

            def get_categories(phrases):
                return list(set(phrase.get('cat', '') for phrase in phrases if phrase.get('cat')))

            def get_hotwords(phrases):
                hotwords = set()
                for phrase in phrases:
                    if phrase.get('hotwords'):
                        hotwords.update(phrase['hotwords'])
                return list(hotwords)

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
        st.error(f"❌ **Unexpected error loading modules**: {e}")
        return None


# 📁 Enhanced configuration with new JSON files
class Config:
    """Centralized configuration management with new security features"""

    def __init__(self):
        self.BASE_DIR = Path(__file__).resolve().parent
        self.DATA_DIR = self.BASE_DIR / "data"

        # Ensure data directory exists
        self.DATA_DIR.mkdir(exist_ok=True)

        # Core data files
        self.PHRASES_PATH = self.DATA_DIR / "181_line__bank_Shoping_Center_en_es.json"
        self.REGISTRY_PATH = self.DATA_DIR / "site_registry.json"

        # New security officer files
        self.OFFICERS_PATH = self.DATA_DIR / "security_officers.json"
        self.SCHEDULES_PATH = self.DATA_DIR / "work_schedules.json"
        self.TIME_LOGS_PATH = self.DATA_DIR / "time_logs.json"

        # Initialize new JSON files if they don't exist
        self._initialize_json_files()

    def _initialize_json_files(self):
        """Initialize new JSON files with empty structures if they don't exist"""
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

        # Inicializar site_registry.json con formato correcto si no existe o está corrupto
        if not self.REGISTRY_PATH.exists():
            default_registry = [
                {
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
                }
            ]
            try:
                with open(self.REGISTRY_PATH, 'w', encoding='utf-8') as f:
                    json.dump(default_registry, f, indent=2, ensure_ascii=False)
            except Exception as e:
                st.error(f"Error creating default registry: {e}")

    def validate_core_paths(self) -> List[str]:
        """Validate that core required files exist"""
        missing_files = []
        for path, name in [(self.PHRASES_PATH, "Phrases"), (self.REGISTRY_PATH, "Registry")]:
            if not path.exists():
                missing_files.append(f"{name}: `{str(path)}`")
        return missing_files


# 📊 Enhanced Data Manager
class DataManager:
    """Manage data loading and caching with security officer features"""

    def __init__(self, config: Config, modules: Dict):
        self.config = config
        self.modules = modules
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
            # Asegurar que el registro tenga el formato correcto
            self._registry = self._validate_and_fix_registry(self._registry)
        return self._registry

    def _validate_and_fix_registry(self, registry_data):
        """Validar y corregir el formato del registro si es necesario"""
        if not registry_data:
            return [{
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

        # Si es una lista de strings, convertir a lista de diccionarios
        if isinstance(registry_data, list) and registry_data and isinstance(registry_data[0], str):
            corrected_data = []
            for i, prefix in enumerate(registry_data):
                corrected_data.append({
                    "prefix": prefix,
                    "site": "ShoppingCenter",
                    "name": f"Site {prefix}",
                    "status": "Active",
                    "address": f"{i + 1} Example Street",
                    "city": "City",
                    "state": "ST",
                    "zip": "12345",
                    "country": "USA"
                })
            # Guardar el formato corregido
            try:
                with open(self.config.REGISTRY_PATH, 'w', encoding='utf-8') as f:
                    json.dump(corrected_data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                st.error(f"Error saving corrected registry: {e}")
            return corrected_data

        # Si es un diccionario individual, convertirlo a lista
        if isinstance(registry_data, dict):
            return [registry_data]

        return registry_data

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
        """Load data with comprehensive error handling"""
        try:
            if data_type == 'phrases':
                return self.modules['load_phrases'](self.config.PHRASES_PATH)
            elif data_type == 'registry':
                return self.modules['load_registry'](self.config.REGISTRY_PATH)
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
            st.error(f"❌ **Error loading {data_type}**: {e}")
            return []

    def save_officers(self, officers_data: List[Dict]):
        """Save officers data"""
        try:
            with open(self.config.OFFICERS_PATH, "w", encoding="utf-8") as f:
                json.dump(officers_data, f, indent=2, ensure_ascii=False)
            self._officers = officers_data
            return True
        except Exception as e:
            st.error(f"Error saving officers: {e}")
            return False

    def save_schedules(self, schedules_data: List[Dict]):
        """Save schedules data"""
        try:
            with open(self.config.SCHEDULES_PATH, "w", encoding="utf-8") as f:
                json.dump(schedules_data, f, indent=2, ensure_ascii=False)
            self._schedules = schedules_data
            return True
        except Exception as e:
            st.error(f"Error saving schedules: {e}")
            return False

    def save_time_logs(self, time_logs_data: List[Dict]):
        """Save time logs data"""
        try:
            with open(self.config.TIME_LOGS_PATH, "w", encoding="utf-8") as f:
                json.dump(time_logs_data, f, indent=2, ensure_ascii=False)
            self._time_logs = time_logs_data
            return True
        except Exception as e:
            st.error(f"Error saving time logs: {e}")
            return False

    def save_registry(self, registry_data: List[Dict]):
        """Save registry data"""
        try:
            with open(self.config.REGISTRY_PATH, "w", encoding="utf-8") as f:
                json.dump(registry_data, f, indent=2, ensure_ascii=False)
            self._registry = registry_data
            return True
        except Exception as e:
            st.error(f"Error saving registry: {e}")
            return False


# 🎯 Enhanced UI Components with Site Management
class UIComponents:
    """Reusable UI components with enhanced site management"""

    @staticmethod
    def show_site_info(site_info: Dict, selected_prefix: str):
        """Display comprehensive site information"""
        if site_info:
            with st.container():
                st.subheader("🏢 Site Details")

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
                        st.markdown(f"🌍 [View on Google Maps]({site_info['maps_link']})")

    @staticmethod
    def site_management(data_manager: DataManager, selected_prefix: str):
        """Enhanced site management with edit/save/delete functionality"""
        st.subheader("🏢 Site Management")

        site_info = data_manager.modules['get_site_by_prefix'](data_manager.registry, selected_prefix)

        # Initialize edit mode in session state
        if f'edit_mode_{selected_prefix}' not in st.session_state:
            st.session_state[f'edit_mode_{selected_prefix}'] = False

        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

        with col1:
            if not st.session_state[f'edit_mode_{selected_prefix}']:
                st.info(f"Currently viewing: **{site_info.get('name', 'Unknown Site')}**")
            else:
                st.warning("📝 Edit Mode Active - Modifying Site Details")

        with col2:
            if not st.session_state[f'edit_mode_{selected_prefix}']:
                if st.button("✏️ Edit Site", key=f"edit_{selected_prefix}"):
                    st.session_state[f'edit_mode_{selected_prefix}'] = True
                    st.rerun()
            else:
                if st.button("💾 Save", key=f"save_{selected_prefix}", type="primary"):
                    if UIComponents._save_site_details(data_manager, selected_prefix):
                        st.session_state[f'edit_mode_{selected_prefix}'] = False
                        st.rerun()

        with col3:
            if st.session_state[f'edit_mode_{selected_prefix}']:
                if st.button("❌ Cancel", key=f"cancel_{selected_prefix}"):
                    st.session_state[f'edit_mode_{selected_prefix}'] = False
                    st.rerun()

        with col4:
            if site_info and st.button("🗑️ Delete", key=f"delete_{selected_prefix}"):
                UIComponents._delete_site_confirmation(data_manager, selected_prefix)

        # Display or edit site details based on mode
        if st.session_state[f'edit_mode_{selected_prefix}']:
            UIComponents._render_site_edit_form(data_manager, site_info, selected_prefix)
        else:
            UIComponents._render_site_display(data_manager, site_info, selected_prefix)

    @staticmethod
    def _render_site_display(data_manager: DataManager, site_info: Dict, selected_prefix: str):
        """Display site details in view mode"""
        if site_info:
            # Create a nice card-like display
            with st.container():
                st.markdown("---")
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("📍 Basic Information")
                    st.write(f"**Prefix:** `{site_info.get('prefix', 'N/A')}`")
                    st.write(f"**Site Type:** {site_info.get('site', 'N/A')}")
                    st.write(f"**Site Name:** {site_info.get('name', 'N/A')}")
                    st.write(f"**Status:** {site_info.get('status', 'Active')}")

                    if site_info.get('contact_name'):
                        st.write(f"**Contact:** {site_info.get('contact_name')}")
                    if site_info.get('contact_phone'):
                        st.write(f"**Contact Phone:** {site_info.get('contact_phone')}")

                with col2:
                    st.subheader("🏠 Address Details")
                    st.write(f"**Address:** {site_info.get('address', 'N/A')}")
                    st.write(f"**City:** {site_info.get('city', 'N/A')}")
                    st.write(f"**State:** {site_info.get('state', 'N/A')}")
                    st.write(f"**ZIP Code:** {site_info.get('zip', 'N/A')}")
                    st.write(f"**Country:** {site_info.get('country', 'USA')}")

                    if site_info.get("maps_link"):
                        st.markdown(f"### 🌍 Navigation")
                        st.markdown(f"[Open in Google Maps]({site_info['maps_link']})")

        else:
            st.warning("No site information available. Please add site details using the Edit button.")

    @staticmethod
    def _render_site_edit_form(data_manager: DataManager, site_info: Dict, selected_prefix: str):
        """Render site edit form"""
        with st.form(key=f"site_edit_form_{selected_prefix}"):
            st.subheader("📝 Edit Site Details")

            # Form organized in tabs for better organization
            tab1, tab2, tab3 = st.tabs(["Basic Info", "Address", "Additional Details"])

            with tab1:
                col1, col2 = st.columns(2)
                with col1:
                    prefix = st.text_input(
                        "🔢 Site Prefix*",
                        value=site_info.get('prefix', selected_prefix) if site_info else selected_prefix,
                        help="Unique identifier for the site"
                    )
                    site_type = st.selectbox(
                        "🏢 Site Type*",
                        options=["ShoppingCenter", "Warehouse", "Parking", "Office", "Residential", "Other"],
                        index=0 if not site_info else ["ShoppingCenter", "Warehouse", "Parking", "Office",
                                                       "Residential", "Other"].index(
                            site_info.get('site', 'ShoppingCenter')
                        ) if site_info.get('site') in ["ShoppingCenter", "Warehouse", "Parking", "Office",
                                                       "Residential", "Other"] else 0
                    )
                    site_name = st.text_input(
                        "🏷️ Site Name*",
                        value=site_info.get('name', ''),
                        help="Official name of the site"
                    )

                with col2:
                    status = st.selectbox(
                        "📊 Status",
                        options=["Active", "Inactive", "Under Maintenance", "Planned"],
                        index=0 if not site_info else ["Active", "Inactive", "Under Maintenance", "Planned"].index(
                            site_info.get('status', 'Active')
                        ) if site_info.get('status') in ["Active", "Inactive", "Under Maintenance", "Planned"] else 0
                    )
                    contact_name = st.text_input(
                        "👤 Contact Person",
                        value=site_info.get('contact_name', ''),
                        help="Primary contact at the site"
                    )
                    contact_phone = st.text_input(
                        "📞 Contact Phone",
                        value=site_info.get('contact_phone', ''),
                        help="Contact phone number"
                    )

            with tab2:
                col1, col2 = st.columns(2)
                with col1:
                    address = st.text_input(
                        "📍 Street Address*",
                        value=site_info.get('address', ''),
                        help="Full street address"
                    )
                    city = st.text_input(
                        "🌆 City*",
                        value=site_info.get('city', ''),
                        help="City name"
                    )

                with col2:
                    state = st.text_input(
                        "🗺️ State/Province*",
                        value=site_info.get('state', ''),
                        help="State or province"
                    )
                    zip_code = st.text_input(
                        "📮 ZIP/Postal Code*",
                        value=site_info.get('zip', ''),
                        help="Postal code"
                    )

                country = st.text_input(
                    "🇺🇸 Country",
                    value=site_info.get('country', 'USA'),
                    help="Country name"
                )

            with tab3:
                notes = st.text_area(
                    "📋 Notes",
                    value=site_info.get('notes', ''),
                    help="Additional notes about the site",
                    height=100
                )
                special_instructions = st.text_area(
                    "⚠️ Special Instructions",
                    value=site_info.get('special_instructions', ''),
                    help="Important instructions for security personnel",
                    height=100
                )

                # Security requirements
                st.subheader("🛡️ Security Requirements")
                col1, col2 = st.columns(2)
                with col1:
                    required_officers = st.number_input(
                        "Minimum Officers Required",
                        min_value=1,
                        max_value=10,
                        value=site_info.get('required_officers', 1) if site_info else 1
                    )
                    patrol_frequency = st.selectbox(
                        "Patrol Frequency",
                        options=["30 minutes", "1 hour", "2 hours", "4 hours", "As needed"],
                        index=0 if not site_info else ["30 minutes", "1 hour", "2 hours", "4 hours", "As needed"].index(
                            site_info.get('patrol_frequency', '1 hour')
                        ) if site_info.get('patrol_frequency') in ["30 minutes", "1 hour", "2 hours", "4 hours",
                                                                   "As needed"] else 1
                    )

                with col2:
                    has_cctv = st.checkbox(
                        "CCTV Available",
                        value=site_info.get('has_cctv', False) if site_info else False
                    )
                    requires_vehicle = st.checkbox(
                        "Vehicle Patrol Required",
                        value=site_info.get('requires_vehicle', False) if site_info else False
                    )

            # Form validation and submission
            st.markdown("**Note:** Fields marked with * are required")

            submit_button = st.form_submit_button("💾 Save Site Details", type="primary")

            if submit_button:
                # Validate required fields
                if not all([prefix, site_name, address, city, state, zip_code]):
                    st.error("Please fill in all required fields (marked with *)")
                else:
                    # Generate maps link
                    full_address = f"{address}, {city}, {state}, {zip_code}, {country}"
                    maps_link = f"https://www.google.com/maps/search/?api=1&query={full_address.replace(' ', '+')}"

                    # Prepare site data
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

                    # Add created date for new sites
                    if not site_info:
                        updated_site["created_date"] = datetime.now().isoformat()

                    # Save to registry
                    registry = data_manager.registry.copy()

                    # Remove existing entry if prefix changed
                    if site_info and site_info.get('prefix') != prefix:
                        registry = [r for r in registry if r.get('prefix') != site_info.get('prefix')]

                    # Update or add entry
                    existing_index = next((i for i, r in enumerate(registry) if r.get('prefix') == prefix), -1)
                    if existing_index >= 0:
                        registry[existing_index] = updated_site
                    else:
                        registry.append(updated_site)

                    if data_manager.save_registry(registry):
                        st.success("✅ Site details saved successfully!")
                        return True

        return False

    @staticmethod
    def _save_site_details(data_manager: DataManager, selected_prefix: str) -> bool:
        """Handle site details saving"""
        # This is now handled within the form above
        return True

    @staticmethod
    def _delete_site_confirmation(data_manager: DataManager, selected_prefix: str):
        """Handle site deletion with confirmation"""
        with st.expander("⚠️ Confirm Deletion", expanded=True):
            st.error(f"**Danger Zone**: You are about to delete site `{selected_prefix}`")
            st.warning("This action cannot be undone and will remove all associated schedules and data!")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Confirm Delete", type="primary"):
                    registry = data_manager.registry.copy()
                    registry = [r for r in registry if r.get('prefix') != selected_prefix]

                    # Also remove associated schedules
                    schedules = data_manager.schedules.copy()
                    schedules = [s for s in schedules if s.get('site_prefix') != selected_prefix]

                    if data_manager.save_registry(registry) and data_manager.save_schedules(schedules):
                        st.success(f"✅ Site `{selected_prefix}` deleted successfully!")
                        st.rerun()

            with col2:
                if st.button("❌ Cancel Deletion"):
                    st.info("Deletion cancelled")

    # ... (el resto de los métodos se mantienen igual, solo muestro los cambios principales)


# 🏠 Enhanced Home Page
def render_home_page(data_manager: DataManager, ui: UIComponents, selected_prefix: str):
    """Render the enhanced home page with security officer features"""
    st.title("🛡️ AmdaOps - Security Management System")

    # Site Management Section
    ui.site_management(data_manager, selected_prefix)

    st.divider()

    # Security Officer Management
    ui.officer_management(data_manager)

    st.divider()

    # Work Scheduling
    ui.work_scheduling(data_manager, selected_prefix)

    st.divider()

    # Time Tracking Dashboard
    ui.time_tracking_dashboard(data_manager, selected_prefix)


# 🔍 Search Page
def render_search_page(data_manager: DataManager, selected_prefix: str):
    """Render the search and filtering page"""
    st.header("🔍 Filter Phrases")

    site_info = data_manager.modules['get_site_by_prefix'](data_manager.registry, selected_prefix)
    filtered_phrases = data_manager.modules['filter_phrases_by_site'](data_manager.phrases, site_info)

    # Search controls
    col1, col2 = st.columns(2)
    with col1:
        categories = data_manager.modules['get_categories'](filtered_phrases)
        category = st.selectbox("📂 Category", [""] + categories)
        limit = st.slider("🔢 Number of phrases", 1, 50, 10, help="Maximum number of results to display")

    with col2:
        hotwords = data_manager.modules['get_hotwords'](filtered_phrases)
        hotword = st.selectbox("🔍 Hotword", [""] + hotwords)
        custom_hotword = st.text_input("✏️ Or type your own hotword")

    final_hotword = custom_hotword.strip() if custom_hotword.strip() else hotword

    # Search button
    if st.button("🔎 Search Phrases", type="primary"):
        with st.spinner("Searching..."):
            results = _search_phrases(filtered_phrases, category, final_hotword, limit)
            _display_search_results(results)


def _search_phrases(phrases: List[Dict], category: str, hotword: str, limit: int) -> List[Dict]:
    """Search and filter phrases based on criteria"""
    results = []
    for phrase in phrases:
        if category and phrase.get("cat") != category:
            continue

        if hotword:
            hw_lower = hotword.lower()
            phrase_en = phrase.get("en", "").lower()
            phrase_es = phrase.get("es", "").lower()
            phrase_hotwords = [h.lower() for h in phrase.get("hotwords", [])]

            if (hw_lower not in phrase_en and
                    hw_lower not in phrase_es and
                    hw_lower not in phrase_hotwords):
                continue

        results.append(phrase)
        if len(results) >= limit:
            break

    return results


def _display_search_results(results: List[Dict]):
    """Display search results in a formatted way"""
    st.subheader(f"🧠 Search Results ({len(results)} found)")

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


# 📋 View All Page
def render_view_all_page(data_manager: DataManager, selected_prefix: str):
    """Render the view all phrases page"""
    st.header("📋 All Phrases")

    site_info = data_manager.modules['get_site_by_prefix'](data_manager.registry, selected_prefix)
    filtered_phrases = data_manager.modules['filter_phrases_by_site'](data_manager.phrases, site_info)

    st.write(f"**Total phrases:** {len(filtered_phrases)}")

    # Category filter for view all
    categories = [""] + data_manager.modules['get_categories'](filtered_phrases)
    selected_category = st.selectbox("Filter by category:", categories, key="view_all_category")

    # Display phrases
    display_phrases = [p for p in filtered_phrases
                       if not selected_category or p.get("cat") == selected_category]

    if not display_phrases:
        st.info("No phrases to display.")
        return

    # Pagination
    phrases_per_page = 20
    total_pages = (len(display_phrases) + phrases_per_page - 1) // phrases_per_page

    if total_pages > 1:
        page = st.number_input("Page", min_value=1, max_value=total_pages, value=1)
        start_idx = (page - 1) * phrases_per_page
        end_idx = min(start_idx + phrases_per_page, len(display_phrases))
        current_phrases = display_phrases[start_idx:end_idx]
        st.write(f"**Showing phrases {start_idx + 1}-{end_idx} of {len(display_phrases)}**")
    else:
        current_phrases = display_phrases

    # Display phrases with better formatting
    for i, phrase in enumerate(current_phrases, start_idx + 1):
        cat = phrase.get('cat', 'N/A')
        en = phrase.get('en', 'No English text')
        es = phrase.get('es', 'No Spanish text')

        st.markdown(f"""
        **#{i} [{cat}]** {en}  
        🌐 *{es}*
        """)
        st.divider()


# 🎯 Enhanced Main Application
def main():
    """Main application entry point"""

    # Initialize configuration
    config = Config()

    # Validate core file paths
    missing_files = config.validate_core_paths()
    if missing_files:
        st.error("❌ **Missing required files:**")
        for file_info in missing_files:
            st.write(f"- {file_info}")
        st.info("💡 **Solution**: Please ensure the data folder exists with the required JSON files.")
        st.stop()

    # Load shared modules
    modules = load_shared_modules()
    if not modules:
        st.info("⚠️ **Note**: Some features may be limited due to missing shared modules.")
        # Continue with limited functionality

    # Initialize data manager
    data_manager = DataManager(config, modules)

    # Initialize UI components
    ui = UIComponents()

    # Enhanced Sidebar
    st.sidebar.title("🧭 AmdaOps Navigation")

    # Site selection with enhanced information
    st.sidebar.subheader("🏷️ Site Selection")

    # Obtener prefixes de manera segura
    try:
        prefixes = modules['get_prefixes'](data_manager.registry) if modules else []
    except Exception as e:
        st.error(f"Error getting prefixes: {e}")
        # Crear lista de prefixes por defecto
        prefixes = ["DEFAULT"]
        if data_manager.registry and isinstance(data_manager.registry, list):
            if data_manager.registry and isinstance(data_manager.registry[0], dict):
                prefixes = [site.get('prefix', 'DEFAULT') for site in data_manager.registry if site.get('prefix')]

    if not prefixes:
        prefixes = ["DEFAULT"]
        # Crear registro por defecto si no hay prefixes
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

    selected_prefix = st.sidebar.selectbox("Select Site", prefixes)

    # Display comprehensive site information in sidebar
    site_info = modules['get_site_by_prefix'](data_manager.registry, selected_prefix) if modules else {}
    if site_info:
        st.sidebar.divider()
        st.sidebar.subheader("📍 Selected Site Info")
        st.sidebar.write(f"**Name:** {site_info.get('name', 'N/A')}")
        st.sidebar.write(f"**Type:** {site_info.get('site', 'N/A')}")
        st.sidebar.write(f"**Status:** {site_info.get('status', 'Active')}")
        st.sidebar.write(f"**Address:** {site_info.get('address', 'N/A')}")

        if site_info.get("maps_link"):
            st.sidebar.markdown(f"🌍 [Google Maps]({site_info['maps_link']})")

    # Navigation
    st.sidebar.divider()
    st.sidebar.subheader("📂 Application Pages")
    menu = st.sidebar.radio("Go to", ["Home", "Search phrases", "View all"])

    # Quick stats in sidebar
    if data_manager.officers:
        st.sidebar.divider()
        st.sidebar.subheader("📊 Quick Stats")
        active_officers = len([o for o in data_manager.officers if o.get('status') == 'Active'])
        total_schedules = len(data_manager.schedules)

        st.sidebar.write(f"**Active Officers:** {active_officers}")
        st.sidebar.write(f"**Total Schedules:** {total_schedules}")

    # Render selected page
    if menu == "Home":
        render_home_page(data_manager, ui, selected_prefix)
    elif menu == "Search phrases":
        render_search_page(data_manager, selected_prefix)
    elif menu == "View all":
        render_view_all_page(data_manager, selected_prefix)


if __name__ == "__main__":
    main()