#!/usr/bin/env python3
"""
ASI Core - Demo der erweiterten Module
Zeigt die neuen Features in Aktion
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# ASI Core Module laden
sys.path.append(str(Path(__file__).parent))

from tests.generate_test_data import generate_sample_reflections, save_test_reflections


def demo_enhanced_search():
    """Demonstriert die erweiterten Suchfunktionen"""
    print("🔍 ASI Core - Erweiterte Suche Demo")
    print("=" * 50)
    
    # Test-Daten generieren
    print("1. Generiere Test-Reflexionen...")
    reflections = generate_sample_reflections(20)
    
    print(f"✅ {len(reflections)} Test-Reflexionen erstellt")
    
    # Kategorien-Übersicht
    categories = {}
    state_ranges = {
        "Low (0-63)": 0,
        "Medium-Low (64-127)": 0,
        "Medium-High (128-191)": 0,
        "High (192-255)": 0
    }
    
    for ref in reflections:
        cat = ref["category"]
        state = ref["state_value"]
        categories[cat] = categories.get(cat, 0) + 1
        
        if 0 <= state <= 63:
            state_ranges["Low (0-63)"] += 1
        elif 64 <= state <= 127:
            state_ranges["Medium-Low (64-127)"] += 1
        elif 128 <= state <= 191:
            state_ranges["Medium-High (128-191)"] += 1
        else:
            state_ranges["High (192-255)"] += 1
    
    print("\n📊 Kategorien-Verteilung:")
    for cat, count in categories.items():
        print(f"  {cat}: {count} Reflexionen")
    
    print("\n🎯 State-Verteilung:")
    for range_name, count in state_ranges.items():
        print(f"  {range_name}: {count} Reflexionen")
    
    # Beispiel-Suchen
    print("\n🔍 Beispiel-Suchen:")
    
    # Suche nach State-Bereich
    work_reflections = [r for r in reflections if r["category"] == "arbeit"]
    if work_reflections:
        example_state = work_reflections[0]["state_value"]
        print(f"  → Suche nach Zustand {example_state} ±10")
        similar_states = [r for r in reflections 
                         if abs(r["state_value"] - example_state) <= 10]
        print(f"    Gefunden: {len(similar_states)} ähnliche Zustände")
    
    # Themen-Suche
    creative_reflections = [r for r in reflections if r["category"] == "kreativität"]
    if creative_reflections:
        print(f"  → Suche nach Kreativitäts-Reflexionen")
        print(f"    Gefunden: {len(creative_reflections)} Einträge")
    
    # Zeitbasierte Suche
    recent = datetime.now() - timedelta(days=7)
    recent_reflections = [r for r in reflections 
                         if datetime.fromisoformat(r["timestamp"]) > recent]
    print(f"  → Suche nach Reflexionen der letzten 7 Tage")
    print(f"    Gefunden: {len(recent_reflections)} Einträge")


def demo_blockchain_client():
    """Demonstriert den erweiterten Blockchain Client"""
    print("\n⛓️ Blockchain Client Demo")
    print("=" * 30)
    
    print("🔧 Features des ASI Blockchain Client:")
    print("  ✅ Vollständige Web3 Integration")
    print("  ✅ Polygon Mumbai Support")
    print("  ✅ Smart Contract ABI Management")
    print("  ✅ Transaction Status Tracking")
    print("  ✅ State Statistics from Chain")
    print("  ✅ Automatisches Gas Management")
    print("  ✅ Comprehensive Error Handling")
    
    print("\n📁 Client-Struktur:")
    print("  → ASIBlockchainClient")
    print("    ├── register_entry_on_chain()")
    print("    ├── get_transaction_status()")
    print("    ├── get_state_statistics()")
    print("    ├── wait_for_confirmation()")
    print("    └── _get_network_name()")


def demo_config_structure():
    """Zeigt die erweiterte Konfiguration"""
    print("\n⚙️ Konfiguration Demo")
    print("=" * 25)
    
    print("📋 Erweiterte settings.json:")
    print("  • ASI Version 2.0.0")
    print("  • State Management aktiviert")
    print("  • HRM Module integriert")
    print("  • Embedding Cache konfiguriert")
    print("  • UI-Einstellungen")
    
    print("\n🔐 secrets.example.json:")
    print("  • Blockchain Credentials")
    print("  • Storage API Keys")
    print("  • Memory Token Configuration")
    print("  • Payment Integration")


def demo_smart_contract():
    """Zeigt Smart Contract Features"""
    print("\n🏗️ Smart Contract Demo")
    print("=" * 28)
    
    print("📜 ASI Smart Contract ABI:")
    print("  ├── registerEntry() - Standard Entry")
    print("  ├── registerHybridEntry() - Mit State Value")
    print("  ├── getStateStatistics() - Statistiken")
    print("  ├── getEntriesByState() - State-Suche")
    print("  ├── getEntry() - Entry Details")
    print("  └── EntryRegistered Event")
    
    print("\n🎯 Hybrid Model Features:")
    print("  • State Value (0-255) Support")
    print("  • On-Chain State Statistics")
    print("  • State-based Entry Retrieval")
    print("  • Event-based Monitoring")


def show_integration_overview():
    """Zeigt Übersicht der Integration"""
    print("\n🚀 ASI Core 2.0 - Integration Overview")
    print("=" * 45)
    
    print("📦 Neue Module:")
    print("  ✅ src/asi_core/blockchain/client.py")
    print("  ✅ src/ai/search.py (erweitert)")
    print("  ✅ contracts/ASI.json")
    print("  ✅ tests/generate_test_data.py")
    print("  ✅ config/settings.json (erweitert)")
    print("  ✅ config/secrets.example.json (erweitert)")
    
    print("\n🔧 Erweiterte Features:")
    print("  • State-basierte Suche")
    print("  • Erweiterte Blockchain Integration")
    print("  • Hybrid Model Smart Contract")
    print("  • Realistische Test-Daten")
    print("  • Konfigurierbare Settings")
    
    print("\n🎯 Ready für:")
    print("  • Polygon Mumbai Deployment")
    print("  • State Management Integration")
    print("  • Erweiterte Suchfunktionen")
    print("  • Comprehensive Testing")
    
    print("\n💡 Nächste Schritte:")
    print("  1. Test-Daten generieren: python tests/generate_test_data.py")
    print("  2. Blockchain konfigurieren: config/secrets.json")
    print("  3. State Management testen")
    print("  4. Smart Contract deployen")


def main():
    """Hauptfunktion der Demo"""
    print("🎉 ASI Core 2.0 - Erweiterte Module Demo")
    print("=" * 60)
    
    try:
        demo_enhanced_search()
        demo_blockchain_client()
        demo_config_structure()
        demo_smart_contract()
        show_integration_overview()
        
        print(f"\n✅ Demo erfolgreich abgeschlossen!")
        print("🚀 ASI Core ist bereit für die nächste Stufe!")
        
    except Exception as e:
        print(f"❌ Fehler in Demo: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
