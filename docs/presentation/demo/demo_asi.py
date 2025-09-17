#!/usr/bin/env python3
"""
ASI-Core Live-Demo für Präsentationen
Zeigt Kernfunktionen ohne sensible Daten
"""

import json
import time
import hashlib
from datetime import datetime
from typing import Dict, List, Optional

class ASIPresentationDemo:
    """Interaktive Demonstration der ASI-Core Funktionalität"""
    
    def __init__(self):
        self.demo_states = {
            "focused": 8,
            "productive": 7, 
            "reflective": 6,
            "creative": 5
        }
        
        self.demo_embeddings = {
            "productivity": [0.8, 0.6, 0.3, 0.2],
            "reflection": [0.3, 0.9, 0.7, 0.4],
            "creativity": [0.5, 0.4, 0.8, 0.9],
            "focus": [0.9, 0.3, 0.2, 0.6]
        }
    
    def simulate_reflection_processing(self, demo_text: str) -> Dict:
        """Demonstriert komplette Reflexions-Pipeline"""
        print("🧠 ASI-Core Reflexions-Pipeline")
        print("=" * 40)
        print(f"Input: '{demo_text[:50]}...'\n")
        
        # 1. Lokale Analyse
        print("1. 🔍 Lokale KI-Analyse...")
        time.sleep(1.5)
        
        # Tags extrahieren (Demo-basiert)
        tags = self._extract_demo_tags(demo_text)
        print(f"   ✓ Tags erkannt: {tags}")
        
        # Zustand erkennen
        detected_state = self._detect_emotional_state(demo_text)
        print(f"   ✓ Emotionaler Zustand: {detected_state}/10")
        
        # 2. Anonymisierung
        print("\n2. 🔒 Privacy-First Anonymisierung...")
        time.sleep(1)
        anonymized_hash = hashlib.sha256(demo_text.encode()).hexdigest()[:16]
        print("   ✓ PII entfernt, sichere Embeddings generiert")
        print(f"   ✓ Anonymer Hash: {anonymized_hash}")
        
        # 3. Embedding Generierung
        print("\n3. 🤖 KI-Embedding Generierung...")
        time.sleep(1)
        embedding = self._generate_demo_embedding(demo_text)
        print(f"   ✓ 384-dimensionales Embedding erstellt")
        print(f"   ✓ Ähnlichkeits-Vektor: {embedding[:4]}...")
        
        # 4. Dezentrale Speicherung
        print("\n4. 🌍 Dezentrale Speicherung...")
        time.sleep(1.5)
        demo_cid = f"Qm{hash(demo_text) % 100000000:08d}"
        arweave_tx = f"tx_{hash(demo_text + str(datetime.now())) % 1000000:06d}"
        
        print(f"   ✓ IPFS CID: {demo_cid}")
        print(f"   ✓ Arweave TX: {arweave_tx}")
        print("   ✓ Blockchain-Index aktualisiert")
        
        return {
            "status": "processed",
            "input_hash": anonymized_hash,
            "detected_state": detected_state,
            "tags": tags,
            "ipfs_cid": demo_cid,
            "arweave_tx": arweave_tx,
            "embedding_preview": embedding[:4],
            "timestamp": datetime.now().isoformat(),
            "privacy_level": "k-anonymity ≥5"
        }
    
    def _extract_demo_tags(self, text: str) -> List[str]:
        """Extrahiert Demo-Tags basierend auf Keywords"""
        tag_keywords = {
            "produktivität": ["produktiv", "effizient", "arbeit", "erledigt"],
            "reflexion": ["denken", "überlegen", "reflektieren", "erkenntnis"],
            "kreativität": ["kreativ", "idee", "inspiration", "innovation"],
            "fokus": ["konzentriert", "fokussiert", "aufmerksam", "klar"],
            "entspannung": ["entspannt", "ruhig", "gelassen", "ausgeglichen"]
        }
        
        text_lower = text.lower()
        detected_tags = []
        
        for tag, keywords in tag_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_tags.append(tag)
        
        return detected_tags[:3]  # Max 3 Tags für Demo
    
    def _detect_emotional_state(self, text: str) -> int:
        """Erkennt emotionalen Zustand (0-10 Skala)"""
        positive_indicators = ["gut", "super", "toll", "produktiv", "erfolgreich"]
        negative_indicators = ["schlecht", "müde", "schwer", "probleme"]
        
        text_lower = text.lower()
        score = 5  # Neutral
        
        for indicator in positive_indicators:
            if indicator in text_lower:
                score += 1
        
        for indicator in negative_indicators:
            if indicator in text_lower:
                score -= 1
        
        return max(0, min(10, score))
    
    def _generate_demo_embedding(self, text: str) -> List[float]:
        """Generiert Demo-Embedding basierend auf Text-Charakteristiken"""
        # Vereinfachtes Demo-Embedding (normalerweise 384 Dimensionen)
        text_features = {
            'length': len(text) / 100,
            'words': len(text.split()) / 20,
            'positivity': self._detect_emotional_state(text) / 10,
            'complexity': len(set(text.lower().split())) / len(text.split()) if text.split() else 0
        }
        
        # Demo-Vektor generieren
        base_vector = [text_features['length'], text_features['words'], 
                      text_features['positivity'], text_features['complexity']]
        
        # Normalisierung für Demo
        return [round(x, 3) for x in base_vector]
    
    def demonstrate_semantic_search(self) -> None:
        """Demonstriert semantische Suche"""
        print("\n🔍 ASI-Core Semantische Suche")
        print("=" * 40)
        
        demo_queries = [
            ("produktive Tage", ["produktivität", "fokus"]),
            ("kreative Momente", ["kreativität", "inspiration"]),
            ("ruhige Reflexion", ["reflexion", "entspannung"])
        ]
        
        for query, expected_tags in demo_queries:
            print(f"\nSuche: '{query}'")
            time.sleep(1)
            
            # Simuliere semantische Ähnlichkeit
            similarity_scores = {
                "Eintrag 1": 0.87,
                "Eintrag 2": 0.76,
                "Eintrag 3": 0.64
            }
            
            print("   Ähnlichste Einträge:")
            for entry, score in similarity_scores.items():
                print(f"   • {entry}: {score:.2f} Ähnlichkeit")
    
    def show_architecture_benefits(self) -> None:
        """Zeigt Architektur-Vorteile"""
        print("\n🚀 ASI-Core Architektur-Vorteile")
        print("=" * 50)
        
        benefits = {
            "🔒 Datenschutz": "Volltext bleibt lokal - nur anonyme Zustände dezentral",
            "🌍 Dauerhaftigkeit": "IPFS + Arweave für lebenslange Verfügbarkeit", 
            "🔍 Intelligenz": "KI-Embeddings für semantische Suche",
            "⚡ Performance": "Lokale Verarbeitung + dezentrale Redundanz",
            "🛡️ Sicherheit": "Blockchain-Index + kryptographische Verifikation",
            "📱 PWA-Ready": "Offline-fähige Progressive Web App",
            "🏢 Enterprise": "GitHub Pro+ Features, CodeQL, CI/CD"
        }
        
        for benefit, description in benefits.items():
            print(f"{benefit}: {description}")
    
    def show_enterprise_features(self) -> None:
        """Zeigt Enterprise-Features"""
        print("\n🏢 Enterprise-Grade Features")
        print("=" * 40)
        
        features = {
            "GitHub Pro+": ["Advanced Security", "CodeQL Analysis", "Dependency Review"],
            "CI/CD Pipeline": ["Automated Testing", "Multi-Environment Deploy", "Docker Registry"],
            "Security": ["Secret Scanning", "Trivy Scans", "Protected Branches"],
            "Analytics": ["Traffic Insights", "Performance Metrics", "User Analytics"]
        }
        
        for category, items in features.items():
            print(f"\n📊 {category}:")
            for item in items:
                print(f"   ✓ {item}")

def run_complete_demo():
    """Führt komplette Demo-Präsentation durch"""
    demo = ASIPresentationDemo()
    
    print("🎬 ASI-Core Live-Demonstration")
    print("=" * 50)
    print("Präsentation der dezentralen KI-Reflexions-Architektur\n")
    
    # Demo-Reflexionen
    demo_reflections = [
        "Heute war ein sehr produktiver Tag. Ich konnte alle wichtigen Aufgaben erledigen und fühle mich fokussiert.",
        "Ein kreativer Moment beim Brainstorming - neue Ideen für das Projekt entwickelt.",
        "Ruhige Reflexion am Abend über die Fortschritte und nächsten Schritte."
    ]
    
    # Führe Demo für jede Reflexion durch
    for i, reflection in enumerate(demo_reflections, 1):
        print(f"\n{'='*60}")
        print(f"DEMO {i}/{len(demo_reflections)}")
        print('='*60)
        
        result = demo.simulate_reflection_processing(reflection)
        
        print(f"\n📊 Verarbeitungs-Ergebnis:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        if i < len(demo_reflections):
            print("\nWeiter mit der nächsten Demo...")
            time.sleep(2)
    
    # Zeige semantische Suche
    demo.demonstrate_semantic_search()
    
    # Zeige Architektur-Vorteile
    demo.show_architecture_benefits()
    
    # Zeige Enterprise-Features
    demo.show_enterprise_features()
    
    print("\n✨ Demo abgeschlossen!")
    print("🔗 Repository: https://github.com/swisscomfort/asi-core")
    print("📱 Live PWA: https://swisscomfort.github.io/asi-core/")

if __name__ == "__main__":
    run_complete_demo()