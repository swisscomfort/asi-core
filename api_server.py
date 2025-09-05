#!/usr/bin/env python3
"""
ASI Core - API Server
Separater Flask-Server für kognitive Analyse-API
"""

import os
import sys
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, request

# ASI Core Module importieren
sys.path.append(str(Path(__file__).parent))

app = Flask(__name__)

# Sicherheits- und Laufzeiteinstellungen via ENV
app.config.update(
    JSONIFY_PRETTYPRINT_REGULAR=False,
)


@app.route("/api/cognitive-insights", methods=["POST"])
def cognitive_insights():
    """
    API-Endpunkt für kognitive Analyse von Texten

    Erwartet JSON mit 'content' Feld
    Gibt strukturierte Insights zurück
    """
    try:
        data = request.json
        if not data or "content" not in data:
            return jsonify({"error": "Inhalt erforderlich", "biases": []}), 400

        content = data["content"]

        # Importiere die Funktionen aus processor
        from src.core.processor import (
            detect_cognitive_biases,
            generate_refinement_suggestions,
        )

        # Analysiere Text auf Denkfallen
        biases = detect_cognitive_biases(content)

        # Generiere Verbesserungsvorschläge
        suggestions = generate_refinement_suggestions(biases)

        return jsonify(
            {
                "biases": biases,
                "suggestions": suggestions,
                "total_biases": len(biases),
            }
        )

    except Exception as e:
        print(f"Fehler bei kognitiver Analyse: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": "Analyse fehlgeschlagen", "biases": []}), 500


@app.route("/api/health", methods=["GET"])
def health_check():
    """Gesundheitscheck für die API"""
    return jsonify(
        {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "features": ["cognitive_insights"],
        }
    )


@app.route("/", methods=["GET"])
def index():
    """Startseite der API"""
    return jsonify(
        {
            "name": "ASI Core - Kognitive Analyse API",
            "version": "1.0",
            "endpoints": ["/api/health", "/api/cognitive-insights"],
        }
    )


if __name__ == "__main__":
    print("Starte ASI Core - Kognitive Analyse API...")
    debug_flag = os.getenv("ASI_API_DEBUG", "true").lower()
    debug_enabled = debug_flag in {"1", "true", "yes"}
    default_host = "127.0.0.1" if not debug_enabled else "0.0.0.0"
    host = os.getenv("ASI_API_HOST", default_host)
    port = int(os.getenv("ASI_API_PORT", "5000"))
    app.run(host=host, port=port, debug=debug_enabled)
