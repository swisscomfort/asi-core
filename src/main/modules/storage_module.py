#!/usr/bin/env python3
"""
💾 ASI Storage Module
Hochperformante, sichere Datenspeicherung
"""

import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import hashlib

logger = logging.getLogger(__name__)


class StorageError(Exception):
    """Storage-spezifische Fehler"""
    pass


class StorageModule:
    """
    Hochperformantes Storage-System mit Multi-Tier Architecture

    - Local SQLite für schnellen Zugriff
    - Optional IPFS für dezentrale Speicherung
    - Optional Arweave für permanente Archivierung
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_path = Path(config.get('storage', {}).get(
            'database_path', 'data/asi_local.db'))
        self.db_connection: Optional[sqlite3.Connection] = None
        self._initialized = False

        # Performance Settings
        self.batch_size = config.get('storage', {}).get('batch_size', 100)
        self.cache_size = config.get('storage', {}).get('cache_size', 1000)
        self._cache: Dict[str, Any] = {}

    def initialize(self):
        """Initialisiert Storage-System"""
        try:
            self._setup_database()
            self._optimize_database()
            self._initialized = True
            logger.info("💾 Storage Module initialized")

        except Exception as e:
            logger.error(f"❌ Storage initialization failed: {e}")
            raise StorageError(f"Storage initialization failed: {e}")

    def _setup_database(self):
        """Erstellt und konfiguriert SQLite Database"""
        # Verzeichnis erstellen
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Connection mit Performance-Optimierungen
        self.db_connection = sqlite3.connect(
            self.db_path,
            check_same_thread=False,
            timeout=30.0
        )

        # Performance Settings
        self.db_connection.execute("PRAGMA journal_mode=WAL")
        self.db_connection.execute("PRAGMA synchronous=NORMAL")
        self.db_connection.execute("PRAGMA cache_size=10000")
        self.db_connection.execute("PRAGMA temp_store=memory")

        # Row Factory für Dict-Output
        self.db_connection.row_factory = sqlite3.Row

        # Tabellen erstellen
        self._create_tables()

        logger.debug("✅ Database setup complete")

    def _create_tables(self):
        """Erstellt alle notwendigen Tabellen"""
        cursor = self.db_connection.cursor()

        # Reflexionen Tabelle
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reflections (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                tags TEXT NOT NULL DEFAULT '[]',
                state INTEGER NOT NULL DEFAULT 0,
                timestamp TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT DEFAULT '{}',
                vector_id TEXT,
                ipfs_hash TEXT,
                arweave_id TEXT
            )
        """)

        # Performance Indices
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_reflections_timestamp ON reflections(timestamp)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_reflections_state ON reflections(state)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_reflections_hash ON reflections(content_hash)")

        # State Statistics Tabelle
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS state_stats (
                state INTEGER PRIMARY KEY,
                count INTEGER NOT NULL DEFAULT 0,
                last_used TEXT,
                avg_duration REAL DEFAULT 0.0
            )
        """)

        # Search Cache Tabelle
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_cache (
                query_hash TEXT PRIMARY KEY,
                query TEXT NOT NULL,
                results TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                hit_count INTEGER DEFAULT 1
            )
        """)

        self.db_connection.commit()
        logger.debug("✅ Database tables created")

    def _optimize_database(self):
        """Optimiert Database Performance"""
        cursor = self.db_connection.cursor()

        # Analyze für Query Optimizer
        cursor.execute("ANALYZE")

        # Vacuum wenn nötig
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()
        if result[0] == "ok":
            logger.debug("✅ Database integrity OK")

        self.db_connection.commit()

    # === PUBLIC INTERFACE ===

    def store_reflection(self, reflection_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Speichert Reflexion mit Performance-Optimierung

        Args:
            reflection_data: Reflexionsdaten

        Returns:
            Gespeicherte Reflexion mit ID
        """
        try:
            if not self._initialized:
                raise StorageError("Storage not initialized")

            # Content Hash für Deduplizierung
            content_hash = self._generate_content_hash(
                reflection_data['content'])

            # Prüfe auf Duplikate
            if self._is_duplicate(content_hash):
                logger.warning(
                    f"⚠️ Duplicate content detected: {content_hash[:8]}...")
                return self._get_by_hash(content_hash)

            # Reflexion speichern
            cursor = self.db_connection.cursor()

            cursor.execute("""
                INSERT INTO reflections 
                (id, content, content_hash, tags, state, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                reflection_data['id'],
                reflection_data['content'],
                content_hash,
                json.dumps(reflection_data.get('tags', [])),
                reflection_data.get('state', 0),
                reflection_data['timestamp'],
                json.dumps(reflection_data.get('metadata', {}))
            ))

            # State Statistics updaten
            self._update_state_stats(reflection_data.get('state', 0))

            self.db_connection.commit()

            # Cache invalidieren
            self._invalidate_search_cache()

            logger.debug(f"✅ Reflection {reflection_data['id']} stored")

            return reflection_data

        except Exception as e:
            logger.error(f"❌ Failed to store reflection: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            raise StorageError(f"Storage failed: {e}")

    def get_reflection(self, reflection_id: str) -> Optional[Dict[str, Any]]:
        """Holt Reflexion nach ID"""
        try:
            # Cache prüfen
            if reflection_id in self._cache:
                return self._cache[reflection_id]

            cursor = self.db_connection.cursor()
            cursor.execute(
                "SELECT * FROM reflections WHERE id = ?",
                (reflection_id,)
            )

            row = cursor.fetchone()
            if row:
                reflection = self._row_to_dict(row)

                # Cache mit LRU-Strategie
                if len(self._cache) >= self.cache_size:
                    # Ältesten Eintrag entfernen
                    oldest_key = next(iter(self._cache))
                    del self._cache[oldest_key]

                self._cache[reflection_id] = reflection
                return reflection

            return None

        except Exception as e:
            logger.error(f"❌ Failed to get reflection {reflection_id}: {e}")
            return None

    def text_search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Text-basierte Suche mit Caching

        Args:
            query: Suchanfrage
            limit: Maximale Ergebnisse

        Returns:
            Liste von Suchergebnissen
        """
        try:
            # Query Hash für Cache
            query_hash = self._generate_content_hash(query.lower())

            # Cache prüfen
            cached_results = self._get_cached_search(query_hash)
            if cached_results:
                return cached_results[:limit]

            # Database Suche
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT * FROM reflections 
                WHERE content LIKE ? OR tags LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (f"%{query}%", f"%{query}%", limit))

            results = [self._row_to_dict(row) for row in cursor.fetchall()]

            # Cache speichern
            self._cache_search_results(query_hash, query, results)

            return results

        except Exception as e:
            logger.error(f"❌ Text search failed: {e}")
            return []

    def get_state_statistics(self) -> Dict[str, Any]:
        """Liefert State Statistics"""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT * FROM state_stats ORDER BY count DESC")

            stats = {}
            total_reflections = 0

            for row in cursor.fetchall():
                state = row['state']
                count = row['count']
                stats[state] = {
                    'count': count,
                    'last_used': row['last_used'],
                    'avg_duration': row['avg_duration']
                }
                total_reflections += count

            return {
                'total_reflections': total_reflections,
                'state_distribution': stats,
                'most_used_state': max(stats.items(), key=lambda x: x[1]['count'])[0] if stats else 0
            }

        except Exception as e:
            logger.error(f"❌ Failed to get state statistics: {e}")
            return {'error': str(e)}

    # === INTERNAL METHODS ===

    def _generate_content_hash(self, content: str) -> str:
        """Generiert Content Hash für Deduplizierung"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def _is_duplicate(self, content_hash: str) -> bool:
        """Prüft auf Duplikate"""
        cursor = self.db_connection.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM reflections WHERE content_hash = ?",
            (content_hash,)
        )
        return cursor.fetchone()[0] > 0

    def _get_by_hash(self, content_hash: str) -> Dict[str, Any]:
        """Holt Reflexion nach Hash"""
        cursor = self.db_connection.cursor()
        cursor.execute(
            "SELECT * FROM reflections WHERE content_hash = ? LIMIT 1",
            (content_hash,)
        )
        row = cursor.fetchone()
        return self._row_to_dict(row) if row else {}

    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Konvertiert SQLite Row zu Dict"""
        return {
            'id': row['id'],
            'content': row['content'],
            'tags': json.loads(row['tags']),
            'state': row['state'],
            'timestamp': row['timestamp'],
            'metadata': json.loads(row['metadata']),
            'created_at': row['created_at']
        }

    def _update_state_stats(self, state: int):
        """Aktualisiert State Statistics"""
        cursor = self.db_connection.cursor()

        # Upsert State Statistics
        cursor.execute("""
            INSERT OR REPLACE INTO state_stats (state, count, last_used)
            VALUES (?, 
                    COALESCE((SELECT count FROM state_stats WHERE state = ?), 0) + 1,
                    ?)
        """, (state, state, datetime.now().isoformat()))

    def _get_cached_search(self, query_hash: str) -> Optional[List[Dict[str, Any]]]:
        """Holt gecachte Suchergebnisse"""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                "SELECT results FROM search_cache WHERE query_hash = ?",
                (query_hash,)
            )

            row = cursor.fetchone()
            if row:
                # Hit Count erhöhen
                cursor.execute(
                    "UPDATE search_cache SET hit_count = hit_count + 1 WHERE query_hash = ?",
                    (query_hash,)
                )
                self.db_connection.commit()

                return json.loads(row['results'])

            return None

        except Exception as e:
            logger.error(f"❌ Cache lookup failed: {e}")
            return None

    def _cache_search_results(self, query_hash: str, query: str, results: List[Dict[str, Any]]):
        """Cached Suchergebnisse"""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO search_cache 
                (query_hash, query, results, timestamp)
                VALUES (?, ?, ?, ?)
            """, (
                query_hash,
                query,
                json.dumps(results),
                datetime.now().isoformat()
            ))
            self.db_connection.commit()

        except Exception as e:
            logger.error(f"❌ Cache store failed: {e}")

    def _invalidate_search_cache(self):
        """Invalidiert Search Cache bei neuen Daten"""
        try:
            cursor = self.db_connection.cursor()
            # Nur ältere Cache-Einträge löschen (letzte 5 Minuten behalten)
            cursor.execute("""
                DELETE FROM search_cache 
                WHERE timestamp < datetime('now', '-5 minutes')
            """)
            self.db_connection.commit()

        except Exception as e:
            logger.error(f"❌ Cache invalidation failed: {e}")

    # === HEALTH & MAINTENANCE ===

    def health_check(self) -> Dict[str, Any]:
        """Storage Health Check"""
        try:
            # Database Connectivity
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM reflections")
            reflection_count = cursor.fetchone()[0]

            # Database Size
            cursor.execute("PRAGMA page_count")
            page_count = cursor.fetchone()[0]
            cursor.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]
            db_size_mb = (page_count * page_size) / (1024 * 1024)

            return {
                'status': 'healthy',
                'initialized': self._initialized,
                'reflection_count': reflection_count,
                'database_size_mb': round(db_size_mb, 2),
                'cache_entries': len(self._cache),
                'database_path': str(self.db_path)
            }

        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'initialized': self._initialized
            }

    def shutdown(self):
        """Beendet Storage sauber"""
        try:
            if self.db_connection:
                self.db_connection.close()

            self._cache.clear()
            logger.info("💾 Storage Module shut down")

        except Exception as e:
            logger.error(f"❌ Storage shutdown failed: {e}")
