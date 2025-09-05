#!/usr/bin/env python3
"""
ASI Core - Demo der semantischen Suche und Embedding-Generierung
Demonstriert die neuen Funktionen des erweiterten ASI-Systems
"""

from asi_core.search import ASIEmbeddingGenerator, ASISemanticSearch


def demo_embedding_generation():
    """Demonstriert die Embedding-Generierung"""
    print("=" * 60)
    print("🧠 ASI EMBEDDING-GENERIERUNG DEMO")
    print("=" * 60)

    # Generator initialisieren
    generator = ASIEmbeddingGenerator()

    # Beispiel-Texte
    sample_texts = [
        "Heute war ich sehr glücklich und entspannt nach dem Yoga-Kurs.",
        "Die Arbeit war stressig und die Deadlines schwer zu schaffen.",
        "Meine Beziehung zu meiner Familie ist sehr wichtig für mich.",
        "Das neue Projekt im Team läuft erfolgreich und macht Spaß.",
        "Gesundheitliche Probleme bereiten mir Sorgen, aber ich gehe proaktiv damit um.",
    ]

    print(f"Generiere Embeddings für {len(sample_texts)} Beispiel-Reflexionen...\n")

    for i, text in enumerate(sample_texts, 1):
        print(f"{i}. Text: {text[:60]}...")
        embedding = generator.generate_embedding(text)
        print(f"   Embedding-Größe: {len(embedding)} Bytes")
        print(f"   Modell: {generator.model_name}\n")


def demo_semantic_search():
    """Demonstriert die semantische Suche"""
    print("=" * 60)
    print("🔍 ASI SEMANTISCHE SUCHE DEMO")
    print("=" * 60)

    # Generator und Suchmaschine initialisieren
    generator = ASIEmbeddingGenerator()
    search_engine = ASISemanticSearch(generator)

    # Test-Daten vorbereiten
    test_data = [
        (
            "work_stress_1",
            "Heute war ein extrem stressiger Tag im Büro. Viele Meetings und enge Deadlines.",
        ),
        (
            "happiness_1",
            "Ich bin sehr glücklich über den schönen Sonnenuntergang und fühle mich entspannt.",
        ),
        (
            "relationship_1",
            "Probleme in der Beziehung sorgen für emotionale Unruhe und Kommunikationsschwierigkeiten.",
        ),
        (
            "team_success_1",
            "Unser Team hat erfolgreich das Projekt abgeschlossen. Zusammenarbeit war excellent.",
        ),
        (
            "health_concern_1",
            "Gesundheitliche Sorgen beschäftigen mich. Arzttermin ist vereinbart.",
        ),
        (
            "creative_work_1",
            "Heute hatte ich viele kreative Ideen für mein neues Kunstprojekt.",
        ),
        (
            "family_time_1",
            "Schöner Familienabend mit interessanten Gesprächen und viel Lachen.",
        ),
        (
            "learning_1",
            "Heute habe ich viel Neues über Machine Learning gelernt. Sehr spannend!",
        ),
    ]

    print(f"Speichere {len(test_data)} Test-Reflektionen...\n")

    # Embeddings generieren und speichern
    for cid, text in test_data:
        embedding = generator.generate_embedding(text)
        search_engine.store_embedding(cid, embedding, text)
        print(f"✓ {cid}: {text[:50]}...")

    print(f"\n📊 Cache-Statistiken:")
    stats = search_engine.get_cache_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")

    # Test-Suchen durchführen
    test_queries = [
        "Stress und Arbeit",
        "Glück und Entspannung",
        "Beziehungsprobleme",
        "Erfolgreiche Teamarbeit",
        "Gesundheitliche Sorgen",
        "Kreativität und Kunst",
        "Familie und Zusammensein",
        "Lernen und Wissen",
    ]

    print(f"\n🔍 Führe {len(test_queries)} Test-Suchen durch...\n")

    for i, query in enumerate(test_queries, 1):
        print(f"{i}. Suche: '{query}'")
        results = search_engine.search_ASI_memory(query, 3)

        if results:
            for j, result in enumerate(results, 1):
                print(
                    f"   {j}. CID: {result['cid']} (Ähnlichkeit: {result['similarity']:.3f})"
                )
                print(f"      Text: {result['text_preview'][:60]}...")
        else:
            print("   Keine Ergebnisse gefunden.")
        print()


def demo_full_integration():
    """Demonstriert die Integration in das ASI-System"""
    print("=" * 60)
    print("🚀 ASI VOLLSTÄNDIGE INTEGRATION DEMO")
    print("=" * 60)

    from main import ASICore

    # ASI Core System initialisieren
    print("Initialisiere ASI Core System...")
    asi = ASICore()

    # Beispiel-Reflexionen verarbeiten
    sample_reflections = [
        "Heute hatte ich einen sehr produktiven Tag. Das neue Projekt macht Fortschritte und ich bin zufrieden mit meiner Leistung.",
        "Die Meditation am Morgen hat mir geholfen, ruhig und fokussiert zu bleiben, trotz des stressigen Arbeitstages.",
        "Konflikte im Team haben mich heute belastet. Ich muss lernen, besser zu kommunizieren und Kompromisse zu finden.",
    ]

    print(f"\nVerarbeite {len(sample_reflections)} Beispiel-Reflexionen...")

    for i, reflection in enumerate(sample_reflections, 1):
        print(f"\n--- Reflexion {i} ---")
        print(f"Text: {reflection[:60]}...")

        try:
            result = asi.process_reflection_workflow(
                content=reflection,
                tags=["demo", f"beispiel_{i}"],
                privacy_level="private",
            )
            print(f"✓ Verarbeitet: ID {result['reflection_id']}")

        except Exception as e:
            print(f"❌ Fehler: {e}")

    # Semantische Suche demonstrieren
    print(f"\n🔍 Demonstriere semantische Suche...")

    search_queries = [
        "Produktivität und Arbeit",
        "Meditation und Ruhe",
        "Konflikte und Kommunikation",
    ]

    for query in search_queries:
        print(f"\nSuche: '{query}'")
        results = asi.search_asi_memories(query, 2)

    # Statistiken anzeigen
    print(f"\n📊 ASI System Statistiken:")
    asi.show_search_stats()


def main():
    """Hauptfunktion der Demo"""
    print("🌟 ASI CORE - SEMANTISCHE SUCHE & EMBEDDING DEMO 🌟")
    print("=" * 70)

    try:
        # 1. Embedding-Generierung demonstrieren
        demo_embedding_generation()

        input("\nDrücke Enter um fortzufahren...")

        # 2. Semantische Suche demonstrieren
        demo_semantic_search()

        input("\nDrücke Enter um die vollständige Integration zu testen...")

        # 3. Vollständige Integration demonstrieren
        demo_full_integration()

        print("\n🎉 Demo erfolgreich abgeschlossen!")
        print("\nDie semantische Suche und Embedding-Generierung sind nun")
        print("vollständig in das ASI-System integriert und funktionsbereit.")

    except KeyboardInterrupt:
        print("\n\nDemo beendet.")
    except Exception as e:
        print(f"\n❌ Fehler in der Demo: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
