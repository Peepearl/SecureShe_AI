"""
SecureShe AI - Clean Interface Version
Online Safety Assistant for Nigerian Women
Run with: streamlit run app.py
"""

import streamlit as st
import re
import pickle
from datetime import datetime

# ============================================
# PAGE CONFIGURATION
# ============================================

st.set_page_config(
    page_title="SecureShe AI - Online Safety Assistant",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
# CUSTOM CSS
# ============================================

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
</style>
""", unsafe_allow_html=True)

# ============================================
# CONFIGURATION - KEYWORDS & THRESHOLDS
# ============================================

KEYWORDS = {
    "harassment": [
        # English - expanded
        "idiot", "stupid", "shut up", "worthless", "trash", "ugly", "die",
        "hate you", "loser", "dumb", "fool", "pathetic", "waste", "shut your",
        "disgusting", "useless", "annoying", "terrible", "awful", "horrible",
        "fat", "skinny", "bitch", "whore", "slut", "hoe", "thot",
        "you're stupid", "you are stupid", "go die", "kill yourself",
        "nobody likes you", "everyone hates you", "piece of shit",
        # Nigerian Pidgin - expanded
        "mumu", "olodo", "ode", "werey", "ashawo", "olofofo", 
        "foolish", "yeye", "you no get sense", "you dey craze", 
        "mad person", "your papa", "your mama", "ode buruku",
        "goat", "cow", "pig", "monkey", "baboon", "mtchew",
        "nonsense", "rubbish", "idiat", "bastard", "son of a bitch"
    ],
    "threats": [
        # Direct threats - expanded
        "kill", "hurt", "beat", "destroy", "ruin", "harm", "damage",
        "suffer", "pain", "die", "dead", "finish", "end you", "murder",
        "stab", "shoot", "attack", "punch", "slap", "hit", "strike",
        "break your", "smash your", "crush", "eliminate", "rape",
        # Warning phrases - expanded
        "watch your back", "you will regret", "i know where you live",
        "i know your address", "i will find you", "coming for you",
        "wait for me", "i'm coming for you", "meet me outside",
        "see what happens", "you'll see", "just wait",
        # Nigerian - expanded
        "i go deal", "i go show you", "you go see", "make i no catch",
        "thunder fire", "i fit finish", "i go wound", "i go scatter",
        "e go pain you", "you don enter wahala", "you go hear am",
        "i go beat", "i go kpai", "you go die", "dem go kill you",
        "boys go come for you", "area boys", "i go send boys"
    ],
    "blackmail": [
        # Explicit blackmail - expanded
        "send nudes", "send nude", "leak", "expose", "publish", "share your",
        "pay me or", "send money or", "or i will", "or else",
        "i have your photos", "i have your pics", "i have screenshots",
        "i recorded you", "i have video", "i saved it",
        "everyone will see", "i'll tell everyone", "post online",
        "send to your family", "send to your friends", "send to your boss",
        # Nigerian context - expanded
        "make you send", "or i go post", "i fit share", "send am or",
        "i get your", "wahala go burst", "scandal go out",
        "i go show your people", "your family go see", "send recharge card or"
    ],
    "stalking": [
        # Location references - expanded
        "i saw you", "i know where", "i was outside", "i was at",
        "i'm following", "tracking you", "watching you", "i can see you",
        "your location", "i know your", "following you", "behind you",
        "i see you at", "you live at", "you work at", "you go to",
        "i know your house", "i know your school", "i know your office",
        "i'm outside your", "i'm near your", "i'm watching your",
        # Nigerian - expanded
        "i dey follow you", "i see where you dey", "i know your area",
        "i sabi where you dey", "i fit trace you", "i don mark you"
    ],
    "scams": [
        # Financial requests - expanded
        "transfer money", "send money", "pay", "account number", 
        "bank account", "atm pin", "password", "otp", "bvn",
        "claim your prize", "you won", "verify your account",
        "processing fee", "activation fee", "customs fee", "delivery fee",
        "congratulations you", "selected winner", "lottery", "jackpot",
        "urgent payment", "tax clearance", "refund", "compensation",
        "inheritance", "beneficiary", "million dollars", "usd",
        # Nigerian platforms - expanded
        "419", "recharge card", "opay", "palmpay", "kuda",
        "paystack", "flutterwave", "mtn", "glo", "airtel", "9mobile",
        "send me card", "buy me card", "help me with", "borrow me",
        "i need urgent 2k", "abeg send", "quick loan"
    ],
    "inappropriate_advances": [
        # Sexual content - expanded
        "send pics", "send nudes", "sexy", "naked", "sex", "fuck",
        "hook up", "come over", "sleep with", "make love", "bed",
        "your body", "show me", "i want you", "turn me on", "horny",
        "boobs", "breast", "ass", "butt", "dick", "pussy", "vagina",
        "touch you", "kiss you", "lick", "suck", "blow job", "head",
        "masturbate", "cum", "orgasm", "wet", "hard", "erection",
        # Nigerian - expanded
        "make we link", "come my place", "i wan see you",
        "how far with your body", "you fine sha", "your backside",
        "oya come", "make we knack", "gbola", "toto", "konji"
    ],
    "impersonation": [
        "fake account", "impersonate", "pretending to be you",
        "posing as you", "using your photos", "using your name",
        "clone", "duplicate account", "someone using your",
        "stolen identity", "copied your profile", "hacked your account"
    ]
}

THRESHOLDS = {
    "harassment": 0.10,           # Very sensitive
    "threats": 0.10,              # Very sensitive  
    "blackmail": 0.10,            # Very sensitive
    "stalking": 0.10,             # Very sensitive
    "scams": 0.10,                # Very sensitive
    "inappropriate_advances": 0.10, # Very sensitive
    "impersonation": 0.10,        # Very sensitive
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
# DETECTION FUNCTIONS
# ============================================

def simple_keyword_match(text, keywords):
    """Simple keyword matching"""
    text_lower = text.lower()
    matched = []
    
    for keyword in keywords:
        keyword_lower = keyword.lower()
        if keyword_lower in text_lower:
            matched.append(keyword)
    
    return len(matched), matched

def analyze_message(text):
    """Analyze message for threats - HIGHLY SENSITIVE"""
    detected = {}
    text_lower = text.lower()
    
    # SEVERITY MULTIPLIERS - Different words = different severity
    severity_multipliers = {
        # CRITICAL threats (instant red flag)
        "threats": {
            "kill": 3.0, "murder": 3.0, "rape": 3.0, "shoot": 3.0, "stab": 3.0,
            "i will kill": 3.5, "gonna kill": 3.5, "i'll kill": 3.5,
            "i know where you live": 3.0, "i know your address": 3.0,
            "coming for you": 2.5, "watch your back": 2.5,
            "hurt": 2.0, "beat": 2.0, "harm": 2.0, "attack": 2.0,
            "die": 1.8, "dead": 1.8, "finish": 1.5
        },
        "blackmail": {
            "send nudes": 3.0, "send nude": 3.0, "leak": 2.5, "expose": 2.5,
            "or i will": 2.5, "or else": 2.5, "pay me or": 3.0,
            "i have your photos": 2.8, "i recorded you": 2.8,
            "everyone will see": 2.5, "post online": 2.0
        },
        "inappropriate_advances": {
            "send nudes": 3.0, "send nude": 3.0, "naked": 2.5, "sex": 2.0,
            "fuck": 2.5, "pussy": 2.5, "dick": 2.5, "boobs": 2.0,
            "come over": 1.5, "hook up": 1.8, "sleep with": 2.0
        },
        "harassment": {
            "bitch": 2.0, "whore": 2.5, "slut": 2.5, "stupid": 1.5,
            "idiot": 1.5, "ugly": 1.8, "kill yourself": 3.0,
            "go die": 2.5, "hate you": 2.0, "worthless": 2.0
        },
        "scams": {
            "send money": 2.5, "account number": 2.0, "otp": 2.5,
            "bvn": 2.5, "atm pin": 3.0, "password": 2.5,
            "you won": 2.0, "claim your prize": 2.0, "419": 3.0
        },
        "stalking": {
            "i know where you live": 3.0, "i saw you": 2.0, "following you": 2.5,
            "watching you": 2.5, "i'm outside": 2.5, "tracking you": 2.8
        }
    }
    
    # CRITICAL PHRASES - Immediate high-risk detection
    critical_phrases = {
        "threats": [
            "i will kill", "i'll kill", "gonna kill", "going to kill you",
            "i will hurt", "i'll hurt", "gonna hurt you",
            "i will beat", "i'll beat you", "gonna beat",
            "i will destroy", "i'll destroy you",
            "i know where you live", "i know your address",
            "coming for you", "i will find you", "i'm coming for you",
            "you will die", "you gonna die", "you're dead",
            "watch your back", "you will regret", "wait for me",
            "i go kill you", "i go finish you", "i go wound you",
            "thunder fire you", "you go die", "i go kpai you"
        ],
        "blackmail": [
            "send nudes or", "send pics or", "pay me or", "give me money or",
            "or i will leak", "or i'll expose", "or i post",
            "or else i", "if you don't send", "or everyone will see",
            "i have your photos", "i have your nudes", "i recorded you",
            "i'll share your", "i go post your", "i fit leak"
        ],
        "inappropriate_advances": [
            "send nudes", "send nude", "send naked pics",
            "show me your body", "send naked", "i want to see you naked",
            "let me see your", "come sleep with me", "let's have sex",
            "make we knack", "come fuck", "send your pussy"
        ],
        "scams": [
            "send me your account number", "what's your otp",
            "send your bvn", "verify your account now",
            "claim your prize now", "you won", "transfer to this account",
            "send your atm pin", "give me your password"
        ],
        "stalking": [
            "i know where you live", "i saw you at", "i'm outside your",
            "i followed you", "i'm watching you", "i know your house",
            "i see where you dey", "i sabi your house"
        ]
    }
    
    # 1. CHECK CRITICAL PHRASES FIRST (instant 90%+ score)
    for category, phrases in critical_phrases.items():
        for phrase in phrases:
            if phrase in text_lower:
                if category not in detected:
                    detected[category] = {
                        "score": 0.95,  # Very high score
                        "confidence": "critical",
                        "evidence": [phrase],
                        "method": "critical-phrase"
                    }
                else:
                    detected[category]["score"] = 0.95
                    if phrase not in detected[category]["evidence"]:
                        detected[category]["evidence"].append(phrase)
                    detected[category]["confidence"] = "critical"
    
    # 2. CHECK KEYWORDS WITH SEVERITY WEIGHTING
    for category, keywords in KEYWORDS.items():
        match_count, matched = simple_keyword_match(text, keywords)
        
        if match_count > 0:
            # Calculate weighted score based on severity
            total_severity = 0
            multipliers = severity_multipliers.get(category, {})
            
            for word in matched:
                # Get multiplier (default 1.0 for unlisted words)
                multiplier = multipliers.get(word.lower(), 1.0)
                total_severity += multiplier
            
            # Base score: each keyword worth 25%, with severity boost
            base_score = min(match_count * 0.25, 1.0)
            severity_score = min(total_severity * 0.15, 1.0)
            final_score = min(base_score + severity_score, 1.0)
            
            threshold = THRESHOLDS.get(category, 0.10)
            
            if final_score >= threshold:
                if category in detected:
                    # Boost existing detection
                    detected[category]["score"] = min(detected[category]["score"] + final_score * 0.2, 1.0)
                    detected[category]["evidence"].extend(matched[:5])
                else:
                    # Determine confidence level
                    if final_score >= 0.8:
                        confidence = "critical"
                    elif final_score >= 0.6:
                        confidence = "high"
                    elif final_score >= 0.4:
                        confidence = "medium"
                    else:
                        confidence = "low"
                    
                    detected[category] = {
                        "score": round(final_score, 3),
                        "confidence": confidence,
                        "evidence": matched[:5],
                        "method": "keyword-weighted"
                    }
    
    # Try ML model if available
    if ML_MODEL is not None:
        try:
            ml_pred = ML_MODEL.predict([text])[0]
            ml_proba = ML_MODEL.predict_proba([text])[0]
            ml_confidence = max(ml_proba)
            
            if ml_pred != "safe" and ml_confidence >= 0.3:
                if ml_pred in detected:
                    detected[ml_pred]["score"] = min(detected[ml_pred]["score"] + 0.2, 1.0)
                    detected[ml_pred]["method"] = "keyword + ML"
                else:
                    detected[ml_pred] = {
                        "score": round(ml_confidence, 3),
                        "confidence": "high" if ml_confidence > 0.7 else "medium",
                        "evidence": ["ML prediction"],
                        "method": "ML-only"
                    }
        except:
            pass
    
    # Determine urgency and risk level
    urgent = False
    
    # Mark as URGENT for critical threats
    if any(d.get("confidence") == "critical" for d in detected.values()):
        urgent = True
    if "threats" in detected and detected["threats"]["score"] >= 0.6:
        urgent = True
    if "blackmail" in detected and detected["blackmail"]["score"] >= 0.6:
        urgent = True
    if len(detected) >= 3:  # Multiple threat types
        urgent = True
    
    if not detected:
        risk_level = "safe"
    else:
        max_score = max(d["score"] for d in detected.values())
        has_critical = any(d.get("confidence") == "critical" for d in detected.values())
        
        # Aggressive risk classification
        if has_critical or max_score >= 0.85:
            risk_level = "urgent"
        elif max_score >= 0.65 or urgent:
            risk_level = "urgent"
        elif max_score >= 0.45:
            risk_level = "high"
        elif max_score >= 0.25:
            risk_level = "medium"
        else:
            risk_level = "low"
    
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
    
    # Main content - Single column layout
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
    
    # Example buttons (compact)
    st.caption("🧪 Quick test examples:")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    examples = {
        "🔴 Threat": "I will kill you if you don't listen",
        "💰 Blackmail": "Send nudes or I leak your photos",
        "🎣 Scam": "Send your account number to claim prize",
        "😡 Harassment": "You are stupid mumu olodo",
        "🟢 Safe": "How are you doing today?"
    }
    
    with col1:
        if st.button("🔴 Threat", use_container_width=True):
            st.session_state.example_message = examples["🔴 Threat"]
            st.rerun()
    with col2:
        if st.button("💰 Blackmail", use_container_width=True):
            st.session_state.example_message = examples["💰 Blackmail"]
            st.rerun()
    with col3:
        if st.button("🎣 Scam", use_container_width=True):
            st.session_state.example_message = examples["🎣 Scam"]
            st.rerun()
    with col4:
        if st.button("😡 Harassment", use_container_width=True):
            st.session_state.example_message = examples["😡 Harassment"]
            st.rerun()
    with col5:
        if st.button("🟢 Safe", use_container_width=True):
            st.session_state.example_message = examples["🟢 Safe"]
            st.rerun()
    
    # Pre-fill example if clicked
    if 'example_message' in st.session_state:
        message = st.session_state.example_message
        st.info(f"📝 Example loaded: {st.session_state.example_message}")
        del st.session_state.example_message
    
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
                    
                    # Show confidence level with appropriate emoji
                    if info.get("confidence") == "critical":
                        conf_icon = "🚨"
                    elif info.get("confidence") == "high":
                        conf_icon = "⚠️"
                    elif info.get("confidence") == "medium":
                        conf_icon = "⚡"
                    else:
                        conf_icon = "ℹ️"
                    
                    evidence_str = ", ".join(info["evidence"][:4])
                    st.write(f"{conf_icon} **{category.replace('_', ' ').title()}**: {confidence_pct}% confidence")
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