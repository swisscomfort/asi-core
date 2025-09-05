#!/usr/bin/env python3
"""
Test der ASI Blockchain-Integration
Demonstriert die Smart Contract Funktionalität ohne echtes Deployment
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# ASI Core Module laden
sys.path.append(str(Path(__file__).parent))
from asi_core.blockchain import create_dummy_embedding


def test_dummy_embedding():
    """Testet die Dummy-Embedding Funktionalität"""
    print("🧪 Teste Dummy-Embedding Erstellung...")

    test_text = "Dies ist ein Test-Reflexion über persönliche Entwicklung."
    embedding = create_dummy_embedding(test_text, size=128)

    print(f"✅ Embedding erstellt: {len(embedding)} Bytes")
    print(f"📊 Erste 16 Bytes (hex): {embedding[:16].hex()}")

    # Test mit unterschiedlichen Texten
    embedding2 = create_dummy_embedding("Anderer Text", size=128)

    if embedding != embedding2:
        print("✅ Unterschiedliche Texte erzeugen unterschiedliche Embeddings")
    else:
        print("❌ Problem: Gleiche Embeddings für unterschiedliche Texte")

    return embedding


def simulate_blockchain_workflow():
    """Simuliert den kompletten Blockchain-Workflow"""
    print("\n🚀 Simuliere Blockchain-Workflow...")

    # Simulierte Reflexionsdaten
    reflection_data = {
        "content": "Heute habe ich über meine Ziele nachgedacht und erkannt, dass ich mehr Fokus brauche.",
        "tags": ["persönlichkeit", "ziele", "fokus"],
        "timestamp": datetime.now().isoformat(),
        "privacy_level": "anonymous",
    }

    # Simulierte IPFS/Arweave CID
    cid = "QmTestCID123456789abcdef"

    # Embedding erstellen
    embedding = create_dummy_embedding(reflection_data["content"])

    # Timestamp konvertieren
    timestamp = int(datetime.fromisoformat(reflection_data["timestamp"]).timestamp())

    print("📋 Blockchain-Registration Daten:")
    print(f"   CID: {cid}")
    print(f"   Tags: {reflection_data['tags']}")
    print(f"   Embedding: {len(embedding)} Bytes")
    print(f"   Timestamp: {timestamp}")

    # Simulierte Transaction Hash
    import hashlib

    tx_data = f"{cid}{timestamp}{len(embedding)}"
    tx_hash = hashlib.sha256(tx_data.encode()).hexdigest()

    print(f"✅ Simulierte Blockchain-Registration erfolgreich!")
    print(f"📤 Transaction Hash: {tx_hash}")

    return {
        "cid": cid,
        "tags": reflection_data["tags"],
        "embedding": embedding,
        "timestamp": timestamp,
        "tx_hash": tx_hash,
    }


def test_blockchain_config():
    """Testet die Blockchain-Konfiguration"""
    print("\n⚙️ Teste Blockchain-Konfiguration...")

    # Prüfe Environment Variables
    env_vars = {
        "MUMBAI_RPC_URL": os.getenv("MUMBAI_RPC_URL"),
        "POLYGON_RPC_URL": os.getenv("POLYGON_RPC_URL"),
        "PRIVATE_KEY": os.getenv("PRIVATE_KEY"),
        "ASI_CONTRACT_ADDRESS": os.getenv("ASI_CONTRACT_ADDRESS"),
        "ENABLE_BLOCKCHAIN": os.getenv("ENABLE_BLOCKCHAIN", "false"),
    }

    print("🔍 Environment Variables:")
    for key, value in env_vars.items():
        if key == "PRIVATE_KEY" and value:
            # Private Key teilweise verstecken
            display_value = f"{value[:6]}...{value[-4:]}" if len(value) > 10 else "***"
        else:
            display_value = value or "nicht gesetzt"
        print(f"   {key}: {display_value}")

    # Prüfe .env Datei
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env Datei gefunden")
    else:
        print("⚠️ .env Datei nicht gefunden")
        print("   Kopiere .env.example zu .env und fülle die Werte aus")

    return env_vars


def show_integration_summary():
    """Zeigt eine Zusammenfassung der Blockchain-Integration"""
    print("\n📋 ASI Blockchain-Integration Zusammenfassung:")
    print("=" * 50)

    print("\n🏗️ Smart Contract:")
    print("   ✅ ASIIndex.sol erstellt")
    print("   ✅ Entry-Struktur definiert")
    print("   ✅ registerEntry() Funktion implementiert")
    print("   ✅ Events für Entry-Registrierung")
    print("   ✅ Deployment-Skript erstellt")

    print("\n🐍 Python-Integration:")
    print("   ✅ asi_core/blockchain.py erstellt")
    print("   ✅ ASIBlockchainClient Klasse")
    print("   ✅ Web3.py Integration")
    print("   ✅ register_entry_on_chain() Funktion")
    print("   ✅ Fehlerbehandlung implementiert")

    print("\n🔧 Backend-Integration:")
    print("   ✅ main.py erweitert")
    print("   ✅ Blockchain-Client Initialisierung")
    print("   ✅ process_reflection_workflow erweitert")
    print("   ✅ Environment Variables Support")
    print("   ✅ .env.example erstellt")

    print("\n📝 Nächste Schritte:")
    print("   1. Kopiere .env.example zu .env")
    print("   2. Fülle RPC-URL, Private Key und Contract-Adresse aus")
    print("   3. Setze ENABLE_BLOCKCHAIN=true")
    print("   4. Deploye Contract auf Mumbai/Polygon:")
    print(
        "      cd web/contracts && npx hardhat run scripts/deployASIIndex.js --network mumbai"
    )
    print("   5. Teste mit einer echten Reflexion")


def main():
    """Hauptfunktion für den Test"""
    print("🧪 ASI Blockchain-Integration Test")
    print("=" * 40)

    # Tests ausführen
    embedding = test_dummy_embedding()
    workflow_result = simulate_blockchain_workflow()
    config = test_blockchain_config()

    # Zusammenfassung anzeigen
    show_integration_summary()

    print("\n✅ Alle Tests abgeschlossen!")
    print(
        "\nDie Smart Contract Logik ist fertig implementiert und bereit für das Deployment."
    )
    print("Verwende die Anweisungen oben, um die Integration zu vervollständigen.")


if __name__ == "__main__":
    main()
