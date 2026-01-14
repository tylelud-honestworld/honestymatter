"""
🔍 THE INTEGRITY PROTOCOL
A Consumer Protection App That Measures Honesty, Not Health

This app calculates a scientific "Integrity Score" (0-100) by measuring
the mathematical gap between Marketing Claims (Front) and Empirical Reality (Back/Ingredients).

Author: Senior Python Full-Stack Developer
Framework: Streamlit + Google Gemini 1.5 Flash (High Efficiency)
"""

import streamlit as st
import google.generativeai as genai
import json
import re
import pandas as pd
from PIL import Image
import requests
import time

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="The Integrity Protocol",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# SECURITY & API SETUP
# =============================================================================
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    else:
        st.error("Error: Could not find API Key in Secrets. Please add GEMINI_API_KEY.")
except Exception as e:
    st.error(f"Security Error: {e}")

# Use 1.5 Flash for higher daily limits (1,500 scans/day)
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash", 
    generation_config={
        "temperature": 0.0,
        "top_p": 1,
        "top_k": 1,
    }
)

# =============================================================================
# CUSTOM STYLING (YOUR ORIGINAL ROSE THEME RESTORED)
# =============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Archivo+Black&family=DM+Sans:wght@400;500;700&display=swap');
    
    /* Main container styling */
    .stApp {
        background: linear-gradient(135deg, #fff5f5 0%, #ffe4e6 50%, #fecdd3 100%) !important;
    }
    
    /* Headers */
    h1 {
        font-family: 'Archivo Black', sans-serif !important;
        background: linear-gradient(90deg, #be185d, #e11d48, #f43f5e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem !important;
        letter-spacing: -2px;
    }
    
    h2, h3 {
        font-family: 'Space Mono', monospace !important;
        color: #881337 !important;
    }
    
    /* General Text */
    p, span, label, .stMarkdown {
        color: #4a044e !important;
        font-family: 'DM Sans', sans-serif !important;
    }

    /* Score Card */
    .score-card {
        background: linear-gradient(145deg, #ffffff, #fff1f2);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 40px rgba(225, 29, 72, 0.15);
        border: 2px solid #fda4af;
        text-align: center;
        margin: 1rem 0;
    }
    
    .score-value {
        font-family: 'Archivo Black', sans-serif;
        font-size: 5rem;
        font-weight: 900;
        line-height: 1;
        margin: 0.5rem 0;
    }
    
    .score-green { color: #15803d; }
    .score-orange { color: #c2410c; }
    .score-red { color: #be123c; }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #be185d, #e11d48) !important;
        color: white !important;
        font-family: 'Space Mono', monospace !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 15px !important;
        padding: 1rem !important;
        width: 100%;
        box-shadow: 0 4px 15px rgba(225, 29, 72, 0.3) !important;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: rgba(255,255,255,0.5);
        padding: 10px;
        border-radius: 15px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        border-radius: 10px;
        background-color: white;
        border: 1px solid #fda4af;
        color: #881337;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #be185d !important;
        color: white !important;
    }

    /* Deduction Cards */
    .deduction-card {
        background: rgba(254, 205, 211, 0.5);
        border-left: 4px solid #e11d48;
        padding: 1rem 1.5rem;
        margin: 0.5rem 0;
        border-radius: 0 10px 10px 0;
        font-family: 'DM Sans', sans-serif;
        color: #881337 !important;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# CONSTANTS & LOGIC (YOUR ORIGINAL 4 LAWS)
# =============================================================================
THE_4_LAWS = """
## THE 4 LAWS OF INTEGRITY (Scoring Algorithm)

You are an INTEGRITY AUDITOR. Your job is NOT to judge if a product is good quality.
Your job is to measure HONESTY - the gap between Marketing Claims and Reality.

1. **PROMINENCE** (-20 pts): Hero ingredient must be in top 5.
2. **DEFINITION** (-15 pts): No unproven buzzwords (Natural, AI, Premium).
3. **SUBSTITUTION** (-30 pts): No cheap fillers in premium products.
4. **FINE PRINT** (-40 pts): No contradictions between claims and specs.

SCORING: 80-100 (Green/Honest), 50-79 (Orange/Suspicious), 0-49 (Red/Deceptive).
"""

GEMINI_PROMPT_TEMPLATE = """
{laws}
TASK: Analyze product images for HONESTY.
USER LOCATION: {location}

OUTPUT JSON ONLY:
{{
    "product_type": "Category",
    "product_name": "Name",
    "score": 0-100,
    "verdict": "Verdict",
    "marketing_claims": ["Claim 1"],
    "deductions": [{{"law": "Law Name", "points": -10, "reason": "Reason"}}],
    "better_alternative": {{
        "product_name": "Product Name in {location}",
        "why_more_honest": "Reason"
    }},
    "honesty_summary": "Summary"
}}
"""

def parse_ai_response(text):
    try:
        text = re.sub(r'```json|```', '', text).strip()
        return json.loads(text)
    except:
        return {"score": 0, "verdict": "Error", "honesty_summary": "Error parsing JSON."}

def analyze_product(images, location):
    pil_images = []
    for img in images:
        if img is not None:
            img.seek(0)
            pil_images.append(Image.open(img))
    
    prompt = GEMINI_PROMPT_TEMPLATE.format(laws=THE_4_LAWS, location=location)
    content = [prompt] + pil_images
    response = model.generate_content(content)
    return parse_ai_response(response.text)

# =============================================================================
# SIDEBAR (YOUR ORIGINAL SIDEBAR)
# =============================================================================
with st.sidebar:
    st.markdown("## 📍 Location Settings")
    
    # Default to Australia as requested
    selected_location = st.selectbox(
        "Select Region:",
        options=["Australia", "United States", "United Kingdom", "Canada", "Europe", "Asia", "Global"],
        index=0
    )
    
    st.markdown("---")
    
    with st.expander("📖 The 4 Laws of Integrity"):
        st.markdown("**1. Prominence:** No Fairy Dusting (-20)")
        st.markdown("**2. Definition:** No Buzzwords (-15)")
        st.markdown("**3. Substitution:** No Cheap Fillers (-30)")
        st.markdown("**4. Fine Print:** No Asterisks (-40)")
    
    st.markdown("---")
    st.markdown("<center style='color:#9f1239'>HonestWorld<br>v1.0.0</center>", unsafe_allow_html=True)

# =============================================================================
# MAIN UI
# =============================================================================

# HEADER
st.markdown("# 🔍 THE INTEGRITY PROTOCOL")
st.markdown("""
<p style="font-family: 'DM Sans', sans-serif; color: #9f1239; font-size: 1.1rem; margin-bottom: 2rem;">
    Measuring the gap between <strong style="color: #be185d;">Marketing Claims</strong> and 
    <strong style="color: #e11d48;">Empirical Reality</strong>
</p>
""", unsafe_allow_html=True)

# --- INPUT SECTION (Tabs for Camera OR Upload) ---
tab_cam, tab_upload = st.tabs(["📸 Camera", "📁 Upload from PC"])

final_images_to_scan = []

# TAB 1: CAMERA (Fixed: No Pop-ups)
with tab_cam:
    if 'captured_images' not in st.session_state:
        st.session_state.captured_images = []
    
    # Show Gallery
    if st.session_state.captured_images:
        st.markdown(f"**Photos Taken ({len(st.session_state.captured_images)}/3):**")
        cols = st.columns(3)
        for i, img in enumerate(st.session_state.captured_images):
            with cols[i]:
                st.image(img, use_container_width=True)
    
    # Camera Input
    if len(st.session_state.captured_images) < 3:
        # Dynamic key ensures camera resets
        cam_key = f"cam_{len(st.session_state.captured_images)}"
        photo = st.camera_input("Take Photo", key=cam_key, label_visibility="collapsed")
        if photo:
            st.session_state.captured_images.append(photo)
            st.rerun()
    
    # Controls
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🗑️ Clear Camera"):
            st.session_state.captured_images = []
            st.rerun()
            
    # Add camera images to final list
    if st.session_state.captured_images:
        final_images_to_scan.extend(st.session_state.captured_images)

# TAB 2: UPLOAD (Restored!)
with tab_upload:
    st.markdown("**Upload existing photos (JPG, PNG, WEBP)**")
    uploaded_files = st.file_uploader(
        "Choose files", 
        type=['png', 'jpg', 'jpeg', 'webp'], 
        accept_multiple_files=True,
        label_visibility="collapsed"
    )
    
    if uploaded_files:
        st.markdown(f"**✅ {len(uploaded_files)} Files Uploaded**")
        final_images_to_scan.extend(uploaded_files)

# --- ANALYSIS SECTION ---
st.markdown("---")
if len(final_images_to_scan) > 0:
    if st.button("🚀 SCAN FOR HONESTY"):
        with st.spinner(f"🔍 Analyzing {len(final_images_to_scan)} images in {selected_location}..."):
            try:
                # RUN ANALYSIS
                result = analyze_product(final_images_to_scan, selected_location)
                
                # DISPLAY RESULTS (Original Layout)
                st.markdown("---")
                st.markdown(f"### 📦 {result.get('product_type', 'Product')} detected")
                
                # Score Card
                score = result.get('score', 0)
                if score >= 80: color = "score-green"
                elif score >= 50: color = "score-orange"
                else: color = "score-red"
                
                st.markdown(f"""
                <div class="score-card">
                    <div class="score-label">Integrity Score</div>
                    <div class="score-value {color}">{score}</div>
                    <div style="font-weight: bold; font-size: 1.2rem;">
                        {result.get('verdict', 'Analyzed')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Summary
                st.info(f"📝 {result.get('honesty_summary')}")
                
                # Deductions
                if result.get('deductions'):
                    st.markdown("### ⚠️ Violations Found")
                    for d in result['deductions']:
                        st.markdown(f"""
                        <div class="deduction-card">
                            <strong style="color:#be123c">-{d['points']} pts: {d['law']}</strong><br>
                            {d['reason']}
                        </div>
                        """, unsafe_allow_html=True)
                        
                # Alternative
                alt = result.get('better_alternative')
                if alt:
                    st.markdown("---")
                    st.success(f"**💡 Honest Alternative: {alt.get('product_name')}**\n\n{alt.get('why_more_honest')}")

            except Exception as e:
                st.error(f"Analysis failed: {e}")
                st.info("Tip: If you see '429 Quota Exceeded', your API key has hit the daily limit.")
else:
    st.info("👆 Please take a photo or upload a file to start.")

# Footer
st.markdown("---")
st.markdown("<center style='color: #be185d;'>HonestWorld • Measuring Honesty, Not Health</center>", unsafe_allow_html=True)