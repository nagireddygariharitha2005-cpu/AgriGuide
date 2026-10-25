"""
Developer Profile and Intent Classifier Service for AgriGuide.
Provides centralized developer metadata, rich digital presentation,
and robust bilingual (English & Telugu) developer and technology intent detection.
"""

import os
import re
from typing import Dict, Any

def get_developer_photo_url() -> str:
    """
    Dynamically checks for the developer's actual uploaded photo in static folders.
    Checks common image extensions (.jpg, .jpeg, .png, .webp) in static/images/ and static/.
    Returns the web path to the photo if found, or the canonical '/static/images/developer.jpg'.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    static_dir = os.path.join(base_dir, "static")
    candidates = [
        ("images", "developer.jpg"),
        ("images", "developer.jpeg"),
        ("images", "developer.png"),
        ("images", "developer.webp"),
        ("", "developer.jpg"),
        ("", "developer.jpeg"),
        ("", "developer.png"),
        ("", "developer.webp"),
    ]
    for sub, fname in candidates:
        full_path = os.path.join(static_dir, sub, fname) if sub else os.path.join(static_dir, fname)
        if os.path.isfile(full_path):
            rel = f"{sub}/{fname}" if sub else fname
            return f"/static/{rel}"

    return "/static/images/developer.jpg"

DEVELOPER_PROFILE: Dict[str, Any] = {
    "developer_name": "Haritha Nagireddygari",
    "role": "Solo Student Developer",
    "qualification": "B.Tech CSE",
    "education": "B.Tech CSE",
    "degree": "B.Tech",
    "department": "Computer Science and Engineering (CSE)",
    "project": "AgriGuide – Smart Fertilizer Information and Farmer Assistance System",
    "project_title": "AgriGuide – Smart Fertilizer Information and Farmer Assistance System",
    "project_type": "Solo Mini-Project (Developed Individually)",
    "college": "PBR Visvodaya Institute of Technology and Sciences",
    "location": "Madanapalli, Tirupathi",
    "email": "nagireddygariharitha2005@gmail.com",
    "photo_url": "/static/images/developer.jpg",
    "photo_url_alt": "/static/developer.jpg",
    "description": (
        "Individually developed AgriGuide as a solo mini-project to help farmers access fertilizer information, "
        "crop recommendations, agricultural price information, and AI farming assistance."
    ),
    "technologies": [
        {
            "name": "Python",
            "category": "Backend Core",
            "icon": "🐍",
            "description": "The main programming language used to build the server logic, perform agricultural calculations, and connect services."
        },
        {
            "name": "Flask",
            "category": "Web Framework",
            "icon": "🌶️",
            "description": "A lightweight Python web framework used to create URL routes, manage user sessions, and render HTML templates."
        },
        {
            "name": "HTML",
            "category": "Page Structure",
            "icon": "📄",
            "description": "The markup language used to build the structure and elements of all web pages, forms, and farmer input fields."
        },
        {
            "name": "CSS",
            "category": "Styling & Design",
            "icon": "🎨",
            "description": "The stylesheet language used to design the responsive green theme, mobile layouts, and modern visual cards."
        },
        {
            "name": "JavaScript",
            "category": "Client Interaction",
            "icon": "⚡",
            "description": "The frontend programming language used for chat messaging, interactive features, microphone speech input, and voice read-aloud."
        },
        {
            "name": "SQLite",
            "category": "Database Storage",
            "icon": "🗄️",
            "description": "A lightweight, serverless relational database used to store registered farmer accounts and secure password hashes."
        },
        {
            "name": "Google Gemini API",
            "category": "Artificial Intelligence",
            "icon": "🤖",
            "description": "The AI model used to provide bilingual conversational answers, analyze crop leaf disease photos, and generate recommendations."
        },
        {
            "name": "GitHub",
            "category": "Version Control",
            "icon": "🐙",
            "description": "The code management platform used to track file changes, manage project versions, and back up the source code."
        },
        {
            "name": "Vercel",
            "category": "Cloud Deployment",
            "icon": "▲",
            "description": "The serverless cloud platform used to host the deployed website online and execute the Flask application at zero cost."
        }
    ],
    "capabilities": [
        "AI-powered bilingual agricultural chatbot (English & Telugu)",
        "Voice speech input & audio read-aloud via Web Speech API",
        "Leaf disease crop photo analysis (Gemini Vision)",
        "Dynamic soil & seasonal crop recommendations",
        "Fertilizer catalog & acreage split-dosage calculator",
        "Official MSP crop market benchmark prices",
        "Local agronomic offline fallback rules",
        "Secure user authentication with password hashing"
    ]
}

# Regex patterns for detecting questions about developer / creator
DEVELOPER_INTENT_PATTERNS = [
    # English direct questions
    r"\bwho (developed|created|made|built|designed|coded|programmed|worked on)\b",
    r"\bwho (is|are) (the|your) (developer|creator|maker|builder|author|architect|engineer|founder|coder)\b",
    r"\bwho (is|are) behind (you|u|this|agriguide|the project|the app|the chatbot)\b",
    r"\b(tell me|tell us|know|info|information|details|about) (about )?(the |your )?(developer|creator|author|maker|haritha)\b",
    r"\b(what is|what's) (the |your )?(developer|creator)('s)? (name|details|education|skills|college|background)\b",
    r"\bwhere does (the |your )?developer (study|live|work|belong)\b",
    r"\b(developer|creator) (details|info|information|profile|resume|bio|contact|email|skills|education|photo)\b",
    r"\b(about|who is) (haritha|nagireddygari|haritha nagireddygari)\b",
    r"\bwho made (u|you)\b",
    r"\bwho (built|created|developed) (u|you)\b",
    r"\byour (developer|creator|maker|author|founder)\b",
    r"\bproject (developer|creator|author)\b",
    r"\bwho developed agriguide\b",
    r"\bwho created agriguide\b",

    # Telugu script patterns
    r"ఎవరు (తయారు|డెవలప్|రూపొందించారు|చేశారు|సృష్టించారు|రాశారు)",
    r"(డెవలపర్|క్రియేటర్|హరిత) ఎవరు",
    r"ఈ (ప్రాజెక్ట్|యాప్|వెబ్‌సైట్|చాట్‌బాట్) ఎవరు చేశారు",
    r"హరిత గురించి చెప్పండి",
    r"డెవలపర్ (వివరాలు|సమాచారం|ఫోటో)",
    r"ఎవరు చేశారు",

    # Tanglish (Romanized Telugu) patterns
    r"\bevaru (develop|chesaru|create|design|tayar) chesaru\b",
    r"\b(project|app|website) evaru (chesaru|develop chesaru)\b",
    r"\bdeveloper evaru\b",
    r"\bharitha evaru\b",
    r"\b(tell me|details|info) about haritha\b"
]

# Regex patterns for detecting questions specifically about technologies / programming languages used
TECH_INTENT_PATTERNS = [
    # English questions about technologies
    r"\bwhat (technologies|tech|tools|languages|programming languages|frameworks|software|stack) (are|were|did) (used|used in|the developer use)\b",
    r"\bwhich (languages|programming languages|technologies|tools|frameworks) (are|were|did) (used|the developer use)\b",
    r"\btechnologies (used|in this project|in agriguide)\b",
    r"\bprogramming languages (used|in this project|in agriguide)\b",
    r"\bwhat is (the )?(tech stack|technology stack)\b",
    r"\bhow is (this project|agriguide) (built|coded|programmed)\b",

    # Telugu questions about technologies
    r"ఏ (టెక్నాలజీలు|సాంకేతికతలు|భాషలు|ప్రోగ్రామింగ్ భాషలు) (వాడారు|ఉపయోగించారు)",
    r"ఏ టెక్నాలజీ (వాడారు|ఉపయోగించారు)",
    r"సాంకేతిక వివరాలు",

    # Tanglish questions
    r"\bye (technologies|languages|tech) use chesaru\b",
    r"\bem (technologies|languages|tech) use chesaru\b"
]

COMPILED_DEV_PATTERNS = [re.compile(p, re.IGNORECASE) for p in DEVELOPER_INTENT_PATTERNS]
COMPILED_TECH_PATTERNS = [re.compile(p, re.IGNORECASE) for p in TECH_INTENT_PATTERNS]

# Agricultural keywords to safeguard against false positives
AGRI_KEYWORDS = {
    "crop", "crops", "soil", "soils", "paddy", "rice", "cotton", "maize", "groundnut",
    "chilli", "fertilizer", "fertilizers", "urea", "dap", "potash", "npk", "yield",
    "pest", "pests", "disease", "diseases", "purugu", "mandhu", "panta", "pantalu",
    "vari", "patti", "nela", "nelalu", "kharif", "rabi", "summer", "price", "prices",
    "msp", "mandi", "water", "irrigation", "sowing", "seed", "seeds"
}


def is_developer_query(query: str) -> bool:
    """
    Intelligently determines if a user message is asking about the developer,
    creator, technologies used, or programming languages in English, Telugu, or Tanglish.
    Safeguards real agricultural farming questions from false positives.
    """
    if not query or not isinstance(query, str):
        return False

    cleaned = query.strip().lower()
    if not cleaned:
        return False

    # Check for direct developer names
    if any(k in cleaned for k in ["haritha", "nagireddygari", "హరిత"]):
        return True

    # Check developer intent regex patterns
    matched_dev = any(pattern.search(cleaned) for pattern in COMPILED_DEV_PATTERNS)
    matched_tech = any(pattern.search(cleaned) for pattern in COMPILED_TECH_PATTERNS)

    if not matched_dev and not matched_tech:
        return False

    # If pattern matched, verify it is not an agricultural inquiry with a coincidental word
    # e.g., "Which technology is used in drip irrigation?" vs "What technologies are used in this project?"
    tokens = set(re.findall(r"[a-zA-Z]+", cleaned))
    agri_matches = tokens.intersection(AGRI_KEYWORDS)

    has_explicit_project_word = any(w in cleaned for w in [
        "developer", "creator", "agriguide", "chatbot", "app", "application",
        "project", "system", "website", "who made you", "who made u", "who built you",
        "who built u", "who developed you", "your developer", "your creator",
        "డెవలపర్", "హరిత", "in this project"
    ])

    if agri_matches and not has_explicit_project_word:
        return False

    return True


def get_developer_profile_response(query: str = "") -> Dict[str, Any]:
    """
    Returns the structured API response for developer and technology queries across English and Telugu,
    including the developer photo, developer information, and the 9 verified technologies used.
    """
    p = dict(DEVELOPER_PROFILE)
    p["photo_url"] = get_developer_photo_url()
    cleaned_query = query.strip().lower()

    is_telugu = any("\u0C00" <= c <= "\u0C7F" for c in query) or any(w in cleaned_query for w in ["evaru", "chesaru", "tayar", "ye tech", "em tech"])
    is_tech_question = any(pattern.search(cleaned_query) for pattern in COMPILED_TECH_PATTERNS)

    if is_tech_question:
        # User asked specifically about technologies / programming languages used
        if is_telugu:
            tech_lines = "\n".join([f"• **{t['name']}**: {t['description']}" for t in p["technologies"]])
            reply_text = (
                f"🛠️ **{p['project']} ప్రాజెక్ట్‌లో ఉపయోగించిన సాంకేతికతలు:**\n\n"
                f"{tech_lines}\n\n"
                f"**డెవలపర్:** {p['developer_name']} ({p['role']})\n\n"
                "👉 పూర్తి వివరాల కోసం [డెవలపర్ పేజీని చూడండి](/developers)."
            )
            lang = "te"
        else:
            tech_lines = "\n".join([f"• **{t['name']}** ({t['category']}): {t['description']}" for t in p["technologies"]])
            reply_text = (
                f"🛠️ **Technologies Used in {p['project']}:**\n\n"
                f"{tech_lines}\n\n"
                f"**Developer:** {p['developer_name']} ({p['role']})\n\n"
                "👉 You can view the complete technical cards on the [Developer Information Page](/developers)."
            )
            lang = "en"
    else:
        # User asked about the developer / who created the project
        tech_summary = ", ".join([t["name"] for t in p["technologies"]])
        if is_telugu:
            reply_text = (
                "👩‍💻 **AgriGuide డెవలపర్ సమాచారం:**\n\n"
                f"![{p['developer_name']}]({p['photo_url']})\n\n"
                f"• **డెవలపర్:** {p['developer_name']} (హరిత నాగిరెడ్డిగారి)\n"
                f"• **విద్యార్హత:** {p['education']}\n"
                f"• **ప్రాజెక్ట్:** {p['project']}\n"
                f"• **ప్రాజెక్ట్ రకం:** సోలో మినీ ప్రాజెక్ట్ (వ్యక్తిగతంగా అభివృద్ధి చేయబడింది)\n"
                f"• **కళాశాల:** {p['college']}\n"
                f"• **వివరణ:** {p['description']}\n\n"
                f"**ఉపయోగించిన సాంకేతికతలు:** {tech_summary}\n\n"
                "👉 పూర్తి వివరాల కోసం [డెవలపర్ సమాచార పేజీని చూడండి](/developers)."
            )
            lang = "te"
        else:
            reply_text = (
                "👩‍💻 **AgriGuide Developer Information:**\n\n"
                f"![{p['developer_name']}]({p['photo_url']})\n\n"
                f"• **Developer:** {p['developer_name']}\n"
                f"• **Qualification:** {p['education']}\n"
                f"• **Project Title:** {p['project']}\n"
                f"• **Project Nature:** Solo Mini-Project (Developed Individually)\n"
                f"• **Institution:** {p['college']}\n"
                f"• **About the Project:** {p['description']}\n\n"
                f"**Technologies Used:** {tech_summary}\n\n"
                "👉 You can view the full profile and technical breakdown on the [Developer Information Page](/developers)."
            )
            lang = "en"

    return {
        "reply": reply_text,
        "is_developer_profile": True,
        "photo_url": p["photo_url"],
        "developer_name": p["developer_name"],
        "developer_profile": p,
        "language": lang,
        "provider": "developer_service",
        "configured": True
    }
