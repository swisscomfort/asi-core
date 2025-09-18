#!/usr/bin/env python3
"""
ASI Core - Hybrid-Modell CLI
Kommandozeilen-Interface für das neue zustandsbasierte System
"""

import argparse
import asyncio
import sys
from pathlib import Path

# ASI Core Module hinzufügen
sys.path.append(str(Path(__file__).parent))
from src.asi_core import ASICore


def main():
    """Hauptfunktion für das CLI"""
    parser = argparse.ArgumentParser(
        description="ASI Core - Hybrid-Modell mit Zustandsmanagement", prog="asi-hybrid"
    )
    subparsers = parser.add_subparsers(dest="command", help="Verfügbare Kommandos")

    # Legacy add-Befehl
    add_parser = subparsers.add_parser("add", help="Fügt eine Reflexion hinzu")
    add_parser.add_argument("content", help="Reflexionsinhalt")
    add_parser.add_argument(
        "--tags", nargs="*", default=[], help="Tags für die Reflexion"
    )

    # Neuer add-state Befehl
    state_parser = subparsers.add_parser(
        "add-state", help="Fügt eine Zustandsreflexion hinzu"
    )
    state_parser.add_argument("content", help="Reflexionsinhalt")
    state_parser.add_argument(
        "--state", type=int, default=0, help="Zustandswert (0-255)"
    )
    state_parser.add_argument(
        "--tags", nargs="*", default=[], help="Tags für die Reflexion"
    )

    # Suchbefehle
    search_parser = subparsers.add_parser("search-state", help="Sucht nach Zustand")
    search_parser.add_argument("state", type=int, help="Zustandswert zum Suchen")

    # Statistiken
    stats_parser = subparsers.add_parser("stats", help="Zeigt Zustandsstatistiken")

    # Export
    export_parser = subparsers.add_parser("export", help="Exportiert Zustandsdaten")
    export_parser.add_argument("--filename", help="Ausgabedatei (optional)")

    # Zustände auflisten
    list_states_parser = subparsers.add_parser(
        "list-states", help="Listet verfügbare Zustände auf"
    )

    # Blockchain-Test
    blockchain_parser = subparsers.add_parser(
        "blockchain", help="Testet Blockchain-Verbindung"
    )

    args = parser.parse_args()

    if not args.command:
        print("🤖 ASI Core - Hybrid-Modell CLI")
        print("Verwende --help für verfügbare Kommandos")
        parser.print_help()
        return

    # ASI System initialisieren
    print("🧠 Initialisiere ASI Core...")
    asi = ASICore()

    # Existierende Reflexionen laden
    asi.load_reflections_from_directory()

    try:
        if args.command == "add":
            # Legacy-Befehl mit automatischer Zustandserkennung
            result = asi.add_reflection(args.content, args.tags)
            print(f"📝 Reflexion hinzugefügt mit automatischem Zustand")

        elif args.command == "add-state":
            # Neuer Zustandsbefehl
            result = asyncio.run(
                asi.add_state_reflection(args.content, args.state, args.tags)
            )
            state_name = asi.state_manager.get_state_name(args.state)
            print(
                f"📝 Zustandsreflexion hinzugefügt: Zustand {args.state} ({state_name})"
            )

        elif args.command == "search-state":
            results = asi.search_by_state(args.state)
            state_name = asi.state_manager.get_state_name(args.state)
            print(f"\n🔍 Suchergebnisse für Zustand {args.state} ({state_name}):")

            if not results:
                print("   Keine Ergebnisse gefunden.")
            else:
                for i, result in enumerate(results, 1):
                    print(f"\n{i}. {result['reflection_text'][:100]}...")
                    print(f"   Tags: {', '.join(result['tags'])}")
                    print(f"   Zeit: {result['timestamp']}")
                    print(f"   Zustand: {result['state_name']}")

        elif args.command == "stats":
            asi.show_state_statistics()

        elif args.command == "export":
            asi.export_state_data(args.filename)

        elif args.command == "list-states":
            states = asi.get_available_states()
            print("\n📋 Verfügbare Zustände:")
            for state_id, info in states.items():
                print(f"  {state_id}: {info['name']} - {info['description']}")

        elif args.command == "blockchain":
            print("\n🔗 Teste Blockchain-Verbindung...")

            if asi.blockchain_client:
                try:
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

                        if blockchain_stats["state_distribution"]:
                            print("   📊 Zustandsverteilung auf Blockchain:")
                            for state, data in blockchain_stats[
                                "state_distribution"
                            ].items():
                                print(
                                    f"      Zustand {state}: {data['count']} ({data['percentage']:.1f}%)"
                                )

                    except Exception as e:
                        print(f"   ⚠️ Statistiken-Fehler: {e}")

                except Exception as e:
                    print(f"   ❌ Blockchain-Fehler: {e}")
            else:
                print("   ⚠️ Keine Blockchain-Konfiguration gefunden")
                print("   💡 Konfiguriere config/secrets.json für Blockchain-Features")

    except KeyboardInterrupt:
        print("\n\n👋 Auf Wiedersehen!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fehler: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
