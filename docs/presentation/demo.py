#!/usr/bin/env python3
"""
ASI-Core Live-Präsentation für Codespace
Einfache, lokale Demo ohne externe Abhängigkeiten
"""

import json
import time
import hashlib
from datetime import datetime
from pathlib import Path

class ASIPresentationDemo:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.demo_data = {
            "states": {
                "focused": 0,
                "meditated": 0,
                "walked": 0,
                "reflected": 0
            },
            "sessions": []
        }
    
    def simulate_reflection_workflow(self, text="Heute war ein produktiver Tag."):
        """Simuliert kompletten ASI-Workflow"""
        print("🧠 ASI-Core Reflexions-Pipeline Demo")
        print("=" * 50)
        
        # Schritt 1: Lokale Analyse
        print("1️⃣ Lokale Verarbeitung...")
        time.sleep(1)
        
        # Einfache Tag-Extraktion (Demo)
        tags = []
        if "produktiv" in text.lower():
            tags.append("produktivität")
        if "tag" in text.lower():
            tags.append("alltag")
        if "gut" in text.lower() or "positiv" in text.lower():
            tags.append("positiv")
        
        print(f"   ✓ Tags extrahiert: {tags}")
        
        # Schritt 2: Anonymisierung
        print("2️⃣ Anonymisierung...")
        time.sleep(1)
        
        # Einfacher Hash als CID-Simulation
        text_hash = hashlib.md5(text.encode()).hexdigest()[:16]
        fake_cid = f"Qm{text_hash}"
        
        print(f"   ✓ PII entfernt, CID generiert: {fake_cid}")
        
        # Schritt 3: Dezentrale Speicherung (Simulation)
        print("3️⃣ Dezentrale Speicherung...")
        time.sleep(1)
        print(f"   ✓ IPFS: {fake_cid}")
        print(f"   ✓ Blockchain-Index aktualisiert")
        
        # Ergebnis speichern
        session = {
            "timestamp": datetime.now().isoformat(),
            "cid": fake_cid,
            "tags": tags,
            "sentiment": "positiv" if any(pos in text.lower() for pos in ["gut", "produktiv", "toll"]) else "neutral"
        }
        
        self.demo_data["sessions"].append(session)
        
        return session
    
    def show_architecture_overview(self):
        """Zeigt Systemarchitektur"""
        print("\n🏗️ ASI-Core Architektur")
        print("=" * 40)
        
        layers = [
            ("🔒 Lokale Ebene", "Volltext, Kontext, Privatsphäre"),
            ("🔄 Verarbeitung", "KI-Analyse, Tag-Extraktion"),
            ("🛡️ Anonymisierung", "PII-Entfernung, Embeddings"),
            ("🌍 Dezentral", "IPFS, Arweave, Blockchain-Index")
        ]
        
        for layer, description in layers:
            print(f"{layer}: {description}")
    
    def show_benefits(self):
        """Zeigt Hauptvorteile"""
        print("\n⭐ Kernvorteile")
        print("=" * 30)
        
        benefits = [
            "🔐 100% Datenschutz durch lokale Verarbeitung",
            "🌐 Dezentrale Redundanz für Dauerhaftigkeit", 
            "🧠 KI-gestützte semantische Suche",
            "⚡ Offline-fähig, keine Cloud-Abhängigkeit",
            "🔍 Verifikierbare Integrität durch Blockchain"
        ]
        
        for benefit in benefits:
            print(f"  {benefit}")
    
    def interactive_demo(self):
        """Interaktive Demo-Session"""
        print("\n🎬 Interaktive ASI-Core Demo")
        print("=" * 40)
        
        # Demo-Reflexionen
        demo_texts = [
            "Heute hatte ich einen sehr produktiven Tag mit klaren Zielen.",
            "Meditation am Morgen hat mir geholfen, fokussiert zu bleiben.",
            "Der Spaziergang war entspannend und inspirierend."
        ]
        
        for i, text in enumerate(demo_texts, 1):
            print(f"\n📝 Demo-Reflexion {i}: {text}")
            result = self.simulate_reflection_workflow(text)
            print(f"📊 Ergebnis: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if i < len(demo_texts):
                input("\n⏸️  Drücke Enter für nächste Demo...")
    
    def export_demo_data(self):
        """Exportiert Demo-Daten"""
        export_file = self.base_path / "demo_results.json"
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(self.demo_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Demo-Daten exportiert: {export_file}")

def main():
    demo = ASIPresentationDemo()
    
    print("🧠 ASI-Core: Dezentrale Datensouveränität")
    print("=" * 50)
    
    # Architektur zeigen
    demo.show_architecture_overview()
    
    # Vorteile aufzeigen
    demo.show_benefits()
    
    # Interaktive Demo
    demo.interactive_demo()
    
    # Export
    demo.export_demo_data()
    
    print("\n✅ Präsentation abgeschlossen!")

if __name__ == "__main__":
    main()
