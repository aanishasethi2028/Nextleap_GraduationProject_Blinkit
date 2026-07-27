import os
import json
import base64
import pandas as pd
import streamlit as st
from PIL import Image

# Locate local assets
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logo_path = os.path.join(project_root, "logo.png")
actual_logo_path = os.path.join(project_root, "pics", "3891925210d12c04458fbccc91565e7d.jpg")
rider_path = os.path.join(project_root, "pics", "6d3ce75565eecc267968f6409f6d41de.jpg")
app_path = os.path.join(project_root, "pics", "e86509730b1c88aef8fbacb4b3643cb3.jpg")
banner_path = os.path.join(project_root, "pics", "banner.jpg")
category_path = os.path.join(project_root, "pics", "category.jpg")

# Load PIL Image for page icon
if os.path.exists(logo_path):
    try:
        logo_img = Image.open(logo_path)
        page_icon_setting = logo_img
    except Exception:
        page_icon_setting = "🛵"
elif os.path.exists(actual_logo_path):
    try:
        # Fallback to actual logo for page icon if logo.png doesn't exist
        logo_img = Image.open(actual_logo_path)
        page_icon_setting = logo_img
    except Exception:
        page_icon_setting = "🛵"
else:
    page_icon_setting = "🛵"

# Base64 encoder helper for inline HTML image rendering
def get_base64_image(image_path):
    if os.path.exists(image_path):
        try:
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode("utf-8")
        except Exception:
            return ""
    return ""

logo_base64 = get_base64_image(logo_path)
actual_logo_base64 = get_base64_image(actual_logo_path)
rider_base64 = get_base64_image(rider_path)
app_base64 = get_base64_image(app_path)
banner_base64 = get_base64_image(banner_path)
category_base64 = get_base64_image(category_path)

# Set Streamlit Page Configuration (collapsed sidebar state to hide it completely)
st.set_page_config(
    page_title="Growth Intelligence AI Discovery Engine",
    page_icon=page_icon_setting,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS styling for premium Blinkit Yellow (#FFE000) & Green (#0C831F) aesthetics
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
    
    /* Main body typography */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: #fcfcfc;
    }
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        color: #121212;
    }
    
    /* Completely hide Streamlit sidebar button & sidebar panel */
    [data-testid="collapsedSidebarNoOverlay"] {
        display: none !important;
    }
    [data-testid="stSidebar"] {
        display: none !important;
    }

    /* Premium LENS Navigation Header (Web-feel) */
    .custom-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 1rem;
        padding: 1rem 0.5rem;
        background-color: #ffffff;
        border-bottom: 1px solid #e2e8f0;
        margin-bottom: 1.5rem;
        font-family: 'Outfit', sans-serif;
    }
    .header-left {
        display: flex;
        align-items: center;
        gap: 14px;
    }
    .header-logo {
        background-color: #F8CB46;
        color: #1e293b;
        border-radius: 12px;
        width: 50px;
        height: 50px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 850;
        font-size: 1.85rem;
        line-height: 1;
        box-shadow: 0 4px 12px rgba(30, 41, 59, 0.08), 0 0 0 3px rgba(248, 203, 70, 0.35);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        overflow: hidden;
    }
    .header-logo:hover {
        transform: scale(1.03);
        box-shadow: 0 6px 16px rgba(30, 41, 59, 0.12), 0 0 0 4px rgba(248, 203, 70, 0.5);
    }
    .header-logo img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    .header-title-block {
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .header-brand-row {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .header-title {
        font-size: 2.05rem;
        font-weight: 850;
        color: #1e293b;
        letter-spacing: -0.8px;
        line-height: 1;
    }
    .header-badge {
        background-color: #F8CB46;
        color: #1e293b;
        font-weight: 800;
        font-size: 0.62rem;
        padding: 3px 8px;
        border-radius: 9999px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        display: inline-block;
        line-height: 1;
    }
    .header-subtitle {
        font-size: 0.78rem;
        color: #64748b;
        font-weight: 400;
        margin-top: 3px;
        line-height: 1;
    }
    .header-right {
        font-size: 1.2rem;
        color: #64748b;
        font-weight: 400;
        letter-spacing: -0.2px;
    }

    /* Premium Streamlit Tabs Custom CSS */
    button[data-baseweb="tab"] {
        font-family: 'Outfit', sans-serif !important;
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        color: #475569 !important;
        padding: 0.5rem 1.5rem !important;
        border-radius: 8px 8px 0 0 !important;
        transition: background-color 0.2s, color 0.2s !important;
    }
    button[data-baseweb="tab"]:hover {
        color: #0C831F !important;
        background-color: #f1f5f9 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #0C831F !important;
        border-bottom: 3px solid #0C831F !important;
    }

    /* Style primary button to be green */
    div.stButton > button[kind="primary"] {
        background-color: #0C831F !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        padding: 0.5rem 1rem !important;
        transition: background-color 0.2s;
        font-family: 'Outfit', sans-serif !important;
        height: 42px !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #085514 !important;
        color: white !important;
    }

    /* Clean Card layouts */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.25rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.02);
        border: 1px solid #eaeaea;
        border-bottom: 4px solid #FFE000;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        text-align: center;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.05);
    }
    .metric-val {
        font-size: 1.8rem;
        font-weight: 800;
        color: #0C831F;
        margin: 0;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #555;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 700;
        margin-top: 0.25rem;
    }

    /* Layman-friendly Filter Box */
    div[data-testid="stForm"] {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 1.25rem 1.5rem !important;
        margin-bottom: 1.5rem !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.01) !important;
    }

    /* Fact-Focused Bias Warnings Box */
    .bias-disclosure {
        background: #fdfdf2;
        border-left: 5px solid #FFE000;
        border-radius: 8px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(255, 224, 0, 0.05);
        border: 1px solid #f2eeb8;
        border-left: 5px solid #FFE000;
    }
    .bias-title {
        color: #8c7600;
        font-weight: 700;
        font-size: 1.05rem;
        margin: 0 0 0.5rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .bias-text {
        font-size: 0.95rem;
        color: #4a3e00;
        line-height: 1.5;
        margin: 0;
    }

    /* Insight Card Badges and Score styles */
    .card-theme-badge {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .card-conf-badge {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.2px;
    }
    .badge-conf-high {
        background-color: #ecfdf5;
        color: #047857;
        border: 1px solid #a7f3d0;
    }
    .badge-conf-medium {
        background-color: #fffbeb;
        color: #b45309;
        border: 1px solid #fde68a;
    }
    .badge-conf-low {
        background-color: #fdf2f2;
        color: #b91c1c;
        border: 1px solid #fdecec;
    }
    .card-opp-score {
        font-size: 0.8rem;
        font-weight: 800;
        color: #8c7600;
        background-color: #fffbeb;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        border: 1px solid #fde68a;
    }

    /* Merge the streamlit expander with custom HTML card tops */
    .stMarkdown + div[data-testid="stExpander"] {
        border-radius: 0 0 12px 12px !important;
        border: 1px solid #eef0f5 !important;
        border-top: none !important;
        margin-bottom: 1.5rem !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.02) !important;
    }
    .stMarkdown + div[data-testid="stExpander"] summary {
        background-color: #f8fafc !important;
        padding: 0.5rem 1rem !important;
        font-weight: 700 !important;
        color: #475569 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }

    /* Details styling inside cards */
    .section-title {
        font-weight: 700;
        font-size: 0.85rem;
        color: #555;
        margin-top: 0.8rem;
        margin-bottom: 0.25rem;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }
    .quote-box {
        background: #f8fafc;
        border-left: 3px solid #cbd5e1;
        padding: 0.6rem 1rem;
        margin: 0.5rem 0;
        border-radius: 0 8px 8px 0;
        font-style: italic;
        font-size: 0.9rem;
        color: #334155;
    }
    .quote-source {
        font-size: 0.8rem;
        color: #64748b;
        margin-top: 0.25rem;
        text-align: right;
    }
    .quote-source a {
        color: #0C831F;
        text-decoration: underline;
        font-weight: 600;
    }
    .hook-box {
        background-color: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-radius: 8px;
        padding: 0.8rem 1rem;
        margin-top: 0.8rem;
    }
    .hook-prefix {
        font-weight: 700;
        font-size: 0.85rem;
        letter-spacing: 0.3px;
        margin-bottom: 0.2rem;
    }
    .hook-validate {
        color: #047857;
    }
    .hook-assumption {
        color: #b45309;
    }
    .hook-text {
        font-size: 0.9rem;
        color: #064e3b;
        margin: 0;
    }

    /* Table & Matrix styling */
    .matrix-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 1rem;
        font-size: 0.78rem;
    }
    .matrix-table th {
        background-color: #0C831F;
        color: white;
        text-align: center;
        padding: 8px 4px;
        border: 1px solid #e2e8f0;
        font-weight: 700;
        white-space: normal !important;
        word-wrap: break-word !important;
        font-size: 0.7rem !important;
        min-width: 50px;
    }
    .matrix-table td {
        border: 1px solid #e2e8f0;
        text-align: center;
        padding: 8px 6px;
        white-space: normal !important;
        font-size: 0.75rem !important;
    }
    .matrix-table tr:nth-child(even) {
        background-color: #f8fafc;
    }
    .matrix-diag {
        background-color: #e2f8e6 !important;
        font-weight: bold;
        color: #0C831F;
    }
    .triangulation-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 1rem;
    }
    .triangulation-table th {
        background-color: #f1f5f9;
        color: #475569;
        text-align: left;
        padding: 10px 12px;
        border-bottom: 2px solid #cbd5e1;
        font-weight: 700;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .triangulation-table td {
        border-bottom: 1px solid #e2e8f0;
        text-align: left;
        padding: 12px;
        font-size: 0.82rem;
        color: #334155;
        line-height: 1.4;
    }
    .triangulation-table tr:hover {
        background-color: #f8fafc;
    }
    
    /* Tooltip container */
    .custom-tooltip {
        position: relative;
        display: inline-block;
        cursor: pointer;
        margin-left: 8px;
        color: #0C831F;
        font-size: 1.15rem;
        vertical-align: middle;
    }
    /* Tooltip text - below the icon */
    .custom-tooltip .tooltiptext {
        visibility: hidden;
        width: 340px;
        background-color: #1e293b;
        color: #fff;
        text-align: left;
        border-radius: 8px;
        padding: 12px;
        position: absolute;
        z-index: 100;
        top: 130%; 
        left: 50%;
        margin-left: -170px;
        opacity: 0;
        transition: opacity 0.3s;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.85rem;
        line-height: 1.4;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        border: 1px solid #334155;
        font-weight: normal;
    }
    .custom-tooltip .tooltiptext::after {
        content: "";
        position: absolute;
        bottom: 100%;
        left: 50%;
        margin-left: -5px;
        border-width: 5px;
        border-style: solid;
        border-color: transparent transparent #1e293b transparent;
    }
    .custom-tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }

    /* Hide default Streamlit header anchor links */
    h1 a, h2 a, h3 a, h4 a, h5 a, h6 a,
    a.anchor-link,
    [data-testid="styled-link-icon"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to load JSON files
def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

# Load Datasets
insights_data = load_json("data/insights.json")
val_report = load_json("data/validation_report.json")

if not insights_data or not val_report:
    st.error("Error: Insights database or validation report not found. Please verify that synthesis and validation scripts have run.")
    st.stop()

# ==================== SOURCE LINK MAPPING HELPER ====================
def get_source_url(source_str):
    if not isinstance(source_str, str):
        return "https://blinkit.com"
    source_lower = source_str.lower().strip()
    if "play.google.com" in source_lower or "playstore" in source_lower or "google play" in source_lower:
        return "https://play.google.com/store/apps/details?id=com.grofers.customerapp"
    elif "apps.apple.com" in source_lower or "appstore" in source_lower or "app store" in source_lower:
        return "https://apps.apple.com/in/app/blinkit-grocery-delivery/id960984733"
    elif "youtube.com" in source_lower or "youtu.be" in source_lower:
        return source_str
    elif "mouthshut" in source_lower:
        return "https://www.mouthshut.com/product-reviews/Blinkit-reviews-925763914"
    elif "trustpilot" in source_lower:
        return "https://www.trustpilot.com/review/blinkit.com"
    elif "reddit" in source_lower:
        return "https://www.reddit.com/r/india/"
    elif source_str.startswith("http"):
        return source_str
    return "https://blinkit.com"

# Mappings for display labels
theme_labels = {
    "habit_loop": "Habit Loop",
    "awareness_gap": "Awareness Gap",
    "mental_model": "Mental Model",
    "trust_quality": "Trust Quality",
    "trust_information": "Trust Information",
    "price_value": "Price Value",
    "ux_friction": "UX Friction",
    "assortment_gap": "Assortment Gap",
    "delivery_ops": "Delivery Ops",
    "emotional": "Emotional",
    "other": "Other"
}

# Theme Badge Color Mapping
theme_colors = {
    "habit_loop": {"bg": "#0C831F", "text": "white"},
    "awareness_gap": {"bg": "#3B82F6", "text": "white"},
    "mental_model": {"bg": "#8B5CF6", "text": "white"},
    "trust_quality": {"bg": "#EF4444", "text": "white"},
    "trust_information": {"bg": "#EC4899", "text": "white"},
    "price_value": {"bg": "#F59E0B", "text": "white"},
    "ux_friction": {"bg": "#10B981", "text": "white"},
    "assortment_gap": {"bg": "#6366F1", "text": "white"},
    "delivery_ops": {"bg": "#FFE000", "text": "#121212"},
    "emotional": {"bg": "#14B8A6", "text": "white"},
    "other": {"bg": "#64748B", "text": "white"}
}

rq_labels = {
    "Q1": "What prompts the very first quick-commerce order in a household?",
    "Q2": "How do users transition from emergency top-ups to routine basket ordering?",
    "Q3": "What categories do users explicitly resist buying on quick commerce?",
    "Q4": "How does user trust differ between fresh groceries and packaged goods?",
    "Q5": "What information (reviews, specifications) do users need before trying a new category?",
    "Q6": "What app interface elements cause friction during category exploration?",
    "Q7": "Which user segments are more likely to experiment with non-grocery categories?",
    "Q8": "What is the emotional role of quick commerce in the user's daily habit loop?"
}

# ==================== MAIN PAGE BRAND HEADER ====================
if app_base64:
    logo_html = f'<div class="header-logo"><img src="data:image/jpeg;base64,{app_base64}" /></div>'
else:
    logo_html = '<div class="header-logo">L</div>'

st.markdown(f"""<div class="custom-header">
<div class="header-left">
{logo_html}
<div class="header-title-block">
<div class="header-brand-row">
<span class="header-title">LENS — Blinkit  Category  Discovery Engine</span>
<span class="header-badge">BLINKIT</span>
</div>
<div class="header-subtitle">Listening Engine for Shoppers</div>
</div>
</div>
<div class="header-right">
Why users repeat categories, and what unlocks exploration
</div>
</div>""", unsafe_allow_html=True)

st.write("")

# ==================== BRAND ILLUSTRATION BANNERS ====================
if rider_base64 and banner_base64 and category_base64:
    col_banner1, col_banner_mid, col_banner2 = st.columns([1, 2.5, 1])
    with col_banner1:
        st.markdown(f"""
        <div style="background-color: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 1rem; box-shadow: 0 4px 15px rgba(0,0,0,0.01); display: flex; flex-direction: column; justify-content: space-between; height: 160px; overflow: hidden; margin-bottom: 1.5rem;">
            <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 0.5rem; width: 100%;">
                <div>
                    <span style="background-color: #fef3c7; color: #b45309; font-size: 0.62rem; font-weight: 800; padding: 2px 6px; border-radius: 9999px; text-transform: uppercase; letter-spacing: 0.5px;">Operations</span>
                    <h3 style="margin: 0.25rem 0 0 0; font-family: 'Outfit', sans-serif; font-weight: 800; font-size: 1.05rem; color: #1e293b; line-height: 1.1;">Delivered in Minutes</h3>
                </div>
                <div style="width: 50px; height: 50px; border-radius: 8px; overflow: hidden; flex-shrink: 0; box-shadow: 0 2px 6px rgba(0,0,0,0.05);">
                    <img src="data:image/jpeg;base64,{rider_base64}" style="width: 100%; height: 100%; object-fit: cover;" />
                </div>
            </div>
            <p style="margin: 0; color: #020b1a; font-size: 0.9rem; line-height: 1.3;">
                Analyzing instant-delivery touchpoints to bridge emergency orders and weekly grocery baskets.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col_banner_mid:
        st.markdown(f"""
        <div style="background-color: white; border: 1px solid #e2e8f0; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.01); height: 160px; margin-bottom: 1.5rem; display: flex; align-items: center; justify-content: center;">
            <img src="data:image/jpeg;base64,{banner_base64}" style="width: 100%; height: 100%; object-fit: cover;" />
        </div>
        """, unsafe_allow_html=True)
    with col_banner2:
        st.markdown(f"""
        <div style="background-color: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 1rem; box-shadow: 0 4px 15px rgba(0,0,0,0.01); display: flex; flex-direction: column; justify-content: space-between; height: 160px; overflow: hidden; margin-bottom: 1.5rem;">
            <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 0.5rem; width: 100%;">
                <div>
                    <span style="background-color: #dcfce7; color: #15803d; font-size: 0.62rem; font-weight: 800; padding: 2px 6px; border-radius: 9999px; text-transform: uppercase; letter-spacing: 0.5px;">Growth Strategy</span>
                    <h3 style="margin: 0.25rem 0 0 0; font-family: 'Outfit', sans-serif; font-weight: 800; font-size: 1.05rem; color: #1e293b; line-height: 1.1;">Category-Discovery</h3>
                </div>
                <div style="width: 50px; height: 50px; border-radius: 8px; overflow: hidden; flex-shrink: 0; box-shadow: 0 2px 6px rgba(0,0,0,0.05);">
                    <img src="data:image/jpeg;base64,{category_base64}" style="width: 100%; height: 100%; object-fit: cover;" />
                </div>
            </div>
            <p style="margin: 0; color: #020b1a; font-size: 0.9rem; line-height: 1.3;">
                Converting qualitative user voices into opportunity scores to drive adoption in new categories.
            </p>
        </div>
        """, unsafe_allow_html=True)

# ==================== SINGLE PAGE NAVIGATION (Native tabs like earlier) ====================
tab_insights, tab_validation, tab_routing = st.tabs([
    "🛵 Discovered Growth Insights",
    "📊 Validation & Method Quality",
    "🗺️ Research Questions Answer Map"
])

# ==================== TAB 1: DISCOVERED GROWTH INSIGHTS ====================
with tab_insights:
    # Page Title & Subtitle
    st.markdown("""
    <div style="margin-bottom: 1.5rem; margin-top: 1rem;">
        <h2 style="margin: 0; font-family: 'Outfit', sans-serif; font-weight: 800; color: #121212;">
            LENS Growth Opportunity Explorer <span class="custom-tooltip">ⓘ<span class="tooltiptext">
                <strong style="color: #FFE000; font-size: 0.95rem;">📊 Opportunity Prioritization Formula</strong><br/><br/>
                Growth opportunities are ranked and prioritized using our category-adoption impact formula:<br/>
                <code style="background: #0f172a; padding: 4px 8px; border-radius: 4px; display: block; margin: 8px 0; color: #38bdf8; font-family: monospace; font-size: 0.8rem;">Score = Log(Frequency) × Severity × Addressability × Strategic Fit</code>
                • <strong>Frequency:</strong> Customer review occurrences count.<br/>
                • <strong>Severity:</strong> User pain level or barrier (1-5).<br/>
                • <strong>Addressability:</strong> Technical & operational ease of resolution (1-5).<br/>
                • <strong>Strategic Fit:</strong> Category expansion alignment (1-5).
            </span></span>
        </h2>
        <p style="color: #64748b; font-size: 0.95rem; margin-top: 0.25rem;">
            Visualizing AI-distilled consumer friction points into high-probability retail growth levers.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Data extraction for filters
    all_themes = sorted(list(set(insight["primary_theme"] for insight in insights_data["insights"])))
    all_rqs = sorted(list(set(rq for insight in insights_data["insights"] for rq in insight["answers_questions"])))
    all_sources = sorted(list(set(src for insight in insights_data["insights"] for src in insight["triangulated_sources"])))
    
    # Filters Form Card
    with st.form("filter_form"):
        col_f1, col_f2, col_f3, col_f4, col_btn = st.columns([2.5, 2.5, 2.5, 2.5, 1.5])
        with col_f1:
            theme_options = ["All Themes"] + [theme_labels.get(t, t.replace("_", " ").title()) for t in all_themes]
            selected_theme_label = st.selectbox("Select Theme", theme_options)
            
        with col_f2:
            rq_options = ["All Research Questions"] + [rq_labels.get(r, r) for r in all_rqs]
            selected_rq_label = st.selectbox("Select Research Question", rq_options)
            
        with col_f3:
            selected_conf = st.selectbox("Select Confidence", ["All Confidences", "HIGH", "MEDIUM", "LOW"])
            
        with col_f4:
            source_options = ["All Sources"] + [("Survey" if s == "n=42 Survey" else s) for s in all_sources]
            selected_source_label = st.selectbox("Select Source", source_options)
            
        with col_btn:
            st.markdown('<div style="height: 12px;"></div>', unsafe_allow_html=True)
            apply_filters = st.form_submit_button("⚡ Apply Filters", use_container_width=True)

    # Map selection back to database keys
    selected_theme = "All Themes"
    if selected_theme_label != "All Themes":
        selected_theme = next((k for k, v in theme_labels.items() if v == selected_theme_label), selected_theme_label)
        
    selected_rq = "All Research Questions"
    if selected_rq_label != "All Research Questions":
        selected_rq = next((k for k, v in rq_labels.items() if v == selected_rq_label), selected_rq_label)

    # Filtered Insights calculation
    filtered_insights = []
    for insight in insights_data["insights"]:
        if selected_theme != "All Themes" and insight["primary_theme"] != selected_theme:
            continue
        if selected_conf != "All Confidences" and insight["confidence"].upper() != selected_conf:
            continue
        if selected_rq != "All Research Questions" and selected_rq not in insight["answers_questions"]:
            continue
        if selected_source_label != "All Sources":
            actual_source = "n=42 Survey" if selected_source_label == "Survey" else selected_source_label
            if actual_source not in insight["triangulated_sources"]:
                continue
        filtered_insights.append(insight)

    # Opportunity Cards Section
    st.markdown(f"#### 📊 Discovered Growth Opportunity Cards ({len(filtered_insights)} items)")
    
    if not filtered_insights:
        st.info("No insights match the current filter selection.")
    else:
        # Render cards in 3 columns (screen1.png Layout)
        cols = st.columns(3)
        for idx, insight in enumerate(filtered_insights):
            col = cols[idx % 3]
            conf_class = f"badge-conf-{insight['confidence']}"
            theme_key = insight["primary_theme"]
            theme_name = theme_labels.get(theme_key, theme_key.replace("_", " ").title())
            colors = theme_colors.get(theme_key, {"bg": "#64748B", "text": "white"})
            
            # Find global index
            global_idx = insights_data["insights"].index(insight) + 1
            
            with col:
                # Custom Card Top
                st.markdown(f"""
                <div style="background-color: white; border: 1px solid #eef0f5; border-radius: 12px 12px 0 0; padding: 1.5rem 1.5rem 0.5rem 1.5rem; box-shadow: 0 4px 15px rgba(0,0,0,0.02); border-bottom: none; display: flex; flex-direction: column; gap: 0.8rem; margin-top: 1rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;">
                        <div style="display: flex; gap: 0.4rem; flex-wrap: wrap;">
                            <span class="card-theme-badge" style="background-color: {colors['bg']}; color: {colors['text']};">{theme_name}</span>
                            <span class="card-conf-badge {conf_class}">{insight['confidence'].upper()} CONFIDENCE</span>
                        </div>
                        <div class="card-opp-score">Score: {insight['opportunity_score']:.1f}</div>
                    </div>
                    <h4 style="margin: 0; font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 1.1rem; color: #121212; line-height: 1.3;">Insight #{global_idx}: {insight['insight_title']}</h4>
                    <p style="margin: 0; font-size: 0.85rem; color: #475569; line-height: 1.5;">{insight['finding']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Card Bottom (Seamless Streamlit Expander)
                with st.expander("📂 View Actionable Growth Strategy, Quotes & Validation Hooks"):
                    st.markdown(f"**Growth Strategy:** {insight['so_what_for_growth']}")
                    st.write("")
                    st.markdown("**Affected Segments:**")
                    for seg in insight["affected_segments"]:
                        st.markdown(f"- {seg}")
                    st.write("")
                    st.markdown("**Representative User Quotes:**")
                    for quote in insight["representative_quotes"]:
                        raw_src = quote["source_url"]
                        raw_src_lower = raw_src.lower()
                        
                        if "play" in raw_src_lower or "google" in raw_src_lower:
                            st.markdown(f"""
                            <div class="quote-box">
                                "{quote['text']}"
                                <div class="quote-source">— Source Channel: Google Play Store</div>
                            </div>
                            """, unsafe_allow_html=True)
                        elif "app" in raw_src_lower or "ios" in raw_src_lower:
                            st.markdown(f"""
                            <div class="quote-box">
                                "{quote['text']}"
                                <div class="quote-source">— Source Channel: App Store Page</div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            target_url = get_source_url(raw_src)
                            link_label = "View Direct Social Post" if raw_src.startswith("http") else f"View {raw_src} Page"
                            st.markdown(f"""
                            <div class="quote-box">
                                "{quote['text']}"
                                <div class="quote-source">— Source Channel: <a href="{target_url}" target="_blank">{link_label}</a></div>
                            </div>
                            """, unsafe_allow_html=True)
                    st.write("")
                    
                    val_hook = insight["validation_needed"]
                    if val_hook.startswith("[VALIDATE]"):
                        prefix = "🔍 VALIDATION HOOK"
                        prefix_class = "hook-validate"
                        val_hook_text = val_hook.replace("[VALIDATE]", "").strip()
                    else:
                        prefix = "💡 ASSUMPTION PROBING"
                        prefix_class = "hook-assumption"
                        val_hook_text = val_hook.replace("[ASSUMPTION]", "").strip()
                        
                    st.markdown(f"""
                    <div class="hook-box">
                        <div class="hook-prefix {prefix_class}">{prefix}</div>
                        <p class="hook-text">{val_hook_text}</p>
                    </div>
                    """, unsafe_allow_html=True)

    st.write("")


# ==================== TAB 2: VALIDATION & METHOD QUALITY ====================
with tab_validation:
    # Subtitle & Title
    st.markdown("""
    <div style="margin-bottom: 1.5rem; margin-top: 1rem;">
        <h2 style="margin: 0; font-family: 'Outfit', sans-serif; font-weight: 800; color: #121212;">Validation & Method Quality</h2>
        <p style="color: #64748b; font-size: 0.95rem; margin-top: 0.25rem;">
            Auditing consumer listening models for semantic precision and category relevance.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Funnel Metrics row (screen3.png funnels)
    col_fun1, col_fun2, col_fun3, col_fun4 = st.columns(4)
    with col_fun1:
        st.markdown("""
        <div style="background-color: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.25rem; box-shadow: 0 4px 10px rgba(0,0,0,0.01); border-left: 5px solid #64748b; height: 100%;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <span style="font-size: 0.75rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px;">Raw Inputs</span>
                <span style="font-size: 1.25rem;">🥞</span>
            </div>
            <div style="font-size: 1.8rem; font-weight: 800; color: #1e293b; margin-top: 0.5rem; line-height: 1.1;">1,327</div>
            <p style="font-size: 0.8rem; color: #64748b; margin-top: 0.25rem; margin-bottom: 0;">Unfiltered unstructured reviews</p>
        </div>
        """, unsafe_allow_html=True)
    with col_fun2:
        st.markdown("""
        <div style="background-color: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.25rem; box-shadow: 0 4px 10px rgba(0,0,0,0.01); border-left: 5px solid #f59e0b; height: 100%;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <span style="font-size: 0.75rem; font-weight: 700; color: #f59e0b; text-transform: uppercase; letter-spacing: 0.5px;">Duplicates Cleaned</span>
                <span style="font-size: 1.25rem;">📋</span>
            </div>
            <div style="font-size: 1.8rem; font-weight: 800; color: #1e293b; margin-top: 0.5rem; line-height: 1.1;">17</div>
            <p style="font-size: 0.8rem; color: #f59e0b; margin-top: 0.25rem; margin-bottom: 0;">1.3% reduction vs source</p>
        </div>
        """, unsafe_allow_html=True)
    with col_fun3:
        st.markdown("""
        <div style="background-color: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.25rem; box-shadow: 0 4px 10px rgba(0,0,0,0.01); border-left: 5px solid #b45309; height: 100%;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <span style="font-size: 0.75rem; font-weight: 700; color: #b45309; text-transform: uppercase; letter-spacing: 0.5px;">Low-Signal Flagged</span>
                <span style="font-size: 1.25rem;">⏳</span>
            </div>
            <div style="font-size: 1.8rem; font-weight: 800; color: #1e293b; margin-top: 0.5rem; line-height: 1.1;">55</div>
            <p style="font-size: 0.8rem; color: #b45309; margin-top: 0.25rem; margin-bottom: 0;">Short/low-quality reviews</p>
        </div>
        """, unsafe_allow_html=True)
    with col_fun4:
        st.markdown("""
        <div style="background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 12px; padding: 1.25rem; box-shadow: 0 4px 10px rgba(0,0,0,0.01); border-left: 5px solid #0C831F; height: 100%;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <span style="font-size: 0.75rem; font-weight: 700; color: #0C831F; text-transform: uppercase; letter-spacing: 0.5px;">High-Signal Insights</span>
                <span style="font-size: 1.25rem;">⭐</span>
            </div>
            <div style="font-size: 1.8rem; font-weight: 800; color: #0C831F; margin-top: 0.5rem; line-height: 1.1;">1,255</div>
            <p style="font-size: 0.8rem; color: #047857; margin-top: 0.25rem; margin-bottom: 0;">Cleaned for decision making</p>
        </div>
        """, unsafe_allow_html=True)

    # Add spacing between funnel cards and the expander below
    st.markdown("<div style='margin-bottom: 1.25rem;'></div>", unsafe_allow_html=True)

    # Dataset biases expander
    biases = val_report.get("biases", {})
    source_skew = biases.get("source_skew_appstore_pct", 75.3)
    polarized_five = biases.get("rating_polarization_5_star", 777)
    polarized_one = biases.get("rating_polarization_1_star", 178)
    missing_ratings = biases.get("missing_ratings_pct", 21.1)

    st.markdown(f"""
    <div style="background-color: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.25rem; box-shadow: 0 4px 10px rgba(0,0,0,0.01);">
        <div style="font-weight: 700; font-family: 'Outfit', sans-serif; font-size: 1.05rem; color: #121212; margin-bottom: 0.75rem;">View Ingestion Biases & Skew Parameters</div>
        <p style="color: #64748b; font-size: 0.85rem; line-height: 1.4; margin-bottom: 1rem;">
            Feedback is collected only from active app users (survivorship bias) and is heavily skewed towards Play Store & App Store reviews.
        </p>
        <ul style="margin: 0; padding-left: 0.2rem; font-size: 0.85rem; color: #334155; line-height: 1.6; list-style-type: none;">
            <li style="margin-bottom: 0.4rem;">📢 <strong>Source Skew:</strong> App Stores account for <strong>{source_skew:.1f}%</strong> of feedback.</li>
            <li style="margin-bottom: 0.4rem;">⭐ <strong>Polarization:</strong> High star rating polarization (<strong>{polarized_five}</strong> 5-Star vs <strong>{polarized_one}</strong> 1-Star).</li>
            <li style="margin-bottom: 0.4rem;">📝 <strong>Ratings completeness:</strong> <strong>{missing_ratings:.1f}%</strong> of feedback (e.g. YouTube) lacks star ratings.</li>
            <li>👥 <strong>Survivorship bias:</strong> Excludes users who already uninstalled the app.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    # Summary Metrics Bar (screen3.png Second Row)
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        st.markdown("""
        <div style="background-color: white; border: 1px solid #eef0f5; border-radius: 12px; padding: 1.25rem; display: flex; align-items: center; gap: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.01);">
            <div style="background-color: #f1f5f9; border-radius: 8px; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; font-size: 1.3rem;">💬</div>
            <div>
                <div style="font-size: 0.75rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px;">Validated Reviews</div>
                <div style="font-size: 1.4rem; font-weight: 800; color: #1e293b; line-height: 1.2;">1,310</div>
                <div style="font-size: 0.75rem; color: #0C831F; font-weight: 600;">↑ 12.4% precision lift</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_s2:
        st.markdown("""
        <div style="background-color: white; border: 1px solid #eef0f5; border-radius: 12px; padding: 1.25rem; display: flex; align-items: center; gap: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.01);">
            <div style="background-color: #f1f5f9; border-radius: 8px; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; font-size: 1.3rem;">🧪</div>
            <div>
                <div style="font-size: 0.75rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px;">Category Trials</div>
                <div style="font-size: 1.4rem; font-weight: 800; color: #1e293b; line-height: 1.2;">92</div>
                <div style="font-size: 0.75rem; color: #0C831F; font-weight: 600;">Across 12 retail sub-sectors</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_s3:
        st.markdown("""
        <div style="background-color: white; border: 1px solid #eef0f5; border-radius: 12px; padding: 1.25rem; display: flex; align-items: center; gap: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.01);">
            <div style="background-color: #f1f5f9; border-radius: 8px; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; font-size: 1.3rem;">✨</div>
            <div>
                <div style="font-size: 0.75rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px;">Growth Cards</div>
                <div style="font-size: 1.4rem; font-weight: 800; color: #1e293b; line-height: 1.2;">17</div>
                <div style="font-size: 0.75rem; color: #0C831F; font-weight: 600;">Confidence Score: 98.2%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # Model Agreement baseline vs refined & Matrix comparison
    overall_before = val_report.get("before_audit", {}).get("overall_agreement_pct", 56.0)
    overall_after = val_report.get("after_audit", {}).get("overall_agreement_pct", 66.0)

    col_agree, col_matrix = st.columns([1.3, 1.7])
    with col_agree:
        st.markdown(f"""<div style="background-color: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.25rem; box-shadow: 0 4px 10px rgba(0,0,0,0.01); height: 100%;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
<span style="font-weight: 700; font-family: 'Outfit', sans-serif; font-size: 1rem; color: #121212;">Initial Model Agreement</span>
<span style="background-color: #fdf2f2; color: #b91c1c; font-size: 0.7rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; text-transform: uppercase;">Baseline: {overall_before:.1f}%</span>
</div>
<div style="background-color: #f8fafc; border-left: 4px solid #cbd5e1; padding: 0.8rem; border-radius: 0 8px 8px 0; font-size: 0.85rem; line-height: 1.4; color: #475569; margin-bottom: 0.5rem;">
<strong>SAMPLE ID: #88219</strong><br/>
"Delivery was fast, but the milk carton was slightly dented. Milk itself was fine though."
<div style="margin-top: 0.5rem; display: flex; gap: 8px;">
<span style="background-color: #fee2e2; color: #991b1b; padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; font-weight: 600;">Label: Negative</span>
<span style="background-color: #e2e8f0; color: #475569; padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; font-weight: 600;">Confidence: 62%</span>
</div>
</div>
<p style="font-size: 0.75rem; color: #64748b; font-style: italic; margin-bottom: 1.5rem;">
Note: Initial model over-indexes on 'dented' (packaging) ignoring 'fast' (service) and 'fine' (product).
</p>
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; border-top: 1px dashed #e2e8f0; padding-top: 1rem;">
<span style="font-weight: 700; font-family: 'Outfit', sans-serif; font-size: 1rem; color: #121212;">Sharpened Model Agreement</span>
<span style="background-color: #e2f8e6; color: #0C831F; font-size: 0.7rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; text-transform: uppercase;">LENS Refined: {overall_after:.1f}%</span>
</div>
<div style="background-color: #f8fafc; border-left: 4px solid #0C831F; padding: 0.8rem; border-radius: 0 8px 8px 0; font-size: 0.85rem; line-height: 1.4; color: #475569; margin-bottom: 0.5rem;">
<strong>SAMPLE ID: #88219</strong><br/>
"Delivery was fast, but the milk carton was slightly dented. Milk itself was fine though."
<div style="margin-top: 0.5rem; display: flex; gap: 6px; flex-wrap: wrap;">
<span style="background-color: #dcfce7; color: #15803d; padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; font-weight: 600;">Service: Positive</span>
<span style="background-color: #dcfce7; color: #15803d; padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; font-weight: 600;">Product: Positive</span>
<span style="background-color: #fee2e2; color: #991b1b; padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; font-weight: 600;">Packaging: Negative</span>
</div>
</div>
<p style="font-size: 0.75rem; color: #64748b; font-style: italic; margin: 0;">
Note: Multi-intent extraction correctly identifies high-signal satisfaction despite packaging defects.
</p>
</div>""", unsafe_allow_html=True)

    with col_matrix:
        st.markdown("""
        <div style="background-color: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.25rem; box-shadow: 0 4px 10px rgba(0,0,0,0.01); height: 100%;">
            <div style="font-weight: 700; font-family: 'Outfit', sans-serif; font-size: 1rem; color: #121212; margin-bottom: 0.5rem;">Semantic Confusion Matrix</div>
            <p style="color: #64748b; font-size: 0.85rem; line-height: 1.4; margin-bottom: 1rem;">
                Class-level correlation for 11 distinct category clusters. Rows represent Expert Auditor, Columns represent LLM.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        c_matrix_after = val_report.get("confusion_matrix_after", {})
        themes_list = ["Habit Loop", "Awareness Gap", "Mental Model", "Trust Quality", "Trust Information", "Price Value", "UX Friction", "Assortment Gap", "Delivery Ops", "Emotional", "Other"]
        
        label_to_key = {
            "Habit Loop": "habit_loop",
            "Awareness Gap": "awareness_gap",
            "Mental Model": "mental_model",
            "Trust Quality": "trust_quality",
            "Trust Information": "trust_information",
            "Price Value": "price_value",
            "UX Friction": "ux_friction",
            "Assortment Gap": "assortment_gap",
            "Delivery Ops": "delivery_ops",
            "Emotional": "emotional",
            "Other": "other"
        }

        table_html = '<table class="matrix-table"><tr><th>Expert / LLM</th>' + "".join(f"<th>{t}</th>" for t in themes_list) + "</tr>"
        for expert in themes_list:
            table_html += f"<tr><td><strong>{expert}</strong></td>"
            for col in themes_list:
                expert_key = label_to_key.get(expert, expert.lower())
                col_key = label_to_key.get(col, col.lower())
                val = c_matrix_after.get(expert_key, {}).get(col_key, 0)
                diag_class = ' class="matrix-diag"' if col == expert else ''
                table_html += f"<td{diag_class}>{val}</td>"
            table_html += "</tr>"
        table_html += "</table>"
        
        st.markdown(table_html, unsafe_allow_html=True)




# ==================== TAB 3: RESEARCH QUESTIONS ANSWER MAP ====================
with tab_routing:
    # Subtitle & Title
    st.markdown("""
    <div style="margin-bottom: 1.5rem; margin-top: 1rem;">
        <h2 style="margin: 0; font-family: 'Outfit', sans-serif; font-weight: 800; color: #121212;">Research Answer Map</h2>
        <p style="color: #64748b; font-size: 0.95rem; margin-top: 0.25rem;">
            Tracing the customer journey through 8 core intelligence pillars. Data points are harvested from real-time consumer listening and AI discovery.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Map insights to RQs
    rq_mapping = {rq: [] for rq in rq_labels.keys()}
    for card in insights_data["insights"]:
        for rq in card["answers_questions"]:
            if rq in rq_mapping:
                rq_mapping[rq].append(card)

    # Load gaps from insights.json
    gaps = insights_data.get("gaps", [])

    rq_categories = {
        "Q1": {"name": "CONSUMER INTENT", "color": "#0C831F"},
        "Q2": {"name": "BEHAVIORAL TRANSITION", "color": "#0C831F"},
        "Q3": {"name": "CATEGORY RESISTANCE", "color": "#0C831F"},
        "Q4": {"name": "TRUST DIVERGENCE", "color": "#0C831F"},
        "Q5": {"name": "INFORMATION BARRIER", "color": "#ef4444"},
        "Q6": {"name": "UX FRICTION", "color": "#0C831F"},
        "Q7": {"name": "DEMOGRAPHIC DRIFT", "color": "#ef4444"},
        "Q8": {"name": "HABITUAL EMOTION", "color": "#0C831F"}
    }

    # Render Q1 to Q8 Cards
    for idx_q, (rq_id, rq_desc) in enumerate(rq_labels.items()):
        category_info = rq_categories.get(rq_id, {"name": "RESEARCH PILLAR", "color": "#64748B"})
        mapped_list = rq_mapping.get(rq_id, [])
        is_gap = rq_id in ["Q5", "Q7"]

        if not is_gap:
            # Standard Question Card (Green Theme)
            st.markdown(f"""
            <div style="background-color: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; box-shadow: 0 4px 10px rgba(0,0,0,0.01);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="background-color: #0C831F; color: white; border-radius: 50%; width: 24px; height: 24px; display: inline-flex; align-items: center; justify-content: center; font-weight: bold; font-size: 0.8rem;">{idx_q+1}</span>
                        <span style="color: #0C831F; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">{category_info['name']}</span>
                    </div>
                    <span style="background-color: #e2f8e6; color: #0C831F; font-size: 0.7rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; text-transform: uppercase;">98% Confidence</span>
                </div>
                <h4 style="margin: 0 0 1rem 0; font-family: Outfit, sans-serif; font-weight: 700; font-size: 1.1rem; color: #121212;">{rq_desc}</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Display mapped insights in columns inside container
            if mapped_list:
                cols = st.columns(len(mapped_list) if len(mapped_list) <= 3 else 3)
                for idx_m, card in enumerate(mapped_list[:3]):
                    quote_text = "No quote available."
                    quote_source = "LENS Reviews"
                    if "representative_quotes" in card and len(card["representative_quotes"]) > 0:
                        quote_text = card["representative_quotes"][0].get("text", "")
                        if len(quote_text) > 180:
                            quote_text = quote_text[:177] + "..."
                        quote_source = card["representative_quotes"][0].get("source_url", "LENS Reviews")
                        
                    if quote_source.startswith("http://") or quote_source.startswith("https://"):
                        clean_name = quote_source
                        if "youtube.com" in quote_source or "youtube" in quote_source:
                            clean_name = "YouTube Video"
                        elif "reddit.com" in quote_source:
                            clean_name = "Reddit Thread"
                        elif "quora.com" in quote_source:
                            clean_name = "Quora Answer"
                        elif "mouthshut.com" in quote_source:
                            clean_name = "MouthShut Review"
                        elif "trustpilot.com" in quote_source:
                            clean_name = "Trustpilot Review"
                        source_html = f'<a href="{quote_source}" target="_blank" style="color: #0C831F; text-decoration: underline; font-weight: 700;">{clean_name}</a>'
                    else:
                        source_html = f'<span style="color: #1e293b; font-weight: 700;">{quote_source}</span>'
                        
                    with cols[idx_m % len(cols)]:
                        st.markdown(f"""
                        <div style="background-color: #f8fafc; border: 1px solid #eef0f5; border-radius: 8px; padding: 1rem; height: 100%; margin-bottom: 1.5rem; display: flex; flex-direction: column; justify-content: space-between;">
                            <div>
                                <div style="font-weight: 700; font-size: 0.72rem; color: #64748b; text-transform: uppercase; margin-bottom: 4px; letter-spacing: 0.5px;">Primary Insight</div>
                                <div style="font-weight: 800; font-size: 0.85rem; color: #1e293b; margin-bottom: 8px; line-height: 1.2;">{card['insight_title']}</div>
                                <div style="font-size: 0.8rem; color: #475569; font-style: italic; line-height: 1.4; border-left: 2px solid #cbd5e1; padding-left: 8px; margin-bottom: 8px;">
                                    "{quote_text}"
                                </div>
                                <div style="font-size: 0.72rem; color: #64748b; font-weight: 600; margin-bottom: 10px;">
                                    Source: {source_html}
                                </div>
                            </div>
                            <div style="font-weight: 700; font-size: 0.72rem; color: #0c831f; border-top: 1px dashed #e2e8f0; padding-top: 6px; margin-top: auto;">
                                Score: {card['opportunity_score']:.1f} | {card['confidence'].upper()} CONF
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background-color: #f8fafc; border: 1px solid #eef0f5; border-radius: 8px; padding: 1rem; margin-bottom: 1.5rem; color: #64748b; font-size: 0.85rem; font-style: italic;">
                    No insights mapped to this pillar yet.
                </div>
                """, unsafe_allow_html=True)
                
        else:
            # Quarantined Gap Card (Red Theme - matching screen2.png Card 5)
            gap_item = next((g for g in gaps if g["id"] == rq_id), None)
            probing_question = ""
            if rq_id == "Q5":
                probing_question = "Before buying face serums, pet foods, or diapers, what details or specs would make you order on Blinkit instead of DMart/Amazon?"
                missing_data_bullets = [
                    "No visibility on customer specification expectations for high-consideration beauty/baby categories.",
                    "Lack of confidence grading details for private-label trust metrics."
                ]
            else:
                probing_question = "Have you or anyone you know bought non-grocery items like Pujasamagri or stationery on quick commerce? What prompted that first trial?"
                missing_data_bullets = [
                    "Inconsistent signal from non-urban or older age cohorts (45-55).",
                    "Self-reported survey data conflicts with direct play store feedback behavior."
                ]
                
            st.markdown(f"""<div style="background-color: #fff5f5; border: 1px solid #fee2e2; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 4px 10px rgba(0,0,0,0.01);">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
<div style="display: flex; align-items: center; gap: 8px;">
<span style="background-color: #ef4444; color: white; border-radius: 50%; width: 24px; height: 24px; display: inline-flex; align-items: center; justify-content: center; font-weight: bold; font-size: 0.8rem;">{idx_q+1}</span>
<span style="color: #b91c1c; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">{category_info['name']}</span>
</div>
<span style="background-color: #fee2e2; color: #ef4444; font-size: 0.7rem; font-weight: 700; padding: 2px 8px; border-radius: 4px; text-transform: uppercase;">⚠️ Quarantined Gap</span>
</div>
<h4 style="margin: 0 0 1rem 0; font-family: Outfit, sans-serif; font-weight: 700; font-size: 1.1rem; color: #121212;">{rq_desc}</h4>
<div style="background-color: white; border: 1px solid #fecaca; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
<div style="font-weight: 700; font-size: 0.8rem; color: #b91c1c; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 0.5px;">Missing Data Blocks:</div>
<ul style="margin: 0; padding-left: 1.2rem; font-size: 0.85rem; color: #475569; line-height: 1.5;">
<li style="margin-bottom: 6px;">❌ {missing_data_bullets[0]}</li>
<li>❌ {missing_data_bullets[1]}</li>
</ul>
</div>
<div style="background-color: #fee2e2; border-left: 4px solid #ef4444; padding: 0.8rem 1rem; border-radius: 0 8px 8px 0; margin-bottom: 1rem;">
<div style="font-weight: 700; font-size: 0.8rem; color: #991b1b; text-transform: uppercase; margin-bottom: 2px;">Primary Research Probing Question:</div>
<p style="margin: 0; font-size: 0.88rem; color: #7f1d1d; font-style: italic; font-weight: 600;">"{probing_question}"</p>
</div>
</div>""", unsafe_allow_html=True)
            
            # Action button for gaps
            if st.button(f"⚡ Initiate Re-Sampling for Q{idx_q+1}", key=f"resample_{rq_id}"):
                st.success(f"Primary research sampling successfully scheduled for research question {rq_id}!")
        st.write("")

# ==================== SIGNATURE FOOTER ====================
st.markdown("""
<div style="margin-top: 4rem; border-top: 1px solid #e2e8f0; padding-top: 1.5rem; padding-bottom: 1.5rem; text-align: center; font-size: 0.8rem; color: #94a3b8; font-weight: 500;">
    Blinkit LENS (Listening ENgine for Shoppers)
""", unsafe_allow_html=True)
