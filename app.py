"""
SecureShe AI - FIXED VERSION
This version WILL detect threats properly
Run with: streamlit run app.py
"""

import streamlit as st
import re
import pickle
from datetime import datetime

import streamlit as st

st.set_page_config(
    page_title="SecureShe AI - Online Safety Assistant",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Now your other Streamlit code
st.title("Welcome to SecureShe AI")


# ============================================
# LOAD ML MODEL (Optional)
# ============================================

@st.cache_resource
def load_ml_model():
    """Load the trained ML model"""
    try:
        with open('secureshe_classifier.pkl', 'rb') as f:
            model = pickle.load(f)
        return model
    except:
        return None

ML_MODEL = load_ml_model()

# ============================================
# PAGE CONFIGURATION
# ============================================

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #e91e63;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .safe-box {
        background-color: #e8f5e9;
        border-left: 5px solid #4caf50;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3e0;
        border-left: 5px solid #ff9800;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .danger-box {
        background-color: #ffebee;
        border-left: 5px solid #f44336;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# CONFIGURATION - EXPANDED KEYWORDS
# ============================================

KEYWORDS = {
    "harassment": [
        # English
        "idiot", "stupid", "shut up", "worthless", "trash", "ugly", "die",
        "hate you", "loser", "dumb", "fool", "pathetic", "waste", "shut your",
        "disgusting", "useless", "annoying", "terrible", "awful", "horrible",
        # Nigerian Pidgin
        "mumu", "olodo", "ode", "werey", "ashawo", "olofofo", 
        "foolish", "yeye", "you no get sense", "you dey craze", 
        "mad person", "your papa", "your mama", "ode buruku"
    ],
    "threats": [
        # Direct threats
        "kill", "hurt", "beat", "destroy", "ruin", "harm", "damage",
        "suffer", "pain", "die", "dead", "finish", "end you",
        # Warning phrases
        "watch your back", "you will regret", "i know where you live",
        "i know your address", "i will find you", "coming for you",
        # Nigerian
        "i go deal", "i go show you", "you go see", "make i no catch",
        "thunder fire", "i fit finish", "i go wound", "i go scatter",
        "e go pain you", "you don enter wahala", "you go hear am"
    ],
    "blackmail": [
        # Explicit blackmail
        "send nudes", "leak", "expose", "publish", "share your",
        "pay me or", "send money or", "or i will", "or else",
        "i have your photos", "i have your pics", "i have screenshots",
        # Nigerian context
        "make you send", "or i go post", "i fit share", "send am or",
        "i get your", "wahala go burst"
    ],
    "stalking": [
        # Location references
        "i saw you", "i know where", "i was outside", "i was at",
        "i'm following", "tracking you", "watching you", "i can see you",
        "your location", "i know your", "following you",
        # Nigerian
        "i dey follow you", "i see where you dey", "i know your area"
    ],
    "scams": [
        # Financial requests
        "transfer money", "send money", "pay", "account number", 
        "bank account", "atm pin", "password", "otp", "bvn",
        "claim your prize", "you won", "verify your account",
        "processing fee", "activation fee", "customs fee",
        # Nigerian platforms
        "419", "recharge card", "opay", "palmpay", "kuda",
        "paystack", "flutterwave"
    ],
    "inappropriate_advances": [
        # Sexual content
        "send pics", "send nudes", "sexy", "naked", "sex",
        "hook up", "come over", "sleep with", "make love",
        "your body", "show me", "i want you", "turn me on",
        # Nigerian
        "make we link", "come my place", "i wan see you",
        "how far with your body"
    ],
    "impersonation": [
        "fake account", "impersonate", "pretending to be you",
        "posing as you", "using your photos", "using your name",
        "clone", "duplicate account", "someone using your"
    ]
}

# LOWERED THRESHOLDS - More sensitive detection
THRESHOLDS = {
    "harassment": 0.15,      # Lower = more sensitive
    "threats": 0.15,
    "blackmail": 0.15,
    "stalking": 0.15,
    "scams": 0.15,
    "inappropriate_advances": 0.15,
    "impersonation": 0.15,
}

ADVICE_TEMPLATES = {
    "harassment": {
        "title": "⚠️ Abusive or Insulting Message",
        "steps": [
            "1️⃣ Do not reply to abusive messages",
            "2️⃣ Block the sender on that platform",
            "3️⃣ Take screenshots if safe to do so",
            "4️⃣ Report to the platform if repeated"
        ]
    },
    "threats": {
        "title": "🚨 Message Contains Threats",
        "steps": [
            "1️⃣ Do NOT reply - your safety is priority",
            "2️⃣ If in immediate danger, contact emergency: 112",
            "3️⃣ Save evidence (screenshots) safely",
            "4️⃣ Share with trusted adult or NGO"
        ]
    },
    "blackmail": {
        "title": "⚠️ Blackmail or Extortion",
        "steps": [
            "1️⃣ Do NOT comply with demands",
            "2️⃣ Do not negotiate - keep records",
            "3️⃣ Report to platform and contact NGO",
            "4️⃣ Seek legal support if needed"
        ]
    },
    "stalking": {
        "title": "👁️ Stalking or Doxxing Behavior",
        "steps": [
            "1️⃣ Do not share your location publicly",
            "2️⃣ Tighten privacy settings",
            "3️⃣ Block sender and inform trusted contacts",
            "4️⃣ Contact authorities if physically unsafe"
        ]
    },
    "scams": {
        "title": "💰 Possible Scam/Fraud Attempt",
        "steps": [
            "1️⃣ Do NOT send money or reveal passwords",
            "2️⃣ Verify via official channels only",
            "3️⃣ Do not click unknown links",
            "4️⃣ Block and report the sender"
        ]
    },
    "inappropriate_advances": {
        "title": "🔞 Unwanted Sexual Advances",
        "steps": [
            "1️⃣ Do not engage or escalate",
            "2️⃣ Block and report if uncomfortable",
            "3️⃣ Tell trusted adult if pressured",
            "4️⃣ Seek counseling support if distressed"
        ]
    },
    "impersonation": {
        "title": "👤 Possible Impersonation/Fake Account",
        "steps": [
            "1️⃣ Do not interact with fake accounts",
            "2️⃣ Report to platform immediately",
            "3️⃣ Collect screenshots safely",
            "4️⃣ Notify friends/followers"
        ]
    }
}

RESOURCES = [
    {"name": "🚨 Emergency Services", "contact": "112"},
    {"name": "👮 Police Cyber Crime", "contact": "155260"},
    {"name": "🏢 Paradigm Initiative", "contact": "+234-814-846-6676"},
    {"name": "💪 Women at Risk Foundation", "contact": "08092178000"}
]

# ============================================
# IMPROVED DETECTION FUNCTIONS
# ============================================

def simple_keyword_match(text, keywords):
    """
    Simple keyword matching - more reliable than fuzzy matching
    """
    text_lower = text.lower()
    matched = []
    
    for keyword in keywords:
        keyword_lower = keyword.lower()
        # Check if keyword is in text (as whole word or part of word)
        if keyword_lower in text_lower:
            matched.append(keyword)
    
    return len(matched), matched

def analyze_message(text):
    """
    FIXED analysis function - will actually detect threats
    """
    detected = {}
    text_lower = text.lower()
    
    # Check each category
    for category, keywords in KEYWORDS.items():
        match_count, matched = simple_keyword_match(text, keywords)
        
        if match_count > 0:
            # Calculate score
            score = min(match_count * 0.3, 1.0)  # Each keyword adds 30%
            
            # Get threshold for this category
            threshold = THRESHOLDS.get(category, 0.15)
            
            # If score exceeds threshold, flag it
            if score >= threshold:
                detected[category] = {
                    "score": round(score, 3),
                    "confidence": "high" if score > 0.6 else "medium" if score > 0.3 else "low",
                    "evidence": matched[:5],  # Show first 5 matches
                    "method": "keyword-based"
                }
    
    # Try ML model if available
    if ML_MODEL is not None:
        try:
            ml_pred = ML_MODEL.predict([text])[0]
            ml_proba = ML_MODEL.predict_proba([text])[0]
            ml_confidence = max(ml_proba)
            
            # Only use ML if it detects something AND is confident
            if ml_pred != "safe" and ml_confidence >= 0.3:
                if ml_pred in detected:
                    # Boost existing detection
                    detected[ml_pred]["score"] = min(detected[ml_pred]["score"] + 0.2, 1.0)
                    detected[ml_pred]["method"] = "keyword + ML"
                else:
                    # Add ML detection
                    detected[ml_pred] = {
                        "score": round(ml_confidence, 3),
                        "confidence": "high" if ml_confidence > 0.7 else "medium",
                        "evidence": ["ML prediction"],
                        "method": "ML-only"
                    }
        except:
            pass  # ML failed, continue with keyword-based
    
    # Determine urgency
    urgent = False
    if "threats" in detected and detected["threats"]["score"] >= 0.5:
        urgent = True
    if len(detected) >= 3:  # Multiple categories detected
        urgent = True
    
    # Determine risk level
    if not detected:
        risk_level = "safe"
    else:
        max_score = max(d["score"] for d in detected.values())
        if max_score >= 0.7 or urgent:
            risk_level = "urgent"
        elif max_score >= 0.4:
            risk_level = "high"
        else:
            risk_level = "medium"
    
    return {
        "detected": detected,
        "risk_level": risk_level,
        "urgent": urgent,
        "ml_used": ML_MODEL is not None
    }

# ============================================
# STREAMLIT APP
# ============================================

def main():
    # Header
    st.markdown('<h1 class="main-header">🛡️ SecureShe AI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Your Personal Online Safety Assistant for Nigerian Women</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/000000/security-shield-green.png", width=100)
        st.title("About SecureShe AI")
        
        # Model status
        if ML_MODEL:
            st.success("✅ ML Model Loaded")
            st.caption("Using keyword + ML detection")
        else:
            st.info("📊 Keyword-Based Mode")
            st.caption("Reliable detection without ML")
        
        st.markdown("""
        **What we detect:**
        - 🗣️ Harassment & abuse
        - ⚠️ Threats & violence
        - 💰 Blackmail & extortion
        - 👁️ Stalking behavior
        - 🎣 Scams & fraud
        - 🔞 Inappropriate advances
        - 👤 Impersonation
        
        **Privacy Promise:**
        - ✅ Messages analyzed, not stored
        - ✅ Completely confidential
        - ✅ No tracking
        """)
        
        st.divider()
        
        st.subheader("📞 Emergency Contacts")
        for resource in RESOURCES:
            st.markdown(f"**{resource['name']}**  \n{resource['contact']}")
        
        st.divider()
        st.caption("⚠️ If you're in immediate danger, call 112")
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📝 Analyze a Message")
        
        # Consent checkbox
        consent = st.checkbox(
            "I understand this is a support tool and not a replacement for emergency services",
            value=False
        )
        
        # Text input
        message = st.text_area(
            "Paste the message you received:",
            height=150,
            placeholder="Example: 'I will kill you' or 'Send nudes now'",
            help="Your message is analyzed but NOT stored"
        )
        
        # Analyze button
        analyze_btn = st.button("🔍 Analyze Message", type="primary", disabled=not consent)
        
        if analyze_btn and message:
            with st.spinner("Analyzing message..."):
                result = analyze_message(message)
                
                st.divider()
                
                # Display results
                if result["risk_level"] == "safe":
                    st.markdown('<div class="safe-box">', unsafe_allow_html=True)
                    st.success("✅ **No Immediate Risks Detected**")
                    st.write("This message doesn't show obvious warning signs. However, trust your instincts—if something feels wrong, it probably is.")
                    if result["ml_used"]:
                        st.caption("🤖 Analyzed with ML + Keywords")
                    else:
                        st.caption("📊 Analyzed with keyword detection")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                else:
                    # Urgent warning
                    if result["urgent"]:
                        st.markdown('<div class="danger-box">', unsafe_allow_html=True)
                        st.error("🚨 **URGENT WARNING**")
                        st.write("**You may be in danger. If you feel unsafe, contact emergency services immediately: 112**")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Risk level
                    if result["risk_level"] == "urgent":
                        st.markdown('<div class="danger-box">', unsafe_allow_html=True)
                        st.error(f"🔴 **Risk Level: {result['risk_level'].upper()}**")
                    elif result["risk_level"] == "high":
                        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
                        st.warning(f"🟠 **Risk Level: {result['risk_level'].upper()}**")
                    else:
                        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
                        st.warning(f"🟡 **Risk Level: {result['risk_level'].upper()}**")
                    
                    # Detected risks
                    st.write("**Detected Risks:**")
                    for category, info in result["detected"].items():
                        confidence_pct = int(info["score"] * 100)
                        evidence_str = ", ".join(info["evidence"][:3])
                        st.write(f"• **{category.replace('_', ' ').title()}**: {confidence_pct}% confidence")
                        st.caption(f"   Matched: {evidence_str}")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Advice
                    st.subheader("💡 What You Should Do")
                    
                    for category in result["detected"].keys():
                        template = ADVICE_TEMPLATES.get(category)
                        if template:
                            with st.expander(template["title"], expanded=True):
                                for step in template["steps"]:
                                    st.write(step)
        
        elif analyze_btn and not message:
            st.warning("⚠️ Please enter a message to analyze")
    
    with col2:
        st.subheader("📊 System Status")
        
        # Model status
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        if ML_MODEL:
            st.metric("Detection Mode", "🤖 Hybrid", "Keyword + ML")
        else:
            st.metric("Detection Mode", "📊 Keywords", "Fast & Reliable")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Sensitivity", "High", "Lowered thresholds")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Categories", "7", "Types of threats")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.divider()
        
        st.subheader("🧪 Try Example Messages")
        
        examples = {
            "🔴 Threat": "I will kill you if you don't listen",
            "💰 Blackmail": "Send nudes or I leak your photos",
            "🎣 Scam": "Send your account number to claim prize",
            "😡 Harassment": "You are stupid mumu olodo",
            "🟢 Safe": "How are you doing today?"
        }
        
        for label, example in examples.items():
            if st.button(label, key=label, use_container_width=True):
                st.session_state.example_message = example
                st.rerun()
    
    # Pre-fill example if clicked
    if 'example_message' in st.session_state:
        st.info(f"📝 Example loaded: {st.session_state.example_message}")
        del st.session_state.example_message
    
    # Footer
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.caption("🔒 Your privacy is protected")
    with col2:
        st.caption("🇳🇬 Built for Nigerian women")
    with col3:
        st.caption("💪 Powered by SecureShe AI")

if __name__ == "__main__":
    main()