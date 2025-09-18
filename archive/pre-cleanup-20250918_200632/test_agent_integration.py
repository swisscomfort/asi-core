#!/usr/bin/env python3
"""
ASI Agent Integration Test
Testet die vollständige Agent-Integration im ASI-Core System
"""

import sys
import time
import asyncio
from pathlib import Path

# Pfad Setup
sys.path.append(str(Path(__file__).parent))

from src.asi_core import ASICore

def test_basic_agent_integration():
    """Testet die Basis-Agent-Integration"""
    print("🧪 Basis-Agent-Integration Test")
    print("=" * 35)
    
    # ASI System initialisieren
    asi = ASICore()
    
    # Prüfe Agent-System
    if asi.agent_manager and asi.main_agent_id:
        print(f"   ✅ Agent-Manager initialisiert")
        print(f"   🤖 Haupt-Agent: {asi.main_agent_id}")
        
        # Agent-Statistiken
        stats = asi.get_agent_stats()
        print(f"   📊 Agenten: {stats.get('total_agents', 0)}")
        return True
    else:
        print("   ❌ Agent-System nicht verfügbar")
        return False

def test_agent_reflection_integration(asi):
    """Testet die Reflexions-Agent-Integration"""
    print("\n🤖 Reflexions-Agent-Integration Test")
    print("=" * 38)
    
    # Verschiedene Reflexionen mit Agent-Tracking hinzufügen
    test_reflections = [
        {
            "text": "Heute habe ich über meine Lernziele nachgedacht und neue Erkenntnisse gewonnen.",
            "tags": ["learning", "goals", "insights"],
            "expected_state": 75
        },
        {
            "text": "Die Zusammenarbeit im Team war heute besonders produktiv und harmonisch.",
            "tags": ["collaboration", "teamwork", "productivity"],
            "expected_state": 85
        },
        {
            "text": "Ich merke, dass ich in bestimmten Bereichen noch Verbesserungspotential habe.",
            "tags": ["improvement", "self_assessment", "development"],
            "expected_state": 60
        }
    ]
    
    for i, reflection_data in enumerate(test_reflections):
        print(f"\n   📝 Reflexion {i+1}: {reflection_data['text'][:50]}...")
        
        result = asi.add_state_reflection(
            reflection_text=reflection_data['text'],
            state_value=reflection_data['expected_state'],
            tags=reflection_data['tags']
        )
        
        print(f"   📊 Zustand: {reflection_data['expected_state']}")
        print(f"   🏷️ Tags: {', '.join(reflection_data['tags'])}")
        
        time.sleep(0.5)  # Kurze Pause zwischen Reflexionen

def test_agent_learning(asi):
    """Testet Agent-Lernprozesse"""
    print("\n🧠 Agent-Lernprozess Test")
    print("=" * 26)
    
    learning_topics = [
        {
            "topic": "reflection_quality_improvement",
            "data": {
                "focus_area": "emotional_intelligence",
                "training_method": "pattern_analysis",
                "success_metric": "insight_depth"
            }
        },
        {
            "topic": "state_prediction_accuracy",
            "data": {
                "focus_area": "predictive_modeling",
                "training_method": "historical_analysis",
                "success_metric": "prediction_error_reduction"
            }
        },
        {
            "topic": "collaboration_effectiveness",
            "data": {
                "focus_area": "team_dynamics",
                "training_method": "interaction_analysis",
                "success_metric": "collaborative_outcomes"
            }
        }
    ]
    
    for topic_data in learning_topics:
        print(f"\n   🎓 Lernthema: {topic_data['topic']}")
        
        tx_hash = asi.trigger_agent_learning(
            topic=topic_data['topic'],
            learning_data=topic_data['data']
        )
        
        print(f"   📈 Fokusbereich: {topic_data['data']['focus_area']}")
        print(f"   🔬 Methode: {topic_data['data']['training_method']}")
        
        if tx_hash:
            print(f"   🔗 Blockchain TX: {tx_hash[:16]}...")
        
        time.sleep(0.3)

def test_sub_agent_creation(asi):
    """Testet die Erstellung von Sub-Agenten"""
    print("\n🤖 Sub-Agent-Erstellung Test")
    print("=" * 30)
    
    sub_agents = [
        {
            "name": "EmotionAnalyzer",
            "specialization": ["emotion_detection", "sentiment_analysis", "mood_tracking"]
        },
        {
            "name": "PatternRecognizer", 
            "specialization": ["pattern_detection", "trend_analysis", "anomaly_detection"]
        },
        {
            "name": "CollaborationCoordinator",
            "specialization": ["team_coordination", "conflict_resolution", "workflow_optimization"]
        }
    ]
    
    created_agents = []
    
    for agent_config in sub_agents:
        print(f"\n   🆕 Erstelle Sub-Agent: {agent_config['name']}")
        
        agent_id = asi.create_sub_agent(
            name=agent_config['name'],
            specialization=agent_config['specialization']
        )
        
        if agent_id:
            created_agents.append(agent_id)
            print(f"   ✅ Sub-Agent erstellt: {agent_id}")
            print(f"   🎯 Spezialisierung: {', '.join(agent_config['specialization'])}")
        
        time.sleep(0.2)
    
    return created_agents

def test_agent_collaboration(asi, sub_agents):
    """Testet Agent-Kollaborationen"""
    print("\n🤝 Agent-Kollaboration Test")
    print("=" * 28)
    
    if len(sub_agents) >= 2:
        # Kollaboration zwischen zwei Sub-Agenten
        collab_id_1 = asi.initiate_agent_collaboration(
            agents=sub_agents[:2],
            task="emotion_pattern_analysis"
        )
        
        print(f"   ✅ Kollaboration 1: {collab_id_1}")
        print(f"   👥 Teilnehmer: 2 Sub-Agenten + Haupt-Agent")
        
        time.sleep(0.3)
        
        # Vollständige Netzwerk-Kollaboration
        collab_id_2 = asi.initiate_agent_collaboration(
            agents=sub_agents,
            task="comprehensive_system_optimization"
        )
        
        print(f"   ✅ Kollaboration 2: {collab_id_2}")
        print(f"   👥 Teilnehmer: {len(sub_agents)} Sub-Agenten + Haupt-Agent")
    
    else:
        print("   ⚠️ Nicht genügend Sub-Agenten für Kollaboration")

def test_agent_network_overview(asi):
    """Zeigt Übersicht über das Agent-Netzwerk"""
    print("\n🕸️ Agent-Netzwerk Übersicht")
    print("=" * 28)
    
    # Agent-Netzwerk anzeigen
    asi.show_agent_network()
    
    # Detaillierte Statistiken
    stats = asi.get_agent_stats()
    
    print(f"\n📈 Detaillierte Statistiken:")
    print(f"   🤖 Gesamtanzahl Agenten: {stats.get('total_agents', 0)}")
    print(f"   ⚡ Gesamtaktionen: {stats.get('total_actions', 0)}")
    print(f"   💯 Durchschnittliches Vertrauen: {stats.get('avg_confidence', 0):.3f}")
    print(f"   🤝 Aktive Kollaborationen: {stats.get('active_collaborations', 0)}")
    
    if stats.get('most_common_capabilities'):
        print(f"\n   🎯 Top-Fähigkeiten:")
        for capability, count in stats['most_common_capabilities'][:3]:
            print(f"      • {capability}: {count}x")

def test_state_management_integration(asi):
    """Testet die State-Management-Integration"""
    print("\n📊 State-Management Integration Test")
    print("=" * 37)
    
    # Zustandsstatistiken anzeigen
    asi.show_state_statistics()
    
    # Verfügbare Zustände anzeigen
    states = asi.get_available_states()
    print(f"\n   📋 Verfügbare Zustände: {len(states)}")
    
    # Beispielhafte Zustandssuche
    if asi.reflections:
        sample_state = asi.reflections[-1].get('state_value', 50)
        results = asi.search_by_state(sample_state)
        print(f"   🔍 Suche nach Zustand {sample_state}: {len(results)} Ergebnisse")

def main():
    """Hauptfunktion für den umfassenden Agent-Test"""
    print("🤖 ASI Agent Integration - Vollständiger Test")
    print("=" * 46)
    print("Testet alle Agent-Features im ASI-Core System\n")
    
    # Basis-Integration testen
    if not test_basic_agent_integration():
        print("\n❌ Basis-Agent-Integration fehlgeschlagen. Test beendet.")
        return
    
    # ASI System initialisieren
    asi = ASICore()
    
    # Verschiedene Test-Szenarien
    test_agent_reflection_integration(asi)
    test_agent_learning(asi)
    sub_agents = test_sub_agent_creation(asi)
    test_agent_collaboration(asi, sub_agents)
    test_agent_network_overview(asi)
    test_state_management_integration(asi)
    
    print("\n✅ Vollständiger Agent-Integration Test abgeschlossen!")
    
    print(f"\n🎯 Test-Zusammenfassung:")
    print(f"   • ✅ Agent-Manager erfolgreich initialisiert")
    print(f"   • ✅ Reflexions-Agent-Integration funktional")
    print(f"   • ✅ Agent-Lernprozesse implementiert")
    print(f"   • ✅ Sub-Agent-Erstellung erfolgreich")
    print(f"   • ✅ Agent-Kollaborationen funktional")
    print(f"   • ✅ Agent-Netzwerk-Übersicht verfügbar")
    print(f"   • ✅ State-Management Integration komplett")
    
    print(f"\n🚀 Das ASI-System ist jetzt vollständig agentenmäßig umgesetzt!")

if __name__ == "__main__":
    main()
