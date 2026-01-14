"""
🔍 THE INTEGRITY PROTOCOL
A Consumer Protection App That Measures Honesty, Not Health

Author: Senior Python Full-Stack Developer
Framework: Streamlit + Google Gemini 1.5 Flash
"""

import streamlit as st
import google.generativeai as genai
import json
import re
import pandas as pd
from PIL import Image
import requests

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

# Use 1.5 Flash (The Fast, Multimodal Model)
# This works because you updated requirements.txt!
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash", 
    generation_config={
        "temperature": 0.0,
        "top_p": 1,
        "top_k": 1,
    }
)

# =============================================================================
# HELPER FUNCTIONS (With Image Resizing Fix)
# =============================================================================

def parse_ai_response(response_text: str) -> dict:
    text = response_text.strip()
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
    """
    Send images to Gemini API with AUTO-RESIZING to prevent timeouts.
    """
    pil_images = []
    
    # --- THE FIX: RESIZE IMAGES ---
    # This stops the "Infinite Spinning" by making images web-friendly (1024px)
    for img in images:
        if img is not None:
            img.seek(0)
            pil_img = Image.open(img)
            
            max_size = 1024
            if pil_img.width > max_size or pil_img.height > max_size:
                pil_img.thumbnail((max_size, max_size))
            
            pil_images.append(pil_img)
    # -----------------------------
    
    prompt = GEMINI_PROMPT_TEMPLATE.format(laws=THE_4_LAWS, location=location)
    content = [prompt] + pil_images
    
    # Send to Gemini
    response = model.generate_content(content)
    return parse_ai_response(response.text)

def get_score_color(score: int):
    if score >= 80: return "green", "🟢", "HONEST PRODUCT"
    elif score >= 50: return "orange", "🟠", "SUSPICIOUS"
    else: return "red", "🔴", "HIGH DECEPTION"

def render_score_card(score: int, verdict: str):
    color, emoji, status = get_score_color(score)
    st.markdown(f"""
    <div class="score-card">
        <div class="score-label">Integrity Score</div>
        <div class="score-value score-{color}">{score}</div>
        <div class="verdict-badge verdict-{color}">{emoji} {verdict}</div>
        <div style="margin-top: 1rem; color: #666; font-family: 'DM Sans', sans-serif;">{status}</div>
    </div>""", unsafe_allow_html=True)

def render_deductions_table(deductions: list):
    if not deductions: return
    st.markdown("### 📋 Violation Report")
    for d in deductions:
        st.markdown(f"""
        <div class="deduction-card">
            <div class="deduction-points">{d.get('points', 0)} points</div>
            <strong>{d.get('law', 'Unknown Law')}</strong><br>
            {d.get('reason', 'No reason provided')}
        </div>""", unsafe_allow_html=True)

def render_alternative(alternative_data, user_location: str):
    if isinstance(alternative_data, str):
        product_name, why_honest = alternative_data, ""
    else:
        product_name = alternative_data.get('product_name', 'No alternative found')
        why_honest = alternative_data.get('why_more_honest', '')

    st.markdown(f"""
    <div class="alternative-card">
        <h4>💡 Honest Alternative in {user_location}</h4>
        <p style="color: #881337; font-weight: 600; font-size: 1.1rem;">{product_name}</p>
        <p style="color: #9f1239; font-size: 0.95rem;">{why_honest}</p>
    </div>""", unsafe_allow_html=True)

def get_user_location():
    try:
        response = requests.get('[https://ipapi.co/json/](https://ipapi.co/json/)', timeout=2)
        if response.status_code == 200:
            data = response.json()
            city = data.get('city', '')
            country = data.get('country_name', 'International')
            return {'full_location': f"{city}, {country}" if city else country}
    except: pass
    return {'full_location': 'International'}

# =============================================================================
# CONSTANTS (The Brains)
# =============================================================================
THE_4_LAWS = """
You are an INTEGRITY AUDITOR.
1. PROMINENCE (-20 pts): Hero ingredient must be in top 5.
2. DEFINITION (-15 pts): No unproven buzzwords.
3. SUBSTITUTION (-30 pts): No cheap fillers in premium products.
4. FINE PRINT (-40 pts): No contradictions.
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
        "product_name": "Product Name",
        "why_more_honest": "Reason"
    }},
    "honesty_summary": "Summary"
}}
"""

# =============================================================================
# CUSTOM STYLING (Rose Theme)
# =============================================================================
st.markdown("""
<style>
    @import url('[https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Archivo+Black&family=DM+Sans:wght@400;500;700&display=swap](https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Archivo+Black&family=DM+Sans:wght@400;500;700&display=swap)');
    .stApp { background: linear-gradient(135deg, #fff5f5 0%, #ffe4e6 50%, #fecdd3 100%) !important; }
    h1 { font-family: 'Archivo Black', sans-serif !important; background: linear-gradient(90deg, #be185d, #e11d48, #f43f5e); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 3rem !important; }
    h2, h3 { font-family: 'Space Mono', monospace !important; color: #881337 !important; }
    p, span, label, .stMarkdown { color: #4a044e !important; font-family: 'DM Sans', sans-serif !important; }
    .score-card { background: linear-gradient(145deg, #ffffff, #fff1f2); border-radius: 20px; padding: 2rem; border: 2px solid #fda4af; text-align: center; margin: 1rem 0; }
    .score-value { font-family: 'Archivo Black', sans-serif; font-size: 5rem; font-weight: 900; line-height: 1; margin: 0.5rem 0; }
    .score-green { color: #15803d; } .score-orange { color: #c2410c; } .score-red { color: #be123c; }
    .stButton > button { background: linear-gradient(90deg, #be185d, #e11d48) !important; color: white !important; font-family: 'Space Mono', monospace !important; font-weight: 700 !important; border-radius: 50px !important; padding: 0.75rem 2rem !important; border: none !important; width: 100%; }
    .deduction-card { background: rgba(254, 205, 211, 0.5); border-left: 4px solid #e11d48; padding: 1rem 1.5rem; margin: 0.5rem 0; border-radius: 0 10px 10px 0; color: #881337 !important; }
    .alternative-card { background: linear-gradient(145deg, #ffffff, #fdf2f8); border: 2px solid #f9a8d4; border-radius: 15px; padding: 1.5rem; margin: 1rem 0; }
    .stSpinner > div { border-top-color: #e11d48 !important; }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# MAIN UI
# =============================================================================

if 'user_location' not in st.session_state:
    st.session_state.user_location = get_user_location()

st.markdown("# 🔍 THE INTEGRITY PROTOCOL")
st.markdown("<p style='font-size: 1.1rem; color: #9f1239;'>Measuring the gap between <strong>Marketing Claims</strong> and <strong>Empirical Reality</strong></p>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(f"**📍 Location:** {st.session_state.user_location['full_location']}")
    st.markdown("---")
    st.markdown("**The 4 Laws:**\n1. Prominence\n2. Definition\n3. Substitution\n4. Fine Print")

# TABS: Camera vs Upload
tab_cam, tab_upload = st.tabs(["📸 Camera", "📁 Upload"])
final_images = []

with tab_cam:
    if 'captured_images' not in st.session_state: st.session_state.captured_images = []
    
    # Display Gallery
    if st.session_state.captured_images:
        cols = st.columns(3)
        for i, img in enumerate(st.session_state.captured_images):
            with cols[i % 3]: st.image(img, use_container_width=True)
            
    # Input
    if len(st.session_state.captured_images) < 3:
        photo = st.camera_input("Take Photo", key=f"cam_{len(st.session_state.captured_images)}", label_visibility="collapsed")
        if photo:
            st.session_state.captured_images.append(photo)
            st.rerun()
            
    # Clear
    if st.button("🗑️ Clear Camera"):
        st.session_state.captured_images = []
        st.rerun()
        
    final_images.extend(st.session_state.captured_images)

with tab_upload:
    uploaded = st.file_uploader("Upload Images", type=['png','jpg','jpeg','webp'], accept_multiple_files=True, label_visibility="collapsed")
    if uploaded: final_images.extend(uploaded)

# SCAN BUTTON
st.markdown("---")
if final_images:
    if st.button("🚀 SCAN FOR HONESTY"):
        with st.spinner("🔍 Analyzing... (Resizing images to prevent timeout...)"):
            try:
                result = analyze_product(final_images, st.session_state.user_location['full_location'])
                
                # Results
                st.markdown("---")
                st.markdown(f"### 📦 {result.get('product_type', 'Product')}")
                render_score_card(result.get('score', 0), result.get('verdict', 'Analyzed'))
                st.info(f"📝 {result.get('honesty_summary')}")
                render_deductions_table(result.get('deductions', []))
                render_alternative(result.get('better_alternative', {}), st.session_state.user_location['full_location'])
                
            except Exception as e:
                st.error(f"Analysis Error: {e}")
else:
    st.info("👆 Please take a photo or upload a file.")