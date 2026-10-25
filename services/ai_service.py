"""
AI Service for AgriGuide:
Provides seamless integration with Google Gemini (primary) and OpenAI (fallback).
Handles standard chat completions, multimodal vision, and structured JSON output
with robust error recovery and zero secret leakage.
"""

import os
import json
import logging
import base64
import io
import requests
from typing import Dict, Any, Optional, Tuple, List
from dotenv import load_dotenv
from openai import OpenAI, RateLimitError, APIConnectionError, APIStatusError, AuthenticationError

# Ensure environment variables are loaded
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

logger = logging.getLogger("agriguide.ai")

# Default models
DEFAULT_GEMINI_MODEL = "gemini-3.5-flash-lite"
BACKUP_GEMINI_MODEL = "gemini-flash-lite-latest"
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"


def get_ai_client_and_model() -> Tuple[Optional[OpenAI], Optional[str], Optional[str]]:
    """
    Returns (client, model_name, provider_name).
    Checks GEMINI_API_KEY first, then OPENAI_API_KEY.
    Returns (None, None, None) if neither is configured.
    """
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key and gemini_key.strip():
        model = os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL).strip()
        # Automatically migrate deprecated, 404, or 503-prone model names that cause timeouts
        if model in (
            "gemini-3.1-flash-lite",
            "gemini-3.8-flash",
            "gemini-3.5-flash",
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite",
            "gemini-2.0-flash",
            "gemini-1.5-flash",
            "gemini-pro"
        ):
            model = DEFAULT_GEMINI_MODEL
        client = OpenAI(
            api_key=gemini_key.strip(),
            base_url=GEMINI_BASE_URL,
            timeout=20.0,
            max_retries=1
        )
        return client, model, "gemini"

    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key and openai_key.strip():
        model = os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL).strip()
        client = OpenAI(
            api_key=openai_key.strip(),
            timeout=20.0,
            max_retries=1
        )
        return client, model, "openai"

    return None, None, None


def check_ai_configuration() -> Dict[str, Any]:
    """
    Returns AI configuration diagnostic status without exposing any secret keys or values.
    Safe for production verification on Vercel.
    """
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    gemini_ok = bool(gemini_key and gemini_key.strip())
    openai_ok = bool(openai_key and openai_key.strip())
    configured_model = os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL).strip()
    return {
        "status": "online" if (gemini_ok or openai_ok) else "offline",
        "gemini_configured": gemini_ok,
        "gemini_key_length": len(gemini_key.strip()) if gemini_ok else 0,
        "primary_model": DEFAULT_GEMINI_MODEL,
        "backup_model": BACKUP_GEMINI_MODEL,
        "configured_model": configured_model,
        "openai_configured": openai_ok,
        "environment": "vercel" if bool(os.getenv("VERCEL")) else "local"
    }


def _safe_scrub(text: Any) -> str:
    """Scrubs any potential sensitive strings/keys from log outputs."""
    raw = str(text or "")
    import re
    # Redact Google API key pattern (AIzaSy...)
    return re.sub(r'AIza[0-9A-Za-z-_]{35}', '[REDACTED_GEMINI_KEY]', raw)


def chat_completion(
    messages: List[Dict[str, Any]],
    temperature: float = 0.6,
    max_tokens: int = 8192,
    response_format: Optional[Dict[str, str]] = None
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Executes a chat completion call using chat.completions.create()
    with configured primary (Gemini) or secondary (OpenAI) provider.
    Includes automated fallback across compatible models on quota/status errors.

    Returns:
        (content, provider_name, error_type)
        On success: (reply_text, "gemini"|"openai", None)
        On error: (None, provider_or_none, "missing_key"|"invalid_key"|"quota"|"timeout"|"status_error"|"unknown")
    """
    client, model, provider = get_ai_client_and_model()
    if not client:
        logger.warning("[AI Service] No valid API key configured. Check GEMINI_API_KEY environment variable.")
        return None, None, "missing_key"

    kwargs: Dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    if response_format:
        kwargs["response_format"] = response_format

    try:
        completion = client.chat.completions.create(**kwargs)
        if not completion.choices or not completion.choices[0].message:
            logger.warning(f"[AI Service] Empty completion choice from provider='{provider}' model='{model}'")
            return None, provider, "empty_response"
        content = completion.choices[0].message.content
        return (content.strip() if content else ""), provider, None

    except AuthenticationError as auth_err:
        logger.error(f"[AI Service] Authentication failed for provider='{provider}' model='{model}': {_safe_scrub(auth_err)}")
        return None, provider, "invalid_key"

    except RateLimitError as err:
        logger.warning(f"[AI Service] Rate limit / quota exceeded for provider='{provider}' model='{model}': {_safe_scrub(err)}")
        # Try alternate model if on Google Gemini
        alt_model = BACKUP_GEMINI_MODEL if model != BACKUP_GEMINI_MODEL else DEFAULT_GEMINI_MODEL
        if provider == "gemini" and model != alt_model:
            try:
                logger.info(f"[AI Service] Attempting fallback to backup model='{alt_model}'")
                kwargs["model"] = alt_model
                completion = client.chat.completions.create(**kwargs)
                if completion.choices and completion.choices[0].message:
                    content = completion.choices[0].message.content
                    if content and content.strip():
                        return content.strip(), provider, None
            except Exception as alt_err:
                logger.warning(f"[AI Service] Fallback model='{alt_model}' also failed: {type(alt_err).__name__} - {_safe_scrub(alt_err)}")
        return None, provider, "quota"

    except (APIConnectionError, TimeoutError) as conn_err:
        logger.warning(f"[AI Service] Connection/timeout exception for provider='{provider}' model='{model}': {type(conn_err).__name__} - {_safe_scrub(conn_err)}")
        alt_model = BACKUP_GEMINI_MODEL if model != BACKUP_GEMINI_MODEL else DEFAULT_GEMINI_MODEL
        if provider == "gemini" and model != alt_model:
            try:
                logger.info(f"[AI Service] Retrying connection with backup model='{alt_model}'")
                kwargs["model"] = alt_model
                completion = client.chat.completions.create(**kwargs)
                if completion.choices and completion.choices[0].message:
                    content = completion.choices[0].message.content
                    if content and content.strip():
                        return content.strip(), provider, None
            except Exception as retry_err:
                logger.warning(f"[AI Service] Backup model retry failed: {type(retry_err).__name__} - {_safe_scrub(retry_err)}")
        return None, provider, "timeout"

    except APIStatusError as err:
        logger.error(f"[AI Service] HTTP status error from provider='{provider}' model='{model}': HTTP {err.status_code} - {_safe_scrub(err.message or err)}")
        # If model returned 503, 500, 502, 504, or 404, retry once with alternate model
        alt_model = BACKUP_GEMINI_MODEL if model != BACKUP_GEMINI_MODEL else DEFAULT_GEMINI_MODEL
        if provider == "gemini" and err.status_code in (404, 500, 502, 503, 504) and model != alt_model:
            try:
                logger.info(f"[AI Service] Retrying status error with backup model='{alt_model}'")
                kwargs["model"] = alt_model
                completion = client.chat.completions.create(**kwargs)
                if completion.choices and completion.choices[0].message:
                    content = completion.choices[0].message.content
                    if content and content.strip():
                        return content.strip(), provider, None
            except Exception as retry_err:
                logger.error(f"[AI Service] Backup status retry failed: {type(retry_err).__name__} - {_safe_scrub(retry_err)}")
        return None, provider, "status_error"

    except Exception as exc:
        logger.error(f"[AI Service] Unexpected completion error for provider='{provider}' model='{model}': {type(exc).__name__} - {_safe_scrub(exc)}")
        return None, provider, "unknown"


def ask_agricultural_chat(message: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
    """
    Processes farmer conversational queries across English, Telugu script, and Tanglish.
    Returns a dictionary: {"reply": str, "language": str, "provider": str, "configured": bool}.
    """
    system_instruction = (
        "You are AgriGuide, an expert, compassionate agricultural advisor for Indian farmers. "
        "You serve farmers speaking English, Telugu script (తెలుగు), and Romanized Telugu (Tanglish). "
        "Strict rules:\n"
        "1. LANGUAGE: Detect the farmer's language immediately:\n"
        "   - If input is in Telugu script (తెలుగు), reply in natural, clear Telugu script (తెలుగు).\n"
        "   - If input is in Romanized Telugu (Tanglish, e.g., 'Purugu pattindi em cheyali?'), provide your reply in Telugu script with key terms transliterated so it is simple to read, or provide a bilingual Telugu+English response.\n"
        "   - If input is in English, reply in English.\n"
        "2. PRACTICAL ADVICE: Provide step-by-step, actionable advice covering soil health, seed treatment, irrigation, bio-fertilizers, and integrated pest management (IPM).\n"
        "3. ACCURACY & CAUTION: Do not invent exact live market prices or unverified chemical dosages. "
        "For chemical fungicides or pesticides, always state safe dilution ratios (e.g. per liter of water) and caution farmers to wear protective gear and consult local Rythu Vedika / Krishi Vigyan Kendra (KVK) / Agricultural Officers.\n"
        "4. STRUCTURE: Use clean bullet points, emojis (🌱, 💧, 🌾), and concise paragraphs. Avoid long, confusing technical jargon."
    )

    messages: List[Dict[str, Any]] = [{"role": "system", "content": system_instruction}]
    if conversation_history:
        for turn in conversation_history[-6:]:  # Keep recent context
            if turn.get("role") in ("user", "assistant") and turn.get("content"):
                messages.append({"role": turn["role"], "content": turn["content"]})

    messages.append({"role": "user", "content": message})

    content, provider, error = chat_completion(messages, temperature=0.6, max_tokens=1200)

    if error == "missing_key":
        return {
            "reply": (
                "⚠️ AI assistant is currently in offline mode. Please configure GEMINI_API_KEY in the .env file. "
                "(AI అసిస్టెంట్ ఆఫ్‌లైన్ లో ఉంది. దయచేసి .env ఫైల్ లో API కీ కాన్ఫిగర్ చేయండి.)"
            ),
            "language": "en",
            "provider": "none",
            "configured": False
        }
    elif error == "invalid_key":
        return {
            "reply": "⚠️ The API key is invalid or unauthorized. Please verify your GEMINI_API_KEY in the .env file.",
            "language": "en",
            "provider": provider or "none",
            "configured": False
        }
    elif error == "quota":
        return {
            "reply": (
                "⚠️ The Google Gemini API free-tier daily request quota has been reached for today. "
                "Please try again tomorrow, or add a fresh free GEMINI_API_KEY from Google AI Studio (https://aistudio.google.com/) into your .env file.\n\n"
                "(గూగుల్ జెమినీ API ఉచిత రోజువారీ కోటా పూర్తయింది. దయచేసి రేపు మళ్లీ ప్రయత్నించండి లేదా Google AI Studio నుండి కొత్త ఉచిత GEMINI_API_KEY ని .env లో జోడించండి.)"
            ),
            "language": "en",
            "provider": provider or "none",
            "configured": True
        }
    elif error in ("timeout", "network"):
        return {
            "reply": (
                "🌐 Network connection to the AI service timed out. Please try asking again in a moment. "
                "(AI సేవకు నెట్‌వర్క్ కనెక్షన్ ఆలస్యమైంది. దయచేసి కాసేపటి తర్వాత మళ్లీ ప్రయత్నించండి.)"
            ),
            "language": "en",
            "provider": provider or "none",
            "configured": True
        }
    elif error or not content:
        return {
            "reply": "Sorry, an unexpected error occurred while processing your farming question. Please try again.",
            "language": "en",
            "provider": provider or "none",
            "configured": True
        }

    is_telugu = any("\u0C00" <= c <= "\u0C7F" for c in content)
    return {
        "reply": content,
        "language": "te" if is_telugu else "en",
        "provider": provider or "gemini",
        "configured": True
    }


def analyze_crop_image(image_bytes: bytes, mime_type: str, user_caption: str = "") -> Dict[str, Any]:
    """
    Analyzes an uploaded leaf/crop image for disease symptoms, nutrient deficiencies, or pests
    using multimodal AI vision.
    Validates image integrity with PIL first.
    """
    # 1. Validate image format and integrity
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(image_bytes))
        img.verify()
    except Exception:
        return {
            "reply": "The uploaded file is not a valid or readable image. Please upload a clear photo of the crop in PNG, JPG, or WEBP format.",
            "language": "en",
            "success": False
        }

    # 2. Check if AI vision provider is configured
    client, model, provider = get_ai_client_and_model()
    if not client:
        return {
            "reply": "Image analysis requires an active GEMINI_API_KEY in the .env file. (చిత్ర విశ్లేషణ ప్రస్తుతం అందుబాటులో లేదు.)",
            "language": "en",
            "success": False
        }

    b64_image = base64.b64encode(image_bytes).decode("utf-8")
    data_uri = f"data:{mime_type};base64,{b64_image}"

    prompt_text = (
        "You are an expert plant pathologist and agronomist. Inspect this agricultural crop/plant image carefully.\n"
        "1. Identify the crop or plant if identifiable.\n"
        "2. Detect any visible symptoms of disease, fungal infection, pest damage, or nutrient deficiency.\n"
        "3. Provide clear diagnosis in both English and Telugu script (తెలుగు).\n"
        "4. Recommend practical treatment: organic/cultural management first, followed by safe chemical recommendations with precise dilution.\n"
        "5. Advise the farmer to confirm with local agricultural extension / Rythu Vedika."
    )
    if user_caption:
        prompt_text += f"\nAdditional farmer note: {user_caption}"

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt_text},
                {"type": "image_url", "image_url": {"url": data_uri}}
            ]
        }
    ]

    content, provider, error = chat_completion(messages, temperature=0.4, max_tokens=8192)

    if error == "quota":
        logger.warning("Crop image vision analysis daily quota reached")
        return {
            "reply": (
                "⚠️ The daily request quota for Google Gemini image analysis has been reached for today. "
                "Please try again tomorrow or configure a new free GEMINI_API_KEY in your .env file.\n"
                "💡 Farmer Guidance: For suspected leaf diseases or pest attacks, take clear close-up photos and consult your local Rythu Vedika / KVK agricultural officer."
            ),
            "language": "en",
            "success": True,
            "provider": provider or "gemini"
        }

    if error or not content:
        logger.warning(f"Crop image vision analysis returned error: {error}")
        return {
            "reply": f"Unable to analyze the image at this moment ({error or 'empty response'}). Please ensure the photo clearly shows affected crop leaves or stem.",
            "language": "en",
            "success": False
        }

    is_telugu = any("\u0C00" <= c <= "\u0C7F" for c in content)
    return {
        "reply": content,
        "language": "te" if is_telugu else "en",
        "success": True,
        "provider": provider or "gemini"
    }


def generate_dynamic_ai_recommendation(normalized_inputs: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Calls Gemini/OpenAI with strict JSON schema to generate a comprehensive, dynamic crop recommendation.
    Returns parsed and validated dict or None if AI is offline/errored.
    """
    soil = normalized_inputs.get("soil_type") or "black"
    season = normalized_inputs.get("season") or "kharif"
    water = normalized_inputs.get("water_availability") or "medium"
    crop = normalized_inputs.get("crop") or ""
    query = normalized_inputs.get("farmer_query") or ""
    lang = normalized_inputs.get("language") or "te"

    system_prompt = (
        "You are the Chief Agronomist for AgriGuide India. Your job is to generate dynamic, scientifically sound, "
        "highly practical crop recommendations based on the farmer's soil, season, water conditions, and query.\n"
        "You MUST respond ONLY with a valid JSON object matching the following structure:\n"
        "{\n"
        '  "language": "te" or "en",\n'
        '  "primary_crops": [\n'
        "    {\n"
        '      "name_en": "Crop Name in English",\n'
        '      "name_te": "తెలుగులో పంట పేరు",\n'
        '      "suitability_score": 90,\n'
        '      "description_en": "Comprehensive English explanation of why this crop fits the given soil and season.",\n'
        '      "description_te": "ఈ నేల మరియు కాలానికి ఈ పంట ఎందుకు అనుకూలమో వివరణ.",\n'
        '      "growing_duration": "Duration in days e.g. 120-150 Days / రోజులు",\n'
        '      "soil_health_tips": "Soil pH, drainage, and conditioning guidelines in bilingual format",\n'
        '      "fertilizer_schedule": "Recommended NPK ratio and split application schedule (Urea, DAP, Potash)",\n'
        '      "irrigation_advice": "Critical watering stages and moisture conservation techniques",\n'
        '      "expected_yield": "Expected average yield per acre e.g. 10 - 15 Quintals/Acre",\n'
        '      "sowing_guidance": "Optimal sowing window, seed rate, and spacing",\n'
        '      "diseases_and_pests": "Key pests to watch for and preventative bio-measures",\n'
        '      "precautions_en": "Crucial risk warnings or weather precautions in English",\n'
        '      "precautions_te": "ముఖ్యమైన జాగ్రత్తలు తెలుగులో"\n'
        "    }\n"
        "  ],\n"
        '  "general_advice_en": "Overall seasonal advice for the farmer in English",\n'
        '  "general_advice_te": "రైతుకు సాధారణ సూచనలు తెలుగులో",\n'
        '  "warnings_en": "General warnings or market advice in English",\n'
        '  "warnings_te": "హెచ్చరికలు మరియు జాగ్రత్తలు తెలుగులో"\n'
        "}\n"
        "Provide 2 to 3 well-suited primary crops. Output strictly JSON without markdown backticks."
    )

    user_prompt = (
        f"Soil Type: {soil}\n"
        f"Season: {season}\n"
        f"Water Availability: {water}\n"
        f"Preferred Crop (if any): {crop or 'None specified'}\n"
        f"Farmer Query: {query or 'Provide best recommendations for my field'}\n"
        f"Preferred Language: {lang}"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    content, provider, error = chat_completion(
        messages=messages,
        temperature=0.5,
        max_tokens=8192,
        response_format={"type": "json_object"}
    )

    if error or not content:
        logger.info(f"AI recommendation bypassed due to error: {error}")
        return None

    try:
        # Clean potential markdown fences if present
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        # Isolate JSON object between outermost braces if needed
        first_brace = content.find('{')
        last_brace = content.rfind('}')
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            content = content[first_brace:last_brace + 1]

        data = json.loads(content)

        # Validate critical fields
        if not isinstance(data, dict) or "primary_crops" not in data or not isinstance(data["primary_crops"], list):
            logger.warning("AI returned JSON without valid primary_crops list")
            return None

        if len(data["primary_crops"]) == 0:
            return None

        # Sanitize crop items
        valid_crops = []
        for c in data["primary_crops"]:
            if not isinstance(c, dict):
                continue
            valid_crops.append({
                "name_en": str(c.get("name_en", "Crop")),
                "name_te": str(c.get("name_te", "పంట")),
                "suitability_score": int(c.get("suitability_score", 85)),
                "description_en": str(c.get("description_en", "Recommended for your soil and season conditions.")),
                "description_te": str(c.get("description_te", "మీ నేల మరియు వాతావరణ పరిస్థితులకు అనుకూలమైనది.")),
                "growing_duration": str(c.get("growing_duration", "120-150 Days")),
                "soil_health_tips": str(c.get("soil_health_tips", "Ensure proper drainage and organic manure incorporation.")),
                "fertilizer_schedule": str(c.get("fertilizer_schedule", "Apply balanced NPK based on soil testing.")),
                "irrigation_advice": str(c.get("irrigation_advice", "Irrigate according to moisture requirements.")),
                "expected_yield": str(c.get("expected_yield", "Average market yield per acre")),
                "sowing_guidance": str(c.get("sowing_guidance", "Sow with certified treated seeds at optimal depth.")),
                "diseases_and_pests": str(c.get("diseases_and_pests", "Regular crop inspection recommended.")),
                "precautions_en": str(c.get("precautions_en", "Follow local agriculture extension warnings.")),
                "precautions_te": str(c.get("precautions_te", "వ్యవసాయ శాఖ సూచనలను పాటించండి."))
            })

        data["primary_crops"] = valid_crops
        data["general_advice_en"] = str(data.get("general_advice_en", "Conduct soil test and use quality certified seeds."))
        data["general_advice_te"] = str(data.get("general_advice_te", "భూసార పరీక్ష చేయించి, నాణ్యమైన విత్తనాలు వాడండి."))
        data["warnings_en"] = str(data.get("warnings_en", "Excessive chemical fertilizer usage harms soil microbiome."))
        data["warnings_te"] = str(data.get("warnings_te", "రసాయన ఎరువులు అధికంగా వాడటం నేల ఆరోగ్యానికి హానికరం."))
        data["language"] = lang

        return data

    except Exception as exc:
        logger.warning(f"Dynamic AI recommendation parsing failed ({type(exc).__name__}), falling back to local agronomy database.")
        return None


def transcribe_farmer_audio(
    audio_bytes: bytes,
    mime_type: str = "audio/wav",
    language_hint: str = "te"
) -> Dict[str, Any]:
    """
    AgriGuide processes microphone voice queries directly in the farmer's browser
    via the native Web Speech API for seamless low-latency English and Telugu recognition.
    """
    is_te = str(language_hint).startswith("te")
    msg_en = "Voice input is processed directly in your browser using the microphone. Please speak into the mic or type your question."
    msg_te = "వాయిస్ ఇన్‌పుట్ మీ బ్రౌజర్ మైక్రోఫోన్ ద్వారా ప్రాసెస్ చేయబడుతుంది. దయచేసి మైక్‌లో మాట్లాడండి లేదా ప్రశ్నను టైప్ చేయండి."
    return {
        "success": False,
        "transcript": "",
        "reply": msg_te if is_te else msg_en,
        "language": language_hint
    }


def process_voice_query(
    audio_bytes: bytes,
    mime_type: str = "audio/wav",
    language_hint: str = "te",
    conversation_history: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """
    AgriGuide uses client-side Web Speech recognition for voice queries.
    """
    return transcribe_farmer_audio(audio_bytes, mime_type, language_hint)


