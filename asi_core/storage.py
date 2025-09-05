"""
ASI-System Dezentrale Speicherfunktionalität

Dieses Modul behandelt die dezentrale Speicherung von Reflexionsdaten auf IPFS
und Metadaten auf Arweave.

HINWEIS: Für die IPFS-Funktionalität muss ein lokaler IPFS-Daemon laufen
(ipfs daemon) oder es sollte ein Pinning-Service-API-Key konfiguriert werden.
Für die lokale Entwicklung kann ein lokaler IPFS-Daemon verwendet werden.

Installation IPFS:
- Download und Installation von https://ipfs.io/
- Nach Installation: ipfs init && ipfs daemon

Alternativ kann ein Pinning-Service wie Pinata oder Infura verwendet werden.
"""

import json

import ipfshttpclient


def upload_to_ipfs(data: dict) -> str:
    """
    Lädt ein Dictionary als JSON-String auf IPFS hoch.

    Args:
        data (dict): Das Dictionary mit Reflexionsdaten von process_reflection

    Returns:
        str: Der Content Identifier (CID) des hochgeladenen Inhalts

    Raises:
        Exception: Wenn der IPFS-Upload fehlschlägt
    """
    try:
        # Verbindung zum lokalen IPFS-Daemon (Standard: localhost:5001)
        # Für Produktionsumgebung sollte hier die entsprechende API-URL
        # verwendet werden
        client = ipfshttpclient.connect("/ip4/127.0.0.1/tcp/5001")

        # JSON-String auf IPFS hochladen
        result = client.add_json(data)

        # CID extrahieren
        cid = result

        print(f"✓ Erfolgreich auf IPFS hochgeladen. CID: {cid}")
        return cid

    except ipfshttpclient.exceptions.ConnectionError as e:
        error_msg = f"Fehler beim Verbinden mit IPFS-Daemon: {e}"
        print(f"✗ {error_msg}")
        print(
            "Hinweis: Stellen Sie sicher, dass ein IPFS-Daemon läuft " "(ipfs daemon)"
        )
        raise ConnectionError(error_msg) from e

    except Exception as e:
        error_msg = f"Unerwarteter Fehler beim IPFS-Upload: {e}"
        print(f"✗ {error_msg}")
        raise RuntimeError(error_msg) from e


def persist_metadata_on_arweave(cid: str, metadata: dict) -> bool:
    """
    Speichert Metadaten (CID, Tags, Timestamp) permanent auf Arweave.

    Diese Funktion ist derzeit als Platzhalter implementiert.
    Für die vollständige Implementierung würde hier eine
    Arweave-API-Integration mit Wallet-Interaktion erforderlich sein.

    Args:
        cid (str): Der IPFS Content Identifier
        metadata (dict): Metadaten wie Tags, Timestamp, etc.

    Returns:
        bool: True wenn erfolgreich, False bei Fehlern
    """
    try:
        print(f"📡 Persisting metadata for CID {cid} on Arweave...")
        print(f"   Metadata: {json.dumps(metadata, indent=2)}")

        # TODO: Hier würde die tatsächliche Arweave-Integration
        # implementiert werden:
        # - Wallet-Authentifizierung
        # - Transaction erstellen mit Metadaten als Tags
        # - Transaction signieren und senden
        # - Transaction-ID zurückgeben

        print("✓ Metadaten erfolgreich auf Arweave gespeichert (simuliert)")
        return True

    except Exception as e:
        error_msg = f"Fehler beim Speichern auf Arweave: {e}"
        print(f"✗ {error_msg}")
        return False


def create_metadata(cid: str, original_data: dict) -> dict:
    """
    Erstellt Metadaten für die Arweave-Speicherung.

    Args:
        cid (str): Der IPFS Content Identifier
        original_data (dict): Die ursprünglichen Reflexionsdaten

    Returns:
        dict: Strukturierte Metadaten
    """
    return {
        "ipfs_cid": cid,
        "content_type": "application/json",
        "data_type": original_data.get("type", "unknown"),
        "timestamp": original_data.get("timestamp"),
        "tags": original_data.get("tags", []),
        "context": original_data.get("context", {}),
        "storage_layer": "ipfs",
        "metadata_layer": "arweave",
    }
