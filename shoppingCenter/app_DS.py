# 📦 Imports
import streamlit as st
from pathlib import Path
import sys
import json
import streamlit.components.v1 as components
from typing import Dict, List, Optional, Any

# 🔗 Add shared folder to path
shared_path = Path(__file__).resolve().parent.parent / "shared"
sys.path.append(str(shared_path))

# ⚙️ Page config
st.set_page_config(
    page_title="AmdaOps Viewer",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="expanded"
)


# 🧠 Load shared modules with better error handling
def load_shared_modules():
    """Dynamically load shared modules with comprehensive error handling"""
    try:
        from loader import load_phrases
        from registry import load_registry, get_prefixes, get_site_by_prefix
        from phrase import filter_phrases_by_site, get_categories, get_hotwords

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
        st.error(f"❌ **Module Import Error**: `{e.name}` not found.")
        st.info("💡 **Solution**: Ensure the shared folder exists and contains all required modules.")
        return None
    except Exception as e:
        st.error(f"❌ **Unexpected error loading modules**: {e}")
        return None


# 📁 Path configuration with validation
class Config:
    """Centralized configuration management"""

    def __init__(self):
        self.BASE_DIR = Path(__file__).resolve().parent
        self.PHRASES_PATH = self.BASE_DIR / "data" / "181_line__bank_Shoping_Center_en_es.json"
        self.REGISTRY_PATH = self.BASE_DIR / "data" / "site_registry.json"

    def validate_paths(self) -> List[str]:
        """Validate that all required files exist"""
        missing_files = []
        for path, name in [(self.PHRASES_PATH, "Phrases"), (self.REGISTRY_PATH, "Registry")]:
            if not path.exists():
                missing_files.append(f"{name}: `{str(path)}`")
        return missing_files


# 📊 Data management
class DataManager:
    """Manage data loading and caching"""

    def __init__(self, config: Config, modules: Dict):
        self.config = config
        self.modules = modules
        self._phrases = None
        self._registry = None

    @property
    def phrases(self) -> List[Dict]:
        """Lazy load phrases with caching"""
        if self._phrases is None:
            self._phrases = self._load_data('phrases')
        return self._phrases

    @property
    def registry(self) -> List[Dict]:
        """Lazy load registry with caching"""
        if self._registry is None:
            self._registry = self._load_data('registry')
        return self._registry

    def _load_data(self, data_type: str) -> Optional[List[Dict]]:
        """Load data with comprehensive error handling"""
        try:
            if data_type == 'phrases':
                return self.modules['load_phrases'](self.config.PHRASES_PATH)
            elif data_type == 'registry':
                return self.modules['load_registry'](self.config.REGISTRY_PATH)
        except json.JSONDecodeError as e:
            st.error(f"❌ **JSON Error in {data_type} file**: {e}")
        except Exception as e:
            st.error(f"❌ **Error loading {data_type}**: {e}")
        return None


# 🎯 UI Components
class UIComponents:
    """Reusable UI components"""

    @staticmethod
    def show_site_info(site_info: Dict, selected_prefix: str):
        """Display site information in a formatted way"""
        if site_info:
            with st.container():
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.subheader("🏢 Site Details")
                    st.write(f"**Prefix:** `{selected_prefix}`")
                    st.write(f"**Site type:** {site_info.get('site', 'N/A')}")
                    st.write(f"**Name:** {site_info.get('name', 'N/A')}")

                with col2:
                    st.subheader("📍 Address Information")
                    st.write(f"**Address:** {site_info.get('address', 'N/A')}")
                    st.write(f"**City:** {site_info.get('city', 'N/A')}")
                    st.write(f"**State:** {site_info.get('state', 'N/A')}")
                    st.write(f"**ZIP code:** {site_info.get('zip', 'N/A')}")

                    if site_info.get("maps_link"):
                        st.markdown(f"🌍 [View on Google Maps]({site_info['maps_link']})")

    @staticmethod
    def site_form(site_info: Dict, selected_prefix: str, registry_path: Path) -> bool:
        """Render and handle site editing form"""
        st.subheader("📝 Edit or Register Unit")

        # Initialize session state for form management
        if "form_cleared" not in st.session_state:
            st.session_state.form_cleared = False

        # Form configuration
        site_options = ["ShoppingCenter", "Warehouse", "Parking", "Other"]
        site_value = site_info.get("site", "ShoppingCenter")
        site_index = site_options.index(site_value) if site_value in site_options else 0

        with st.form(key=f"site_form_{selected_prefix}"):
            # Form fields organized in columns for better layout
            col1, col2 = st.columns(2)

            with col1:
                unit_id = st.text_input(
                    "🔢 Unit ID",
                    value="" if st.session_state.form_cleared else site_info.get("prefix", ""),
                    placeholder="e.g. 343",
                    help="Número de unidad"
                )
                address = st.text_input(
                    "📍 Full Address",
                    value="" if st.session_state.form_cleared else site_info.get("address", ""),
                    help="Dirección completa"
                )
                site_name = st.text_input(
                    "🏷️ Site Name",
                    value="" if st.session_state.form_cleared else site_info.get("name", ""),
                    help="Nombre del sitio"
                )
                site_type = st.selectbox(
                    "🏢 Site Type",
                    site_options,
                    index=site_index,
                    help="Tipo de sitio"
                )

            with col2:
                city = st.text_input(
                    "🌆 City",
                    value="" if st.session_state.form_cleared else site_info.get("city", ""),
                    help="Ciudad"
                )
                state = st.text_input(
                    "🗺️ State",
                    value="" if st.session_state.form_cleared else site_info.get("state", ""),
                    help="Estado"
                )
                zip_code = st.text_input(
                    "📮 ZIP Code",
                    value="" if st.session_state.form_cleared else site_info.get("zip", ""),
                    help="Código postal"
                )

            # Action buttons
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            with col1:
                save_btn = st.form_submit_button("💾 Save Unit", type="primary")
            with col2:
                delete_btn = st.form_submit_button("🗑️ Delete Unit")
            with col3:
                clear_btn = st.form_submit_button("🧹 Clear Form")
            with col4:
                cancel_btn = st.form_submit_button("❌ Cancel")

            # Handle form actions
            if save_btn:
                return UIComponents._handle_save(
                    unit_id, address, city, state, zip_code, site_type, site_name, registry_path
                )
            elif delete_btn:
                return UIComponents._handle_delete(selected_prefix, registry_path)
            elif clear_btn:
                st.session_state.form_cleared = True
                st.rerun()
            elif cancel_btn:
                st.session_state.form_cleared = False
                st.info("Operation cancelled")

        return False

    @staticmethod
    def _handle_save(unit_id, address, city, state, zip_code, site_type, site_name, registry_path) -> bool:
        """Handle save operation with validation"""
        required_fields = [unit_id, address, site_name]
        if not all(required_fields):
            st.warning("⚠️ Please complete at least **Unit ID**, **Address**, and **Site Name**.")
            return False

        try:
            # Load current registry
            with open(registry_path, 'r', encoding='utf-8') as f:
                registry = json.load(f)

            # Prepare new entry
            full_address = f"{address}, {city}, {state}, {zip_code}"
            maps_link = f"https://www.google.com/maps/search/?api=1&query={full_address.replace(' ', '+')}"

            new_entry = {
                "prefix": unit_id,
                "site": site_type,
                "name": site_name,
                "address": address,
                "city": city,
                "state": state,
                "zip": zip_code,
                "maps_link": maps_link
            }

            # Update registry
            registry = [r for r in registry if r.get("prefix") != unit_id]
            registry.append(new_entry)

            # Save to file
            with open(registry_path, "w", encoding="utf-8") as f:
                json.dump(registry, f, indent=2, ensure_ascii=False)

            st.success("✅ Unit saved successfully!")
            st.session_state.form_cleared = False
            return True

        except Exception as e:
            st.error(f"❌ Error saving unit: {e}")
            return False

    @staticmethod
    def _handle_delete(selected_prefix: str, registry_path: Path) -> bool:
        """Handle delete operation with confirmation"""
        if not selected_prefix:
            st.warning("No unit selected for deletion.")
            return False

        with st.expander("⚠️ Confirm Deletion", expanded=True):
            st.warning(f"You are about to delete unit `{selected_prefix}`. This action cannot be undone.")
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"✅ Confirm Delete", type="primary"):
                    try:
                        with open(registry_path, 'r', encoding='utf-8') as f:
                            registry = json.load(f)

                        registry = [r for r in registry if r.get("prefix") != selected_prefix]

                        with open(registry_path, "w", encoding="utf-8") as f:
                            json.dump(registry, f, indent=2, ensure_ascii=False)

                        st.success(f"✅ Unit `{selected_prefix}` deleted successfully!")
                        st.session_state.form_cleared = False
                        return True
                    except Exception as e:
                        st.error(f"❌ Error deleting unit: {e}")
            with col2:
                if st.button("❌ Cancel"):
                    st.info("Deletion cancelled")

        return False


# 🏠 Home Page
def render_home_page(data_manager: DataManager, ui: UIComponents, selected_prefix: str):
    """Render the home page with site management"""
    st.title("🛡️ AmdaOps - Operational Phrase Viewer")

    site_info = data_manager.modules['get_site_by_prefix'](data_manager.registry, selected_prefix)
    ui.show_site_info(site_info, selected_prefix)

    # Site management form
    ui.site_form(site_info, selected_prefix, data_manager.config.REGISTRY_PATH)


# 🔍 Search Page
def render_search_page(data_manager: DataManager, selected_prefix: str):
    """Render the search and filtering page"""
    st.header("🔍 Filter Phrases")

    site_info = data_manager.modules['get_site_by_prefix'](data_manager.registry, selected_prefix)
    filtered_phrases = data_manager.modules['filter_phrases_by_site'](data_manager.phrases, site_info)

    # Search controls
    col1, col2 = st.columns(2)
    with col1:
        category = st.selectbox("📂 Category", [""] + data_manager.modules['get_categories'](filtered_phrases))
        limit = st.slider("🔢 Number of phrases", 1, 50, 10, help="Maximum number of results to display")

    with col2:
        hotword = st.selectbox("🔍 Hotword", [""] + data_manager.modules['get_hotwords'](filtered_phrases))
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
        # Category filter
        if category and phrase.get("cat") != category:
            continue

        # Hotword filter
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


# 🎯 Main application
def main():
    """Main application entry point"""

    # Initialize configuration
    config = Config()

    # Validate file paths
    missing_files = config.validate_paths()
    if missing_files:
        st.error("❌ **Missing required files:**")
        for file_info in missing_files:
            st.write(f"- {file_info}")
        st.stop()

    # Load shared modules
    modules = load_shared_modules()
    if not modules:
        st.stop()

    # Initialize data manager
    data_manager = DataManager(config, modules)

    # Initialize UI components
    ui = UIComponents()

    # Sidebar navigation
    st.sidebar.title("🧭 Navigation")
    menu = st.sidebar.radio("Go to", ["Home", "Search phrases", "View all"])

    # Site selection
    st.sidebar.divider()
    st.sidebar.subheader("🏷️ Site Selection")
    prefixes = modules['get_prefixes'](data_manager.registry)
    selected_prefix = st.sidebar.selectbox("Select Site", prefixes)

    # Display Google Maps link if available
    site_info = modules['get_site_by_prefix'](data_manager.registry, selected_prefix)
    if site_info and site_info.get("maps_link"):
        st.sidebar.divider()
        st.sidebar.markdown(f"🌍 [Google Maps Link]({site_info['maps_link']})")

    # Render selected page
    if menu == "Home":
        render_home_page(data_manager, ui, selected_prefix)
    elif menu == "Search phrases":
        render_search_page(data_manager, selected_prefix)
    elif menu == "View all":
        render_view_all_page(data_manager, selected_prefix)


if __name__ == "__main__":
    main()