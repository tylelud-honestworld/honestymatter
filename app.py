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
    # This grabs the key safely from the Streamlit "Safe"
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    else:
        st.error("Error: Could not find API Key in Secrets. Please add GEMINI_API_KEY.")
except Exception as e:
    st.error(f"Security Error: {e}")

# --- MODEL SETUP (SWITCHED TO 1.5 FLASH FOR HIGHER LIMITS) ---
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash", 
    generation_config={
        "temperature": 0.0,
        "top_p": 1,
        "top_k": 1,
    }
)

# =============================================================================
# CUSTOM STYLING (ROSE THEME PRESERVED)
# =============================================================================
st.markdown("""
<style>
    /* Import distinctive fonts */
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Archivo+Black&family=DM+Sans:wght@400;500;700&display=swap');
    
    /* Main container styling - ROSE/LIGHT THEME */
    .stApp {
        background: linear-gradient(135deg, #fff5f5 0%, #ffe4e6 50%, #fecdd3 100%) !important;
    }
    
    .main .block-container {
        background: transparent !important;
    }
    
    /* Header styling */
    .stApp header {
        background-color: rgba(255, 245, 245, 0.9) !important;
    }
    
    /* Title styling */
    h1 {
        font-family: 'Archivo Black', sans-serif !important;
        background: linear-gradient(90deg, #be185d, #e11d48, #f43f5e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3rem !important;
        letter-spacing: -2px;
    }
    
    h2, h3 {
        font-family: 'Space Mono', monospace !important;
        color: #881337 !important;
    }
    
    /* General text color for light theme */
    p, span, label, .stMarkdown {
        color: #4a044e !important;
    }
    
    /* Custom metric card */
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
    
    .score-label {
        font-family: 'Space Mono', monospace;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 3px;
        color: #9f1239;
    }
    
    /* Traffic light colors */
    .score-green { color: #15803d; text-shadow: 0 0 20px rgba(21, 128, 61, 0.3); }
    .score-orange { color: #c2410c; text-shadow: 0 0 20px rgba(194, 65, 12, 0.3); }
    .score-red { color: #be123c; text-shadow: 0 0 20px rgba(190, 18, 60, 0.3); }
    
    /* Verdict badge */
    .verdict-badge {
        display: inline-block;
        padding: 0.5rem 1.5rem;
        border-radius: 50px;
        font-family: 'Space Mono', monospace;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-top: 1rem;
    }
    
    .verdict-green { background: rgba(21, 128, 61, 0.15); border: 2px solid #15803d; color: #15803d; }
    .verdict-orange { background: rgba(194, 65, 12, 0.15); border: 2px solid #c2410c; color: #c2410c; }
    .verdict-red { background: rgba(190, 18, 60, 0.15); border: 2px solid #be123c; color: #be123c; }
    
    /* Deduction cards */
    .deduction-card {
        background: rgba(254, 205, 211, 0.5);
        border-left: 4px solid #e11d48;
        padding: 1rem 1.5rem;
        margin: 0.5rem 0;
        border-radius: 0 10px 10px 0;
        font-family: 'DM Sans', sans-serif;
        color: #881337 !important;
    }
    
    .deduction-card strong {
        color: #9f1239 !important;
    }
    
    .deduction-points {
        font-family: 'Space Mono', monospace;
        color: #be123c;
        font-weight: 700;
        font-size: 1.2rem;
    }
    
    /* Alternative suggestion */
    .alternative-card {
        background: linear-gradient(145deg, #ffffff, #fdf2f8);
        border: 2px solid #f9a8d4;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .alternative-card h4 {
        color: #be185d !important;
        font-family: 'Space Mono', monospace !important;
        margin-bottom: 0.5rem;
    }
    
    .alternative-card p {
        color: #831843 !important;
    }
    
    /* File uploader styling */
    .stFileUploader {
        background: rgba(255, 255, 255, 0.7) !important;
        border-radius: 15px !important;
        padding: 1rem !important;
        border: 2px dashed #f9a8d4 !important;
    }
    
    /* Button styling (MOBILE OPTIMIZED) */
    .stButton > button {
        background: linear-gradient(90deg, #be185d, #e11d48) !important;
        color: white !important;
        font-family: 'Space Mono', monospace !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 0.75rem 2rem !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        transition: all 0.3s ease !important;
        width: 100%;
        min-height: 50px; /* Big touch target */
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 30px rgba(225, 29, 72, 0.4) !important;
    }
    
    /* Sidebar styling - Rose theme */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #fff1f2, #ffe4e6) !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown span,
    [data-testid="stSidebar"] label {
        color: #881337 !important;
    }
    
    [data-testid="stSidebar"] h2 {
        color: #9f1239 !important;
    }
    
    /* Info boxes */
    .law-box {
        background: rgba(251, 207, 232, 0.4);
        border-left: 4px solid #ec4899;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0 10px 10px 0;
    }
    
    .law-title {
        font-family: 'Space Mono', monospace;
        color: #be185d;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .law-box br + text, .law-box {
        color: #831843 !important;
    }
    
    /* Summary box styling */
    .summary-box {
        background: rgba(255, 255, 255, 0.8);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #fda4af;
        color: #881337 !important;
    }
    
    /* Camera Styling */
    div[data-testid="stCameraInput"] {
        border: 2px dashed #fda4af;
        border-radius: 15px;
        background: rgba(255,255,255,0.5);
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# CONSTANTS & CONFIGURATION
# =============================================================================

# The 4 Laws of Integrity - Core Logic
THE_4_LAWS = """
## THE 4 LAWS OF INTEGRITY (Scoring Algorithm)

You are an INTEGRITY AUDITOR. Your job is NOT to judge if a product is good quality or useful.
Your job is to measure HONESTY - the mathematical gap between Marketing Claims and Reality.

This applies to ALL product types: Food, Cosmetics, Electronics, Hardware, Supplements, Software, Services, etc.

Start with a Score of 100 (Perfect Integrity) and DEDUCT points based on these violations:

### LAW 1: THE LAW OF PROMINENCE ("Fairy Dusting") - DEDUCT 20 POINTS
- LOGIC: Highlighting a feature/ingredient that is actually minor or barely present.
- DEDUCTION: -20 points

### LAW 2: THE LAW OF DEFINITION ("Buzzwords") - DEDUCT 15 POINTS  
- LOGIC: Using unregulated marketing words that imply value but have no proof or certification.
- BUZZWORDS TO FLAG: "Natural", "Premium", "AI-Powered", "Professional", "Clinically Proven".
- DEDUCTION: -15 points

### LAW 3: THE LAW OF SUBSTITUTION ("Cheap Reality") - DEDUCT 30 POINTS
- LOGIC: Premium marketing hiding cheap/basic reality.
- DEDUCTION: -30 points

### LAW 4: THE LAW OF FINE PRINT ("The Asterisk") - DEDUCT 40 POINTS
- LOGIC: A headline claim directly contradicted by fine print, specs, or disclaimers.
- DEDUCTION: -40 points (MOST SEVERE - direct contradiction)

## SCORING THRESHOLDS:
- 80-100: GREEN (Honest Product)
- 50-79: ORANGE (Suspicious)
- 0-49: RED (High Deception)
"""

GEMINI_PROMPT_TEMPLATE = """
{laws}

## YOUR TASK:
Analyze these product image(s) and calculate the INTEGRITY SCORE.
**USER LOCATION:** {location}

## FINDING HONEST ALTERNATIVES:
When suggesting alternatives, you MUST:
1. Identify what TYPE of product this is.
2. Suggest a specific product available in {location}.
3. The alternative must have HIGHER integrity (honest marketing).
4. Include the BRAND NAME and PRODUCT NAME.

## STRICT OUTPUT FORMAT (JSON ONLY):
You MUST respond with ONLY a valid JSON object. No markdown, no explanation, just JSON.

{{
    "product_type": "<detected product category>",
    "product_name": "<identified product name if visible>",
    "score": <integer 0-100>,
    "verdict": "<short verdict string>",
    "marketing_claims": ["<list of marketing claims found>"],
    "deductions": [
        {{
            "law": "<Law 1/2/3/4 name>",
            "reason": "<specific explanation of the violation>",
            "points": <negative integer>
        }}
    ],
    "product_analysis": {{
        "main_components": ["<list top 5 ingredients OR key specs>"],
        "hero_feature_position": "<position of featured item or 'Not Found'>",
        "cheap_filler_detected": "<identified filler or 'None'>"
    }},
    "better_alternative": {{
        "product_name": "<specific brand + product name available in user's location>",
        "why_more_honest": "<why this is better>",
        "estimated_score": <integer 80-100>
    }},
    "honesty_summary": "<2-3 sentence summary>"
}}
"""

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_score_color(score: int) -> tuple:
    if score >= 80:
        return "green", "🟢", "HONEST PRODUCT"
    elif score >= 50:
        return "orange", "🟠", "SUSPICIOUS"
    else:
        return "red", "🔴", "HIGH DECEPTION"

def render_score_card(score: int, verdict: str):
    color, emoji, status = get_score_color(score)
    st.markdown(f"""
    <div class="score-card">
        <div class="score-label">Integrity Score</div>
        <div class="score-value score-{color}">{score}</div>
        <div class="verdict-badge verdict-{color}">{emoji} {verdict}</div>
        <div style="margin-top: 1rem; color: #666; font-family: 'DM Sans', sans-serif;">
            {status}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_deductions_table(deductions: list):
    if not deductions:
        st.success("✅ No integrity violations detected!")
        return
    
    st.markdown("### 📋 Violation Report")
    for d in deductions:
        st.markdown(f"""
        <div class="deduction-card">
            <div class="deduction-points">{d.get('points', 0)} points</div>
            <strong>{d.get('law', 'Unknown Law')}</strong><br>
            {d.get('reason', 'No reason provided')}
        </div>
        """, unsafe_allow_html=True)

def render_alternative(alternative_data, user_location: str):
    if isinstance(alternative_data, str):
        product_name = alternative_data
        why_honest = ""
    else:
        product_name = alternative_data.get('product_name', 'No alternative found')
        why_honest = alternative_data.get('why_more_honest', '')
    
    st.markdown(f"""
    <div class="alternative-card">
        <h4>💡 Honest Alternative in {user_location}</h4>
        <p style="color: #881337; font-family: 'DM Sans', sans-serif; font-size: 1.1rem; 
                  font-weight: 600; margin: 0.5rem 0;">
            {product_name}
        </p>
        <p style="color: #9f1239; font-family: 'DM Sans', sans-serif; margin: 0.5rem 0; font-size: 0.95rem;">
            {why_honest}
        </p>
    </div>
    """, unsafe_allow_html=True)

def parse_ai_response(response_text: str) -> dict:
    text = response_text.strip()
    # Try to extract JSON from code blocks
    json_patterns = [r'```json\s*(.*?)\s*```', r'```\s*(.*?)\s*```', r'\{.*\}']
    for pattern in json_patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            try:
                json_str = match.group(1) if '```' in pattern else match.group(0)
                return json.loads(json_str)
            except json.JSONDecodeError:
                continue
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"score": 0, "verdict": "Error", "honesty_summary": "Error parsing AI response. Please try again."}

def analyze_product(images: list, location: str) -> dict:
    pil_images = []
    for img in images:
        if img is not None:
            img.seek(0)
            pil_images.append(Image.open(img))
    
    prompt = GEMINI_PROMPT_TEMPLATE.format(laws=THE_4_LAWS, location=location)
    content = [prompt]
    for i, pil_img in enumerate(pil_images, 1):
        content.append(f"IMAGE {i}:")
        content.append(pil_img)
    
    response = model.generate_content(content)
    return parse_ai_response(response.text)

# =============================================================================
# SIDEBAR
# =============================================================================

with st.sidebar:
    st.markdown("## 📍 Location Settings")
    
    # MANUAL SELECTOR (Default to Australia)
    region_options = ["Australia", "United States", "United Kingdom", "Canada", "Europe", "Asia", "Global"]
    selected_location = st.selectbox("Select Region:", options=region_options, index=0)
    
    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.5); padding: 1rem; border-radius: 10px; 
                text-align: center; border: 1px solid #fda4af;">
        <span style="font-size: 1.5rem;">🌍</span><br>
        <strong style="color: #881337; font-size: 1.1rem;">{selected_location}</strong>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    with st.expander("📖 The 4 Laws of Integrity"):
        st.markdown("**1. Prominence:** No Fairy Dusting (-20)")
        st.markdown("**2. Definition:** No Buzzwords (-15)")
        st.markdown("**3. Substitution:** No Cheap Fillers (-30)")
        st.markdown("**4. Fine Print:** No Asterisks (-40)")
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #9f1239; font-size: 0.8rem;">
        Built by<br><strong style="font-size: 1.1rem;">🌍 HonestWorld</strong><br>v1.0.0
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# MAIN APPLICATION
# =============================================================================

st.markdown("# 🔍 THE INTEGRITY PROTOCOL")
st.markdown("""
<p style="font-family: 'DM Sans', sans-serif; color: #9f1239; font-size: 1.1rem; margin-bottom: 2rem;">
    Measuring the gap between <strong style="color: #be185d;">Marketing Claims</strong> and 
    <strong style="color: #e11d48;">Empirical Reality</strong>
</p>
""", unsafe_allow_html=True)

# MOBILE CAMERA LOGIC (No Pop-ups)
st.markdown("### 📷 Scan Product")

if 'captured_images' not in st.session_state:
    st.session_state.captured_images = []
if 'camera_active' not in st.session_state:
    st.session_state.camera_active = True

# 1. SHOW PHOTOS
if st.session_state.captured_images:
    st.markdown(f"**✅ {len(st.session_state.captured_images)} Photos Captured:**")
    cols = st.columns(3)
    for i, img in enumerate(st.session_state.captured_images):
        with cols[i]:
            st.image(img, caption=f"Photo {i+1}", use_container_width=True)

# 2. CAMERA INPUT
if st.session_state.camera_active and len(st.session_state.captured_images) < 3:
    st.markdown("---")
    # Dynamic key ensures camera resets after photo
    cam_key = f"camera_{len(st.session_state.captured_images)}"
    new_photo = st.camera_input("Take a photo", key=cam_key, label_visibility="collapsed")
    
    if new_photo:
        st.session_state.captured_images.append(new_photo)
        st.rerun()

    if len(st.session_state.captured_images) > 0:
        if st.button("✅ I have enough pictures - Close Camera", use_container_width=True):
            st.session_state.camera_active = False
            st.rerun()

else:
    col_reset, col_add = st.columns(2)
    with col_reset:
        if st.button("🗑️ Clear & Retake", use_container_width=True):
            st.session_state.captured_images = []
            st.session_state.camera_active = True
            st.rerun()
    with col_add:
        if len(st.session_state.captured_images) < 3:
            if st.button("📸 Add More Photos", use_container_width=True):
                st.session_state.camera_active = True
                st.rerun()

# ANALYSIS BUTTON
st.markdown("---")
product_images = st.session_state.captured_images

analyze_button = st.button("🔍 SCAN FOR HONESTY", use_container_width=True, disabled=len(product_images) == 0)

if analyze_button and len(product_images) > 0:
    with st.spinner(f"🔍 Scanning in {selected_location}... Applying the 4 Laws..."):
        try:
            result = analyze_product(product_images, selected_location)
            
            st.markdown("---")
            st.markdown("## 📊 Analysis Results")
            
            # Product Type Badge
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.6); padding: 0.8rem; border-radius: 10px; border: 1px solid #fda4af; margin-bottom: 1rem;">
                <span style="color: #9f1239; font-weight: bold;">📦 {result.get('product_type', 'Product')}</span> · 
                <span style="color: #881337;">{result.get('product_name', 'Unknown')}</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Score
            render_score_card(result.get('score', 0), result.get('verdict', 'Unknown'))
            
            # Summary
            st.markdown("### 📝 Summary")
            st.markdown(f"<div class='summary-box'>{result.get('honesty_summary', 'No summary')}</div>", unsafe_allow_html=True)
            
            # Deductions
            st.markdown("---")
            render_deductions_table(result.get('deductions', []))
            
            # Alternative
            st.markdown("---")
            render_alternative(result.get('better_alternative', {}), selected_location)
                
        except Exception as e:
            st.error(f"❌ Analysis Error: {str(e)}")
            st.info("💡 Tip: If you get a 429 Error, wait 2 minutes or use a new API Key.")

st.markdown("---")
st.markdown("<center style='color: #9f1239; font-size: 0.8rem;'>HonestWorld • Measuring Honesty, Not Health</center>", unsafe_allow_html=True)