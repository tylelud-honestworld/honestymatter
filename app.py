"""
🔍 THE INTEGRITY PROTOCOL
A Consumer Protection App That Measures Honesty, Not Health

This app calculates a scientific "Integrity Score" (0-100) by measuring
the mathematical gap between Marketing Claims (Front) and Empirical Reality (Back/Ingredients).

Author: Senior Python Full-Stack Developer
Framework: Streamlit + Google Gemini 2.5 Flash
"""

import streamlit as st
import google.generativeai as genai
import json
import re
import pandas as pd
from PIL import Image
import io
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
# CUSTOM STYLING
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
    
    /* Traffic light colors - adjusted for light theme */
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
    
    /* Button styling */
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
    
    /* DataFrame styling */
    .dataframe {
        font-family: 'DM Sans', sans-serif !important;
        color: #4a044e !important;
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
    
    /* Expander styling */
    .streamlit-expanderHeader {
        font-family: 'Space Mono', monospace !important;
        background: rgba(255, 255, 255, 0.7) !important;
        border-radius: 10px !important;
        color: #881337 !important;
    }
    
    /* Input fields */
    .stTextInput input, .stSelectbox select {
        background: white !important;
        color: #4a044e !important;
        border: 2px solid #fda4af !important;
    }
    
    /* Summary box styling */
    .summary-box {
        background: rgba(255, 255, 255, 0.8);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #fda4af;
        color: #881337 !important;
    }
    
    /* Metric styling */
    [data-testid="stMetricValue"] {
        color: #9f1239 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #881337 !important;
    }
    
    /* Warning and info boxes */
    .stAlert {
        background: rgba(255, 255, 255, 0.8) !important;
        color: #4a044e !important;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #e11d48 !important;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# CONSTANTS & CONFIGURATION
# =============================================================================

# Global regions - will be auto-detected
GLOBAL_REGIONS = {
    "AU": "Australia",
    "US": "United States", 
    "GB": "United Kingdom",
    "CA": "Canada",
    "NZ": "New Zealand",
    "DE": "Germany",
    "FR": "France",
    "JP": "Japan",
    "SG": "Singapore",
    "IN": "India",
    "BR": "Brazil",
    "MX": "Mexico",
    "ZA": "South Africa",
    "AE": "UAE",
    "OTHER": "International"
}

def get_user_location():
    """Auto-detect user's country from IP address."""
    try:
        response = requests.get('https://ipapi.co/json/', timeout=5)
        if response.status_code == 200:
            data = response.json()
            country_code = data.get('country_code', 'OTHER')
            country_name = data.get('country_name', 'International')
            city = data.get('city', '')
            return {
                'country_code': country_code,
                'country_name': country_name,
                'city': city,
                'full_location': f"{city}, {country_name}" if city else country_name
            }
    except:
        pass
    return {
        'country_code': 'OTHER',
        'country_name': 'International',
        'city': '',
        'full_location': 'International'
    }

# The 4 Laws of Integrity - Core Logic
THE_4_LAWS = """
## THE 4 LAWS OF INTEGRITY (Scoring Algorithm)

You are an INTEGRITY AUDITOR. Your job is NOT to judge if a product is good quality or useful.
Your job is to measure HONESTY - the mathematical gap between Marketing Claims and Reality.

This applies to ALL product types: Food, Cosmetics, Electronics, Hardware, Supplements, Software, Services, etc.

## PRODUCT TYPE DETECTION:
First, identify what type of product this is:
- **CONSUMABLES** (Food, Beverages, Supplements): Look for ingredients list, nutrition facts
- **COSMETICS/PERSONAL CARE**: Look for ingredients list, usage instructions
- **ELECTRONICS/TECH**: Look for specifications, features list, model numbers
- **HARDWARE/TOOLS**: Look for specifications, materials, ratings
- **SOFTWARE/SERVICES**: Look for features, terms, limitations
- **OTHER**: Adapt analysis to whatever information is visible

## FLEXIBLE IMAGE ANALYSIS:
Products may have different layouts. Analyze ALL visible information:
- If there's a FRONT and BACK: Compare marketing (front) vs reality (back)
- If there's only ONE SIDE: Look for marketing claims vs fine print/specs on same surface
- If it's a BOX: Analyze all visible sides shown
- If it's a SCREEN/DIGITAL: Analyze headlines vs details/disclaimers
- If it's PACKAGING with a PRODUCT visible: Analyze both

Start with a Score of 100 (Perfect Integrity) and DEDUCT points based on these violations:

### LAW 1: THE LAW OF PROMINENCE ("Fairy Dusting") - DEDUCT 20 POINTS
- LOGIC: Highlighting a feature/ingredient that is actually minor or barely present.
- FOR CONSUMABLES: Hero ingredient not in top 5 ingredients
- FOR ELECTRONICS: Featured capability is actually basic/standard or barely functional
- FOR SERVICES: Highlighted benefit has major limitations
- DEDUCTION: -20 points

### LAW 2: THE LAW OF DEFINITION ("Buzzwords") - DEDUCT 15 POINTS  
- LOGIC: Using unregulated marketing words that imply value but have no proof or certification.
- BUZZWORDS TO FLAG: "Natural", "Premium", "Professional", "Military Grade", "Lab Tested",
  "Clinically Proven", "AI-Powered", "Smart", "Quantum", "Nano", "Pro", "Elite", "Advanced", 
  "Next-Gen", "Revolutionary", "Breakthrough", "Innovative", "World's Best", "Ultimate",
  "Industrial Strength", "Hospital Grade", "Aircraft Aluminum", "Space Age", "Eco-Friendly"
- TEST: These words appear WITHOUT specific certification, test results, or verifiable proof
- DEDUCTION: -15 points

### LAW 3: THE LAW OF SUBSTITUTION ("Cheap Reality") - DEDUCT 30 POINTS
- LOGIC: Premium marketing hiding cheap/basic reality.
- FOR CONSUMABLES: Premium claims but #1 ingredient is water, sugar, filler
- FOR ELECTRONICS: Premium price but generic/basic components or specs
- FOR SERVICES: Premium tier but basic features repackaged
- DEDUCTION: -30 points

### LAW 4: THE LAW OF FINE PRINT ("The Asterisk") - DEDUCT 40 POINTS
- LOGIC: A headline claim directly contradicted by fine print, specs, or disclaimers.
- EXAMPLES:
  * "Unlimited" but has limits/throttling
  * "Free" but requires payment/subscription
  * "Waterproof" but only splash resistant
  * "All-Day Battery" but only under lab conditions
  * "No Added Sugar" but contains sweeteners/concentrates
  * "Works with all devices" but major compatibility limits
  * "Instant Results" but "results may vary, 8 weeks needed"
  * "Lifetime Warranty" but with major exclusions
  * "Up to 50% off" but only on select items
- DEDUCTION: -40 points (MOST SEVERE - direct contradiction)

## SCORING THRESHOLDS:
- 80-100: GREEN (Honest Product) - Minor or no deceptions
- 50-79: ORANGE (Suspicious) - Notable gaps between claims and reality  
- 0-49: RED (High Deception) - Significant misleading marketing
"""

GEMINI_PROMPT_TEMPLATE = """
{laws}

## YOUR TASK:

Analyze these product image(s) and calculate the INTEGRITY SCORE.

**USER LOCATION:** {location}

## FINDING HONEST ALTERNATIVES:
When suggesting alternatives, you MUST:
1. Identify what TYPE of product this is (e.g., honey cereal, face moisturizer, USB cable)
2. Search your knowledge for SIMILAR products available in {location}
3. Suggest a specific product that:
   - Is available in the user's country/region ({location})
   - Has HONEST marketing (no fairy dusting, no misleading claims)
   - If it's food: the hero ingredient IS in the top ingredients
   - If it's cosmetics: claims are backed by real certifications
   - If it's electronics: specs match the marketing claims
   - Has a higher integrity score than the scanned product
4. Include the BRAND NAME and PRODUCT NAME specifically
5. Briefly explain WHY this alternative is more honest

Example good alternatives:
- "In Australia, try 'Capilano Pure Australian Honey' - the only ingredient is 100% Australian honey, no fillers or added sugars"
- "In the US, try 'Anker PowerLine III USB-C Cable' - specs are accurately stated, no exaggerated claims"
- "In the UK, try 'The Ordinary Hyaluronic Acid 2% + B5' - transparent ingredient list, no buzzword marketing"

## FLEXIBLE IMAGE ANALYSIS:
- Analyze ALL images provided (could be 1, 2, or more angles)
- Identify what type of product this is
- Find ALL marketing claims visible
- Find ALL specifications, ingredients, fine print, or disclaimers
- Compare claims vs reality

## ANALYSIS REQUIREMENTS:

1. IDENTIFY the product type (Food, Electronics, Cosmetics, Hardware, Service, etc.)
2. EXTRACT all marketing claims from prominent/headline areas
3. EXTRACT all factual information (ingredients, specs, fine print, disclaimers)
4. APPLY each of the 4 Laws and note specific violations
5. CALCULATE the final score (starting from 100, minus deductions)
6. SUGGEST a MORE HONEST alternative available in {location} (specific brand + product name)

## STRICT OUTPUT FORMAT (JSON ONLY):

You MUST respond with ONLY a valid JSON object. No markdown, no explanation, just JSON.

{{
    "product_type": "<detected product category>",
    "product_name": "<identified product name if visible>",
    "score": <integer 0-100>,
    "verdict": "<short verdict string, max 50 chars>",
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
        "hero_feature_position": "<position of featured item or 'Not Found' or 'N/A'>",
        "cheap_filler_detected": "<identified filler/basic component or 'None'>"
    }},
    "better_alternative": {{
        "product_name": "<specific brand + product name available in user's location>",
        "why_more_honest": "<1-2 sentences explaining why this alternative has better integrity>",
        "estimated_score": <integer 80-100 estimated integrity score>
    }},
    "honesty_summary": "<2-3 sentence summary of the gap between marketing and reality>"
}}
"""

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_score_color(score: int) -> tuple:
    """Return color class and emoji based on score threshold."""
    if score >= 80:
        return "green", "🟢", "HONEST PRODUCT"
    elif score >= 50:
        return "orange", "🟠", "SUSPICIOUS"
    else:
        return "red", "🔴", "HIGH DECEPTION"

def render_score_card(score: int, verdict: str):
    """Render the main score display with traffic light coloring."""
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
    """Render deductions as both cards and a DataFrame."""
    if not deductions:
        st.success("✅ No integrity violations detected!")
        return
    
    st.markdown("### 📋 Violation Report")
    
    # Render as styled cards
    for d in deductions:
        st.markdown(f"""
        <div class="deduction-card">
            <div class="deduction-points">{d.get('points', 0)} points</div>
            <strong>{d.get('law', 'Unknown Law')}</strong><br>
            {d.get('reason', 'No reason provided')}
        </div>
        """, unsafe_allow_html=True)
    
    # Also render as DataFrame for export
    st.markdown("#### 📊 Truth Table")
    df = pd.DataFrame(deductions)
    if not df.empty:
        df.columns = [col.replace('_', ' ').title() for col in df.columns]
        st.dataframe(df, use_container_width=True, hide_index=True)

def render_alternative(alternative_data, user_location: str):
    """Render the better alternative suggestion with score."""
    
    # Handle both old string format and new dict format
    if isinstance(alternative_data, str):
        product_name = alternative_data
        why_honest = ""
        est_score = None
    else:
        product_name = alternative_data.get('product_name', 'No alternative found')
        why_honest = alternative_data.get('why_more_honest', '')
        est_score = alternative_data.get('estimated_score', None)
    
    score_html = ""
    if est_score:
        score_html = f"""
        <div style="display: inline-block; background: rgba(21, 128, 61, 0.2); 
                    padding: 0.3rem 0.8rem; border-radius: 20px; margin-top: 0.5rem;
                    border: 1px solid #15803d;">
            <span style="color: #15803d; font-family: 'Space Mono', monospace; font-weight: bold;">
                🟢 Est. Score: {est_score}/100
            </span>
        </div>
        """
    
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
        {score_html}
    </div>
    """, unsafe_allow_html=True)

def parse_ai_response(response_text: str) -> dict:
    """
    Parse the AI response, handling potential JSON extraction issues.
    Returns parsed dict or raises ValueError with helpful message.
    """
    # Clean the response
    text = response_text.strip()
    
    # Try to extract JSON from markdown code blocks if present
    json_patterns = [
        r'```json\s*(.*?)\s*```',
        r'```\s*(.*?)\s*```',
        r'\{.*\}'
    ]
    
    for pattern in json_patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            try:
                json_str = match.group(1) if '```' in pattern else match.group(0)
                return json.loads(json_str)
            except json.JSONDecodeError:
                continue
    
    # Last attempt: try parsing the whole response
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Could not parse AI response as JSON: {e}\n\nRaw response:\n{text}")

def analyze_product(images: list, location: str) -> dict:
    """
    Send images to Gemini API and get integrity analysis.
    Uses temperature=0.0 for consistent, deterministic scoring.
    Handles 1 or more images flexibly.
    """
# Configure Gemini with embedded API key
import streamlit as st
import google.generativeai as genai

if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("API Key not found! Please check your Streamlit Secrets.")
    
    # Initialize model with strict temperature for consistency
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        generation_config={
            "temperature": 0.0,  # CRITICAL: No creativity, consistent scores
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 4096,
        }
    )
    
    # Process all images
    pil_images = []
    for img in images:
        if img is not None:
            img.seek(0)
            pil_images.append(Image.open(img))
    
    # Build the prompt
    prompt = GEMINI_PROMPT_TEMPLATE.format(
        laws=THE_4_LAWS,
        location=location
    )
    
    # Create content with all images
    content = [prompt]
    for i, pil_img in enumerate(pil_images, 1):
        content.append(f"IMAGE {i}:")
        content.append(pil_img)
    
    # Send to Gemini
    response = model.generate_content(content)
    
    # Parse and return
    return parse_ai_response(response.text)

# =============================================================================
# SIDEBAR
# =============================================================================

with st.sidebar:
    # Auto-detect location
    if 'user_location' not in st.session_state:
        st.session_state.user_location = get_user_location()
    
    location = st.session_state.user_location
    
    st.markdown("## 📍 Your Location")
    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.5); padding: 1rem; border-radius: 10px; 
                text-align: center; border: 1px solid #fda4af;">
        <span style="font-size: 1.5rem;">🌍</span><br>
        <strong style="color: #881337; font-size: 1.1rem;">{location['full_location']}</strong>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("")
    
    st.markdown("---")
    
    # The 4 Laws explanation
    with st.expander("📖 The 4 Laws of Integrity"):
        st.markdown("""
        <div class="law-box">
            <div class="law-title">LAW 1: PROMINENCE</div>
            <span style="color: #831843;">"Fairy Dusting" - Hero ingredient not in top 5</span><br>
            <strong style="color: #be185d;">-20 points</strong>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="law-box">
            <div class="law-title">LAW 2: DEFINITION</div>
            <span style="color: #831843;">"Buzzwords" - Unproven marketing terms</span><br>
            <strong style="color: #be185d;">-15 points</strong>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="law-box">
            <div class="law-title">LAW 3: SUBSTITUTION</div>
            <span style="color: #831843;">"Cheap Fillers" - Premium claims, cheap ingredients</span><br>
            <strong style="color: #be185d;">-30 points</strong>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="law-box">
            <div class="law-title">LAW 4: FINE PRINT</div>
            <span style="color: #831843;">"The Asterisk" - Claims contradicted by fine print</span><br>
            <strong style="color: #be185d;">-40 points</strong>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #9f1239; font-size: 0.8rem;">
        Built by<br>
        <strong style="font-size: 1.1rem;">🌍 HonestWorld</strong><br>
        v1.0.0
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# MAIN APPLICATION
# =============================================================================

# Header
st.markdown("# 🔍 THE INTEGRITY PROTOCOL")
st.markdown("""
<p style="font-family: 'DM Sans', sans-serif; color: #9f1239; font-size: 1.1rem; margin-bottom: 2rem;">
    Measuring the gap between <strong style="color: #be185d;">Marketing Claims</strong> and 
    <strong style="color: #e11d48;">Empirical Reality</strong>
</p>
""", unsafe_allow_html=True)

# Instructions
with st.expander("📱 How to Use This App", expanded=False):
    st.markdown("""
    ### Quick Scan (1-3 photos):
    1. **Take Photo(s)** of your product - any angle with visible text
    2. Tap **"SCAN FOR HONESTY"**
    3. Get your Integrity Score instantly!
    
    ### What to Photograph:
    - 📦 **Packaging** - Front, back, sides with text
    - 🏷️ **Labels** - Ingredients, specs, fine print
    - 📱 **Screens** - Product pages, ads, claims
    - 📄 **Documents** - Contracts, terms, offers
    
    ### Works With ANY Product:
    - 🍎 Food & Beverages
    - 💄 Cosmetics & Skincare  
    - 🔌 Electronics & Tech
    - 🧹 Household Products
    - 💊 Health & Supplements
    - 🛠️ Hardware & Tools
    - 📱 Apps & Services
    - 📋 Contracts & Offers
    
    ### What We Measure:
    ✅ Is the marketing HONEST?<br>
    ❌ Not quality, taste, or effectiveness
    """)

# Image upload section with camera support for mobile
st.markdown("### 📷 Scan Product")

# Initialize session state for images
if 'captured_images' not in st.session_state:
    st.session_state.captured_images = []
if 'capture_step' not in st.session_state:
    st.session_state.capture_step = 1

# Input method selector
input_method = st.radio(
    "Choose input method:",
    ["📸 Take Photos", "📁 Upload Images"],
    horizontal=True,
    label_visibility="collapsed"
)

# Store images in a list
product_images = []

if input_method == "📸 Take Photos":
    
    # Show captured images so far
    if st.session_state.captured_images:
        st.markdown(f"**✅ {len(st.session_state.captured_images)} photo(s) captured**")
        cols = st.columns(len(st.session_state.captured_images))
        for i, img in enumerate(st.session_state.captured_images):
            with cols[i]:
                st.image(img, caption=f"Photo {i+1}", use_container_width=True)
        
        # Option to clear and start over
        col_clear, col_scan = st.columns(2)
        with col_clear:
            if st.button("🗑️ Clear & Retake", use_container_width=True):
                st.session_state.captured_images = []
                st.session_state.capture_step = 1
                st.rerun()
    
    # Show camera for next capture
    num_captured = len(st.session_state.captured_images)
    
    if num_captured < 3:
        if num_captured == 0:
            st.markdown("**📸 Take Photo 1** (front/main side)")
        elif num_captured == 1:
            st.markdown("**📸 Take Photo 2** (back/ingredients - optional)")
        else:
            st.markdown("**📸 Take Photo 3** (additional angle - optional)")
        
        # Single camera input
        new_photo = st.camera_input(
            f"Capture photo {num_captured + 1}",
            key=f"camera_{st.session_state.capture_step}",
            label_visibility="collapsed"
        )
        
        if new_photo:
            st.session_state.captured_images.append(new_photo)
            st.session_state.capture_step += 1
            st.rerun()
        
        # Skip button for optional photos
        if num_captured >= 1:
            if st.button("⏭️ Skip - I have enough photos", use_container_width=True):
                pass  # Just continue with what we have
    
    else:
        st.success("✅ Maximum 3 photos captured!")
    
    # Use captured images
    product_images = st.session_state.captured_images

else:
    st.markdown("**Upload 1-3 images of your product**")
    
    uploaded_files = st.file_uploader(
        "Upload product images",
        type=['png', 'jpg', 'jpeg', 'webp'],
        accept_multiple_files=True,
        key="upload_multi",
        label_visibility="collapsed"
    )
    
    if uploaded_files:
        product_images = uploaded_files[:3]  # Limit to 3
        
        # Display uploaded images
        cols = st.columns(min(len(product_images), 3))
        for i, img in enumerate(product_images):
            with cols[i]:
                st.image(img, caption=f"Image {i+1}", use_container_width=True)

# Show image count
if product_images:
    st.success(f"✅ {len(product_images)} image(s) ready to scan")

# Analysis button
st.markdown("---")

analyze_button = st.button(
    "🔍 SCAN FOR HONESTY",
    use_container_width=True,
    disabled=len(product_images) == 0
)

if len(product_images) == 0:
    st.info("📸 Take or upload at least one photo to scan")

# Run analysis
if analyze_button and len(product_images) > 0:
    # Get location
    location = st.session_state.get('user_location', get_user_location())
    
    with st.spinner("🔍 Scanning product... Applying the 4 Laws of Integrity..."):
        try:
            # Get analysis with flexible images
            result = analyze_product(product_images, location['full_location'])
            
            # Clear captured images after successful scan (for camera mode)
            if 'captured_images' in st.session_state:
                st.session_state.captured_images = []
                st.session_state.capture_step = 1
            
            st.markdown("---")
            st.markdown("## 📊 Analysis Results")
            
            # Product identification
            product_type = result.get('product_type', 'Unknown')
            product_name = result.get('product_name', 'Unknown Product')
            
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.6); padding: 0.8rem 1.2rem; border-radius: 10px; 
                        margin-bottom: 1rem; border: 1px solid #fda4af;">
                <span style="color: #9f1239; font-family: 'Space Mono', monospace;">
                    📦 {product_type.upper()}</span> · 
                <span style="color: #881337;">{product_name}</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Main score display
            col_score, col_details = st.columns([1, 2])
            
            with col_score:
                render_score_card(
                    result.get('score', 0),
                    result.get('verdict', 'Unknown')
                )
            
            with col_details:
                # Honesty summary
                st.markdown("### 📝 Summary")
                st.markdown(f"""
                <div class="summary-box">
                    {result.get('honesty_summary', 'No summary available')}
                </div>
                """, unsafe_allow_html=True)
                
                # Marketing claims found
                if result.get('marketing_claims'):
                    st.markdown("**Marketing Claims Found:**")
                    claims = result.get('marketing_claims', [])
                    for claim in claims[:5]:  # Limit to 5
                        st.markdown(f"• {claim}")
            
            # Deductions table
            st.markdown("---")
            render_deductions_table(result.get('deductions', []))
            
            # Product analysis
            if result.get('product_analysis'):
                st.markdown("---")
                st.markdown("### 🧪 Product Analysis")
                
                prod_analysis = result['product_analysis']
                col_ing1, col_ing2, col_ing3 = st.columns(3)
                
                with col_ing1:
                    st.markdown("**Main Components:**")
                    components = prod_analysis.get('main_components', [])
                    for i, comp in enumerate(components[:5], 1):
                        st.markdown(f"{i}. {comp}")
                
                with col_ing2:
                    hero_pos = prod_analysis.get('hero_feature_position', 'N/A')
                    st.metric("Hero Feature Position", hero_pos)
                
                with col_ing3:
                    filler = prod_analysis.get('cheap_filler_detected', 'None')
                    if filler != 'None':
                        st.metric("⚠️ Cheap Filler", filler)
                    else:
                        st.metric("✅ Cheap Filler", "None Detected")
            
            # Better alternative
            st.markdown("---")
            render_alternative(
                result.get('better_alternative', 'No alternative suggested'),
                location['full_location']
            )
            
            # Raw JSON (collapsible for debugging)
            with st.expander("🔧 Raw API Response (Debug)"):
                st.json(result)
                
        except ValueError as e:
            st.error(f"❌ JSON Parsing Error: {e}")
            st.markdown("**Troubleshooting:**")
            st.markdown("- Ensure images are clear and readable")
            st.markdown("- Try with different product images")
            st.markdown("- Check that your API key is valid")
            
        except Exception as e:
            st.error(f"❌ Analysis Error: {str(e)}")
            st.markdown("**Possible causes:**")
            st.markdown("- Invalid API key")
            st.markdown("- API rate limit exceeded")
            st.markdown("- Network connection issues")
            st.markdown("- Images too large or unclear")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; color: #9f1239;">
    <p style="font-family: 'Space Mono', monospace; font-size: 0.8rem;">
        🌍 HONESTWORLD<br>
        <span style="color: #be185d;">Measuring Honesty, Not Health</span>
    </p>
    <p style="font-family: 'DM Sans', sans-serif; font-size: 0.75rem; color: #881337;">
        This tool is for educational purposes. Always read product labels carefully.<br>
        Works with food, cosmetics, electronics, supplements & more.
    </p>
</div>
""", unsafe_allow_html=True)
