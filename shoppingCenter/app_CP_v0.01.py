# 📦 Imports
import streamlit as st
from pathlib import Path
import sys
import json
import streamlit.components.v1 as components

# 🔗 Add shared folder to path
shared_path = Path(__file__).resolve().parent.parent / "shared"
sys.path.append(str(shared_path))

# ⚙️ Page config
st.set_page_config(page_title="AmdaOps Viewer", layout="wide")

# 🧠 Load shared modules
try:
    from loader import load_phrases
    from registry import load_registry, get_prefixes, get_site_by_prefix
    from phrase import filter_phrases_by_site, get_categories, get_hotwords
except ModuleNotFoundError as e:
    st.error(f"❌ Shared module `{e.name}` not found.")
    st.stop()

# 📁 Paths
BASE_DIR = Path(__file__).resolve().parent
PHRASES_PATH = BASE_DIR / "data" / "181_line__bank_Shoping_Center_en_es.json"
REGISTRY_PATH = BASE_DIR / "data" / "site_registry.json"

# 🔍 File validation
missing_files = []
if not PHRASES_PATH.exists():
    missing_files.append(str(PHRASES_PATH))
if not REGISTRY_PATH.exists():
    missing_files.append(str(REGISTRY_PATH))

if missing_files:
    st.error("❌ Missing required files:")
    for f in missing_files:
        st.markdown(f"- `{f}`")
    st.stop()

# 📌 Load data
try:
    phrases = load_phrases(PHRASES_PATH)
    registry = load_registry(REGISTRY_PATH)
except Exception as e:
    st.error(f"❌ Error loading JSON files: {e}")
    st.stop()

# 🧭 Sidebar navigation
menu = st.sidebar.radio("📂 Navigation", ["Home", "Search phrases", "View all"])
prefixes = get_prefixes(registry)
selected_prefix = st.sidebar.selectbox("🏷️ Site", prefixes)
site_info = get_site_by_prefix(registry, selected_prefix)
filtered_phrases = filter_phrases_by_site(phrases, site_info)

# 🌍 Show Google Maps link in sidebar
if site_info and site_info.get("maps_link"):
    st.sidebar.markdown(f"🌍 [Google Maps link]({site_info['maps_link']})")

# 🧩 Home section
if menu == "Home":
    st.title("🛡️ AmdaOps - Operational Phrase Viewer")

    if site_info:
        st.markdown(f"""
        **Prefix:** `{selected_prefix}`  
        **Site type:** {site_info['site']}  
        **Name:** {site_info['name']}  
        **Address:** {site_info['address']}  
        **City:** {site_info['city']}  
        **State:** {site_info['state']}  
        **ZIP code:** {site_info['zip']}  
        🌍 [View on Google Maps]({site_info.get('maps_link', '#')})
        """)

    # 🧹 Form state
    if "clear_form" not in st.session_state:
        st.session_state.clear_form = False

    # 📝 Form
    site_options = ["ShoppingCenter", "Warehouse", "Parking", "Other"]
    site_value = site_info.get("site", "ShoppingCenter")
    site_index = site_options.index(site_value) if site_value in site_options else 0

    form_key = f"form_{selected_prefix}"
    with st.form(form_key):
        st.subheader("📝 Edit or register unit")

        if st.session_state.clear_form:
            site_info = {}

        unit_id = st.text_input("🔢 Unit ID", value=site_info.get("prefix", ""), placeholder="e.g. 343", help="Número de unidad")
        address = st.text_input("📍 Full address", value=site_info.get("address", ""), help="Dirección completa")
        city = st.text_input("🌆 City", value=site_info.get("city", ""), help="Ciudad")
        state = st.text_input("🗺️ State", value=site_info.get("state", ""), help="Estado")
        zip_code = st.text_input("📮 ZIP code", value=site_info.get("zip", ""), help="Código postal")
        site_type = st.selectbox("🏢 Site type", site_options, index=site_index, help="Tipo de sitio")
        site_name = st.text_input("🏷️ Site name", value=site_info.get("name", ""), help="Nombre del sitio")

        if site_info.get("maps_link"):
            st.markdown(f"🌍 [View on Google Maps]({site_info['maps_link']})")

        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            save = st.form_submit_button("💾 Save unit")
        with col2:
            delete = st.form_submit_button("🗑️ Delete unit")
        with col3:
            clear = st.form_submit_button("🧹 Clear form")

    # 💾 Save logic
    if save:
        required = [unit_id, address, site_name]
        if all(required):
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

            registry = [r for r in registry if r.get("prefix") != unit_id]
            registry.append(new_entry)

            try:
                with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
                    json.dump(registry, f, indent=2, ensure_ascii=False)
                st.success("✅ Unit saved successfully.")
            except Exception as e:
                st.error(f"Error saving unit: {e}")
        else:
            st.warning("Please complete at least Unit ID, Address and Site Name.")

    # 🗑️ Delete logic
    if delete and site_info:
        with st.expander("⚠️ Confirm deletion", expanded=True):
            confirm = st.button(f"❌ Yes, delete `{selected_prefix}`")
            if confirm:
                registry = [r for r in registry if r.get("prefix") != selected_prefix]
                try:
                    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
                        json.dump(registry, f, indent=2, ensure_ascii=False)
                    st.success(f"Unit `{selected_prefix}` deleted successfully.")
                except Exception as e:
                    st.error(f"Error deleting unit: {e}")

    # 🧹 Clear logic
    if clear:
        st.session_state.clear_form = True
        components.html("""
        <script>
        setTimeout(() => {
            const input = window.parent.document.querySelector('input[placeholder="e.g. 343"]');
            if (input) input.focus();
        }, 100);
        </script>
        """, height=0)

# 🔍 Search phrases
elif menu == "Search phrases":
    st.header("🔍 Filter phrases")
    category = st.selectbox("📂 Category", [""] + get_categories(filtered_phrases))
    hotword = st.selectbox("🔍 Hotword", [""] + get_hotwords(filtered_phrases))
    custom_hotword = st.text_input("✏️ Or type your own")
    final_hotword = custom_hotword if custom_hotword else hotword
    limit = st.slider("🔢 Number of phrases", 1, 20, 5)

    if st.button("Search"):
        results = []
        for p in filtered_phrases:
            if category and p.get("cat") != category:
                continue
            if final_hotword:
                hw = final_hotword.lower()
                if hw not in p.get("en", "").lower() and hw not in p.get("es", "").lower() and hw not in [h.lower() for h in p.get("hotwords", [])]:
                    continue
            results.append(p)
            if len(results) >= limit:
                break

        st.subheader("🧠 Results")
        if results:
            for p in results:
                st.markdown(f"✅ **[{p['cat']}]** {p['en']}  \n🌐 *{p['es']}*")
        else:
            st.warning("No phrases found with those filters.")

# 📋 View all phrases
elif menu == "View all":
    st.header("📋 All phrases")
    for p in filtered_phrases:
        if p.get("en") and p.get("es"):
            st.markdown(f"- **[{p['cat']}]** {p['en']}  \n🌐 *{p['es']}*")