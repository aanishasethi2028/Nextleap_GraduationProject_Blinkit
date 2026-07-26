import os
import json
import pandas as pd
import streamlit as st

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="Blinkit LENS Growth Dashboard",
    page_icon="🛵",
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
    
    /* Premium Blinkit Navigation Header (Web-feel) */
    .premium-header {
        background-color: #ffffff;
        border-bottom: 3px solid #FFE000;
        padding: 1rem 2rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        border-radius: 8px;
    }
    .brand-logo-container {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .blinkit-logo {
        background-color: #0C831F;
        color: #FFE000;
        font-family: 'Outfit', sans-serif;
        font-weight: 900;
        font-size: 2rem;
        padding: 2px 14px;
        border-radius: 6px;
        text-transform: lowercase;
        letter-spacing: -1px;
    }
    .brand-subtitle {
        font-family: 'Outfit', sans-serif;
        font-size: 1.6rem;
        color: #0C831F;
        font-weight: 700;
    }
    .header-tagline {
        font-size: 0.95rem;
        color: #555;
        font-weight: 500;
    }

    /* Core Metrics Card Styling */
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
    .filter-panel {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 10px rgba(0,0,0,0.01);
    }
    .filter-panel-title {
        margin-top: 0;
        margin-bottom: 0.75rem;
        color: #0C831F;
        font-size: 1.15rem;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 0.5rem;
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
    .bias-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin-top: 0.8rem;
        border-top: 1px dashed rgba(140, 118, 0, 0.2);
        padding-top: 0.6rem;
    }
    .bias-stat {
        font-size: 0.85rem;
        color: #594f0e;
    }
    .bias-stat strong {
        color: #0C831F;
    }

    /* Insight Card Styling */
    .insight-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.02);
        border: 1px solid #eef0f5;
        border-left: 6px solid #0C831F;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .insight-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(12, 131, 31, 0.06);
    }
    .insight-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 0.75rem;
        flex-wrap: wrap;
        gap: 0.5rem;
    }
    .insight-title {
        font-size: 1.25rem;
        color: #121212;
        font-weight: 700;
        margin: 0;
    }
    .badge-container {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
        margin-bottom: 0.75rem;
    }
    .badge {
        padding: 0.25rem 0.6rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.2px;
    }
    .badge-theme {
        background-color: #f0fdf4;
        color: #0c831f;
        border: 1px solid #bbf7d0;
    }
    .badge-source {
        background-color: #f8fafc;
        color: #475569;
        border: 1px solid #e2e8f0;
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
    .opp-score {
        font-size: 1.15rem;
        font-weight: 800;
        color: #8c7600;
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
        padding: 0.35rem 0.75rem;
        border-radius: 8px;
        border: 1px solid #fde68a;
    }
    .section-title {
        font-weight: 700;
        font-size: 0.9rem;
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
    .quote-source a:hover {
        color: #085514;
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

    /* Table styling */
    .matrix-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 1rem;
        font-size: 0.85rem;
    }
    .matrix-table th {
        background-color: #0C831F;
        color: white;
        text-align: center;
        padding: 8px;
        border: 1px solid #dddddd;
        font-weight: 600;
    }
    .matrix-table td {
        border: 1px solid #dddddd;
        text-align: center;
        padding: 8px;
    }
    .matrix-table tr:nth-child(even) {
        background-color: #f8fafc;
    }
    .matrix-diag {
        background-color: #e2f8e6 !important;
        font-weight: bold;
        color: #0C831F;
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

# Premium Web Header
st.markdown("""
<div class="premium-header">
    <div class="brand-logo-container">
        <span class="blinkit-logo">blinkit</span>
        <span class="brand-subtitle">LENS — From Habit Loop to New Category</span>
    </div>
    <div class="header-tagline">🎯 An evidence engine for category-adoption growth</div>
</div>
""", unsafe_allow_html=True)

if not insights_data or not val_report:
    st.error("Error: Insights database or validation report not found. Please verify that synthesis and validation scripts have run.")
    st.stop()

# Core Metrics Bar
overall_before = val_report.get("before_audit", {}).get("overall_agreement_pct", 56.0)
overall_after = val_report.get("after_audit", {}).get("overall_agreement_pct", 66.0)
strat_before = val_report.get("before_audit", {}).get("stratified_agreement_pct", 60.0)
strat_after = val_report.get("after_audit", {}).get("stratified_agreement_pct", 80.0)

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.markdown('<div class="metric-card"><div class="metric-val">1,310</div><div class="metric-label">Reviews Analyzed</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="metric-card"><div class="metric-val">92</div><div class="metric-label">Category Trials</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="metric-card"><div class="metric-val">17</div><div class="metric-label">Growth Cards</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="metric-card"><div class="metric-val">42</div><div class="metric-label">Survey Responses</div></div>', unsafe_allow_html=True)
with col5:
    st.markdown(f'<div class="metric-card"><div class="metric-val">{overall_after:.1f}%</div><div class="metric-label">Audit Agreement</div></div>', unsafe_allow_html=True)

st.write("")

# Navigation Tabs
tab_insights, tab_validation, tab_routing = st.tabs([
    "🛵 Discovered Growth Insights",
    "📊 Validation & Method Quality",
    "🗺️ Research Questions Answer Map"
])

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
        return source_str # already is a link
    elif "mouthshut" in source_lower:
        return "https://www.mouthshut.com/product-reviews/Blinkit-reviews-925763914"
    elif "trustpilot" in source_lower:
        return "https://www.trustpilot.com/review/blinkit.com"
    elif "reddit" in source_lower:
        return "https://www.reddit.com/r/india/"
    elif source_str.startswith("http"):
        return source_str
    return "https://blinkit.com"

# ==================== TAB 1: GROWTH INSIGHTS ====================
with tab_insights:
    # Mappings for layman-friendly display
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

    # 🎛️ Layman-Friendly Selectbox Filters (No Tag Chip Clutter)
    all_themes = sorted(list(set(insight["primary_theme"] for insight in insights_data["insights"])))
    all_rqs = sorted(list(set(rq for insight in insights_data["insights"] for rq in insight["answers_questions"])))
    all_sources = sorted(list(set(src for insight in insights_data["insights"] for src in insight["triangulated_sources"])))
    
    help_text = """
    💡 **LENS Prioritization & Triangulation Guide**
    
    - **Opportunity Score**: Prioritizes growth impact: Log(Frequency) * Severity * Addressability * Strategic Fit. Higher scores represent higher priority opportunities.
    - **Confidence Level**:
      - **HIGH**: Validated by both customer reviews and the user survey (n=42).
      - **LOW**: Found only in customer reviews (requires survey validation).
    - **Research Questions (Q1-Q8)**:
      - **Q1**: What prompts the very first quick-commerce order?
      - **Q2**: How do users transition from emergency to routine replenishment?
      - **Q3**: What categories do users explicitly resist buying on quick commerce?
      - **Q4**: Fresh grocery vs packaged goods trust?
      - **Q5**: Info needed before trying new category? (Quarantined Gap)
      - **Q6**: UI friction during exploration?
      - **Q7**: Target segments likely to experiment? (Quarantined Gap)
      - **Q8**: Emotional role in daily habit loops?
    """
    st.subheader("🔍 Segment & Filter Findings", help=help_text)
    
    with st.form("filter_form"):
        col_f1, col_f2, col_f3, col_f4, col_btn = st.columns([2.5, 2.5, 2.5, 2.5, 1.5])
        with col_f1:
            theme_options = ["All Themes"] + [theme_labels.get(t, t.replace("_", " ").title()) for t in all_themes]
            selected_theme_label = st.selectbox("Select Theme", theme_options)
            
        with col_f2:
            rq_options = ["All Research Questions"] + [rq_labels.get(r, r) for r in all_rqs]
            selected_rq_label = st.selectbox("Select Research Question", rq_options)
            
        with col_f3:
            selected_conf = st.selectbox("Select Confidence Level", ["All Confidences", "HIGH", "MEDIUM", "LOW"])
            
        with col_f4:
            selected_source = st.selectbox("Select Triangulated Source", ["All Sources"] + all_sources)
            
        with col_btn:
            st.markdown('<div style="height: 28px;"></div>', unsafe_allow_html=True)
            apply_filters = st.form_submit_button("⚡ Apply Filters")

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
        # Theme check
        if selected_theme != "All Themes" and insight["primary_theme"] != selected_theme:
            continue
        # Confidence check
        if selected_conf != "All Confidences" and insight["confidence"].upper() != selected_conf:
            continue
        # RQ check
        if selected_rq != "All Research Questions" and selected_rq not in insight["answers_questions"]:
            continue
        # Triangulation Source check
        if selected_source != "All Sources" and selected_source not in insight["triangulated_sources"]:
            continue
        filtered_insights.append(insight)

    # 1. FACT-FOCUSED BIAS DISCLOSURE
    biases = val_report.get("biases", {})
    source_skew = biases.get("source_skew_appstore_pct", 75.3)
    polarized_five = biases.get("rating_polarization_5_star", 777)
    polarized_one = biases.get("rating_polarization_1_star", 178)
    missing_ratings = biases.get("missing_ratings_pct", 21.1)
    
    st.markdown(f"""
    <div class="bias-disclosure">
        <div class="bias-title">⚠️ Data Bias Warning & Structural Parameters</div>
        <p class="bias-text">
            Feedback is collected only from active app users (survivorship bias) and is heavily skewed towards Play Store & App Store reviews.
        </p>
        <div class="bias-grid">
            <div class="bias-stat">📢 <strong>Source Skew:</strong> App Stores account for <strong>{source_skew:.1f}%</strong> of feedback.</div>
            <div class="bias-stat">⭐ <strong>Polarization:</strong> High star rating polarization (<strong>{polarized_five}</strong> 5-Star vs <strong>{polarized_one}</strong> 1-Star).</div>
            <div class="bias-stat">📝 <strong>Ratings completeness:</strong> <strong>{missing_ratings:.1f}%</strong> of feedback (e.g. YouTube) lacks star ratings.</div>
            <div class="bias-stat">👥 <strong>Survivorship bias:</strong> Excludes users who already uninstalled the app.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Render Insight cards
    st.markdown("### 📊 Discovered Growth Opportunity Cards")
    if not filtered_insights:
        st.info("No insights match the current filter selection.")
    else:
        for idx, insight in enumerate(filtered_insights):
            conf_class = f"badge-conf-{insight['confidence']}"
            theme_name = theme_labels.get(insight["primary_theme"], insight["primary_theme"].replace("_", " ").title())
            
            # Format badges
            sources_html = "".join(f'<span class="badge badge-source">{src}</span>' for src in insight["triangulated_sources"])
            
            # Render card header
            st.markdown(f"""
            <div class="insight-card">
                <div class="insight-header">
                    <div class="insight-title">{insight['insight_title']}</div>
                    <div class="opp-score">Opportunity Score: {insight['opportunity_score']:.2f}</div>
                </div>
                <div class="badge-container">
                    <span class="badge badge-theme">{theme_name}</span>
                    <span class="badge {conf_class}">{insight['confidence'].upper()} Confidence</span>
                    {sources_html}
                </div>
                <div class="section-title">Core Research Findings</div>
                <div style="font-size: 0.95rem; color: #334155; line-height: 1.5; margin-bottom: 0.8rem;">{insight['finding']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Use Streamlit expander for collapsible rich details
            with st.expander("🛵 View Actionable Growth Strategy, Quotes & Validation Hooks"):
                st.markdown(f"**Growth Strategy (So What?):** {insight['so_what_for_growth']}")
                st.write("")
                
                st.markdown("**Affected Customer Segments:**")
                for seg in insight["affected_segments"]:
                    st.markdown(f"- {seg}")
                    
                st.write("")
                st.markdown("**Representative User Quotes:**")
                for quote in insight["representative_quotes"]:
                    # Create clean clickable link using source url mapping
                    raw_src = quote["source_url"]
                    target_url = get_source_url(raw_src)
                    
                    if raw_src.startswith("http"):
                        link_label = "View Direct Social Post"
                    else:
                        link_label = f"View {raw_src} Page"
                    
                    st.markdown(f"""
                    <div class="quote-box">
                        "{quote['text']}"
                        <div class="quote-source">— Source Channel: <a href="{target_url}" target="_blank">{link_label}</a></div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.write("")
                # Render validation hook
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
            st.write("---")

# ==================== TAB 2: VALIDATION & METHOD AUDIT ====================
with tab_validation:
    st.markdown("### 📊 LENS Method Verification & Alignment Audit")
    
    st.markdown(f"""
    Following the LENS roadmap guidelines, we established a robust verification layer to validate LLM classification quality. 
    Since the initial classification agreement score on the 50-item audit sample was **{overall_before:.1f}%**, we executed an 
    **improvement loop** by diagnosing boundaries using the confusion table, sharpening the theme prompt definitions, 
    upgrading to the high-nuance model (`llama-3.3-70b-versatile`), and re-auditing the sample.
    """)
    
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown(f"""
        <div class="metric-card" style="border-left: 5px solid #ffb020;">
            <div class="metric-val" style="color: #b27b00;">{overall_before:.1f}%</div>
            <div class="metric-label">Initial Audit Agreement (Llama 8B)</div>
            <p style="font-size: 0.8rem; color: #888; margin-top: 0.5rem;">Unbiased random draw: {val_report.get('before_audit', {}).get('random_agreement_pct', 54.3):.1f}% | Stratified draw: {val_report.get('before_audit', {}).get('stratified_agreement_pct', 60.0):.1f}%</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_r:
        st.markdown(f"""
        <div class="metric-card" style="border-left: 5px solid #0C831F; background: #f0fdf4;">
            <div class="metric-val">{overall_after:.1f}%</div>
            <div class="metric-label">Sharpened Audit Agreement (Llama 70B Upgrade)</div>
            <p style="font-size: 0.8rem; color: #555; margin-top: 0.5rem;">Unbiased random draw: {val_report.get('after_audit', {}).get('random_agreement_pct', 57.1):.1f}% | Stratified draw: {val_report.get('after_audit', {}).get('stratified_agreement_pct', 66.7):.1f}%</p>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    
    # Render Confusion Matrices side by side in expander
    with st.expander("🗺️ View 11x11 Classification Confusion Matrix (Documented Improvement Loop)"):
        st.markdown("#### Initial Classification Confusion Matrix (Llama 3.1 8B)")
        st.markdown("Rows represent **Expert Auditor** (Ground Truth), Columns represent **Original LLM**:")
        
        c_matrix_before = val_report.get("confusion_matrix", {})
        themes_list = ["Habit Loop", "Awareness Gap", "Mental Model", "Trust Quality", "Trust Information", "Price Value", "UX Friction", "Assortment Gap", "Delivery Ops", "Emotional", "Other"]
        
        # Map capitalized name to lowercase database keys
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

        # Build HTML table for before
        table_html = '<table class="matrix-table"><tr><th>Expert / LLM</th>' + "".join(f"<th>{t[:8]}</th>" for t in themes_list) + "</tr>"
        for expert in themes_list:
            table_html += f"<tr><td><strong>{expert}</strong></td>"
            for col in themes_list:
                expert_key = label_to_key.get(expert, expert.lower())
                col_key = label_to_key.get(col, col.lower())
                val = c_matrix_before.get(expert_key, {}).get(col_key, 0)
                diag_class = ' class="matrix-diag"' if col == expert else ''
                table_html += f"<td{diag_class}>{val}</td>"
            table_html += "</tr>"
        table_html += "</table>"
        st.markdown(table_html, unsafe_allow_html=True)
        
        st.write("")
        st.write("")
        
        st.markdown("#### Sharpened Classification Confusion Matrix (Llama 3.3 70B)")
        st.markdown("Rows represent **Expert Auditor** (Ground Truth), Columns represent **Sharpened Classifier**:")
        
        c_matrix_after = val_report.get("confusion_matrix_after", {})
        table_html_after = '<table class="matrix-table"><tr><th>Expert / LLM</th>' + "".join(f"<th>{t[:8]}</th>" for t in themes_list) + "</tr>"
        for expert in themes_list:
            table_html_after += f"<tr><td><strong>{expert}</strong></td>"
            for col in themes_list:
                expert_key = label_to_key.get(expert, expert.lower())
                col_key = label_to_key.get(col, col.lower())
                val = c_matrix_after.get(expert_key, {}).get(col_key, 0)
                diag_class = ' class="matrix-diag"' if col == expert else ''
                table_html_after += f"<td{diag_class}>{val}</td>"
            table_html_after += "</tr>"
        table_html_after += "</table>"
        st.markdown(table_html_after, unsafe_allow_html=True)

    # Triangulation Matrix
    with st.expander("📐 View Triangulation Matrix (LENS Reviews vs Survey)"):
        st.markdown("This matrix shows which LENS insights are backed by which research lenses to calibrate confidence levels:")
        
        tri_records = []
        for card in insights_data["insights"]:
            tri_records.append({
                "Insight Title": card["insight_title"],
                "LENS Reviews": "✅" if "LENS Reviews" in card["triangulated_sources"] else "❌",
                "n=42 Survey": "✅" if "n=42 Survey" in card["triangulated_sources"] else "❌",
                "Confidence": card["confidence"].upper()
            })
            
        df_tri = pd.DataFrame(tri_records)
        st.dataframe(df_tri, use_container_width=True)

# ==================== TAB 3: RQ MAP & GAPS ====================
with tab_routing:
    st.markdown("### 🗺️ Core Research Questions Alignment Map")
    st.write("Below is the alignment mapping between the 8 Core Research Questions and the discovered LENS insights, including quarantined gaps.")
    
    # Dictionary mapping Q1-Q8 to text
    rq_text = {
        "Q1": "Q1: What prompts the very first quick-commerce order in a household?",
        "Q2": "Q2: How do users transition from emergency top-ups to routine basket ordering?",
        "Q3": "Q3: What categories do users explicitly resist buying on quick commerce?",
        "Q4": "Q4: How does user trust differ between fresh groceries and packaged goods?",
        "Q5": "Q5: What information (reviews, specifications) do users need before trying a new category?",
        "Q6": "Q6: What app interface elements cause friction during category exploration?",
        "Q7": "Q7: Which user segments are more likely to experiment with non-grocery categories?",
        "Q8": "Q8: What is the emotional role of quick commerce in the user's daily habit loop?"
    }

    # Map insights to RQs
    rq_mapping = {rq: [] for rq in rq_text.keys()}
    for card in insights_data["insights"]:
        for rq in card["answers_questions"]:
            if rq in rq_mapping:
                rq_mapping[rq].append(card["insight_title"])

    # Load gaps from insights.json
    gaps = insights_data.get("gaps", [])

    for rq_id, rq_desc in rq_text.items():
        st.markdown(f"#### ❓ {rq_desc}")
        
        # Check if mapped to any insights
        mapped_insights = rq_mapping[rq_id]
        if mapped_insights:
            for mi in mapped_insights:
                st.markdown(f"- ✅ **Insight Card**: {mi}")
        else:
            # Check if it is a quarantined gap
            gap_item = next((g for g in gaps if g["id"] == rq_id), None)
            if gap_item:
                probing_question = ""
                if rq_id == "Q5":
                    probing_question = "'Before buying face serums, pet foods, or diapers, what details or specs would make you order on Blinkit instead of DMart/Amazon?'"
                elif rq_id == "Q7":
                    probing_question = "'Have you or anyone you know bought non-grocery items like Pujasamagri or stationery on quick commerce? What prompted that first trial?'"
                    
                st.markdown(f"""
                <div style="background-color: #fef2f2; border-left: 4px solid #ef4444; padding: 0.8rem 1rem; border-radius: 4px; margin-bottom: 0.5rem;">
                    <strong style="color: #991b1b;">⚠️ Quarantined Gap:</strong> {gap_item['description']}<br/>
                    <span style="color: #7f1d1d; font-size: 0.9rem;">Routed to Primary Research Probing Question: <strong>{probing_question}</strong></span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("- ❌ *No insights or gaps mapped.*")
        st.write("")