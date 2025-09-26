# ðŸ“¦ Imports
import streamlit as st
from pathlib import Path
import sys
import json
import pandas as pd
from datetime import datetime, timedelta, time
import streamlit.components.v1 as components
from typing import Dict, List, Optional, Any, Tuple
import uuid

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
        st.error(f"âŒ **Module Import Error**: `{e.name}` not found.")
        st.info("ðŸ’¡ **Solution**: Ensure the shared folder exists and contains all required modules.")
        return None
    except Exception as e:
        st.error(f"âŒ **Unexpected error loading modules**: {e}")
        return None


# ðŸ“ Enhanced configuration with new JSON files
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
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(default_data, f, indent=2, ensure_ascii=False)

    def validate_core_paths(self) -> List[str]:
        """Validate that core required files exist"""
        missing_files = []
        for path, name in [(self.PHRASES_PATH, "Phrases"), (self.REGISTRY_PATH, "Registry")]:
            if not path.exists():
                missing_files.append(f"{name}: `{str(path)}`")
        return missing_files


# ðŸ“Š Enhanced Data Manager with error handling for registry structure
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
        return self._registry

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
                data = self.modules['load_registry'](self.config.REGISTRY_PATH)
                # Fix registry structure if it's not a list of dictionaries
                return self._fix_registry_structure(data)
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

    def _fix_registry_structure(self, registry_data: Any) -> List[Dict]:
        """Fix registry structure if it's not in the expected format"""
        if registry_data is None:
            return []

        # If it's already a list of dictionaries, return as is
        if isinstance(registry_data, list) and len(registry_data) > 0 and isinstance(registry_data[0], dict):
            return registry_data

        # If it's a single dictionary, wrap it in a list
        if isinstance(registry_data, dict):
            return [registry_data]

        # If it's a list of strings or other types, try to convert
        if isinstance(registry_data, list):
            fixed_data = []
            for item in registry_data:
                if isinstance(item, dict):
                    fixed_data.append(item)
                elif isinstance(item, str):
                    try:
                        # Try to parse string as JSON
                        parsed = json.loads(item)
                        if isinstance(parsed, dict):
                            fixed_data.append(parsed)
                    except:
                        # If parsing fails, create a basic dict
                        fixed_data.append({'prefix': str(item), 'name': f'Site {item}'})
            return fixed_data

        # If it's something else, create a basic structure
        st.warning("âš ï¸ Registry structure unexpected. Creating default structure.")
        return [{'prefix': 'default', 'name': 'Default Site', 'site': 'ShoppingCenter'}]

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


# ðŸ› ï¸ Custom registry functions to handle structure issues
def safe_get_prefixes(registry: List[Dict]) -> List[str]:
    """Safely get prefixes from registry handling various structures"""
    if not registry:
        return ["default"]

    prefixes = []
    for item in registry:
        if isinstance(item, dict):
            # Try different possible key names for prefix
            prefix = item.get('prefix') or item.get('id') or item.get('site_id') or str(hash(str(item)))
            if prefix and prefix not in prefixes:
                prefixes.append(prefix)
        elif isinstance(item, str):
            prefixes.append(item)

    return prefixes if prefixes else ["default"]


def safe_get_site_by_prefix(registry: List[Dict], prefix: str) -> Optional[Dict]:
    """Safely get site by prefix handling various structures"""
    if not registry:
        return None

    for item in registry:
        if isinstance(item, dict):
            # Try different possible key names for prefix
            item_prefix = item.get('prefix') or item.get('id') or item.get('site_id')
            if item_prefix == prefix:
                return item
        elif isinstance(item, str) and item == prefix:
            return {'prefix': prefix, 'name': f'Site {prefix}', 'site': 'ShoppingCenter'}

    return None


# ðŸŽ¯ Enhanced UI Components with Site Management
class UIComponents:
    """Reusable UI components with enhanced site management"""

    @staticmethod
    def show_site_info(site_info: Dict, selected_prefix: str):
        """Display comprehensive site information"""
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
    def site_management(data_manager: DataManager, selected_prefix: str):
        """Enhanced site management with edit/save/delete functionality"""
        st.subheader("ðŸ¢ Site Management")

        site_info = safe_get_site_by_prefix(data_manager.registry, selected_prefix)

        # Initialize edit mode in session state
        if f'edit_mode_{selected_prefix}' not in st.session_state:
            st.session_state[f'edit_mode_{selected_prefix}'] = False

        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

        with col1:
            if not st.session_state[f'edit_mode_{selected_prefix}']:
                if site_info:
                    st.info(f"Currently viewing: **{site_info.get('name', 'Unknown Site')}**")
                else:
                    st.warning("No site information available. Click Edit to add details.")
            else:
                st.warning("ðŸ“ Edit Mode Active - Modifying Site Details")

        with col2:
            if not st.session_state[f'edit_mode_{selected_prefix}']:
                if st.button("âœï¸ Edit Site", key=f"edit_{selected_prefix}"):
                    st.session_state[f'edit_mode_{selected_prefix}'] = True
                    st.rerun()
            else:
                if st.button("ðŸ’¾ Save", key=f"save_{selected_prefix}", type="primary"):
                    if UIComponents._save_site_details(data_manager, selected_prefix):
                        st.session_state[f'edit_mode_{selected_prefix}'] = False
                        st.rerun()

        with col3:
            if st.session_state[f'edit_mode_{selected_prefix}']:
                if st.button("âŒ Cancel", key=f"cancel_{selected_prefix}"):
                    st.session_state[f'edit_mode_{selected_prefix}'] = False
                    st.rerun()

        with col4:
            if site_info and st.button("ðŸ—‘ï¸ Delete", key=f"delete_{selected_prefix}"):
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
                    st.subheader("ðŸ“ Basic Information")
                    st.write(f"**Prefix:** `{site_info.get('prefix', selected_prefix)}`")
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

                # Additional site information
                if site_info.get('notes') or site_info.get('special_instructions'):
                    with st.expander("ðŸ“‹ Additional Information"):
                        if site_info.get('notes'):
                            st.write(f"**Notes:** {site_info.get('notes')}")
                        if site_info.get('special_instructions'):
                            st.write(f"**Special Instructions:** {site_info.get('special_instructions')}")
        else:
            st.info("No site information available. Click the Edit button to add site details.")

    @staticmethod
    def _render_site_edit_form(data_manager: DataManager, site_info: Dict, selected_prefix: str):
        """Render site edit form"""
        with st.form(key=f"site_edit_form_{selected_prefix}"):
            st.subheader("ðŸ“ Edit Site Details")

            # Form organized in tabs for better organization
            tab1, tab2, tab3 = st.tabs(["Basic Info", "Address", "Additional Details"])

            with tab1:
                col1, col2 = st.columns(2)
                with col1:
                    prefix = st.text_input(
                        "ðŸ”¢ Site Prefix*",
                        value=site_info.get('prefix', selected_prefix) if site_info else selected_prefix,
                        help="Unique identifier for the site"
                    )
                    site_type = st.selectbox(
                        "ðŸ¢ Site Type*",
                        options=["ShoppingCenter", "Warehouse", "Parking", "Office", "Residential", "Other"],
                        index=0 if not site_info else ["ShoppingCenter", "Warehouse", "Parking", "Office",
                                                       "Residential", "Other"].index(
                            site_info.get('site', 'ShoppingCenter')
                        ) if site_info.get('site') in ["ShoppingCenter", "Warehouse", "Parking", "Office",
                                                       "Residential", "Other"] else 0
                    )
                    site_name = st.text_input(
                        "ðŸ·ï¸ Site Name*",
                        value=site_info.get('name', ''),
                        help="Official name of the site"
                    )

                with col2:
                    status = st.selectbox(
                        "ðŸ“Š Status",
                        options=["Active", "Inactive", "Under Maintenance", "Planned"],
                        index=0 if not site_info else ["Active", "Inactive", "Under Maintenance", "Planned"].index(
                            site_info.get('status', 'Active')
                        ) if site_info.get('status') in ["Active", "Inactive", "Under Maintenance", "Planned"] else 0
                    )
                    contact_name = st.text_input(
                        "ðŸ‘¤ Contact Person",
                        value=site_info.get('contact_name', ''),
                        help="Primary contact at the site"
                    )
                    contact_phone = st.text_input(
                        "ðŸ“ž Contact Phone",
                        value=site_info.get('contact_phone', ''),
                        help="Contact phone number"
                    )

            with tab2:
                col1, col2 = st.columns(2)
                with col1:
                    address = st.text_input(
                        "ðŸ“ Street Address*",
                        value=site_info.get('address', ''),
                        help="Full street address"
                    )
                    city = st.text_input(
                        "ðŸŒ† City*",
                        value=site_info.get('city', ''),
                        help="City name"
                    )

                with col2:
                    state = st.text_input(
                        "ðŸ—ºï¸ State/Province*",
                        value=site_info.get('state', ''),
                        help="State or province"
                    )
                    zip_code = st.text_input(
                        "ðŸ“® ZIP/Postal Code*",
                        value=site_info.get('zip', ''),
                        help="Postal code"
                    )

                country = st.text_input(
                    "ðŸ‡ºðŸ‡¸ Country",
                    value=site_info.get('country', 'USA'),
                    help="Country name"
                )

                # Google Maps integration
                if address and city and state:
                    full_address = f"{address}, {city}, {state}, {zip_code}, {country}"
                    maps_link = f"https://www.google.com/maps/search/?api=1&query={full_address.replace(' ', '+')}"
                    st.success(f"ðŸ“ Maps Link: [View on Google Maps]({maps_link})")

            with tab3:
                notes = st.text_area(
                    "ðŸ“‹ Notes",
                    value=site_info.get('notes', ''),
                    help="Additional notes about the site",
                    height=100
                )
                special_instructions = st.text_area(
                    "âš ï¸ Special Instructions",
                    value=site_info.get('special_instructions', ''),
                    help="Important instructions for security personnel",
                    height=100
                )

            # Form validation and submission
            st.markdown("**Note:** Fields marked with * are required")

            submit_button = st.form_submit_button("ðŸ’¾ Save Site Details", type="primary")

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
                        "last_updated": datetime.now().isoformat()
                    }

                    # Add created date for new sites
                    if not site_info:
                        updated_site["created_date"] = datetime.now().isoformat()
                    else:
                        # Preserve existing fields that we're not editing
                        for key in site_info:
                            if key not in updated_site:
                                updated_site[key] = site_info[key]

                    # Save to registry
                    registry = data_manager.registry.copy()

                    # Remove existing entry if prefix changed
                    if site_info and site_info.get('prefix') != prefix:
                        registry = [r for r in registry if not (
                                (isinstance(r, dict) and r.get('prefix') == site_info.get('prefix')) or
                                (isinstance(r, str) and r == site_info.get('prefix'))
                        )]

                    # Remove any existing entry with the same prefix
                    registry = [r for r in registry if not (
                            (isinstance(r, dict) and r.get('prefix') == prefix) or
                            (isinstance(r, str) and r == prefix)
                    )]

                    registry.append(updated_site)

                    if data_manager.save_registry(registry):
                        st.success("âœ… Site details saved successfully!")
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
        with st.expander("âš ï¸ Confirm Deletion", expanded=True):
            st.error(f"**Danger Zone**: You are about to delete site `{selected_prefix}`")
            st.warning("This action cannot be undone and will remove all associated schedules and data!")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("âœ… Confirm Delete", type="primary"):
                    registry = data_manager.registry.copy()
                    # Remove the site from registry
                    registry = [r for r in registry if not (
                            (isinstance(r, dict) and r.get('prefix') == selected_prefix) or
                            (isinstance(r, str) and r == selected_prefix)
                    )]

                    # Also remove associated schedules
                    schedules = data_manager.schedules.copy()
                    schedules = [s for s in schedules if s.get('site_prefix') != selected_prefix]

                    if data_manager.save_registry(registry) and data_manager.save_schedules(schedules):
                        st.success(f"âœ… Site `{selected_prefix}` deleted successfully!")
                        st.rerun()

            with col2:
                if st.button("âŒ Cancel Deletion"):
                    st.info("Deletion cancelled")

    # ... (rest of the UIComponents methods remain the same as previous version)
    # Including officer_management, work_scheduling, time_tracking_dashboard, etc.


# ðŸ  Enhanced Home Page
def render_home_page(data_manager: DataManager, ui: UIComponents, selected_prefix: str):
    """Render the enhanced home page with security officer features"""
    st.title("ðŸ›¡ï¸ AmdaOps - Security Management System")

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


# ðŸŽ¯ Enhanced Main Application with error handling
def main():
    """Main application entry point"""

    # Initialize configuration
    config = Config()

    # Validate core file paths
    missing_files = config.validate_core_paths()
    if missing_files:
        st.error("âŒ **Missing required files:**")
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

    # Enhanced Sidebar
    st.sidebar.title("ðŸ§­ AmdaOps Navigation")

    # Site selection with enhanced information - WITH ERROR HANDLING
    st.sidebar.subheader("ðŸ·ï¸ Site Selection")

    try:
        # Use our safe function instead of the module's function
        prefixes = safe_get_prefixes(data_manager.registry)
        selected_prefix = st.sidebar.selectbox("Select Site", prefixes)
    except Exception as e:
        st.sidebar.error("Error loading sites")
        st.sidebar.info("Using default site")
        prefixes = ["default"]
        selected_prefix = "default"

    # Display comprehensive site information in sidebar
    site_info = safe_get_site_by_prefix(data_manager.registry, selected_prefix)
    if site_info:
        st.sidebar.divider()
        st.sidebar.subheader("ðŸ“ Selected Site Info")
        st.sidebar.write(f"**Name:** {site_info.get('name', 'N/A')}")
        st.sidebar.write(f"**Type:** {site_info.get('site', 'N/A')}")
        st.sidebar.write(f"**Status:** {site_info.get('status', 'Active')}")

        if site_info.get("maps_link"):
            st.sidebar.markdown(f"ðŸŒ [Google Maps]({site_info['maps_link']})")

    # Navigation
    st.sidebar.divider()
    st.sidebar.subheader("ðŸ“‚ Application Pages")
    menu = st.sidebar.radio("Go to", ["Home", "Search phrases", "View all"])

    # Quick stats in sidebar
    if data_manager.officers:
        st.sidebar.divider()
        st.sidebar.subheader("ðŸ“Š Quick Stats")
        active_officers = len([o for o in data_manager.officers if o.get('status') == 'Active'])
        total_schedules = len(data_manager.schedules)

        st.sidebar.write(f"**Active Officers:** {active_officers}")
        st.sidebar.write(f"**Total Schedules:** {total_schedules}")

    # Render selected page
    try:
        if menu == "Home":
            render_home_page(data_manager, ui, selected_prefix)
        elif menu == "Search phrases":
            # You'll need to implement these functions or import them
            st.info("Search functionality coming soon...")
        elif menu == "View all":
            st.info("View all functionality coming soon...")
    except Exception as e:
        st.error(f"Error rendering page: {e}")
        st.info("Please check the data files and try again.")


if __name__ == "__main__":
    main()
