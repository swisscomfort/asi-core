"""
HRM (Hierarchical Reasoning Model) Module
Implementiert zweistufiges KI-Denken für ASI Core

High-Level: Abstrakte Planung & Mustererkennung
Low-Level: Konkrete Ausführung & Detailanalyse
"""

from .high_level.planner import Planner
from .high_level.pattern_recognition import PatternRecognizer
from .low_level.executor import Executor
from .low_level.detail_analysis import DetailAnalyzer

__all__ = [
    'Planner',
    'PatternRecognizer', 
    'Executor',
    'DetailAnalyzer'
]
