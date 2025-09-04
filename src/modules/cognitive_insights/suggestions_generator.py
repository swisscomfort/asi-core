"""
Suggestions Generator - Generiert sanfte Verbesserungsvorschläge
"""

from typing import Dict, List


class SuggestionsGenerator:
    def __init__(self):
        self.suggestion_templates = {
            "absolute_terms": {
                "question": "Könntest du präzisieren, wie oft das wirklich der Fall ist?",
                "alternatives": {
                    "immer": "häufig, meistens, oft",
                    "nie": "selten, bisher nicht, nur in Ausnahmefällen",
                    "alle": "viele, die meisten, ein Großteil",
                    "niemand": "wenige, die wenigsten, kaum jemand",
                    "nichts": "wenig, nur weniges, kaum etwas",
                    "alles": "vieles, das meiste, ein Großteil",
                },
            },
            "overgeneralization": {
                "question": "Auf welche konkreten Erfahrungen bezieht sich diese Aussage?",
                "suggestion": "Versuche spezifischere Beispiele zu nennen.",
            },
            "circular_reasoning": {
                "question": "Welche Argumente oder Belege stützen diese Ansicht?",
                "suggestion": "Überlege dir konkrete Gründe für deine Position.",
            },
            "emotional_reasoning": {
                "question": "Was sind die sachlichen Aspekte dieser Situation?",
                "suggestion": "Gefühle sind wichtig, aber welche Fakten gibt es auch?",
            },
            "binary_thinking": {
                "question": "Gibt es vielleicht auch Zwischentöne oder weitere Optionen?",
                "suggestion": "Die Realität ist oft nuancierter als schwarz oder weiß.",
            },
        }

    def generate_suggestions(self, biases: List[Dict]) -> List[Dict]:
        """Generiert Verbesserungsvorschläge basierend auf erkannten Denkfallen"""
        suggestions = []

        for bias in biases:
            bias_type = bias["type"]
            template = self.suggestion_templates.get(bias_type)

            if not template:
                continue

            suggestion = {
                "bias_type": bias_type,
                "question": template["question"],
                "severity": bias["severity"],
            }

            # Spezielle Behandlung für absolute Begriffe
            if bias_type == "absolute_terms":
                instances = bias["instances"]
                alternatives = []
                for instance in instances:
                    alt = template["alternatives"].get(instance.lower())
                    if alt:
                        alternatives.append({"original": instance, "alternatives": alt})
                suggestion["alternatives"] = alternatives

            # Spezielle Behandlung für andere Bias-Typen
            elif bias_type in [
                "overgeneralization",
                "circular_reasoning",
                "emotional_reasoning",
                "binary_thinking",
            ]:
                suggestion["general_advice"] = template["suggestion"]

            suggestions.append(suggestion)

        return suggestions

    def create_example_reformulations(
        self, text: str, biases: List[Dict]
    ) -> List[Dict]:
        """Erstellt Beispiele für bessere Formulierungen"""
        reformulations = []

        # Einfache Beispiele für häufige Muster
        examples = {
            "absolute_terms": [
                {
                    "original": "Ich schaffe das nie.",
                    "suggestion": "Ich habe Schwierigkeiten mit dieser Aufgabe.",
                    "alternative": "Bisher ist es mir noch nicht gelungen, aber ich kann es weiter versuchen.",
                },
                {
                    "original": "Alle Menschen sind egoistisch.",
                    "suggestion": "Viele Menschen handeln manchmal eigennützig.",
                    "alternative": "In meiner Erfahrung verhalten sich manche Menschen in bestimmten Situationen egoistisch.",
                },
            ],
            "overgeneralization": [
                {
                    "original": "Das passiert ständig.",
                    "suggestion": "Das ist mir in letzter Zeit häufiger aufgefallen.",
                    "alternative": "In den letzten Wochen ist mir das drei- oder viermal passiert.",
                }
            ],
            "binary_thinking": [
                {
                    "original": "Entweder man ist erfolgreich oder ein Versager.",
                    "suggestion": "Erfolg hat viele Facetten und entwickelt sich über Zeit.",
                    "alternative": "Menschen können in verschiedenen Bereichen unterschiedlich erfolgreich sein.",
                }
            ],
        }

        for bias in biases:
            bias_type = bias["type"]
            if bias_type in examples:
                reformulations.extend(examples[bias_type])

        return reformulations[:2]  # Maximal 2 Beispiele
