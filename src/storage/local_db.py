"""
ASI Core - Local Database
SQLite für temporäre Daten und Metadaten
"""

import sqlite3
import json
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class ReflectionRecord:
    """Datenbank-Record für Reflexionen"""

    id: int
    hash: str
    content_preview: str
    timestamp: datetime
    privacy_level: str
    ipfs_hash: Optional[str]
    arweave_tx: Optional[str]
    tags: List[str]
    themes: List[str]
    sentiment: Optional[str]


class LocalDatabase:
    """SQLite-Datenbank für lokale ASI-Daten"""

    def __init__(self, db_path: str = "data/asi_local.db"):
        self.db_path = db_path
        self.ensure_db_directory()
        self.init_database()

    def ensure_db_directory(self):
        """Stellt sicher, dass das DB-Verzeichnis existiert"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        """
        Erstellt eine Datenbankverbindung

        Returns:
            sqlite3.Connection: Datenbankverbindung
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Ermöglicht dict-ähnlichen Zugriff
        return conn

    def init_database(self):
        """Initialisiert die Datenbank-Tabellen"""
        with self.get_connection() as conn:
            # Reflexionen-Tabelle
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS reflections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hash TEXT UNIQUE NOT NULL,
                    content_preview TEXT NOT NULL,
                    full_content TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    privacy_level TEXT NOT NULL DEFAULT 'private',
                    ipfs_hash TEXT,
                    arweave_tx TEXT,
                    tags TEXT,  -- JSON array
                    themes TEXT,  -- JSON array
                    sentiment TEXT,
                    word_count INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Upload-Status Tabelle
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS upload_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    reflection_hash TEXT NOT NULL,
                    storage_type TEXT NOT NULL,  -- ipfs, arweave
                    storage_hash TEXT,
                    status TEXT NOT NULL,  -- pending, uploaded, failed
                    attempt_count INTEGER DEFAULT 0,
                    last_attempt DATETIME,
                    error_message TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (reflection_hash) REFERENCES reflections (hash)
                )
            """
            )

            # Insights-Tabelle
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    related_themes TEXT,  -- JSON array
                    actionable BOOLEAN NOT NULL DEFAULT 0,
                    shown_to_user BOOLEAN DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Indizes für bessere Performance
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_reflections_timestamp ON reflections (timestamp)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_reflections_privacy ON reflections (privacy_level)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_upload_status_reflection ON upload_status (reflection_hash)"
            )

            conn.commit()

    def store_reflection(self, processed_reflection: Dict) -> int:
        """
        Speichert eine verarbeitete Reflexion

        Args:
            processed_reflection: Verarbeitete Reflexionsdaten

        Returns:
            int: ID des gespeicherten Records
        """
        with self.get_connection() as conn:
            # Content-Preview erstellen (erste 100 Zeichen)
            full_content = processed_reflection.get("content", "")
            preview = (
                full_content[:100] + "..." if len(full_content) > 100 else full_content
            )

            # Tags und Themes als JSON speichern
            tags_json = json.dumps(processed_reflection.get("tags", []))
            themes_json = json.dumps(processed_reflection.get("themes", []))

            cursor = conn.execute(
                """
                INSERT INTO reflections (
                    hash, content_preview, full_content, timestamp,
                    privacy_level, tags, themes, sentiment, word_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    processed_reflection.get("hash", ""),
                    preview,
                    full_content,
                    processed_reflection.get("timestamp", datetime.now().isoformat()),
                    processed_reflection.get("privacy", "private"),
                    tags_json,
                    themes_json,
                    processed_reflection.get("sentiment", ""),
                    processed_reflection.get("structure", {}).get("word_count", 0),
                ),
            )

            return cursor.lastrowid

    def update_storage_reference(
        self, reflection_hash: str, storage_type: str, storage_hash: str
    ):
        """
        Aktualisiert Storage-Referenzen

        Args:
            reflection_hash: Hash der Reflexion
            storage_type: 'ipfs' oder 'arweave'
            storage_hash: Hash/TX-ID im Storage-System
        """
        with self.get_connection() as conn:
            if storage_type == "ipfs":
                conn.execute(
                    "UPDATE reflections SET ipfs_hash = ? WHERE hash = ?",
                    (storage_hash, reflection_hash),
                )
            elif storage_type == "arweave":
                conn.execute(
                    "UPDATE reflections SET arweave_tx = ? WHERE hash = ?",
                    (storage_hash, reflection_hash),
                )

            # Upload-Status aktualisieren
            conn.execute(
                """
                INSERT OR REPLACE INTO upload_status 
                (reflection_hash, storage_type, storage_hash, status, last_attempt)
                VALUES (?, ?, ?, 'uploaded', CURRENT_TIMESTAMP)
            """,
                (reflection_hash, storage_type, storage_hash),
            )

            conn.commit()

    def get_reflections(
        self, limit: int = 50, privacy_level: str = None, days_back: int = None
    ) -> List[ReflectionRecord]:
        """
        Ruft Reflexionen ab

        Args:
            limit: Maximale Anzahl
            privacy_level: Filter nach Privacy-Level
            days_back: Nur Reflexionen der letzten X Tage

        Returns:
            List[ReflectionRecord]: Liste der Reflexionen
        """
        with self.get_connection() as conn:
            query = "SELECT * FROM reflections WHERE 1=1"
            params = []

            if privacy_level:
                query += " AND privacy_level = ?"
                params.append(privacy_level)

            if days_back:
                cutoff_date = datetime.now() - timedelta(days=days_back)
                query += " AND timestamp >= ?"
                params.append(cutoff_date.isoformat())

            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            cursor = conn.execute(query, params)
            rows = cursor.fetchall()

            records = []
            for row in rows:
                record = ReflectionRecord(
                    id=row["id"],
                    hash=row["hash"],
                    content_preview=row["content_preview"],
                    timestamp=datetime.fromisoformat(row["timestamp"]),
                    privacy_level=row["privacy_level"],
                    ipfs_hash=row["ipfs_hash"],
                    arweave_tx=row["arweave_tx"],
                    tags=json.loads(row["tags"]) if row["tags"] else [],
                    themes=json.loads(row["themes"]) if row["themes"] else [],
                    sentiment=row["sentiment"],
                )
                records.append(record)

            return records

    def get_reflection_by_hash(self, reflection_hash: str) -> Optional[Dict]:
        """
        Ruft eine spezifische Reflexion ab

        Args:
            reflection_hash: Hash der Reflexion

        Returns:
            Optional[Dict]: Reflexionsdaten
        """
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM reflections WHERE hash = ?", (reflection_hash,)
            )
            row = cursor.fetchone()

            if row:
                return {
                    "id": row["id"],
                    "hash": row["hash"],
                    "content": row["full_content"],
                    "preview": row["content_preview"],
                    "timestamp": row["timestamp"],
                    "privacy_level": row["privacy_level"],
                    "ipfs_hash": row["ipfs_hash"],
                    "arweave_tx": row["arweave_tx"],
                    "tags": json.loads(row["tags"]) if row["tags"] else [],
                    "themes": json.loads(row["themes"]) if row["themes"] else [],
                    "sentiment": row["sentiment"],
                    "word_count": row["word_count"],
                }

            return None

    def store_insight(self, insight_data: Dict) -> int:
        """
        Speichert eine Erkenntnis

        Args:
            insight_data: Erkenntnisdaten

        Returns:
            int: ID der gespeicherten Erkenntnis
        """
        with self.get_connection() as conn:
            related_themes_json = json.dumps(insight_data.get("related_themes", []))

            cursor = conn.execute(
                """
                INSERT INTO insights (
                    type, title, description, confidence, 
                    related_themes, actionable
                ) VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    insight_data.get("type", ""),
                    insight_data.get("title", ""),
                    insight_data.get("description", ""),
                    insight_data.get("confidence", 0.0),
                    related_themes_json,
                    insight_data.get("actionable", False),
                ),
            )

            return cursor.lastrowid

    def get_recent_insights(
        self, days_back: int = 7, only_actionable: bool = False
    ) -> List[Dict]:
        """
        Ruft aktuelle Erkenntnisse ab

        Args:
            days_back: Tage zurück
            only_actionable: Nur umsetzbare Erkenntnisse

        Returns:
            List[Dict]: Liste der Erkenntnisse
        """
        with self.get_connection() as conn:
            query = """
                SELECT * FROM insights 
                WHERE created_at >= datetime('now', '-{} days')
            """.format(
                days_back
            )

            if only_actionable:
                query += " AND actionable = 1"

            query += " ORDER BY created_at DESC"

            cursor = conn.execute(query)
            rows = cursor.fetchall()

            insights = []
            for row in rows:
                insight = {
                    "id": row["id"],
                    "type": row["type"],
                    "title": row["title"],
                    "description": row["description"],
                    "confidence": row["confidence"],
                    "related_themes": (
                        json.loads(row["related_themes"])
                        if row["related_themes"]
                        else []
                    ),
                    "actionable": bool(row["actionable"]),
                    "shown_to_user": bool(row["shown_to_user"]),
                    "created_at": row["created_at"],
                }
                insights.append(insight)

            return insights

    def get_statistics(self) -> Dict:
        """
        Ruft Datenbank-Statistiken ab

        Returns:
            Dict: Statistiken
        """
        with self.get_connection() as conn:
            stats = {}

            # Gesamtanzahl Reflexionen
            cursor = conn.execute("SELECT COUNT(*) as count FROM reflections")
            stats["total_reflections"] = cursor.fetchone()["count"]

            # Reflexionen der letzten 7 Tage
            cursor = conn.execute(
                """
                SELECT COUNT(*) as count FROM reflections 
                WHERE timestamp >= datetime('now', '-7 days')
            """
            )
            stats["reflections_last_7_days"] = cursor.fetchone()["count"]

            # Privacy-Level Verteilung
            cursor = conn.execute(
                """
                SELECT privacy_level, COUNT(*) as count 
                FROM reflections 
                GROUP BY privacy_level
            """
            )
            stats["privacy_distribution"] = {
                row["privacy_level"]: row["count"] for row in cursor.fetchall()
            }

            # Upload-Status
            cursor = conn.execute(
                """
                SELECT storage_type, status, COUNT(*) as count 
                FROM upload_status 
                GROUP BY storage_type, status
            """
            )
            upload_stats = {}
            for row in cursor.fetchall():
                if row["storage_type"] not in upload_stats:
                    upload_stats[row["storage_type"]] = {}
                upload_stats[row["storage_type"]][row["status"]] = row["count"]
            stats["upload_status"] = upload_stats

            # Gesamte Wortanzahl
            cursor = conn.execute("SELECT SUM(word_count) as total FROM reflections")
            result = cursor.fetchone()
            stats["total_words"] = result["total"] if result["total"] else 0

            return stats

    def cleanup_old_data(self, days_to_keep: int = 365):
        """
        Bereinigt alte Daten

        Args:
            days_to_keep: Tage die behalten werden sollen
        """
        with self.get_connection() as conn:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)

            # Alte Reflexionen entfernen (außer die mit permanenter Speicherung)
            conn.execute(
                """
                DELETE FROM reflections 
                WHERE timestamp < ? AND arweave_tx IS NULL
            """,
                (cutoff_date.isoformat(),),
            )

            # Alte Upload-Status Einträge
            conn.execute(
                """
                DELETE FROM upload_status 
                WHERE created_at < ?
            """,
                (cutoff_date.isoformat(),),
            )

            # Alte Insights
            conn.execute(
                """
                DELETE FROM insights 
                WHERE created_at < ?
            """,
                (cutoff_date.isoformat(),),
            )

            conn.commit()


if __name__ == "__main__":
    # Beispiel-Nutzung
    db = LocalDatabase()

    print("=== Lokale Datenbank Test ===")

    # Test-Reflexion speichern
    test_reflection = {
        "hash": "test_hash_123",
        "content": "Das ist eine Test-Reflexion für die lokale Datenbank.",
        "timestamp": datetime.now().isoformat(),
        "privacy": "private",
        "tags": ["test", "datenbank"],
        "themes": ["technologie"],
        "sentiment": "neutral(0.5)",
        "structure": {"word_count": 10},
    }

    reflection_id = db.store_reflection(test_reflection)
    print(f"Reflexion gespeichert mit ID: {reflection_id}")

    # Reflexionen abrufen
    reflections = db.get_reflections(limit=5)
    print(f"Gefunden: {len(reflections)} Reflexionen")

    # Statistiken
    stats = db.get_statistics()
    print("Statistiken:")
    print(f"  Gesamt: {stats['total_reflections']} Reflexionen")
    print(f"  Letzte 7 Tage: {stats['reflections_last_7_days']}")
    print(f"  Gesamte Wörter: {stats['total_words']}")
