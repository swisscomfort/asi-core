#!/usr/bin/env python3
"""
ASI-System Dezentrale Speicherung Launcher

Dieses Script demonstriert die neue dezentrale Speicherfunktionalität:
1. Verarbeitung einer Reflexion mit process_reflection
2. Upload der verarbeiteten Daten auf IPFS
3. Speicherung der Metadaten auf Arweave (simuliert)

Verwendung:
    python decentralized_storage_demo.py

Voraussetzungen:
- IPFS-Daemon muss laufen (ipfs daemon)
- Alle Dependencies müssen installiert sein (siehe requirements.txt)
"""

import sys
import traceback

from asi_core.processing import process_reflection
from asi_core.storage import (
    create_metadata,
    persist_metadata_on_arweave,
    upload_to_ipfs,
)


def main():
    """Hauptfunktion für dezentrale Speicherung Demo"""
    print("🚀 ASI-System - Dezentrale Speicherung Demo")
    print("=" * 50)

    try:
        # Beispieltext für die Reflexion
        # In einer echten Implementierung würde dieser Text von einem
        # Input-Interface oder einer anderen Quelle kommen
        sample_reflection = (
            "Heute habe ich über die Bedeutung von dezentraler "
            "Speicherung nachgedacht. Es ist faszinierend, wie "
            "Technologien wie IPFS und Arweave es ermöglichen, "
            "Daten dauerhaft und zensurresistent zu speichern."
        )

        print("📝 Schritt 1: Verarbeitung der Reflexion")
        print(f"   Input-Text: {sample_reflection[:50]}...")

        # Reflexion verarbeiten
        processed_data = process_reflection(sample_reflection)
        print(f"✓ Reflexion verarbeitet. Typ: {processed_data['type']}")
        print(f"   Timestamp: {processed_data['timestamp']}")
        print(f"   Tags: {processed_data['tags']}")

        print("\n🌐 Schritt 2: Upload auf IPFS")

        # Daten auf IPFS hochladen
        cid = upload_to_ipfs(processed_data)
        print("✓ IPFS-Upload abgeschlossen")
        print(f"   CID: {cid}")

        print("\n🔗 Schritt 3: Metadaten für Arweave vorbereiten")

        # Metadaten erstellen
        metadata = create_metadata(cid, processed_data)
        print("✓ Metadaten erstellt:")
        for key, value in metadata.items():
            print(f"   {key}: {value}")

        print("\n📡 Schritt 4: Persistierung auf Arweave")

        # Metadaten auf Arweave speichern (simuliert)
        arweave_success = persist_metadata_on_arweave(cid, metadata)

        print("\n" + "=" * 50)
        print("🎉 ASI-System Workflow abgeschlossen!")
        print("=" * 50)
        print("📊 ZUSAMMENFASSUNG:")
        print("   ✓ Reflexion verarbeitet")
        print(f"   ✓ IPFS CID: {cid}")
        status = "Erfolgreich" if arweave_success else "Fehlgeschlagen"
        print(f"   ✓ Arweave-Status: {status}")
        print(f"   ✓ Metadaten-Felder: {len(metadata)}")

        return 0

    except ConnectionError as e:
        print(f"\n❌ Verbindungsfehler: {e}")
        print("💡 Lösungsvorschläge:")
        print("   - IPFS-Daemon starten: ipfs daemon")
        print("   - IPFS-Installation prüfen: ipfs version")
        return 1

    except (RuntimeError, OSError, ValueError) as e:
        print(f"\n❌ Unerwarteter Fehler: {e}")
        print("🔍 Vollständiger Stack Trace:")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
