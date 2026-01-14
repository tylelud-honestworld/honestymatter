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
from PIL import Image
import requests
import time

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="Integrity Protocol",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =============================================================================
# 1. SECURITY & API SETUP (Fixed)
# =============================================================================
try:
    # This securely grabs the key from Streamlit Secrets
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    else:
        st.error("⚠️ API Key missing! Please add GEMINI_API_KEY to Streamlit Secrets.")
except Exception as e:
    st.error(f"⚠️ Security Configuration Error: {e}")

# Initialize Model (Gemini 2.0 Flash for speed)
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash", 
    generation_config={
        "temperature": 0.0,
        "top_p": 1,
        "top_k": 1,
    }
)

# =============================================================================
# 2. CUSTOM VISUALS (Mobile Modern)
# =============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Archivo+Black&display=swap');
    
    /* Main Background */
    .stApp {
        background: linear-gradient(135deg, #fff5f5 0%, #fff0f1 100%) !important;
    }
    
    /* Mobile-Friendly Header */
    h1 {
        font-family: 'Archivo Black', sans-serif !important;
        background: linear-gradient(90deg, #be185d, #e11d48);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 1.8rem !important;
        margin-bottom: 0px !important;
        padding-bottom: 0px !important;
    }
    
    /* Big Thumb-Friendly Buttons */
    .stButton > button {
        width: 100%;
        height: 3.5rem;
        border-radius: 15px !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1) !important;
        transition: transform 0.1s;
    }
    
    .stButton > button:active {
        transform: scale(0.98);
    }
    
    /* Primary Action (Scan) */
    div[data-testid="stButton"] > button:first-child {
        background: linear-gradient(90deg, #be185d, #e11d48) !important;
        color: white !important;
    }

    /* Score Card */
    .score-card {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 10px 30px rgba(225, 29, 72, 0.15);
        text-align: center;
        margin-top: 1rem;
        border: 2px solid #fecdd3;
    }
    
    /* Location Box */
    .location-badge {
        background: rgba(255,255,255,0.8);
        padding: 8px 15px;
        border-radius: 20px;
        font-size: 0.85rem;
        color: #881337;
        border: 1px solid #fecdd3;
        display: inline-block;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# 3. LOCATION INTELLIGENCE (The Real Fix)
# =============================================================================
def get_user_country():
    """
    Attempts to get the REAL user location, not the Server location.
    Falls back to a safe default if it fails.
    """
    # 1. Try to get IP from Streamlit Headers (works on Cloud)
    try:
        from streamlit.web.server.websocket_headers import _get_websocket_headers
        headers = _get_websocket_headers()
        # X-Forwarded-For contains the real user IP
        user_ip = headers.get("X-Forwarded-For")
        
        if user_ip:
            # We found a real IP! Let's check where it is.
            first_ip = user_ip.split(",")[0] # Get the first IP in the list
            response = requests.get(f'https://ipapi.co/{first_ip}/json/', timeout=3)
            data = response.json()
            return f"{data.get('city')}, {data.get('country_name')}"
    except:
        pass # If anything fails, just continue
        
    return "Select Location" # Default state

# Initialize Location
if 'detected_location' not in st.session_state:
    st.session_state.detected_location = get_user_country()

# =============================================================================
# 4. CORE AI LOGIC
# =============================================================================
GEMINI_PROMPT = """
Analyze these product images for HONESTY based on the "4 Laws of Integrity":
1. Law of Prominence (Fairy Dusting)
2. Law of Definition (Buzzwords)
3. Law of Substitution (Cheap Fillers)
4. Law of Fine Print (Contradictions)

USER LOCATION: {location} 
(IMPORTANT: Suggest alternatives that actually exist in {location})

OUTPUT JSON ONLY:
{{
    "product_name": "Name",
    "score": 0-100,
    "verdict": "Short Verdict",
    "honesty_summary": "One sentence summary.",
    "deductions": [{{"law": "Law Name", "points": -10, "reason": "Short reason"}}],
    "better_alternative": {{
        "product_name": "Specific Product in {location}",
        "why_more_honest": "Why it is better"
    }}
}}
"""

def analyze_product(images, location):
    pil_images = []
    for img in images:
        img.seek(0)
        pil_images.append(Image.open(img))
    
    content = [GEMINI_PROMPT.format(location=location)] + pil_images
    response = model.generate_content(content)
    text = response.text.replace("```json", "").replace("```", "")
    return json.loads(text)

# =============================================================================
# 5. MAIN APP INTERFACE
# =============================================================================

# HEADER
col_head, col_loc = st.columns([2, 1])
with col_head:
    st.markdown("<h1>🔍 INTEGRITY PROTOCOL</h1>", unsafe_allow_html=True)
with col_loc:
    # Location Selector (Defaults to Detected, but User can fix it)
    countries = ["Australia", "United States", "United Kingdom", "Europe", "Asia", "Global"]
    
    # Logic to set default index
    default_idx = 0
    if "Australia" in st.session_state.detected_location: default_idx = 0
    elif "United States" in st.session_state.detected_location: default_idx = 1
    
    selected_location = st.selectbox(
        "📍 Your Region",
        options=countries,
        index=default_idx,
        label_visibility="collapsed"
    )

st.write("") # Spacer

# CAMERA LOGIC (The "Pop-up" Fix)
if 'captured_images' not in st.session_state:
    st.session_state.captured_images = []
if 'camera_active' not in st.session_state:
    st.session_state.camera_active = True

# 1. SHOW GALLERY (Horizontal)
if st.session_state.captured_images:
    st.markdown(f"**📸 Captured Photos ({len(st.session_state.captured_images)}/3)**")
    cols = st.columns(3)
    for i, img in enumerate(st.session_state.captured_images):
        with cols[i]:
            st.image(img, use_container_width=True)

# 2. CAMERA CONTROLS
if st.session_state.camera_active and len(st.session_state.captured_images) < 3:
    # The actual camera input
    photo = st.camera_input("Take Photo", label_visibility="collapsed")
    
    if photo:
        st.session_state.captured_images.append(photo)
        # We DO NOT clear the list, we just append
        st.rerun()

    # "I have enough pictures" Button
    if len(st.session_state.captured_images) > 0:
        if st.button("✅ I have enough pictures"):
            st.session_state.camera_active = False # Hide camera
            st.rerun()

else:
    # Camera is hidden (either full or user said "enough")
    col_reset, col_add = st.columns(2)
    with col_reset:
        if st.button("🗑️ Start Over"):
            st.session_state.captured_images = []
            st.session_state.camera_active = True
            st.rerun()
    with col_add:
        if len(st.session_state.captured_images) < 3:
            if st.button("📸 Add More Photos"):
                st.session_state.camera_active = True
                st.rerun()

# 3. SCAN BUTTON (Only appears when photos exist)
if len(st.session_state.captured_images) > 0:
    st.markdown("---")
    if st.button("🚀 ANALYZE INTEGRITY", type="primary"):
        with st.spinner("🤖 Applying the 4 Laws..."):
            try:
                result = analyze_product(st.session_state.captured_images, selected_location)
                
                # --- RESULTS UI ---
                score = result.get('score', 0)
                color = "#15803d" if score >= 80 else "#c2410c" if score >= 50 else "#be123c"
                
                st.markdown(f"""
                <div class="score-card" style="border-color: {color};">
                    <div style="color: {color}; font-weight: bold; letter-spacing: 2px;">INTEGRITY SCORE</div>
                    <div style="font-size: 4rem; font-weight: 900; color: {color}; line-height: 1;">{score}</div>
                    <div style="background: {color}15; color: {color}; display: inline-block; 
                         padding: 5px 15px; border-radius: 15px; font-weight: bold; margin-top: 10px;">
                        {result.get('verdict', 'Analyzed')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.info(f"📝 {result.get('honesty_summary')}")
                
                # Deductions
                if result.get('deductions'):
                    st.markdown("### ⚠️ Violations")
                    for d in result['deductions']:
                        st.markdown(f"**-{d['points']} pts: {d['law']}**")
                        st.caption(d['reason'])
                
                # Alternatives
                alt = result.get('better_alternative')
                if alt:
                    st.success(f"**💡 Try this in {selected_location}: {alt['product_name']}**\n\n{alt['why_more_honest']}")
                    
            except Exception as e:
                st.error(f"Analysis failed. Please try again. Error: {e}")

# Footer
st.markdown("---")
st.caption("HonestyMatter v2.5 • Consumer Protection AI")