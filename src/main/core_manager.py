#!/usr/bin/env python3
"""
🧠 ASI Core Manager
Zentrale Orchestrierung aller ASI-Komponenten
"""

from typing import Dict, Any, Optional, List
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)


class ASICoreManager:
    """
    Zentrale Manager-Klasse für alle ASI-Operationen

    Ersetzt die 1051-Zeilen ASICore Monolith-Klasse
    mit Clean Architecture und Dependency Injection.
    """

    def __init__(self, config: Dict[str, Any], modules: Dict[str, Any]):
        self.config = config
        self.modules = modules
        self._api_router: Optional[Any] = None
        self._running = False
        self._health_status = "unknown"

        # Initialisierung
        self._setup_logging()
        self._validate_configuration()
        self._initialize_modules()

        logger.info("🧠 ASI Core Manager initialized")

    def _setup_logging(self):
        """Konfiguriert Logging für Core Manager"""
        log_level = self.config.get('logging', {}).get('level', 'INFO')
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def _validate_configuration(self):
        """Validiert Basiskonfiguration"""
        required_sections = ['features', 'storage', 'ai']

        for section in required_sections:
            if section not in self.config:
                raise ValueError(
                    f"❌ Missing required config section: {section}")

        logger.debug("✅ Configuration validated")

    def _initialize_modules(self):
        """Initialisiert alle geladenen Module"""
        for name, module in self.modules.items():
            try:
                if hasattr(module, 'initialize'):
                    module.initialize()
                logger.debug(f"✅ Module '{name}' initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize module '{name}': {e}")
                raise

    # === PUBLIC INTERFACE ===

    def add_reflection(self, content: str, tags: Optional[List[str]] = None,
                       auto_detect_state: bool = True) -> Dict[str, Any]:
        """
        Fügt eine neue Reflexion hinzu

        Args:
            content: Reflexionsinhalt
            tags: Liste von Tags
            auto_detect_state: Automatische Zustandserkennung

        Returns:
            Reflexionsdaten mit ID und Metadaten
        """
        try:
            # State Detection über AI Module
            suggested_state = 0
            if auto_detect_state and 'ai' in self.modules:
                suggested_state = self.modules['ai'].suggest_state_from_text(
                    content)

            # Reflexion erstellen
            reflection_data = {
                'content': content,
                'tags': tags or [],
                'state': suggested_state,
                'timestamp': datetime.now().isoformat(),
                'id': self._generate_reflection_id()
            }

            # Storage speichern
            if 'storage' in self.modules:
                stored_reflection = self.modules['storage'].store_reflection(
                    reflection_data)

                # Blockchain optional
                if 'blockchain' in self.modules:
                    self.modules['blockchain'].log_reflection(
                        stored_reflection['id'])

                logger.info(f"✅ Reflection {stored_reflection['id']} added")
                return stored_reflection

            raise ValueError("❌ Storage module not available")

        except Exception as e:
            logger.error(f"❌ Failed to add reflection: {e}")
            raise

    def search_reflections(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Sucht Reflexionen semantisch

        Args:
            query: Suchanfrage
            limit: Maximale Anzahl Ergebnisse

        Returns:
            Liste von Suchergebnissen
        """
        try:
            if 'ai' in self.modules:
                results = self.modules['ai'].semantic_search(query, limit)
                logger.debug(f"🔍 Found {len(results)} results for '{query}'")
                return results

            # Fallback: Text-basierte Suche
            if 'storage' in self.modules:
                return self.modules['storage'].text_search(query, limit)

            return []

        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            return []

    def run(self):
        """Startet den Core Manager"""
        logger.info("🚀 Starting ASI Core Manager")

        try:
            self._running = True
            self._health_status = "healthy"

            # Event Loop für Demo
            import time
            while self._running:
                time.sleep(1)

        except KeyboardInterrupt:
            logger.info("🛑 Shutdown requested")
        except Exception as e:
            logger.error(f"💥 Runtime error: {e}")
            self._health_status = "error"
        finally:
            self.shutdown()

    def shutdown(self):
        """Beendet den Core Manager sauber"""
        logger.info("🛑 Shutting down ASI Core Manager")
        self._running = False
        logger.info("✅ ASI Core Manager shut down complete")

    def health_check(self) -> Dict[str, Any]:
        """Umfassender Health Check"""
        return {
            'status': self._health_status,
            'running': self._running,
            'timestamp': datetime.now().isoformat(),
            'modules': list(self.modules.keys())
        }

    def _generate_reflection_id(self) -> str:
        """Generiert eindeutige Reflexions-ID"""
        import uuid
        return f"refl_{uuid.uuid4().hex[:8]}"

    def set_api_router(self, api_router):
        """Setzt API Router für Web-Integration"""
        self._api_router = api_router
        logger.debug("✅ API Router set")
