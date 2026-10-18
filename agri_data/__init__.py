"""
Agronomic reference data and matching rules package for AgriGuide.
"""

from .soils import SOIL_PROFILES
from .crops import CROPS_DATABASE
from .fertilizers import FERTILIZERS_CATALOG, calculate_fertilizer_guidance
from .rules import evaluate_agronomic_recommendation

__all__ = [
    "SOIL_PROFILES",
    "CROPS_DATABASE",
    "FERTILIZERS_CATALOG",
    "calculate_fertilizer_guidance",
    "evaluate_agronomic_recommendation"
]
