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
# CUSTOM STYLING (ROSE THEME)
# =============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Archivo+Black&family=DM+Sans:wght@400;500;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #fff5f5 0%, #ffe4e6 50%, #fecdd3 100%) !important;
    }
    
    h1 {
        font-family: 'Archivo Black', sans-serif !important;
        background: linear-gradient(90deg, #be185d, #e11d48, #f43f5e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem !important;
        letter-spacing: -2px;
    }
    
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
        color: #be123c;
        line-height: 1;
    }
    
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
</style>
""", unsafe_allow_html=True)

# =============================================================================
# CONSTANTS & LOGIC
# =============================================================================
THE_4_LAWS = """
## THE 4 LAWS OF INTEGRITY
1. **PROMINENCE** (-20 pts): Hero ingredient must be in top 5.
2. **DEFINITION** (-15 pts): No unproven buzzwords (Natural, AI, Premium).
3. **SUBSTITUTION** (-30 pts): No cheap fillers in premium products.
4. **FINE PRINT** (-40 pts): No contradictions between claims and specs.

SCORING: 80-100 (Green), 50-79 (Orange), 0-49 (Red).
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
# MAIN UI
# =============================================================================

# HEADER
st.markdown("# 🔍 INTEGRITY PROTOCOL")

# LOCATION SELECTOR
col_loc1, col_loc2 = st.columns([1, 2])
with col_loc1:
    st.markdown("**📍 Region:**")
with col_loc2:
    selected_location = st.selectbox(
        "Region", 
        ["Australia", "United States", "United Kingdom", "Canada", "Europe", "Asia"], 
        index=0, 
        label_visibility="collapsed"
    )

st.markdown("---")

# --- INPUT SECTION (Tabs for Camera OR Upload) ---
tab_cam, tab_upload = st.tabs(["📸 Camera", "📁 Upload from PC"])

final_images_to_scan = []

# TAB 1: CAMERA
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

# TAB 2: UPLOAD
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
                
                # DISPLAY RESULTS
                st.markdown("---")
                st.markdown(f"### 📦 {result.get('product_type', 'Product')} detected")
                
                # Score Card
                score = result.get('score', 0)
                color = "#15803d" if score >= 80 else "#c2410c" if score >= 50 else "#be123c"
                
                st.markdown(f"""
                <div class="score-card" style="border-color: {color};">
                    <div style="color: {color}; font-weight: bold; letter-spacing: 2px;">INTEGRITY SCORE</div>
                    <div class="score-value" style="color: {color};">{score}</div>
                    <div style="background: {color}20; color: {color}; display: inline-block; 
                         padding: 5px 15px; border-radius: 20px; font-weight: bold;">
                        {result.get('verdict', 'Analyzed')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Summary
                st.info(f"📝 {result.get('honesty_summary')}")
                
                # Deductions
                if result.get('deductions'):
                    st.markdown("### ⚠️ Violations")
                    for d in result['deductions']:
                        st.markdown(f"**-{d['points']} pts: {d['law']}**")
                        st.caption(d['reason'])
                        
                # Alternative
                alt = result.get('better_alternative')
                if alt:
                    st.success(f"**💡 Try: {alt.get('product_name')}**\n\n{alt.get('why_more_honest')}")

            except Exception as e:
                st.error(f"Analysis failed: {e}")
                st.info("Tip: If you see '429 Quota Exceeded', please change your API Key.")
else:
    st.info("👆 Please take a photo or upload a file to start.")

# Footer
st.markdown("---")
st.markdown("<center style='color: #be185d;'>HonestWorld • Measuring Honesty, Not Health</center>", unsafe_allow_html=True)