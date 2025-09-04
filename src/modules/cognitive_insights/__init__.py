"""
Cognitive Insights Module
Erkennt Denkfallen und bietet sanfte Verbesserungsvorschläge
"""

from .api import cognitive_insights_bp
from .bias_detector import BiasDetector
from .suggestions_generator import SuggestionsGenerator

__all__ = ["BiasDetector", "SuggestionsGenerator", "cognitive_insights_bp"]
