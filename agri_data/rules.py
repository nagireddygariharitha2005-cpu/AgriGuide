"""
Agronomic matching rules and fallback recommendation engine for AgriGuide.
Produces scientifically grounded, rich dynamic recommendations adhering to the strict schema.
"""

from typing import Dict, Any, List
from .crops import CROPS_DATABASE
from .soils import SOIL_PROFILES


def evaluate_agronomic_recommendation(normalized: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates soil type, season, water availability, crop preference, and farmer queries.
    Returns a structured dictionary matching the strict Phase 5 schema.
    """
    soil = (normalized.get("soil_type") or "black").lower()
    season = (normalized.get("season") or "kharif").lower()
    water = (normalized.get("water_availability") or "medium").lower()
    crop_pref = (normalized.get("crop") or "").lower()
    lang = normalized.get("language") or "te"

    # Score each candidate crop in the database
    scored_candidates = []

    for crop_id, crop_data in CROPS_DATABASE.items():
        score = 50  # Base score

        # 1. Soil compatibility
        if soil in crop_data["suitable_soils"]:
            score += 25
        else:
            score -= 20

        # 2. Season compatibility
        if season in crop_data["suitable_seasons"]:
            score += 20
        else:
            score -= 25

        # 3. Water availability alignment
        req = crop_data["water_requirement"]
        if water == "high":
            if req == "high":
                score += 15
            elif req == "medium":
                score += 10
            elif req == "low":
                score += 0
        elif water == "medium":
            if req == "medium":
                score += 15
            elif req == "low":
                score += 10
            elif req == "high":
                score -= 15
        elif water == "low":
            if req == "low":
                score += 20
            elif req == "medium":
                score += 5
            elif req == "high":
                score -= 30

        # 4. Preferred crop bonus
        if crop_pref and crop_pref == crop_id:
            score += 20

        # Bound score between 40 and 98
        bounded_score = max(40, min(score, 98))
        scored_candidates.append((bounded_score, crop_data))

    # Sort descending by score
    scored_candidates.sort(key=lambda x: x[0], reverse=True)

    # Pick top 2 or 3 recommendations
    top_matches = scored_candidates[:3]

    primary_crops = []
    for score, crop in top_matches:
        primary_crops.append({
            "name_en": crop["name_en"],
            "name_te": crop["name_te"],
            "suitability_score": score,
            "description_en": crop["description_en"],
            "description_te": crop["description_te"],
            "growing_duration": crop["growing_duration"],
            "soil_health_tips": crop["soil_health_tips"],
            "fertilizer_schedule": crop["fertilizer_schedule"],
            "irrigation_advice": crop["irrigation_advice"],
            "expected_yield": crop["expected_yield"],
            "sowing_guidance": crop["sowing_guidance"],
            "diseases_and_pests": crop["diseases_and_pests"],
            "precautions_en": crop["precautions_en"],
            "precautions_te": crop["precautions_te"]
        })

    # Retrieve soil context if available
    soil_profile = SOIL_PROFILES.get(soil, SOIL_PROFILES["black"])

    general_advice_en = (
        f"For {soil_profile['name_en']} during {season.capitalize()} season with {water} water availability: "
        "Conduct a soil test prior to sowing. Apply 4-5 tonnes of organic FYM per acre. "
        "Treat all seeds with bio-fungicide (Trichoderma viride @ 10g/kg seed) to prevent damping off."
    )
    general_advice_te = (
        f"{soil_profile['name_te']} లో {season.upper()} సీజన్ లో {water} నీటి లభ్యతతో సాగు చేసేటప్పుడు: "
        "విత్తే ముందు విధిగా భూసార పరీక్ష చేయించండి. ఎకరానికి 4-5 ట్రాక్టర్ల పశువుల ఎరువు వేయండి. "
        "మొలక కుళ్లు తెగులు రాకుండా విత్తనాలను ట్రైకోడెర్మా విరిడె (కిలో విత్తనానికి 10 గ్రాములు) తో శుద్ధి చేయండి."
    )

    warnings_en = (
        "Avoid water stagnation in root zones. Use balanced fertilizers rather than excessive urea. "
        "Consult your local Mandal Agricultural Officer or Rythu Vedika for certified seeds."
    )
    warnings_te = (
        "పొలంలో నీరు నిల్వ ఉండకుండా డ్రైనేజీ కాలువలు తీయండి. విచ్చలవిడిగా యూరియా వాడకండి. "
        "నాణ్యమైన విత్తనాల కొరకు స్థానిక వ్యవసాయ విస్తరణాధికారి (AEO) లేదా రైతు వేదికను సంప్రదించండి."
    )

    return {
        "language": lang,
        "primary_crops": primary_crops,
        "general_advice_en": general_advice_en,
        "general_advice_te": general_advice_te,
        "warnings_en": warnings_en,
        "warnings_te": warnings_te
    }
