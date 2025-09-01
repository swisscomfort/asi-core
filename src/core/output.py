"""
ASI Core - Output Module
Lokale Ausgabe, Hinweise und Feedback-Generierung
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class Insight:
    """Struktur für Erkenntnisse und Hinweise"""

    type: str  # pattern, suggestion, reflection
    title: str
    description: str
    confidence: float
    related_themes: List[str]
    actionable: bool = False


class OutputGenerator:
    """Hauptklasse für die Ausgabe und Hinweis-Generierung"""

    def __init__(self, data_dir: str = "data/local"):
        self.data_dir = data_dir
        self.ensure_data_dir()

        # Muster für Erkenntnisse
        self.insight_patterns = {
            "emotional_trend": {
                "description": "Emotionale Entwicklung über Zeit",
                "min_entries": 3,
            },
            "recurring_themes": {
                "description": "Wiederkehrende Themen",
                "min_entries": 2,
            },
            "growth_moments": {
                "description": "Momente persönlichen Wachstums",
                "min_entries": 1,
            },
        }

    def ensure_data_dir(self):
        """Stellt sicher, dass das Datenverzeichnis existiert"""
        os.makedirs(self.data_dir, exist_ok=True)

    def save_local_copy(self, processed_data: Dict, filename: str = None) -> str:
        """
        Speichert eine lokale Kopie der verarbeiteten Daten

        Args:
            processed_data: Verarbeitete Reflexionsdaten
            filename: Optionaler Dateiname

        Returns:
            str: Pfad zur gespeicherten Datei
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reflection_{timestamp}.json"

        filepath = os.path.join(self.data_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(processed_data, f, indent=2, ensure_ascii=False)

        return filepath

    def load_local_reflections(self, days_back: int = 30) -> List[Dict]:
        """
        Lädt lokale Reflexionen der letzten Tage

        Args:
            days_back: Anzahl Tage zurück

        Returns:
            List[Dict]: Liste der Reflexionen
        """
        reflections = []
        cutoff_date = datetime.now() - timedelta(days=days_back)

        if not os.path.exists(self.data_dir):
            return reflections

        for filename in os.listdir(self.data_dir):
            if filename.endswith(".json") and filename.startswith("reflection_"):
                filepath = os.path.join(self.data_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    # Prüfe Datum
                    if "timestamp" in data:
                        file_date = datetime.fromisoformat(
                            data["timestamp"].replace("Z", "+00:00")
                        )
                        if file_date >= cutoff_date:
                            reflections.append(data)
                except Exception as e:
                    print(f"Fehler beim Laden von {filename}: {e}")

        return sorted(reflections, key=lambda x: x.get("timestamp", ""))

    def analyze_emotional_trends(self, reflections: List[Dict]) -> Optional[Insight]:
        """
        Analysiert emotionale Trends

        Args:
            reflections: Liste der Reflexionen

        Returns:
            Optional[Insight]: Erkenntnisse zu emotionalen Trends
        """
        if len(reflections) < 3:
            return None

        emotions = []
        for reflection in reflections[-7:]:  # Letzte 7 Einträge
            sentiment = reflection.get("sentiment", "")
            if sentiment:
                emotion_type = sentiment.split("(")[0]
                emotions.append(emotion_type)

        if not emotions:
            return None

        # Trend analysieren
        recent_emotions = emotions[-3:]
        positive_trend = sum(1 for e in recent_emotions if e == "positive")
        negative_trend = sum(1 for e in recent_emotions if e == "negative")

        if positive_trend >= 2:
            return Insight(
                type="pattern",
                title="Positive emotionale Entwicklung",
                description="Deine letzten Reflexionen zeigen eine positive Tendenz. "
                "Das ist ein gutes Zeichen für dein Wohlbefinden.",
                confidence=0.8,
                related_themes=["emotional_health"],
                actionable=False,
            )
        elif negative_trend >= 2:
            return Insight(
                type="suggestion",
                title="Emotionale Herausforderung erkannt",
                description="Du durchlebst gerade eine schwierigere Phase. "
                "Erwäge, mit jemandem zu sprechen oder dir bewusst "
                "Zeit für Selbstfürsorge zu nehmen.",
                confidence=0.7,
                related_themes=["emotional_health", "self_care"],
                actionable=True,
            )

        return None

    def identify_recurring_themes(self, reflections: List[Dict]) -> List[Insight]:
        """
        Identifiziert wiederkehrende Themen

        Args:
            reflections: Liste der Reflexionen

        Returns:
            List[Insight]: Erkenntnisse zu wiederkehrenden Themen
        """
        theme_counts = {}

        for reflection in reflections:
            themes = reflection.get("themes", [])
            for theme in themes:
                theme_counts[theme] = theme_counts.get(theme, 0) + 1

        insights = []
        for theme, count in theme_counts.items():
            if count >= 3:  # Mindestens 3x erwähnt
                insights.append(
                    Insight(
                        type="pattern",
                        title=f"Wiederkehrendes Thema: {theme.title()}",
                        description=f'Das Thema "{theme}" beschäftigt dich häufig '
                        f"({count}x in den letzten Reflexionen). "
                        f"Es könnte hilfreich sein, tiefer darüber nachzudenken.",
                        confidence=min(count / len(reflections), 1.0),
                        related_themes=[theme],
                        actionable=True,
                    )
                )

        return insights

    def generate_reflection_prompt(self, recent_insights: List[Insight]) -> str:
        """
        Generiert einen Reflexions-Prompt basierend auf Erkenntnissen

        Args:
            recent_insights: Aktuelle Erkenntnisse

        Returns:
            str: Reflexions-Prompt
        """
        if not recent_insights:
            return "Nimm dir einen Moment Zeit für dich. " "Was beschäftigt dich heute?"

        actionable_insights = [i for i in recent_insights if i.actionable]

        if actionable_insights:
            insight = actionable_insights[0]
            related_theme = (
                insight.related_themes[0] if insight.related_themes else "Leben"
            )

            return (
                f"Du hast kürzlich oft über {related_theme} nachgedacht. "
                f"Wie entwickelt sich dieses Thema für dich? "
                f"Was hast du dazu gelernt?"
            )

        return (
            "Schau auf deine letzten Reflexionen zurück. "
            "Welche Erkenntnisse nimmst du mit?"
        )

    def create_daily_summary(self, reflections: List[Dict]) -> Dict:
        """
        Erstellt eine Tages-Zusammenfassung

        Args:
            reflections: Reflexionen des Tages

        Returns:
            Dict: Tages-Zusammenfassung
        """
        if not reflections:
            return {"message": "Keine Reflexionen heute erfasst."}

        total_words = sum(
            r.get("structure", {}).get("word_count", 0) for r in reflections
        )

        all_themes = []
        emotions = []

        for reflection in reflections:
            all_themes.extend(reflection.get("themes", []))
            sentiment = reflection.get("sentiment", "")
            if sentiment:
                emotions.append(sentiment.split("(")[0])

        # Häufigste Themen
        theme_counts = {}
        for theme in all_themes:
            theme_counts[theme] = theme_counts.get(theme, 0) + 1

        top_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)[:3]

        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "reflection_count": len(reflections),
            "total_words": total_words,
            "top_themes": [theme for theme, _ in top_themes],
            "emotions": list(set(emotions)),
            "message": f"Du hast heute {len(reflections)} Reflexion(en) "
            f"mit {total_words} Wörtern erfasst.",
        }

    def generate_insights(self, reflections: List[Dict]) -> List[Insight]:
        """
        Generiert alle verfügbaren Erkenntnisse

        Args:
            reflections: Liste der Reflexionen

        Returns:
            List[Insight]: Alle generierten Erkenntnisse
        """
        insights = []

        # Emotionale Trends
        emotional_insight = self.analyze_emotional_trends(reflections)
        if emotional_insight:
            insights.append(emotional_insight)

        # Wiederkehrende Themen
        theme_insights = self.identify_recurring_themes(reflections)
        insights.extend(theme_insights)

        return insights

    def create_weekly_report(self) -> Dict:
        """
        Erstellt einen Wochenbericht

        Returns:
            Dict: Wochenbericht
        """
        reflections = self.load_local_reflections(days_back=7)
        insights = self.generate_insights(reflections)

        return {
            "period": "Letzte 7 Tage",
            "reflection_count": len(reflections),
            "insights": [
                {
                    "type": insight.type,
                    "title": insight.title,
                    "description": insight.description,
                    "actionable": insight.actionable,
                }
                for insight in insights
            ],
            "next_prompt": self.generate_reflection_prompt(insights),
        }


if __name__ == "__main__":
    # Beispiel-Nutzung
    output_gen = OutputGenerator()

    # Test-Daten laden
    reflections = output_gen.load_local_reflections()

    if reflections:
        print("=== Tages-Zusammenfassung ===")
        summary = output_gen.create_daily_summary(reflections)
        print(json.dumps(summary, indent=2, ensure_ascii=False))

        print("\n=== Erkenntnisse ===")
        insights = output_gen.generate_insights(reflections)
        for insight in insights:
            print(f"• {insight.title}")
            print(f"  {insight.description}")
    else:
        print("Keine lokalen Reflexionen gefunden.")
        print("Starte mit einer neuen Reflexion!")
