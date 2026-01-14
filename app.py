"""
🔍 THE INTEGRITY PROTOCOL
A Consumer Protection App That Measures Honesty, Not Health

This app calculates a scientific "Integrity Score" (0-100) by measuring
the mathematical gap between Marketing Claims (Front) and Empirical Reality (Back/Ingredients).

Author: Senior Python Full-Stack Developer
Framework: Streamlit + Google Gemini 2.0 Flash
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
    initial_sidebar_state="collapsed"
)

# =============================================================================
# 1. SECURITY & API SETUP
# =============================================================================
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    else:
        st.error("⚠️ API Key missing! Please add GEMINI_API_KEY to Streamlit Secrets.")
except Exception as e:
    st.error(f"⚠️ Security Error: {e}")

# Initialize Model (Gemini 2.0 Flash)
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash", 
    generation_config={
        "temperature": 0.0,
        "top_p": 1,
        "top_k": 1,
    }
)

# =============================================================================
# 2. CUSTOM STYLING (YOUR ORIGINAL ROSE THEME)
# =============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Archivo+Black&family=DM+Sans:wght@400;500;700&display=swap');
    
    /* Main container styling - ROSE/LIGHT THEME */
    .stApp {
        background: linear-gradient(135deg, #fff5f5 0%, #ffe4e6 50%, #fecdd3 100%) !important;
    }
    
    .main .block-container {
        background: transparent !important;
    }
    
    /* Mobile-Friendly Headers */
    h1 {
        font-family: 'Archivo Black', sans-serif !important;
        background: linear-gradient(90deg, #be185d, #e11d48, #f43f5e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.2rem !important;
        letter-spacing: -1px;
        line-height: 1.1;
    }
    
    h2, h3 {
        font-family: 'Space Mono', monospace !important;
        color: #881337 !important;
    }
    
    /* General text */
    p, span, label, .stMarkdown {
        color: #4a044e !important;
        font-family: 'DM Sans', sans-serif !important;
    }
    
    /* Custom metric card */
    .score-card {
        background: linear-gradient(145deg, #ffffff, #fff1f2);
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 10px 40px rgba(225, 29, 72, 0.15);
        border: 2px solid #fda4af;
        text-align: center;
        margin: 1rem 0;
    }
    
    .score-value {
        font-family: 'Archivo Black', sans-serif;
        font-size: 4.5rem;
        font-weight: 900;
        line-height: 1;
        margin: 0.5rem 0;
    }
    
    .score-label {
        font-family: 'Space Mono', monospace;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 3px;
        color: #9f1239;
    }
    
    /* Traffic light colors */
    .score-green { color: #15803d; }
    .score-orange { color: #c2410c; }
    .score-red { color: #be123c; }
    
    /* BIG TAPPABLE BUTTONS FOR MOBILE */
    .stButton > button {
        background: linear-gradient(90deg, #be185d, #e11d48) !important;
        color: white !important;
        font-family: 'Space Mono', monospace !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 15px !important;
        padding: 1rem 1rem !important; /* Larger touch area */
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        box-shadow: 0 4px 15px rgba(225, 29, 72, 0.3) !important;
        width: 100%;
    }
    
    /* Secondary buttons (Clear/Reset) */
    div[data-testid="column"] button {
        background: white !important;
        color: #be185d !important;
        border: 1px solid #be185d !important;
    }
    
    /* Camera Input Styling */
    div[data-testid="stCameraInput"] {
        border: 2px dashed #fda4af;
        border-radius: 15px;
        background: rgba(255,255,255,0.5);
    }

    /* Location Box */
    .location-box {
        background: rgba(255,255,255,0.7);
        padding: 10px;
        border-radius: 10px;
        border: 1px solid #f9a8d4;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# 3. LOCATION INTELLIGENCE (Fixed)
# =============================================================================
def get_user_location_smart():
    """
    1. Tries to get real IP from Cloud Headers (X-Forwarded-For).
    2. Fallback to 'International'.
    """
    try:
        from streamlit.web.server.websocket_headers import _get_websocket_headers
        headers = _get_websocket_headers()
        user_ip = headers.get("X-Forwarded-For")
        if user_ip:
            ip = user_ip.split(",")[0]
            response = requests.get(f'https://ipapi.co/{ip}/json/', timeout=2)
            if response.status_code == 200:
                data = response.json()
                return f"{data.get('city')}, {data.get('country_name')}"
    except:
        pass
    return "Detecting..." 

# Initialize Location in Session State
if 'user_loc_str' not in st.session_state:
    st.session_state.user_loc_str = get_user_location_smart()

# =============================================================================
# 4. CORE LOGIC (YOUR ORIGINAL 4 LAWS)
# =============================================================================
THE_4_LAWS = """
## THE 4 LAWS OF INTEGRITY (Scoring Algorithm)

You are an INTEGRITY AUDITOR. Your job is NOT to judge if a product is good quality.
Your job is to measure HONESTY - the gap between Claims and Reality.

1. LAW OF PROMINENCE ("Fairy Dusting") [-20 pts]: Hero ingredient not in top 5.
2. LAW OF DEFINITION ("Buzzwords") [-15 pts]: "Premium", "AI", "Natural" without proof.
3. LAW OF SUBSTITUTION ("Cheap Reality") [-30 pts]: Premium claims, cheap ingredients.
4. LAW OF FINE PRINT ("The Asterisk") [-40 pts]: Claims contradicted by fine print.

SCORING: 80-100 (Green/Honest), 50-79 (Orange/Suspicious), 0-49 (Red/Deceptive).
"""

GEMINI_PROMPT_TEMPLATE = """
{laws}

## YOUR TASK:
Analyze these product image(s) and calculate the INTEGRITY SCORE.
USER LOCATION: {location}

## FINDING HONEST ALTERNATIVES:
Suggest a specific product that:
- Is available in {location}
- Has HONEST marketing
- Include BRAND NAME and PRODUCT NAME

## STRICT OUTPUT FORMAT (JSON ONLY):
{{
    "product_type": "Category",
    "product_name": "Name",
    "score": 0-100,
    "verdict": "Verdict string",
    "marketing_claims": ["Claim 1", "Claim 2"],
    "deductions": [
        {{
            "law": "Law Name",
            "reason": "Explanation",
            "points": -10
        }}
    ],
    "product_analysis": {{
        "main_components": ["Component 1", "Component 2"],
        "hero_feature_position": "Position or N/A",
        "cheap_filler_detected": "Filler Name or None"
    }},
    "better_alternative": {{
        "product_name": "Specific Product",
        "why_more_honest": "Explanation",
        "estimated_score": 95
    }},
    "honesty_summary": "Summary text"
}}
"""

def parse_ai_response(text):
    try:
        text = re.sub(r'```json|```', '', text).strip()
        return json.loads(text)
    except:
        return {"score": 0, "verdict": "Error", "honesty_summary": "Could not parse JSON."}

def analyze_product(images, location):
    pil_images = []
    for img in images:
        img.seek(0)
        pil_images.append(Image.open(img))
    
    prompt = GEMINI_PROMPT_TEMPLATE.format(laws=THE_4_LAWS, location=location)
    content = [prompt] + pil_images
    response = model.generate_content(content)
    return parse_ai_response(response.text)

# =============================================================================
# 5. MAIN APP UI
# =============================================================================

# HEADER
st.markdown("# 🔍 THE INTEGRITY PROTOCOL")

# --- LOCATION FIX ---
# We show a manual selector that DEFAULTS to "Australia" if detection fails or is generic
region_options = ["Australia", "United States", "United Kingdom", "Canada", "Europe", "Asia", "Global"]
default_index = 0  # Default to Australia (Index 0)

# If we detected something specific (like "Prague"), we can try to use it, 
# otherwise we default to the dropdown.
st.markdown('<div class="location-box">', unsafe_allow_html=True)
col_l1, col_l2 = st.columns([1, 2])
with col_l1:
    st.markdown("**📍 Your Region:**")
with col_l2:
    selected_location = st.selectbox(
        "Region", 
        region_options, 
        index=default_index, 
        label_visibility="collapsed"
    )
st.markdown("</div>", unsafe_allow_html=True)

# --- CAMERA LOGIC (FIXED: No Pop-ups) ---
if 'captured_images' not in st.session_state:
    st.session_state.captured_images = []
if 'camera_active' not in st.session_state:
    st.session_state.camera_active = True

# 1. SHOW CAPTURED PHOTOS
if st.session_state.captured_images:
    st.markdown(f"**📸 Photos Ready ({len(st.session_state.captured_images)}/3)**")
    cols = st.columns(3)
    for i, img in enumerate(st.session_state.captured_images):
        with cols[i]:
            st.image(img, use_container_width=True)

# 2. CAMERA INTERFACE
if st.session_state.camera_active and len(st.session_state.captured_images) < 3:
    st.markdown("### 📷 Take a Photo")
    # Using a dynamic key helps reset the camera
    photo = st.camera_input("Camera", label_visibility="collapsed")
    
    if photo:
        st.session_state.captured_images.append(photo)
        st.rerun() # Refresh to show the photo above

    # "I HAVE ENOUGH" BUTTON
    if len(st.session_state.captured_images) > 0:
        st.markdown("---")
        if st.button("✅ I have enough pictures - Close Camera"):
            st.session_state.camera_active = False
            st.rerun()

else:
    # Camera is hidden/closed
    col_reset, col_add = st.columns(2)
    with col_reset:
        if st.button("🗑️ Clear All & Retake"):
            st.session_state.captured_images = []
            st.session_state.camera_active = True
            st.rerun()
    with col_add:
        if len(st.session_state.captured_images) < 3:
            if st.button("📸 Add More Photos"):
                st.session_state.camera_active = True
                st.rerun()

# 3. SCAN BUTTON
st.markdown("---")
if len(st.session_state.captured_images) > 0:
    if st.button("🔍 SCAN FOR HONESTY"):
        with st.spinner(f"🔍 Scanning in {selected_location}... Applying 4 Laws..."):
            try:
                # RUN ANALYSIS
                result = analyze_product(st.session_state.captured_images, selected_location)
                
                # --- DISPLAY RESULTS (Original Rose Style) ---
                st.markdown("---")
                
                # Product Name
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.6); padding: 1rem; border-radius: 10px; border: 1px solid #fda4af; text-align: center;">
                    <span style="color: #9f1239; font-weight: bold;">📦 {result.get('product_type', 'Product')}</span><br>
                    <span style="color: #881337; font-size: 1.2rem;">{result.get('product_name', 'Unknown')}</span>
                </div>
                """, unsafe_allow_html=True)
                
                # Score Card
                score = result.get('score', 0)
                # Determine color
                if score >= 80: color_cls, emoji = "score-green", "🟢"
                elif score >= 50: color_cls, emoji = "score-orange", "🟠"
                else: color_cls, emoji = "score-red", "🔴"
                
                st.markdown(f"""
                <div class="score-card">
                    <div class="score-label">Integrity Score</div>
                    <div class="score-value {color_cls}">{score}</div>
                    <div style="font-family: 'Space Mono', monospace; font-weight: bold; font-size: 1.2rem;">
                        {emoji} {result.get('verdict', 'Analyzed')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Summary
                st.info(f"📝 {result.get('honesty_summary')}")
                
                # Deductions
                deductions = result.get('deductions', [])
                if deductions:
                    st.markdown("### ⚠️ Violations Found")
                    for d in deductions:
                        st.markdown(f"""
                        <div style="background: rgba(255,255,255,0.8); border-left: 4px solid #be123c; padding: 10px; margin-bottom: 5px; border-radius: 0 10px 10px 0;">
                            <strong style="color: #be123c;">{d.get('points')} pts: {d.get('law')}</strong><br>
                            <span style="color: #333;">{d.get('reason')}</span>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Alternatives
                alt = result.get('better_alternative')
                if alt:
                    st.markdown("---")
                    st.markdown(f"""
                    <div style="background: #f0fdf4; border: 2px solid #166534; padding: 1.5rem; border-radius: 15px;">
                        <h4 style="color: #166534; margin: 0;">💡 Honest Alternative in {selected_location}</h4>
                        <p style="color: #14532d; font-size: 1.1rem; font-weight: bold; margin: 0.5rem 0;">
                            {alt.get('product_name')}
                        </p>
                        <p style="color: #14532d;">{alt.get('why_more_honest')}</p>
                    </div>
                    """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"❌ Analysis Error: {str(e)}")
else:
    st.info("👆 Take a photo to start scanning")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #9f1239; font-size: 0.8rem;">
    🌍 HONESTYMATTER v3.0<br>
    Measuring Honesty, Not Health
</div>
""", unsafe_allow_html=True)