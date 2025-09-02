"""
HRM High-Level Planner
Abstrakte Planung & strategisches Denken für ASI Core
"""

from datetime import datetime
from typing import Dict, List, Any
from .pattern_recognition import PatternRecognizer


class Planner:
    """
    High-Level Planner für abstrakte Planung und strategische Einsichten
    """

    def __init__(self):
        self.pattern_recognizer = PatternRecognizer()
        self.planning_history = []

    def create_abstract_plan(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Erstellt abstrakte Pläne basierend auf erkannten Mustern
        
        Args:
            user_context: Kontext der aktuellen Reflexion
            
        Returns:
            Dict mit abstraktem Plan, Zielen und Einsichten
        """
        # Erkenne Muster im Nutzerkontext
        patterns = self.pattern_recognizer.recognize_patterns(user_context)
        
        # Leite Ziele aus Mustern ab
        suggested_goals = self._derive_goals_from_patterns(patterns)
        
        # Extrahiere langfristige Einsichten
        long_term_insights = self._extract_long_term_insights(patterns)
        
        # Erstelle strategische Empfehlungen
        strategic_recommendations = self._generate_strategic_recommendations(
            patterns, user_context
        )
        
        plan = {
            "timestamp": datetime.now().isoformat(),
            "patterns": patterns,
            "suggested_goals": suggested_goals,
            "long_term_insights": long_term_insights,
            "strategic_recommendations": strategic_recommendations,
            "confidence_score": self._calculate_confidence(patterns)
        }
        
        # Speichere für zukünftige Referenz
        self.planning_history.append(plan)
        
        return plan

    def _derive_goals_from_patterns(self, patterns: List[Dict]) -> List[str]:
        """
        Leitet konkrete Ziele aus erkannten Mustern ab
        """
        goals = []
        
        for pattern in patterns[:3]:  # Top 3 Muster
            if pattern['type'] == 'similarity':
                # Ziele basierend auf ähnlichen Reflexionen
                tags = pattern.get('tags', [])
                if 'fokus' in [tag.lower() for tag in tags]:
                    goals.append(f"Optimiere Fokus basierend auf Muster (Ähnlichkeit: {pattern['similarity']:.2f})")
                elif 'arbeit' in [tag.lower() for tag in tags]:
                    goals.append(f"Verbessere Work-Life-Balance (Muster-Stärke: {pattern['similarity']:.2f})")
                elif 'gesundheit' in [tag.lower() for tag in tags]:
                    goals.append(f"Stärke Gesundheitsroutinen (Ähnlichkeit: {pattern['similarity']:.2f})")
                else:
                    goals.append(f"Entwickle {', '.join(tags[:2])}-Strategien weiter")
                    
            elif pattern['type'] == 'temporal':
                # Ziele basierend auf zeitlichen Mustern
                if pattern['frequency'] >= 3:
                    goals.append(f"Vertiefe {pattern['tag']}-Gewohnheiten (erscheint {pattern['frequency']}x)")
                else:
                    goals.append(f"Erkunde {pattern['tag']}-Thema intensiver")
        
        # Fallback wenn keine spezifischen Muster
        if not goals:
            goals.append("Entwickle bewusstere Selbstreflexions-Gewohnheiten")
            
        return goals[:5]  # Max 5 Ziele

    def _extract_long_term_insights(self, patterns: List[Dict]) -> List[str]:
        """
        Extrahiert langfristige Einsichten aus Mustern
        """
        insights = []
        
        # Temporale Einsichten
        temporal_patterns = [p for p in patterns if p['type'] == 'temporal']
        for pattern in temporal_patterns:
            if pattern['frequency'] >= 4:
                insights.append(
                    f"{pattern['tag']}-Thema zeigt starke Konsistenz "
                    f"({pattern['frequency']} Erwähnungen) - möglicherweise Kernbereich"
                )
            elif pattern.get('trend') == 'increasing':
                insights.append(
                    f"{pattern['tag']}-Interesse wächst - idealer Zeitpunkt für Vertiefung"
                )
        
        # Ähnlichkeits-Einsichten
        similarity_patterns = [p for p in patterns if p['type'] == 'similarity']
        if len(similarity_patterns) >= 2:
            high_sim = [p for p in similarity_patterns if p['similarity'] > 0.8]
            if high_sim:
                insights.append(
                    "Starke thematische Wiederholung erkannt - "
                    "möglicherweise unbewusste Fokusthemen"
                )
        
        # Meta-Einsichten
        if len(patterns) >= 5:
            insights.append(
                "Reiches Reflexionsmuster erkannt - hohe Selbstwahrnehmung entwickelt"
            )
        elif len(patterns) <= 1:
            insights.append(
                "Potenzial für tiefere Selbstreflexion - erkunde verschiedene Lebensbereiche"
            )
            
        return insights

    def _generate_strategic_recommendations(
        self, 
        patterns: List[Dict], 
        user_context: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """
        Generiert strategische Empfehlungen basierend auf Kontext und Mustern
        """
        recommendations = []
        
        # Empfehlung basierend auf Reflexionshäufigkeit
        if len(patterns) >= 3:
            recommendations.append({
                "type": "consistency",
                "title": "Konsistenz stärken",
                "description": "Deine regelmäßigen Reflexionen zeigen Wirkung. "
                             "Plane feste Reflexionszeiten für noch tiefere Einsichten."
            })
        
        # Empfehlung basierend auf Themenvielfalt
        unique_tags = set()
        for pattern in patterns:
            if 'tags' in pattern:
                unique_tags.update(pattern['tags'])
        
        if len(unique_tags) >= 5:
            recommendations.append({
                "type": "focus",
                "title": "Fokus entwickeln", 
                "description": f"Du reflektierst über {len(unique_tags)} verschiedene Bereiche. "
                             "Wähle 2-3 Kernthemen für tiefere Entwicklung."
            })
        elif len(unique_tags) <= 2:
            recommendations.append({
                "type": "explore",
                "title": "Horizont erweitern",
                "description": "Erkunde neue Lebensbereiche in deinen Reflexionen "
                             "für ganzheitlichere Selbsterkenntnis."
            })
        
        # Zeitbasierte Empfehlung
        current_hour = datetime.now().hour
        if 6 <= current_hour <= 10:
            recommendations.append({
                "type": "timing",
                "title": "Morgen-Momentum nutzen",
                "description": "Morgenreflexionen können den Tag bewusster gestalten. "
                             "Plane konkrete Schritte für heute."
            })
        elif 18 <= current_hour <= 22:
            recommendations.append({
                "type": "timing", 
                "title": "Tagesabschluss optimieren",
                "description": "Abendreflexionen helfen beim Lernen und Loslassen. "
                             "Was war heute wertvoll?"
            })
            
        return recommendations

    def _calculate_confidence(self, patterns: List[Dict]) -> float:
        """
        Berechnet Konfidenz-Score für die Planungsqualität
        """
        if not patterns:
            return 0.2
        
        # Faktoren für Konfidenz
        pattern_count = len(patterns)
        avg_similarity = sum(
            p.get('similarity', 0.5) for p in patterns 
            if p['type'] == 'similarity'
        ) / max(1, len([p for p in patterns if p['type'] == 'similarity']))
        
        temporal_strength = sum(
            min(p.get('frequency', 1) / 10, 1.0) for p in patterns 
            if p['type'] == 'temporal'
        ) / max(1, len([p for p in patterns if p['type'] == 'temporal']))
        
        # Gewichtete Kombination
        confidence = (
            min(pattern_count / 5, 1.0) * 0.4 +  # Musteranzahl
            avg_similarity * 0.4 +                # Ähnlichkeitsstärke  
            temporal_strength * 0.2               # Zeitliche Konsistenz
        )
        
        return round(min(confidence, 1.0), 2)

    def get_planning_history(self) -> List[Dict[str, Any]]:
        """
        Gibt die Planungshistorie zurück
        """
        return self.planning_history.copy()

    def analyze_planning_evolution(self) -> Dict[str, Any]:
        """
        Analysiert die Entwicklung der Planung über Zeit
        """
        if len(self.planning_history) < 2:
            return {"message": "Zu wenig Daten für Evolutionsanalyse"}
        
        recent_plans = self.planning_history[-5:]  # Letzte 5 Pläne
        
        # Konfidenz-Entwicklung
        confidence_trend = [p['confidence_score'] for p in recent_plans]
        confidence_improvement = confidence_trend[-1] - confidence_trend[0]
        
        # Ziel-Komplexität
        goal_complexity = [len(p['suggested_goals']) for p in recent_plans]
        avg_complexity = sum(goal_complexity) / len(goal_complexity)
        
        return {
            "confidence_trend": confidence_improvement,
            "average_goal_complexity": avg_complexity,
            "planning_maturity": "hoch" if confidence_improvement > 0.1 else "entwickelnd",
            "recommendation": self._get_evolution_recommendation(confidence_improvement)
        }

    def _get_evolution_recommendation(self, confidence_trend: float) -> str:
        """
        Gibt Empfehlung basierend auf Planungsentwicklung
        """
        if confidence_trend > 0.2:
            return "Deine Planungsfähigkeiten verbessern sich stark. Zeit für komplexere Ziele."
        elif confidence_trend > 0.0:
            return "Stetige Verbesserung erkennbar. Bleibe bei regelmäßigen Reflexionen."
        else:
            return "Fokussiere dich auf konsistentere Reflexionsmuster für bessere Planung."
