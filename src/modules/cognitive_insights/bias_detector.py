"""
Bias Detector - Erkennt kognitive Verzerrungen in Texten
"""

import re
from typing import Dict, List, Tuple


class BiasDetector:
    def __init__(self):
        self.patterns = {
            "absolute_terms": {
                "keywords": [
                    "immer",
                    "nie",
                    "alle",
                    "niemand",
                    "nichts",
                    "alles",
                    "niemals",
                    "stets",
                    "ausnahmslos",
                ],
                "weight": 0.8,
            },
            "overgeneralization": {
                "patterns": [
                    r"jeder\s+(?:denkt|glaubt|weiß|meint)",
                    r"das\s+passiert\s+(?:ständig|dauernd|immer)",
                    r"alle\s+(?:Menschen|Leute|Frauen|Männer)",
                    r"man\s+(?:kann|muss|sollte)\s+(?:immer|nie)",
                    r"typisch\s+(?:für|dass)",
                ],
                "weight": 0.7,
            },
            "circular_reasoning": {
                "patterns": [
                    r"weil\s+es\s+(?:so|falsch|richtig)\s+ist",
                    r"das\s+ist\s+(?:einfach|halt)\s+so",
                    r"(?:natürlich|selbstverständlich|offensichtlich)",
                    r"deshalb\s+ist\s+es\s+(?:richtig|falsch)",
                ],
                "weight": 0.6,
            },
            "emotional_reasoning": {
                "patterns": [
                    r"(?:fühlt|wirkt)\s+sich\s+(?:falsch|richtig)\s+an",
                    r"ich\s+(?:spüre|fühle|habe\s+das\s+Gefühl)",
                    r"mein\s+(?:Bauchgefühl|Instinkt)\s+sagt",
                    r"das\s+(?:macht|gibt)\s+mir\s+(?:Angst|Sorge)",
                ],
                "weight": 0.5,
            },
            "binary_thinking": {
                "patterns": [
                    r"entweder\s+.*\s+oder",
                    r"(?:nur|ausschließlich)\s+(?:schwarz|weiß)",
                    r"(?:gut|schlecht|richtig|falsch)\s+oder\s+(?:gut|schlecht|richtig|falsch)",
                    r"es\s+gibt\s+(?:nur|ausschließlich)\s+(?:zwei|2)",
                ],
                "weight": 0.6,
            },
        }

    def detect_biases(self, text: str) -> List[Dict]:
        """Erkennt kognitive Verzerrungen im Text"""
        biases = []
        text_lower = text.lower()

        # Absolute Begriffe erkennen
        absolute_instances = []
        absolute_positions = []
        for keyword in self.patterns["absolute_terms"]["keywords"]:
            matches = list(re.finditer(r"\b" + re.escape(keyword) + r"\b", text_lower))
            for match in matches:
                absolute_instances.append(keyword)
                absolute_positions.append([match.start(), match.end()])

        if absolute_instances:
            biases.append(
                {
                    "type": "absolute_terms",
                    "instances": absolute_instances,
                    "positions": absolute_positions,
                    "severity": min(len(absolute_instances) * 0.2 + 0.3, 1.0),
                }
            )

        # Übergeneralisierungen erkennen
        for pattern in self.patterns["overgeneralization"]["patterns"]:
            matches = list(re.finditer(pattern, text_lower))
            if matches:
                biases.append(
                    {
                        "type": "overgeneralization",
                        "instances": [match.group() for match in matches],
                        "positions": [
                            [match.start(), match.end()] for match in matches
                        ],
                        "severity": self.patterns["overgeneralization"]["weight"],
                    }
                )

        # Kreisdenken erkennen
        circular_matches = []
        circular_positions = []
        for pattern in self.patterns["circular_reasoning"]["patterns"]:
            matches = list(re.finditer(pattern, text_lower))
            for match in matches:
                circular_matches.append(match.group())
                circular_positions.append([match.start(), match.end()])

        if circular_matches:
            biases.append(
                {
                    "type": "circular_reasoning",
                    "instances": circular_matches,
                    "positions": circular_positions,
                    "severity": self.patterns["circular_reasoning"]["weight"],
                }
            )

        # Emotionale Begründungen erkennen
        emotional_matches = []
        emotional_positions = []
        for pattern in self.patterns["emotional_reasoning"]["patterns"]:
            matches = list(re.finditer(pattern, text_lower))
            for match in matches:
                emotional_matches.append(match.group())
                emotional_positions.append([match.start(), match.end()])

        if emotional_matches:
            biases.append(
                {
                    "type": "emotional_reasoning",
                    "instances": emotional_matches,
                    "positions": emotional_positions,
                    "severity": self.patterns["emotional_reasoning"]["weight"],
                }
            )

        # Binäres Denken erkennen
        binary_matches = []
        binary_positions = []
        for pattern in self.patterns["binary_thinking"]["patterns"]:
            matches = list(re.finditer(pattern, text_lower))
            for match in matches:
                binary_matches.append(match.group())
                binary_positions.append([match.start(), match.end()])

        if binary_matches:
            biases.append(
                {
                    "type": "binary_thinking",
                    "instances": binary_matches,
                    "positions": binary_positions,
                    "severity": self.patterns["binary_thinking"]["weight"],
                }
            )

        # Sortiere nach Schweregrad und limitiere auf 3
        biases.sort(key=lambda x: x["severity"], reverse=True)
        return biases[:3]
