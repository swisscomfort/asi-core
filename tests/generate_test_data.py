#!/usr/bin/env python3
"""
ASI Core - Test-Daten Generator
Erstellt realistische Beispiel-Reflexionen
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict


def generate_sample_reflections(count: int = 10) -> List[Dict]:
    """
    Generiert realistische deutsche Reflexionstexte.
    
    Args:
        count: Anzahl zu generierender Reflexionen
        
    Returns:
        Liste von Reflexions-Dictionaries
    """
    
    # Beispiel-Templates für verschiedene Lebensbereiche
    templates = {
        "arbeit": [
            "Heute war ein {adj} Tag im Büro. Das Projekt {verb} {adv}. Ich fühle mich {emotion}.",
            "Die Präsentation ist {adj} gelaufen. Meine Kollegen waren {reaction}. {learning}",
            "Deadline für {project} rückt näher. {stress_level}. Muss {action} priorisieren."
        ],
        "familie": [
            "Zeit mit {family_member} verbracht. Es war {adj}. {emotion} über unsere Beziehung.",
            "Familienessen war {adj}. {conflict_or_harmony}. Ich {reflection}.",
            "{family_event} steht bevor. Bin {emotion}. Muss noch {preparation}."
        ],
        "gesundheit": [
            "Heute {exercise} gemacht. Fühle mich {physical_state}. {motivation_level}.",
            "Schlaf war {sleep_quality}. {energy_level} heute. Sollte {health_action}.",
            "Ernährung {diet_assessment}. {body_feeling}. Ziel: {health_goal}."
        ],
        "kreativität": [
            "Neue Idee für {creative_project}. Bin {excitement_level}. {next_steps}.",
            "Kreative Blockade bei {activity}. {frustration}. Versuche {solution}.",
            "Durchbruch bei {project}! {emotion}. Die Lösung war {insight}."
        ],
        "persönlich": [
            "Über {life_topic} nachgedacht. {realization}. Fühle mich {emotion}.",
            "Heute {personal_achievement}. Bin {pride_level} auf mich. {learning}.",
            "Herausforderung: {challenge}. {coping_strategy}. {growth_observation}."
        ]
    }
    
    # Füllwörter für Templates
    replacements = {
        "adj": ["anstrengender", "produktiver", "chaotischer", "ruhiger", "erfolgreicher", "schwieriger", "interessanter"],
        "verb": ["läuft", "entwickelt sich", "stagniert", "überrascht", "fordert"],
        "adv": ["gut", "schleppend", "überraschend schnell", "komplizierter als erwartet", "reibungslos"],
        "emotion": ["erschöpft", "zufrieden", "gestresst", "motiviert", "nachdenklich", "dankbar", "frustriert"],
        "reaction": ["begeistert", "skeptisch", "unterstützend", "überrascht", "hilfreich"],
        "learning": ["Habe viel gelernt.", "Muss noch an Details arbeiten.", "Wichtige Erkenntnis gewonnen."],
        "project": ["das neue Feature", "die Analyse", "der Bericht", "die Strategie"],
        "stress_level": ["Stresslevel steigt", "Bin entspannt", "Leichter Druck spürbar"],
        "action": ["Aufgaben besser", "meine Zeit anders", "Prioritäten klarer"],
        "family_member": ["meinen Eltern", "meiner Schwester", "meinem Partner", "den Kindern"],
        "conflict_or_harmony": ["Kleine Meinungsverschiedenheit", "Alle waren gut gelaunt", "Spannung lag in der Luft"],
        "reflection": ["denke noch darüber nach", "bin dankbar dafür", "muss das verarbeiten"],
        "family_event": ["Geburtstag", "Familientreffen", "Weihnachten", "Urlaub"],
        "preparation": ["Geschenk besorgen", "alles organisieren", "mental vorbereiten"],
        "exercise": ["30 Minuten Sport", "Yoga", "einen langen Spaziergang", "Krafttraining"],
        "physical_state": ["energiegeladen", "ausgepowert", "ausgeglichen", "müde aber gut"],
        "motivation_level": ["Motivation steigt", "Brauche mehr Disziplin", "Routine hilft"],
        "sleep_quality": ["erholsam", "unruhig", "zu kurz", "traumreich"],
        "energy_level": ["Voller Energie", "Etwas träge", "Normale Energie"],
        "health_action": ["früher schlafen", "mehr Wasser trinken", "gesünder essen"],
        "diet_assessment": ["war ausgewogen", "könnte besser sein", "war sehr gut"],
        "body_feeling": ["Körper fühlt sich gut an", "Bin etwas träge", "Fühle mich fit"],
        "health_goal": ["mehr Bewegung", "bessere Ernährung", "Work-Life-Balance"],
        "creative_project": ["mein Buchprojekt", "die App-Idee", "das Kunstwerk", "die Musik"],
        "excitement_level": ["total begeistert", "vorsichtig optimistisch", "voller Vorfreude"],
        "next_steps": ["Muss Konzept ausarbeiten", "Erste Skizzen machen", "Recherche vertiefen"],
        "activity": ["dem Schreiben", "der Komposition", "dem Design", "der Problemlösung"],
        "frustration": ["Frustrierend", "Herausfordernd", "Brauche eine Pause"],
        "solution": ["anderen Ansatz", "morgen nochmal", "Inspiration zu suchen"],
        "insight": ["simpler als gedacht", "eine neue Perspektive", "unkonventionell aber effektiv"],
        "life_topic": ["meine Ziele", "Beziehungen", "die Zukunft", "vergangene Entscheidungen"],
        "realization": ["Mir wurde klar, dass ich mehr Zeit für mich brauche", "Erkenne Muster in meinem Verhalten", "Verstehe jetzt den Zusammenhang"],
        "personal_achievement": ["eine Angst überwunden", "Grenze gesetzt", "wichtige Entscheidung getroffen"],
        "pride_level": ["sehr stolz", "zufrieden", "glücklich"],
        "challenge": ["Konflikt lösen", "Gewohnheit ändern", "Komfortzone verlassen"],
        "coping_strategy": ["Schritt für Schritt angehen", "Um Hilfe bitten", "Akzeptanz üben"],
        "growth_observation": ["Wachse daran", "Lerne viel über mich", "Entwickle neue Stärken"]
    }
    
    reflections = []
    
    for i in range(count):
        # Zufällige Kategorie wählen
        category = random.choice(list(templates.keys()))
        template = random.choice(templates[category])
        
        # Template mit Ersetzungen füllen
        text = template
        for key, values in replacements.items():
            placeholder = "{" + key + "}"
            while placeholder in text:
                replacement = random.choice(values)
                text = text.replace(placeholder, replacement, 1)
        
        # Zustandswert basierend auf Kategorie und Inhalt
        state_mapping = {
            "arbeit": random.randint(10, 90),  # Fokussiert bis Produktiv
            "familie": random.randint(50, 100),  # Entspannt bis Glücklich
            "gesundheit": random.randint(0, 60),  # Neutral bis Motiviert
            "kreativität": random.randint(20, 150),  # Kreativ bis Inspiriert
            "persönlich": random.randint(70, 200)  # Reflektiv bis Flow
        }
        
        # Tags generieren
        tag_pool = {
            "arbeit": ["work", "productivity", "career", "office", "project"],
            "familie": ["family", "relationships", "love", "connection", "home"],
            "gesundheit": ["health", "fitness", "wellness", "selfcare", "energy"],
            "kreativität": ["creative", "art", "ideas", "innovation", "expression"],
            "persönlich": ["growth", "reflection", "mindfulness", "development", "insight"]
        }
        
        tags = random.sample(tag_pool[category], k=random.randint(2, 4))
        tags.append(category)
        
        # Zeitstempel generieren (letzte 30 Tage)
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        timestamp = datetime.now() - timedelta(days=days_ago, hours=hours_ago)
        
        reflection = {
            "content": text,
            "reflection_text": text,  # Für Kompatibilität
            "state_value": state_mapping[category],
            "tags": tags,
            "category": category,
            "timestamp": timestamp.isoformat(),
            "unix_timestamp": int(timestamp.timestamp()),
            "word_count": len(text.split()),
            "character_count": len(text),
            "privacy_level": random.choice(["private", "private", "anonymous"]),  # Meist privat
            "test_data": True
        }
        
        reflections.append(reflection)
    
    return reflections


def save_test_reflections(reflections: List[Dict], output_dir: str = "data/reflections"):
    """
    Speichert Test-Reflexionen als JSON-Dateien.
    
    Args:
        reflections: Liste von Reflexions-Daten
        output_dir: Ausgabeverzeichnis
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    for i, reflection in enumerate(reflections):
        # Dateiname mit Zeitstempel
        timestamp = datetime.fromisoformat(reflection["timestamp"])
        filename = f"state_{timestamp.strftime('%Y%m%d_%H%M%S')}_{i:03d}.json"
        filepath = output_path / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(reflection, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Gespeichert: {filename}")


def main():
    """Hauptfunktion zum Generieren von Test-Daten."""
    print("🎲 ASI Core Test-Daten Generator")
    print("=" * 40)
    
    # Parameter
    count = 10  # Anzahl Reflexionen
    
    print(f"Generiere {count} Test-Reflexionen...")
    reflections = generate_sample_reflections(count)
    
    print(f"\n📊 Statistiken:")
    categories = {}
    for ref in reflections:
        cat = ref["category"]
        categories[cat] = categories.get(cat, 0) + 1
    
    for cat, cnt in categories.items():
        print(f"  {cat}: {cnt} Reflexionen")
    
    # Speichern
    save_test_reflections(reflections)
    
    print(f"\n✅ {count} Test-Reflexionen erstellt!")
    print("Dateien gespeichert in: data/reflections/")


if __name__ == "__main__":
    main()
