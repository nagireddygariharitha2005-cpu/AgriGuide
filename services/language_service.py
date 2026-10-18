"""
Language service for AgriGuide:
Detects language mode (English, Telugu script, or Romanized Telugu / Tanglish)
and normalizes diverse multilingual farmer inputs into standardized agronomic attributes.
"""

import re
from typing import Dict, Any, Optional

# Telugu Unicode range
TELUGU_CHAR_PATTERN = re.compile(r"[\u0C00-\u0C7F]")

# Common transliterated / Romanized Telugu agricultural keywords
TANGLISH_KEYWORDS = {
    "nela", "nelalu", "panta", "pantalu", "purugu", "mandhu", "mandulu", "eppudu",
    "veyali", "kottali", "thota", "neeru", "neeti", "vari", "patti", "verusanaga",
    "mokkajonna", "mirapa", "kharif", "rabi", "entha", "chesukovali", "pasupu",
    "pesara", "minumu", "kandulu", "sodi", "ragulu", "dhigiubadi", "thakkuva",
    "ekkuva", "bagundi", "raithu", "rythu", "vithanali", "vithanam", "varsham",
    "chettu", "aaku", "matti", "nallaregadi", "erranela", "isukanela", "bankamatti",
    "urea", "dap", "potash", "eruvulu", "eruvu"
}

SOIL_SYNONYMS = {
    "black": ["black", "black soil", "నల్లరేగడి", "నల్లరేగడి నేల", "నల్ల నేల", "nalla regadi", "nallaregadi", "regadi", "black cotton"],
    "red": ["red", "red soil", "ఎర్ర నేల", "ఎర్రమట్టి", "ఎర్రరేగడి", "erra nela", "erranela", "erra matti", "lal mitti"],
    "alluvial": ["alluvial", "alluvial soil", "ఒండ్రు నేల", "ఒండ్రు మట్టి", "ondru nela", "ondrumatti", "ganga nela"],
    "sandy": ["sandy", "sandy soil", "ఇసుక నేల", "ఇసుక మట్టి", "isuka nela", "isukanela", "isuka"],
    "clay": ["clay", "clay soil", "బంకమట్టి", "బంకమట్టి నేల", "banka matti", "bankamatti", "banka"],
    "loamy": ["loamy", "loamy soil", "గరప నేల", "దుబ్బ నేల", "దుబ్బ", "garapa nela", "dubba nela", "loam"]
}

SEASON_SYNONYMS = {
    "kharif": ["kharif", "ఖరీఫ్", "వర్షాకాలం", "monsoon", "varshakalam", "rainy", "sarva"],
    "rabi": ["rabi", "రబీ", "శీతాకాలం", "winter", "seethakalam", "dalva", "chalikalam"],
    "summer": ["summer", "ఎండాకాలం", "zaid", "endakalam", "yasangi", "summer crop"]
}

WATER_SYNONYMS = {
    "high": ["high", "ఎక్కువ", "అధిక", "బోరు బావి", "కాలువ నీరు", "ekkuva", "bore", "canal", "abundant", "baga"],
    "medium": ["medium", "మధ్యస్థం", "సాధారణ", "బోరు", "బావి", "madhyastham", "paravaledu", "moderate", "normal"],
    "low": ["low", "తక్కువ", "స్వల్ప", "వర్షాధారం", "డ్రై", "thakkuva", "rainfed", "dryland", "bore ledhu", "no water"]
}

CROP_SYNONYMS = {
    "cotton": ["cotton", "పత్తి", "patti", "prathi"],
    "rice": ["rice", "paddy", "వరి", "vari", "biyyam", "dhan"],
    "maize": ["maize", "corn", "మొక్కజొన్న", "mokkajonna", "makka"],
    "groundnut": ["groundnut", "peanut", "వేరుశనగ", "పల్లీ", "verusanaga", "palli"],
    "chilli": ["chilli", "chili", "mirchi", "మిరప", "mirapa"],
    "redgram": ["red gram", "pigeon pea", "కంది", "కందులు", "kandi", "kandulu"],
    "greengram": ["green gram", "moong", "పెసర", "పెసలు", "pesara", "pesalu"],
    "blackgram": ["black gram", "urad", "మినుము", "మినుములు", "minumu", "minumulu"],
    "wheat": ["wheat", "గోధుమ", "గోధుమలు", "godhuma", "godhumalu"],
    "bengalgram": ["chickpea", "bengal gram", "శనగ", "శనగలు", "sanaga", "sanagalu"],
    "tomato": ["tomato", "టమోటా", "తక్కాలి", "tamota", "tamata"]
}


def detect_language(text: Optional[str]) -> str:
    """
    Detects whether the input text is predominantly:
    - 'te': Telugu script
    - 'tanglish': Romanized Telugu (Telugu words in Latin script)
    - 'en': English
    """
    if not text or not isinstance(text, str):
        return "en"
    
    cleaned = text.strip()
    if not cleaned:
        return "en"
    
    # 1. Check for Telugu script
    if TELUGU_CHAR_PATTERN.search(cleaned):
        return "te"
    
    # 2. Check for Tanglish keywords
    tokens = set(re.findall(r"[a-zA-Z]+", cleaned.lower()))
    matches = tokens.intersection(TANGLISH_KEYWORDS)
    if len(matches) >= 1:
        return "tanglish"
    
    return "en"


def _match_category(raw_val: str, free_text: str, category_dict: Dict[str, list]) -> Optional[str]:
    """Helper to match against a category dictionary using both direct value and free text context."""
    combined = f"{raw_val.lower()} {free_text.lower()}".strip()
    
    # Direct match check on key
    for standard_key, synonyms in category_dict.items():
        if raw_val.lower() == standard_key:
            return standard_key
            
    # Synonym containment check
    for standard_key, synonyms in category_dict.items():
        for syn in synonyms:
            if re.search(r"\b" + re.escape(syn) + r"\b", combined, re.IGNORECASE):
                return standard_key
            if syn in combined and len(syn) > 3:
                return standard_key
                
    return None


def normalize_farmer_input(
    soil: Optional[str] = "",
    season: Optional[str] = "",
    water: Optional[str] = "",
    crop_preference: Optional[str] = "",
    farmer_query: Optional[str] = "",
    language_pref: Optional[str] = ""
) -> Dict[str, Any]:
    """
    Normalizes diverse multimodal/multilingual inputs into structured internal attributes.
    Preserves original farmer query.
    """
    raw_query = (farmer_query or "").strip()
    raw_soil = (soil or "").strip()
    raw_season = (season or "").strip()
    raw_water = (water or "").strip()
    raw_crop = (crop_preference or "").strip()

    # Determine overall effective language
    detected_from_query = detect_language(raw_query) if raw_query else "en"
    detected_from_soil = detect_language(raw_soil)
    detected_from_season = detect_language(raw_season)

    if language_pref in ("te", "te-IN"):
        effective_lang = "te"
    elif language_pref in ("tanglish", "te-Latn"):
        effective_lang = "tanglish"
    elif detected_from_query != "en":
        effective_lang = detected_from_query
    elif detected_from_soil == "te" or detected_from_season == "te":
        effective_lang = "te"
    else:
        effective_lang = "en"

    # Match soil
    norm_soil = _match_category(raw_soil, raw_query, SOIL_SYNONYMS) or (raw_soil.lower() if raw_soil else "black")

    # Match season
    norm_season = _match_category(raw_season, raw_query, SEASON_SYNONYMS) or (raw_season.lower() if raw_season else "kharif")

    # Match water
    norm_water = _match_category(raw_water, raw_query, WATER_SYNONYMS) or (raw_water.lower() if raw_water else "medium")

    # Match preferred crop if specified
    norm_crop = _match_category(raw_crop, raw_query, CROP_SYNONYMS)

    return {
        "language": effective_lang,
        "soil_type": norm_soil,
        "season": norm_season,
        "water_availability": norm_water,
        "crop": norm_crop,
        "farmer_query": raw_query,
        "raw_inputs": {
            "soil": raw_soil,
            "season": raw_season,
            "water": raw_water,
            "crop_preference": raw_crop
        }
    }
