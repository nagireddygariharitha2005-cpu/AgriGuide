"""
Services package for AgriGuide.
Exports AI service, language processing service, pricing service, and developer profile service.
"""

from .ai_service import (
    chat_completion,
    ask_agricultural_chat,
    analyze_crop_image,
    generate_dynamic_ai_recommendation,
    get_ai_client_and_model
)
from .language_service import normalize_farmer_input, detect_language
from .price_service import get_crop_prices
from .developer_service import (
    DEVELOPER_PROFILE,
    is_developer_query,
    get_developer_profile_response
)

__all__ = [
    "chat_completion",
    "ask_agricultural_chat",
    "analyze_crop_image",
    "generate_dynamic_ai_recommendation",
    "get_ai_client_and_model",
    "normalize_farmer_input",
    "detect_language",
    "get_crop_prices",
    "DEVELOPER_PROFILE",
    "is_developer_query",
    "get_developer_profile_response"
]
