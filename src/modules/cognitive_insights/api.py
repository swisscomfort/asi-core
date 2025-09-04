"""
API Module - REST-Endpunkt für cognitive insights
"""

from flask import Blueprint, jsonify, request

from .bias_detector import BiasDetector
from .suggestions_generator import SuggestionsGenerator

cognitive_insights_bp = Blueprint("cognitive_insights", __name__)

# Instanzen der Klassen
bias_detector = BiasDetector()
suggestions_generator = SuggestionsGenerator()


@cognitive_insights_bp.route("/api/cognitive-insights", methods=["POST"])
def analyze_cognitive_insights():
    """Analysiert Text auf kognitive Verzerrungen und gibt Verbesserungsvorschläge"""
    try:
        data = request.get_json()

        if not data or "content" not in data:
            return jsonify({"error": "Content field is required"}), 400

        content = data["content"]

        if not isinstance(content, str) or len(content.strip()) == 0:
            return jsonify({"error": "Content must be a non-empty string"}), 400

        # Begrenze Textlänge
        if len(content) > 2000:
            content = content[:2000]

        # Erkenne Denkfallen
        biases = bias_detector.detect_biases(content)

        # Generiere Vorschläge
        suggestions = suggestions_generator.generate_suggestions(biases)

        # Erstelle Beispiele für Reformulierungen
        examples = suggestions_generator.create_example_reformulations(content, biases)

        # Erstelle Zusammenfassung
        summary = create_summary(biases)

        return jsonify(
            {
                "biases": biases,
                "suggestions": suggestions,
                "examples": examples,
                "summary": summary,
                "analysis_info": {
                    "text_length": len(content),
                    "biases_found": len(biases),
                    "suggestions_count": len(suggestions),
                },
            }
        )

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


def create_summary(biases):
    """Erstellt eine menschenlesbare Zusammenfassung der gefundenen Denkfallen"""
    if not biases:
        return "Dein Text wirkt ausgewogen und differenziert. 👍"

    bias_counts = {}
    for bias in biases:
        bias_type = bias["type"]
        bias_counts[bias_type] = bias_counts.get(bias_type, 0) + 1

    summary_parts = []

    # Deutsche Beschreibungen der Denkfallen
    bias_descriptions = {
        "absolute_terms": "absolute Begriffe",
        "overgeneralization": "Übergeneralisierungen",
        "circular_reasoning": "Kreisdenken",
        "emotional_reasoning": "emotionale Begründungen",
        "binary_thinking": "schwarz-weiß-Denken",
    }

    for bias_type, count in bias_counts.items():
        description = bias_descriptions.get(bias_type, bias_type)
        if count == 1:
            summary_parts.append(f"eine Tendenz zu {description}")
        else:
            summary_parts.append(f"mehrere Tendenzen zu {description}")

    if len(summary_parts) == 1:
        summary = f"Dein Text zeigt {summary_parts[0]}. "
    elif len(summary_parts) == 2:
        summary = f"Dein Text zeigt {summary_parts[0]} und {summary_parts[1]}. "
    else:
        summary = (
            f"Dein Text zeigt {', '.join(summary_parts[:-1])} und {summary_parts[-1]}. "
        )

    summary += "Die Vorschläge können dir helfen, präziser zu formulieren."

    return summary
