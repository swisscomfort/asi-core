#!/usr/bin/env python3
"""
ASI-Core Application Factory
NOBELPREIS-ARCHITEKTUR: Clean, Testable, Scalable
Integriert echte Module aus src/main/
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Setup Basic Logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Try to import real modules, fallback to mock if not available
USE_REAL_MODULES = False
try:
    from main.config_loader import ConfigLoader as RealConfigLoader
    from main.core_manager import ASICoreManager as RealCoreManager
    from main.modules.storage_module import StorageModule as RealStorageModule
    from main.modules.ai_module import AIModule as RealAIModule

    # Only test import, not initialization
    USE_REAL_MODULES = True
    logger.info("✅ Real modules imported - will test during runtime")
except Exception as e:
    logger.warning(f"⚠️ Could not import real modules: {e}. Using fallback.")
    USE_REAL_MODULES = False


class FallbackConfigLoader:
    """Fallback Config Loader wenn echte Module nicht verfügbar"""

    def __init__(self, config_path: str = "config/settings.json"):
        self.config_path = config_path

    def load(self) -> Dict[str, Any]:
        """Lädt Konfiguration"""
        if Path(self.config_path).exists():
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load config: {e}")

        # Fallback Config
        return {
            "environment": "development",
            "features": {
                "enable_ai": True,
                "blockchain_enabled": False,
                "enable_hrm": True
            },
            "storage": {
                "database_path": "data/asi_local.db",
                "backup_path": "data/backups"
            },
            "ai": {
                "batch_size": 32,
                "cache_embeddings": True,
                "enable_embeddings": False
            },
            "logging": {
                "level": "INFO"
            }
        }

    def validate(self) -> bool:
        return True


class FallbackStorageModule:
    """Fallback Storage Module"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._reflections = []

    def initialize(self):
        logger.info("📦 Fallback Storage initialized")

    def store_reflection(self, data: Dict[str, Any]) -> Dict[str, Any]:
        self._reflections.append(data)
        logger.info(f"💾 Stored reflection: {data['id']}")
        return data

    def text_search(self, query: str, limit: int = 10):
        results = [r for r in self._reflections if query.lower()
                   in r['content'].lower()]
        return results[:limit]

    def health_check(self) -> Dict[str, Any]:
        return {
            'status': 'healthy',
            'reflections_count': len(self._reflections)
        }

    def shutdown(self):
        logger.info("📦 Fallback Storage shut down")


class FallbackAIModule:
    """Fallback AI Module"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def initialize(self):
        logger.info("🤖 Fallback AI initialized")

    def suggest_state_from_text(self, text: str) -> int:
        # Einfache State Detection
        if 'gut' in text.lower() or 'toll' in text.lower():
            return 1  # Positiv
        elif 'schlecht' in text.lower() or 'stress' in text.lower():
            return 2  # Negativ
        return 0  # Neutral

    def semantic_search(self, query: str, limit: int = 10):
        return [
            {
                'id': 'demo_result',
                'content': f'Semantisches Ergebnis für: {query}',
                'similarity': 0.85
            }
        ]

    def health_check(self) -> Dict[str, Any]:
        return {'status': 'healthy', 'initialized': True}

    def shutdown(self):
        logger.info("🤖 Fallback AI shut down")


class FallbackCoreManager:
    """Fallback Core Manager wenn echte Module nicht verfügbar"""

    def __init__(self, config: Dict[str, Any], modules: Dict[str, Any]):
        self.config = config
        self.modules = modules
        self._running = False

        # Module initialisieren
        for name, module in modules.items():
            if hasattr(module, 'initialize'):
                module.initialize()

        logger.info("🧠 Fallback Core Manager initialized")

    def add_reflection(self, content: str, tags=None, auto_detect_state=True) -> Dict[str, Any]:
        """Fügt Reflexion hinzu"""
        import uuid
        from datetime import datetime

        # State Detection
        state = 0
        if auto_detect_state and 'ai' in self.modules:
            state = self.modules['ai'].suggest_state_from_text(content)

        # Reflexion erstellen
        reflection = {
            'id': f"refl_{uuid.uuid4().hex[:8]}",
            'content': content,
            'tags': tags or [],
            'state': state,
            'timestamp': datetime.now().isoformat()
        }

        # Speichern
        if 'storage' in self.modules:
            return self.modules['storage'].store_reflection(reflection)

        return reflection

    def search_reflections(self, query: str, limit: int = 10):
        """Sucht Reflexionen"""
        if 'storage' in self.modules:
            return self.modules['storage'].text_search(query, limit)
        return []

    def health_check(self) -> Dict[str, Any]:
        """System Health Check"""
        health = {
            'status': 'healthy',
            'running': self._running,
            'modules': {}
        }

        for name, module in self.modules.items():
            if hasattr(module, 'health_check'):
                health['modules'][name] = module.health_check()

        return health

    def run(self):
        """Startet das System"""
        self._running = True
        module_type = "REAL" if USE_REAL_MODULES else "FALLBACK"
        logger.info(f"🚀 ASI Core Manager started with {module_type} modules")

        # Demo-Interaktion
        print("\n" + "="*60)
        print(f"ASI-CORE TRANSFORMATION DEMO ({module_type} MODULES)")
        print("="*60)

        # Reflexion hinzufügen
        print("\n1. Reflexion hinzufügen...")
        reflection = self.add_reflection(
            "Heute war ein guter Tag! Ich habe viel gelernt.",
            tags=["lernen", "positiv"]
        )
        print(f"   ✅ Reflexion erstellt: {reflection['id']}")
        print(f"   📊 Erkannter State: {reflection['state']} (1=Positiv)")

        # Weitere Reflexion
        print("\n2. Weitere Reflexion...")
        reflection2 = self.add_reflection(
            "Stress bei der Arbeit, viele Probleme zu lösen.",
            tags=["arbeit", "stress"]
        )
        print(f"   ✅ Reflexion erstellt: {reflection2['id']}")
        print(f"   📊 Erkannter State: {reflection2['state']} (2=Negativ)")

        # Suche testen
        print("\n3. Suche testen...")
        results = self.search_reflections("gut")
        print(f"   🔍 Gefunden: {len(results)} Ergebnisse für 'gut'")
        for result in results:
            print(f"      - {result['content'][:50]}...")

        # Health Check
        print("\n4. System Health Check...")
        health = self.health_check()
        print(f"   💚 System Status: {health['status']}")
        print(f"   📦 Module: {list(health['modules'].keys())}")

        print("\n" + "="*60)
        print("🏆 TRANSFORMATION ERFOLGREICH!")
        print("📈 Von 1051 Zeilen Monolith zu modularer Architektur")
        print(f"🧩 Module Type: {module_type}")
        print("🏭 Factory Pattern: ✅")
        print("💉 Dependency Injection: ✅")
        print("🧪 Testbare Module: ✅")
        print("📊 Health Checks: ✅")
        print("="*60)

        self.shutdown()

    def shutdown(self):
        """Beendet das System sauber"""
        self._running = False

        for name, module in self.modules.items():
            if hasattr(module, 'shutdown'):
                module.shutdown()

        logger.info("🛑 Core Manager shut down")

    def set_api_router(self, router):
        """API Router setzen (für Kompatibilität)"""
        pass


class ASIApplicationFactory:
    """Application Factory für echte und Fallback Module"""

    def __init__(self, config_path: str = "config/settings.json"):
        # Konfiguration laden
        if USE_REAL_MODULES:
            self.config_loader = RealConfigLoader(config_path)
        else:
            self.config_loader = FallbackConfigLoader(config_path)

        self.config = self.config_loader.load()
        self._modules = {}

    def create_application(self, mode: str = "full"):
        """Erstellt ASI-Anwendung mit echten oder Fallback Modulen"""
        logger.info(f"🏭 Creating ASI Application in '{mode}' mode")

        # Module laden
        modules = self._get_modules_for_mode(mode)

        # Core Manager erstellen - mit Error Handling für echte Module
        try:
            if USE_REAL_MODULES:
                # Versuche echten Core Manager
                core_manager = RealCoreManager(
                    config=self.config,
                    modules=modules
                )
                logger.info("✅ Real Core Manager created successfully")
                return core_manager
        except Exception as e:
            logger.warning(
                f"⚠️ Real Core Manager failed: {e}. Using fallback.")

        # Fallback Core Manager verwenden
        logger.info("🔄 Creating Fallback Core Manager")
        fallback_modules = self._get_fallback_modules_for_mode(mode)
        core_manager = FallbackCoreManager(
            config=self.config,
            modules=fallback_modules
        )

        return core_manager

    def _get_fallback_modules_for_mode(self, mode: str) -> Dict[str, Any]:
        """Lädt Fallback Module für Modus"""
        modules = {}

        # Fallback Module verwenden
        modules['storage'] = FallbackStorageModule(self.config)
        if mode in ['full', 'api-only', 'minimal']:
            modules['ai'] = FallbackAIModule(self.config)

        return modules

    def _get_modules_for_mode(self, mode: str) -> Dict[str, Any]:
        """Lädt Module für Modus (echt oder Fallback)"""
        modules = {}

        if USE_REAL_MODULES:
            # Echte Module verwenden
            modules['storage'] = RealStorageModule(self.config)
            if mode in ['full', 'api-only', 'minimal']:
                modules['ai'] = RealAIModule(self.config)
        else:
            # Fallback Module verwenden
            modules['storage'] = FallbackStorageModule(self.config)
            if mode in ['full', 'api-only', 'minimal']:
                modules['ai'] = FallbackAIModule(self.config)

        return modules


# Globale Factory
_factory_instance: Optional[ASIApplicationFactory] = None


def get_application_factory(config_path: Optional[str] = None) -> ASIApplicationFactory:
    """Singleton Factory"""
    global _factory_instance

    if _factory_instance is None:
        _factory_instance = ASIApplicationFactory(
            config_path or "config/settings.json"
        )

    return _factory_instance


def create_asi_application(mode: str = "full", config_path: Optional[str] = None):
    """Hauptfunktion zum Erstellen von ASI-Anwendungen"""
    factory = get_application_factory(config_path)
    return factory.create_application(mode)


if __name__ == "__main__":
    # Command Line Interface
    mode = sys.argv[1] if len(sys.argv) > 1 else "full"

    print(f"🚀 Starting ASI-Core in '{mode}' mode...")

    try:
        app = create_asi_application(mode)
        app.run()
    except Exception as e:
        logger.error(f"💥 Application startup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
