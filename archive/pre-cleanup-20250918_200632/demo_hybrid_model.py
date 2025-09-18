#!/usr/bin/env python3
"""
ASI Core - Hybrid-Modell Demo
Demonstration der zustandsbasierten Speicherung und Blockchain-Integration
"""

import asyncio
import sys
from pathlib import Path

# ASI Core Module hinzufügen
sys.path.append(str(Path(__file__).parent))
from src.asi_core import ASICore


async def demo_hybrid_model():
    """Demonstriert das Hybrid-Modell mit verschiedenen Zuständen"""

    print("🚀 ASI Core Hybrid-Modell Demo")
    print("=" * 50)

    # ASI System initialisieren
    asi = ASICore()

    # Existierende Reflexionen laden
    asi.load_reflections_from_directory()

    print("\n📋 Verfügbare Zustände:")
    states = asi.get_available_states()
    for state_id, info in states.items():
        print(f"  {state_id}: {info['name']} - {info['description']}")

    print("\n🔄 Erstelle Demo-Reflexionen mit verschiedenen Zuständen...")

    # Demo-Reflexionen mit verschiedenen Zuständen
    demo_reflections = [
        {
            "text": "Heute habe ich einen wichtigen Durchbruch bei der Blockchain-Integration erzielt. Das neue Hybrid-Modell funktioniert perfekt!",
            "state": 1,  # Positiv
            "tags": ["#blockchain", "#durchbruch", "#erfolg"],
        },
        {
            "text": "Probleme mit der Smart Contract Compilation. Muss die Syntax nochmal überprüfen und Fehler beheben.",
            "state": 2,  # Negativ/Herausfordernd
            "tags": ["#problem", "#smartcontract", "#debugging"],
        },
        {
            "text": "Kritische Erkenntnis: Die Zustandsverteilung ermöglicht es, Reflexionen viel gezielter zu kategorisieren und zu durchsuchen.",
            "state": 3,  # Kritisch/Wichtig
            "tags": ["#erkenntnis", "#wichtig", "#zustandsmodell"],
        },
        {
            "text": "Experimentiere mit verschiedenen Embedding-Größen für die Blockchain-Speicherung. 128 Bytes scheinen optimal zu sein.",
            "state": 4,  # Experimentell
            "tags": ["#experiment", "#embedding", "#optimierung"],
        },
        {
            "text": "Standard-Reflexion ohne besonderen Fokus. Einfach ein paar Gedanken für heute festhalten.",
            "state": 0,  # Neutral
            "tags": ["#alltag", "#gedanken"],
        },
    ]

    # Reflexionen hinzufügen
    for i, reflection in enumerate(demo_reflections, 1):
        print(f"\n{i}. Füge Reflexion hinzu (Zustand: {reflection['state']})...")

        try:
            result = await asi.add_state_reflection(
                reflection["text"], reflection["state"], reflection["tags"]
            )

            print(f"   ✅ Erfolgreich: {result['state_name']}")

            # Kurze Pause zwischen den Transaktionen
            await asyncio.sleep(1)

        except Exception as e:
            print(f"   ❌ Fehler: {e}")

    print("\n📊 Zustandsstatistiken nach Demo:")
    asi.show_state_statistics()

    print("\n🔍 Test: Suche nach verschiedenen Zuständen")

    # Test verschiedener Suchvorgänge
    test_states = [1, 2, 3]
    for state in test_states:
        results = asi.search_by_state(state)
        state_name = asi.state_manager.get_state_name(state)
        print(f"\n   Zustand {state} ({state_name}): {len(results)} Ergebnisse")

        for result in results:
            print(f"     • {result['reflection_text'][:60]}...")

    print("\n💾 Exportiere Zustandsdaten...")
    try:
        export_file = "data/state_exports/demo_export.json"
        asi.export_state_data(export_file)
        print(f"   ✅ Export gespeichert: {export_file}")
    except Exception as e:
        print(f"   ❌ Export-Fehler: {e}")

    print("\n🎯 Demo abgeschlossen!")
    print("\nVerwenden Sie folgende Kommandos zum Testen:")
    print("  python main.py add-state 'Meine Reflexion' --state 1 --tags '#test'")
    print("  python main.py search-state 1")
    print("  python main.py stats")
    print("  python main.py list-states")


def demo_blockchain_connection():
    """Testet die Blockchain-Verbindung"""
    print("\n🔗 Teste Blockchain-Verbindung...")

    try:
        asi = ASICore()

        if asi.blockchain_client:
            total_entries = asi.blockchain_client.get_total_entries()
            balance = asi.blockchain_client.get_balance()

            print(f"   ✅ Verbindung erfolgreich")
            print(f"   📊 Einträge im Contract: {total_entries}")
            print(f"   💰 Wallet Balance: {balance:.4f} ETH")

            # Test State Statistics vom Contract
            try:
                blockchain_stats = asi.blockchain_client.get_state_statistics()
                print(
                    f"   📈 Blockchain-Statistiken: {blockchain_stats['total_entries']} Einträge"
                )
            except Exception as e:
                print(f"   ⚠️ Statistiken-Fehler: {e}")

        else:
            print("   ⚠️ Keine Blockchain-Konfiguration gefunden")

    except Exception as e:
        print(f"   ❌ Blockchain-Fehler: {e}")


if __name__ == "__main__":
    print("🤖 ASI Core Hybrid-Modell Demo")

    if len(sys.argv) > 1 and sys.argv[1] == "blockchain":
        demo_blockchain_connection()
    else:
        # Hauptdemo ausführen
        asyncio.run(demo_hybrid_model())
