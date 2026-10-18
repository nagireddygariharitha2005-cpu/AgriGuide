"""
Developer Profile and Intent Classifier Service for AgriGuide.
Provides centralized developer metadata, rich digital resume presentation,
and robust developer-intent detection.
"""

import re
from typing import Dict, Any

DEVELOPER_PROFILE: Dict[str, Any] = {
    "developer_name": "Nagireddygari Haritha",
    "photo_url": "/static/images/haritha.jpg",
    "college": "PBR Visvodaya Institute of Technology and Sciences",
    "degree": "B.Tech",
    "department": "Computer Science and Engineering (CSE)",
    "year": "3rd Year",
    "expected_graduation": "2028",
    "location": "Madanapalli, Tirupathi",
    "email": "nagireddygariharitha2005@gmail.com",
    "role": "Developer",
    "technical_skills": ["Python", "SQL", "Excel"],
    "development_tools": [
        "Antigravity",
        "Visual Studio Code",
        "Claude",
        "AI-assisted development tools"
    ],
    "project_name": "AgriGuide – AI-Powered Agricultural Assistant",
    "about_developer": (
        "Nagireddygari Haritha is a B.Tech Computer Science and Engineering student and "
        "the developer of AgriGuide, an AI-powered agricultural assistant designed to provide "
        "accessible agricultural guidance through AI-based recommendations, multilingual "
        "chatbot interaction, crop image analysis, fertilizer guidance and agricultural information."
    ),
    "education": {
        "degree": "B.Tech – Computer Science and Engineering",
        "college": "PBR Visvodaya Institute of Technology and Sciences",
        "timeline": "3rd Year | Expected Graduation: 2028"
    },
    "project_description": (
        "AgriGuide is an AI-powered agricultural assistant that helps users with crop recommendations, "
        "agricultural questions, fertilizer guidance, crop image analysis and agricultural price information. "
        "The system supports English, Telugu and Tanglish interactions and combines Gemini-based AI capabilities "
        "with a local agronomic fallback system for reliable structured responses."
    ),
    "developer_role_description": (
        "Project Developer. Developed using Antigravity and Visual Studio Code with assistance from "
        "Claude and other modern AI development tools. Integrates Gemini AI for agricultural chat, "
        "multimodal leaf disease vision, and automated agronomic recommendations."
    ),
    "ai_development_disclosure": (
        "AgriGuide was developed using Antigravity and Visual Studio Code, with AI-assisted "
        "development support from Claude and other AI tools. The application itself also integrates "
        "Gemini AI for agricultural conversations, recommendations and multimodal image analysis."
    ),
    "capabilities": [
        "AI-powered agricultural chatbot",
        "English, Telugu and Tanglish support",
        "AI-based crop recommendations",
        "Crop image analysis",
        "Fertilizer search and calculation",
        "Agricultural price / MSP reference information",
        "Local agronomic fallback system",
        "Secure authentication",
        "Responsive web interface"
    ]
}

# Regex patterns for detecting developer / project-creation intent
DEVELOPER_INTENT_PATTERNS = [
    # Direct questions about developer/creator
    r"\bwho (developed|created|made|built|designed|coded|programmed|worked on)\b",
    r"\bwho (is|are) (the|your) (developer|creator|maker|builder|author|architect|engineer|founder|coder)\b",
    r"\bwho (is|are) behind (you|u|this|agriguide|the project|the app|the chatbot)\b",
    r"\b(tell me|tell us|know|info|information|details|about) (about )?(the |your )?(developer|creator|author|maker|haritha)\b",
    r"\b(what is|what's) (the |your )?(developer|creator)('s)? (name|details|education|skills|college|background)\b",
    r"\bwhere does (the |your )?developer (study|live|work|belong)\b",
    r"\bwhat are (the |your )?developer('s)? (skills|tools|technologies)\b",
    r"\b(developer|creator) (details|info|information|profile|resume|bio|contact|email|skills|education)\b",
    r"\b(about|who is) (haritha|nagireddygari|nagireddygari haritha)\b",
    
    # Casual/conversational phrasing
    r"\bwho made (u|you)\b",
    r"\bwho (built|created|developed) (u|you)\b",
    r"\byour (developer|creator|maker|author|founder|master|parent)\b",
    
    # Questions regarding project creation, technologies, and AI development tools
    r"\b(how was|how is) (this|agriguide|the project|the app|the chatbot) (developed|built|created|made)\b",
    r"\bwhat (tools|tech|technologies|frameworks|software) were used to (develop|build|create|make) (this|agriguide|the project|the app|the chatbot|you|u)\b",
    r"\b(was|is|did) (ai|claude|antigravity|llm) (used|help|assist) (to develop|in developing|for this|to build)\b",
    r"\bwho used antigravity\b",
    r"\bwho developed .* using antigravity\b",
    r"\bdevelopment (team|tools|technologies|stack|process)\b",
    r"\bproject (developer|creator|author)\b"
]

COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in DEVELOPER_INTENT_PATTERNS]

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
    creator, development tools (Antigravity/Claude), or project creation.
    Safeguards real agricultural farming questions from false positives.
    """
    if not query or not isinstance(query, str):
        return False

    cleaned = query.strip().lower()
    if not cleaned:
        return False

    # Check for direct developer names or tool-specific questions
    if any(k in cleaned for k in ["haritha", "nagireddygari", "antigravity", "claude"]):
        return True

    # Check developer intent regex patterns
    matched_intent = any(pattern.search(cleaned) for pattern in COMPILED_PATTERNS)

    if not matched_intent:
        return False

    # If pattern matched, verify it is not an agricultural inquiry with a coincidental word
    # e.g., "Who developed this new variety of paddy seed?" vs "Who developed AgriGuide?"
    tokens = set(re.findall(r"[a-zA-Z]+", cleaned))
    agri_matches = tokens.intersection(AGRI_KEYWORDS)

    # If heavy agricultural context is present and no explicit developer keyword is present, avoid false positive
    has_explicit_dev_word = any(w in cleaned for w in [
        "developer", "creator", "agriguide", "chatbot", "app", "application",
        "project", "system", "website", "who made you", "who made u", "who built you",
        "who built u", "who developed you", "your developer", "your creator"
    ])

    if agri_matches and not has_explicit_dev_word:
        return False

    return True


def build_developer_profile_html() -> str:
    """
    Builds a visually stunning, responsive Developer Profile Card / Mini Resume HTML component.
    Adheres to the AgriGuide visual identity, mobile responsiveness, and clean card architecture.
    """
    p = DEVELOPER_PROFILE
    skills_badges = "".join([f'<span class="dev-badge dev-badge-skill">{skill}</span>' for skill in p["technical_skills"]])
    tools_badges = "".join([f'<span class="dev-badge dev-badge-tool">{tool}</span>' for tool in p["development_tools"]])
    capabilities_items = "".join([f'<li><span class="cap-dot">✓</span> {cap}</li>' for cap in p["capabilities"]])

    html = f"""
<div class="dev-profile-card">

    <!-- Card Header with Photo & Identity -->
    <div class="dev-header">
        <div class="dev-avatar-container">
            <img src="{p['photo_url']}" 
                 alt="{p['developer_name']}" 
                 class="dev-avatar-img" 
                 onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';" />
            <div class="dev-avatar-fallback">
                <span>NH</span>
            </div>
            <div class="dev-status-badge" title="Project Developer">🌱</div>
        </div>
        <div class="dev-identity">
            <div class="dev-role-pill">{p['role']}</div>
            <h2 class="dev-name">{p['developer_name']}</h2>
            <p class="dev-headline">B.Tech CSE | {p['year']}</p>
            <p class="dev-institution">{p['college']}</p>
        </div>
    </div>

    <!-- About Section -->
    <div class="dev-section">
        <h4 class="dev-section-title">
            <span class="sec-icon">👤</span> About the Developer
        </h4>
        <p class="dev-text">{p['about_developer']}</p>
    </div>

    <!-- Education Section -->
    <div class="dev-section">
        <h4 class="dev-section-title">
            <span class="sec-icon">🎓</span> Education
        </h4>
        <div class="dev-edu-box">
            <div class="dev-edu-title">{p['education']['degree']}</div>
            <div class="dev-edu-sub">{p['education']['college']}</div>
            <div class="dev-edu-timeline">📅 {p['education']['timeline']}</div>
        </div>
    </div>

    <!-- Skills & Tools Split Grid -->
    <div class="dev-grid-2">
        <div class="dev-section">
            <h4 class="dev-section-title">
                <span class="sec-icon">💻</span> Technical Skills
            </h4>
            <div class="dev-badges-wrap">
                {skills_badges}
            </div>
        </div>
        <div class="dev-section">
            <h4 class="dev-section-title">
                <span class="sec-icon">🛠️</span> Development Tools
            </h4>
            <div class="dev-badges-wrap">
                {tools_badges}
            </div>
        </div>
    </div>

    <!-- Project Information Card -->
    <div class="dev-section dev-project-box">
        <h4 class="dev-section-title">
            <span class="sec-icon">🌾</span> Project: {p['project_name']}
        </h4>
        <p class="dev-text">{p['project_description']}</p>
        
        <div class="dev-cap-header">Key Architectural Capabilities:</div>
        <ul class="dev-capabilities-list">
            {capabilities_items}
        </ul>
    </div>

    <!-- Developer Role & AI Disclosure -->
    <div class="dev-section dev-disclosure-box">
        <h4 class="dev-section-title">
            <span class="sec-icon">🤖</span> Developer Role & Tooling Disclosure
        </h4>
        <p class="dev-text">{p['ai_development_disclosure']}</p>
    </div>

    <!-- Contact & Location Footer -->
    <div class="dev-contact-footer">
        <div class="dev-contact-item">
            <span class="contact-icon">📧</span>
            <a href="mailto:{p['email']}" class="dev-email-link">{p['email']}</a>
        </div>
        <div class="dev-contact-item">
            <span class="contact-icon">📍</span>
            <span>{p['location']}</span>
        </div>
    </div>

</div>
"""
    return html.strip()


def get_developer_profile_response() -> Dict[str, Any]:
    """
    Returns the complete structured API response for developer queries,
    containing both rich HTML for UI rendering and clean text summary for speech/text clients.
    """
    plain_summary = (
        f"{DEVELOPER_PROFILE['developer_name']} is a B.Tech Computer Science and Engineering student at "
        f"{DEVELOPER_PROFILE['college']} (3rd Year, Class of {DEVELOPER_PROFILE['expected_graduation']}). "
        f"She is the developer of AgriGuide, an AI-powered agricultural assistant built using Antigravity, "
        f"Visual Studio Code, and AI-assisted development tools like Claude, integrating Gemini AI for "
        f"multilingual farming advice, crop recommendations, and leaf disease vision analysis."
    )

    return {
        "reply": plain_summary,
        "is_developer_profile": True,
        "profile_html": build_developer_profile_html(),
        "developer_profile": DEVELOPER_PROFILE,
        "language": "en",
        "provider": "developer_service",
        "configured": True
    }
