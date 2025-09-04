#!/usr/bin/env python3
"""
ASI Core - API Server
Separater Flask-Server für kognitive Analyse-API
"""

import json
import sys
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, request

# ASI Core Module importieren
sys.path.append(str(Path(__file__).parent))

app = Flask(__name__)


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
            {"biases": biases, "suggestions": suggestions, "total_biases": len(biases)}
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
    app.run(host="0.0.0.0", port=5000, debug=True)
