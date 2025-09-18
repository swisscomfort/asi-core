#!/usr/bin/env python3
"""
⚙️ ASI Config Loader
Sichere und validierte Konfigurationsverwaltung
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Konfigurationsfehler"""
    pass


class ConfigLoader:
    """
    Sichere Konfigurationsverwaltung mit Validierung
    """

    def __init__(self, config_path: str = "config/settings.json"):
        self.config_path = Path(config_path)
        self.secrets_path = Path("config/secrets.json")
        self._config: Optional[Dict[str, Any]] = None
        self._secrets: Optional[Dict[str, Any]] = None

    def load(self) -> Dict[str, Any]:
        """
        Lädt und validiert Konfiguration

        Returns:
            Vollständige Konfiguration mit Secrets
        """
        if self._config is None:
            self._config = self._load_main_config()
            self._secrets = self._load_secrets()
            self._merge_environment_variables()
            self._validate_config()

        return self._config

    def _load_main_config(self) -> Dict[str, Any]:
        """Lädt Hauptkonfiguration"""
        if not self.config_path.exists():
            raise ConfigurationError(
                f"❌ Config file not found: {self.config_path}")

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            logger.debug(f"✅ Main config loaded from {self.config_path}")
            return config

        except json.JSONDecodeError as e:
            raise ConfigurationError(f"❌ Invalid JSON in config file: {e}")
        except Exception as e:
            raise ConfigurationError(f"❌ Failed to load config: {e}")

    def _load_secrets(self) -> Dict[str, Any]:
        """Lädt Secrets (optional)"""
        if not self.secrets_path.exists():
            logger.warning(f"⚠️ Secrets file not found: {self.secrets_path}")
            return {}

        try:
            with open(self.secrets_path, 'r', encoding='utf-8') as f:
                secrets = json.load(f)

            logger.debug("✅ Secrets loaded")
            return secrets

        except Exception as e:
            logger.error(f"❌ Failed to load secrets: {e}")
            return {}

    def _merge_environment_variables(self):
        """Merged Environment Variables in Config"""
        env_mappings = {
            'ASI_SECRET_KEY': ['security', 'secret_key'],
            'ASI_ENVIRONMENT': ['environment'],
            'ASI_DEBUG': ['debug'],
            'ASI_LOG_LEVEL': ['logging', 'level']
        }

        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                self._set_nested_config(config_path, value)

    def _set_nested_config(self, path: list, value: str):
        """Setzt verschachtelte Konfigurationswerte"""
        if self._config is None:
            return

        current = self._config

        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        # Type conversion
        converted_value: Any = value
        if value.lower() in ['true', 'false']:
            converted_value = value.lower() == 'true'
        elif value.isdigit():
            converted_value = int(value)

        current[path[-1]] = converted_value

    def _validate_config(self):
        """Validiert Konfiguration"""
        if self._config is None:
            raise ConfigurationError("❌ Config not loaded")

        required_sections = ['features', 'storage', 'ai']

        for section in required_sections:
            if section not in self._config:
                raise ConfigurationError(
                    f"❌ Missing required section: {section}")

        # Security validations
        environment = self._config.get('environment', 'development')

        if environment == 'production':
            # Production-spezifische Validierungen
            if not self._config.get('security', {}).get('secret_key'):
                raise ConfigurationError(
                    "❌ CRITICAL: secret_key required in production!"
                )

            if self._config.get('debug', False):
                raise ConfigurationError(
                    "❌ CRITICAL: debug must be False in production!"
                )

        logger.debug("✅ Configuration validated")

    def validate(self) -> bool:
        """
        Öffentliche Validierungsmethode

        Returns:
            True wenn Konfiguration valid
        """
        try:
            if self._config is None:
                self.load()
            self._validate_config()
            return True
        except ConfigurationError:
            return False

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Holt Konfigurationswert über Pfad

        Args:
            key_path: Pfad wie 'features.blockchain_enabled'
            default: Default-Wert

        Returns:
            Konfigurationswert oder Default
        """
        if self._config is None:
            self.load()

        if self._config is None:
            return default

        keys = key_path.split('.')
        current = self._config

        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default

    def reload(self):
        """Lädt Konfiguration neu"""
        self._config = None
        self._secrets = None
        return self.load()
