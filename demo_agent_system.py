#!/usr/bin/env python3
"""
ASI Agent System Demo - Autonome Agent-Verwaltung
Demonstriert die Agent-spezifischen Blockchain-Features
"""

import os
import sys
import time
from pathlib import Path

# ASI Core Module laden
sys.path.append(str(Path(__file__).parent))

from asi_core.blockchain import ASIBlockchainClient, create_blockchain_client_from_config, create_dummy_embedding
from asi_core.agent_manager import ASIAgentManager, create_agent_manager_from_config

def demo_agent_registration():
    """Demonstriert die Agent-Registrierung"""
    print("\n🤖 Agent-Registrierung Demo")
    print("=" * 35)
    
    # Agent-Manager erstellen
    agent_manager = create_agent_manager_from_config()
    
    # Verschiedene Agent-Typen registrieren
    agents = [
        {
            "name": "ReflectionBot",
            "capabilities": ["reflection", "emotional_analysis", "pattern_recognition"],
            "learning_goals": ["improve_emotional_intelligence", "better_pattern_matching"]
        },
        {
            "name": "DataAnalyzer",
            "capabilities": ["data_analysis", "statistical_modeling", "prediction"],
            "learning_goals": ["accuracy_improvement", "speed_optimization"]
        },
        {
            "name": "CollaborationAgent",
            "capabilities": ["coordination", "communication", "conflict_resolution"],
            "learning_goals": ["team_dynamics", "negotiation_skills"]
        }
    ]
    
    registered_agents = []
    for agent_config in agents:
        agent_id = agent_manager.register_agent(**agent_config)
        registered_agents.append(agent_id)
        print(f"   ✅ {agent_config['name']} registriert: {agent_id}")
    
    return agent_manager, registered_agents

def demo_agent_actions(agent_manager, agent_ids):
    """Demonstriert Agent-Aktionen"""
    print("\n⚡ Agent-Aktionen Demo")
    print("=" * 25)
    
    actions = [
        {"agent_id": agent_ids[0], "action": "reflection", "confidence": 0.85, "data": {"mood": "optimistic", "insights": 3}},
        {"agent_id": agent_ids[1], "action": "analysis", "confidence": 0.92, "data": {"dataset_size": 1000, "accuracy": 0.94}},
        {"agent_id": agent_ids[2], "action": "coordination", "confidence": 0.78, "data": {"team_size": 5, "conflicts_resolved": 2}},
        {"agent_id": agent_ids[0], "action": "pattern_detection", "confidence": 0.88, "data": {"patterns_found": 7, "relevance": "high"}},
    ]
    
    for action in actions:
        tx_hash = agent_manager.record_agent_action(
            agent_id=action["agent_id"],
            action_type=action["action"],
            result_data=action["data"],
            confidence=action["confidence"]
        )
        
        agent = agent_manager.get_agent(action["agent_id"])
        print(f"   📝 {agent.name}: {action['action']} (Confidence: {action['confidence']:.2f})")
        if tx_hash:
            print(f"      🔗 Blockchain TX: {tx_hash[:16]}...")
    
    time.sleep(1)  # Kurze Pause für Demonstration

def demo_agent_learning(agent_manager, agent_ids):
    """Demonstriert Agent-Lernprozesse"""
    print("\n🧠 Agent-Lernprozesse Demo")
    print("=" * 30)
    
    learning_sessions = [
        {
            "agent_id": agent_ids[0],
            "topic": "emotional_pattern_recognition",
            "improvement": 0.15,
            "data": {"training_samples": 500, "accuracy_gain": 0.12, "method": "supervised_learning"}
        },
        {
            "agent_id": agent_ids[1],
            "topic": "statistical_modeling_optimization",
            "improvement": 0.08,
            "data": {"algorithms_tested": 3, "performance_gain": 0.22, "method": "hyperparameter_tuning"}
        },
        {
            "agent_id": agent_ids[2],
            "topic": "conflict_resolution_strategies",
            "improvement": 0.20,
            "data": {"scenarios_practiced": 25, "success_rate_improvement": 0.18, "method": "reinforcement_learning"}
        }
    ]
    
    for session in learning_sessions:
        tx_hash = agent_manager.record_agent_learning(
            agent_id=session["agent_id"],
            topic=session["topic"],
            improvement_score=session["improvement"],
            learning_data=session["data"]
        )
        
        agent = agent_manager.get_agent(session["agent_id"])
        print(f"   🎓 {agent.name}: {session['topic']}")
        print(f"      📈 Verbesserung: +{session['improvement']:.1%}")
        if tx_hash:
            print(f"      🔗 Blockchain TX: {tx_hash[:16]}...")

def demo_agent_collaboration(agent_manager, agent_ids):
    """Demonstriert Agent-Kollaborationen"""
    print("\n🤝 Agent-Kollaboration Demo")
    print("=" * 30)
    
    # Kollaboration zwischen ReflectionBot und DataAnalyzer
    collab_id = agent_manager.initiate_collaboration(
        agent_ids=agent_ids[:2],
        collaboration_type="data_reflection_analysis",
        goals=["combine_emotional_and_statistical_insights", "improve_prediction_accuracy"]
    )
    
    print(f"   ✅ Kollaboration gestartet: {collab_id}")
    print(f"   👥 Teilnehmer: {len(agent_ids[:2])} Agenten")
    
    # Kollaboration zwischen allen drei Agenten
    full_collab_id = agent_manager.initiate_collaboration(
        agent_ids=agent_ids,
        collaboration_type="comprehensive_analysis",
        goals=["holistic_data_understanding", "optimal_team_coordination"]
    )
    
    print(f"   ✅ Vollständige Kollaboration: {full_collab_id}")
    print(f"   👥 Teilnehmer: {len(agent_ids)} Agenten")

def demo_agent_statistics(agent_manager):
    """Zeigt Agent-Statistiken"""
    print("\n📊 Agent-Statistiken")
    print("=" * 20)
    
    stats = agent_manager.get_agent_statistics()
    
    print(f"   🤖 Gesamtanzahl Agenten: {stats['total_agents']}")
    print(f"   ✅ Aktive Agenten (24h): {stats['active_agents']}")
    print(f"   ⚡ Gesamtaktionen: {stats['total_actions']}")
    print(f"   💯 Durchschnittliches Vertrauen: {stats['avg_confidence']:.3f}")
    print(f"   🤝 Aktive Kollaborationen: {stats['active_collaborations']}")
    
    if stats['most_common_capabilities']:
        print("\n   🎯 Häufigste Fähigkeiten:")
        for capability, count in stats['most_common_capabilities']:
            print(f"      • {capability}: {count}x")

def demo_blockchain_integration():
    """Demonstriert die Blockchain-Integration"""
    print("\n🔗 Blockchain-Integration Demo")
    print("=" * 33)
    
    # Versuche Blockchain-Client zu erstellen
    blockchain_client = create_blockchain_client_from_config()
    
    if blockchain_client and blockchain_client.is_connected():
        print("   ✅ Blockchain-Verbindung aktiv")
        
        # Netzwerk-Statistiken
        try:
            network_stats = blockchain_client.get_agent_network_stats()
            print(f"   📈 Netzwerk-Agenten: {network_stats.get('total_agents', 0)}")
            print(f"   ⚡ Netzwerk-Aktionen: {network_stats.get('total_actions', 0)}")
            print(f"   👥 Aktive Agenten (24h): {network_stats.get('active_agents_24h', 0)}")
        except Exception as e:
            print(f"   ⚠️ Netzwerk-Statistiken nicht verfügbar: {e}")
        
        return blockchain_client
    else:
        print("   ⚠️ Keine Blockchain-Verbindung")
        print("   💡 Für Blockchain-Features konfiguriere:")
        print("      • MUMBAI_RPC_URL")
        print("      • PRIVATE_KEY") 
        print("      • ASI_CONTRACT_ADDRESS")
        return None

def show_agent_profiles(agent_manager):
    """Zeigt detaillierte Agent-Profile"""
    print("\n👤 Agent-Profile")
    print("=" * 16)
    
    agents = agent_manager.list_agents()
    
    for agent in agents:
        print(f"\n   🤖 {agent.name} (ID: {agent.agent_id})")
        print(f"      📦 Version: {agent.version}")
        print(f"      🎯 Fähigkeiten: {', '.join(agent.capabilities)}")
        print(f"      🎓 Lernziele: {', '.join(agent.learning_goals)}")
        print(f"      ⚡ Aktionen: {agent.total_actions}")
        print(f"      💯 Avg. Vertrauen: {agent.avg_confidence:.3f}")
        print(f"      ⏰ Letzte Aktivität: {agent.last_active[:19]}")

def main():
    """Hauptfunktion für das Agent-Demo"""
    print("🤖 ASI Agent System Demo")
    print("=" * 25)
    print("Demonstriert autonome Agent-Verwaltung mit Blockchain-Integration\n")
    
    # Blockchain-Integration testen
    blockchain_client = demo_blockchain_integration()
    
    # Agent-Manager mit Blockchain-Client erstellen
    if blockchain_client:
        agent_manager = ASIAgentManager(blockchain_client=blockchain_client)
    else:
        agent_manager = create_agent_manager_from_config()
    
    # Demo-Sequenz ausführen
    agent_manager, agent_ids = demo_agent_registration()
    demo_agent_actions(agent_manager, agent_ids)
    demo_agent_learning(agent_manager, agent_ids)
    demo_agent_collaboration(agent_manager, agent_ids)
    demo_agent_statistics(agent_manager)
    show_agent_profiles(agent_manager)
    
    print("\n✅ Agent-Demo abgeschlossen!")
    print("\nDas ASI Agent System bietet:")
    print("• 🤖 Autonome Agent-Registrierung und -Verwaltung")
    print("• ⚡ Blockchain-basierte Aktionsprotokollierung") 
    print("• 🧠 Lernprozess-Tracking mit Verbesserungsmetriken")
    print("• 🤝 Multi-Agent-Kollaborationen")
    print("• 📊 Umfassende Agent- und Netzwerk-Statistiken")
    print("• 🔗 Vollständige Polygon Mumbai Testnet-Integration")

if __name__ == "__main__":
    main()
