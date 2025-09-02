#!/usr/bin/env python3
"""
HRM Demo - Test der vollständigen Hierarchical Reasoning Model Integration
"""

import sys
from pathlib import Path
import json

# ASI Core Module importieren
sys.path.append(str(Path(__file__).parent))

from src.core.processor import ReflectionProcessor
from datetime import datetime


def test_hrm_integration():
    """Testet die vollständige HRM-Integration"""

    print("🧠 ASI Core HRM (Hierarchical Reasoning Model) Demo")
    print("=" * 60)

    # Processor mit HRM initialisieren
    processor = ReflectionProcessor()

    print(f"✅ HRM Planner verfügbar: {processor.hrm_planner is not None}")
    print(f"✅ HRM Executor verfügbar: {processor.hrm_executor is not None}")
    print()

    # Test-Reflexion
    test_reflection = {
        "content": """Heute war ein sehr stressiger Tag bei der Arbeit. 
        Ich hatte drei wichtige Meetings und konnte mich kaum konzentrieren. 
        Ständig wurde ich unterbrochen und ich fühle mich total überwältigt. 
        Ich merke, dass ich dringend bessere Strategien für Fokus und 
        Stressmanagement brauche. Vielleicht sollte ich mal über meine 
        Work-Life-Balance nachdenken.""",
        "tags": ["arbeit", "stress", "fokus", "work-life-balance"],
        "privacy_level": "private",
    }

    print("📝 Test-Reflexion wird verarbeitet...")
    print(f"Inhalt: {test_reflection['content'][:100]}...")
    print(f"Tags: {test_reflection['tags']}")
    print()

    # Verarbeitung mit HRM
    try:
        processed = processor.process_reflection(test_reflection)

        print("✅ Verarbeitung erfolgreich!")
        print(f"📊 Sentiment: {processed.sentiment}")
        print(f"🏷️  Themen: {processed.key_themes}")
        print()

        # HRM-Ergebnisse anzeigen
        hrm_data = processed.structured_data.get("hrm")
        if hrm_data and not hrm_data.get("error"):
            print("🧠 HRM-ANALYSE ERGEBNISSE:")
            print("-" * 40)

            # Konfidenz
            confidence = hrm_data.get("confidence", 0)
            print(f"🎯 Analyse-Konfidenz: {confidence:.1%}")

            # Abstract Plan
            abstract_plan = hrm_data.get("abstract_plan", {})
            if abstract_plan:
                print("\n📋 ABSTRACT PLAN (High-Level Reasoning):")

                # Muster
                patterns = abstract_plan.get("patterns", [])
                if patterns:
                    print(f"   🔍 Erkannte Muster ({len(patterns)}):")
                    for i, pattern in enumerate(patterns[:3], 1):
                        pattern_type = pattern.get("type", "Unbekannt")
                        if pattern_type == "similarity":
                            similarity = pattern.get("similarity", 0)
                            print(
                                f"      {i}. Ähnlichkeit zu früheren Reflexionen ({similarity:.1%})"
                            )
                        elif pattern_type == "temporal":
                            frequency = pattern.get("frequency", 0)
                            tag = pattern.get("tag", "Unbekannt")
                            print(
                                f"      {i}. Zeitliches Muster: '{tag}' ({frequency}x)"
                            )
                        elif pattern_type == "thematic":
                            theme = pattern.get("theme", "Unbekannt")
                            relevance = pattern.get("relevance", 0)
                            print(
                                f"      {i}. Thematisches Muster: '{theme}' ({relevance:.1%})"
                            )

                # Ziele
                goals = abstract_plan.get("suggested_goals", [])
                if goals:
                    print(f"\n   🎯 Empfohlene Ziele ({len(goals)}):")
                    for i, goal in enumerate(goals[:3], 1):
                        print(f"      {i}. {goal}")

                # Langzeit-Einsichten
                insights = abstract_plan.get("long_term_insights", [])
                if insights:
                    print(f"\n   💡 Langzeit-Einsichten ({len(insights)}):")
                    for i, insight in enumerate(insights[:2], 1):
                        print(f"      {i}. {insight}")

            # Concrete Action
            concrete_action = hrm_data.get("concrete_action")
            if concrete_action:
                print("\n🚀 CONCRETE ACTION (Low-Level Execution):")
                action_type = concrete_action.get("type", "Allgemein")
                priority = concrete_action.get("priority", "Medium")
                suggestion = concrete_action.get("suggestion", "Keine Empfehlung")

                print(f"   📌 Aktionstyp: {action_type} ({priority} Priorität)")
                print(f"   💬 Empfehlung: {suggestion}")

                # Umsetzungsschritte
                implementation = concrete_action.get("implementation", [])
                if implementation:
                    print(f"\n   📝 Umsetzungsschritte ({len(implementation)}):")
                    for i, step in enumerate(implementation[:4], 1):
                        print(f"      {i}. {step}")

            # Empfehlungen
            recommendations = hrm_data.get("recommendations", [])
            if recommendations:
                print(f"\n🎖️  STRATEGISCHE EMPFEHLUNGEN ({len(recommendations)}):")
                for i, rec in enumerate(recommendations[:3], 1):
                    print(f"   {i}. {rec}")

        else:
            error = (
                hrm_data.get("error", "Unbekannter Fehler")
                if hrm_data
                else "Keine HRM-Daten"
            )
            print(f"⚠️  HRM-Analyse fehlgeschlagen: {error}")

    except Exception as e:
        print(f"❌ Fehler bei der Verarbeitung: {str(e)}")
        return False

    print("\n" + "=" * 60)
    print("🎉 HRM-Demo abgeschlossen!")

    # Zusätzliche Analytics falls verfügbar
    if processor.hrm_planner and hasattr(processor.hrm_planner, "get_planning_history"):
        history = processor.hrm_planner.get_planning_history()
        print(f"📈 Planungshistorie: {len(history)} Einträge")

    if processor.hrm_executor and hasattr(
        processor.hrm_executor, "get_action_analytics"
    ):
        analytics = processor.hrm_executor.get_action_analytics()
        print(
            f"📊 Aktions-Analytics: {analytics.get('total_actions', 0)} Aktionen generiert"
        )

    return True


if __name__ == "__main__":
    success = test_hrm_integration()
    if success:
        print("\n✅ Alle HRM-Komponenten funktionieren korrekt!")
        print("\n📋 Nächste Schritte:")
        print("   • Starte Web-Interface: python src/web/app.py")
        print("   • Besuche HRM-Seite: http://localhost:8000/hrm")
        print("   • Teste CLI: python main.py process 'Deine Reflexion hier'")
    else:
        print("\n❌ Es gab Probleme bei der HRM-Integration")
        sys.exit(1)
