"""
ASI Core - Web Interface
Flask-basierte Web-Anwendung für ASI Core
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for

# ASI Core Module importieren
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.ai.embedding import ReflectionEmbedding
from src.ai.search import SemanticSearchEngine
from src.blockchain.contract import ASISmartContract
from src.blockchain.wallet import CryptoWallet
from src.core.input import InputHandler
from src.core.output import OutputGenerator
from src.core.processor import ReflectionProcessor
from src.storage.arweave_client import ArweaveClient
from src.storage.ipfs_client import IPFSClient
from src.storage.local_db import LocalDatabase

# Flask App initialisieren
app = Flask(__name__)

# Sicherheitsrelevante Einstellungen
# Secret Key: aus ENV beziehen, sonst zur Laufzeit einen temporären Dev-Key generieren
_env_secret = os.getenv("ASI_SECRET_KEY")
if _env_secret:
    app.secret_key = _env_secret
else:
    # Hinweis: Dieser temporäre Schlüssel ist nur für lokale Entwicklung geeignet
    # In Produktion MUSS ASI_SECRET_KEY gesetzt sein (siehe README/.env.example)
    import secrets

    app.secret_key = secrets.token_hex(32)

# Sichere Cookie-Defaults (wirken nur, wenn Sessions/Cookies verwendet werden)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.getenv("ASI_COOKIE_SECURE", "false").lower()
    in {"1", "true", "yes"},
)


# ASI Core System initialisieren
def init_asi_system():
    """Initialisiert das ASI Core System"""
    try:
        # Storage-Module
        local_db = LocalDatabase("data/asi_local.db")
        ipfs_client = IPFSClient()
        arweave_client = ArweaveClient()

        # AI-Module
        embedding_system = ReflectionEmbedding()
        search_engine = SemanticSearchEngine(embedding_system, local_db)

        # Core-Module
        input_handler = InputHandler()
        processor = ReflectionProcessor(embedding_system, local_db)
        output_generator = OutputGenerator()

        # Blockchain-Module
        smart_contract = ASISmartContract()
        wallet = CryptoWallet()

        return {
            "input_handler": input_handler,
            "processor": processor,
            "output_generator": output_generator,
            "local_db": local_db,
            "ipfs_client": ipfs_client,
            "arweave_client": arweave_client,
            "embedding_system": embedding_system,
            "search_engine": search_engine,
            "smart_contract": smart_contract,
            "wallet": wallet,
        }
    except Exception as e:
        print(f"Fehler bei ASI-Initialisierung: {e}")
        return None


# Globale ASI-Instanz
asi_system = init_asi_system()


@app.route("/")
def index():
    """Startseite"""
    stats = None
    if asi_system and asi_system["local_db"]:
        try:
            stats = asi_system["local_db"].get_statistics()
        except Exception as e:
            print(f"Fehler beim Laden der Statistiken: {e}")

    return render_template("index.html", stats=stats)


# ===== API Health Check =====
@app.route("/api/health")
def api_health():
    """Health Check Endpoint für Debugging"""
    try:
        status = {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "asi_system_loaded": asi_system is not None,
            "components": {},
        }

        if asi_system:
            status["components"] = {
                "input_handler": "ok",
                "processor": "ok",
                "output_generator": "ok",
                "local_db": "ok",
                "search_engine": "ok",
            }

        return jsonify(status)
    except Exception as e:
        return (
            jsonify(
                {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            500,
        )


@app.route("/reflect")
def reflect():
    """Reflexions-Seite"""
    return render_template("reflect.html")


@app.route("/api/reflect", methods=["POST"])
def api_reflect():
    """API-Endpoint für neue Reflexion"""
    if not asi_system:
        return jsonify({"error": "ASI System nicht verfügbar"}), 500

    try:
        data = request.get_json()
        content = data.get("content", "").strip()
        tags = data.get("tags", [])
        privacy_level = data.get("privacy_level", "private")

        if not content:
            return jsonify({"error": "Reflexionsinhalt ist erforderlich"}), 400

        # Reflexion verarbeiten
        input_handler = asi_system["input_handler"]
        processor = asi_system["processor"]
        local_db = asi_system["local_db"]
        output_generator = asi_system["output_generator"]

        # 1. Eingabe erfassen
        reflection_entry = input_handler.capture_reflection(content, tags)
        reflection_entry.privacy_level = privacy_level

        # 2. Verarbeitung
        reflection_data = {
            "content": reflection_entry.content,
            "timestamp": reflection_entry.timestamp.isoformat(),
            "tags": reflection_entry.tags,
            "privacy_level": reflection_entry.privacy_level,
        }

        processed_reflection = processor.process_reflection(reflection_data)
        exported_data = processor.export_processed(processed_reflection)

        # 3. Speicherung
        reflection_id = local_db.store_reflection(exported_data)

        # 4. Lokale Ausgabe
        local_file = output_generator.save_local_copy(exported_data)

        return jsonify(
            {
                "success": True,
                "reflection_id": reflection_id,
                "hash": exported_data["hash"],
                "themes": exported_data["themes"],
                "sentiment": exported_data["sentiment"],
                "message": "Reflexion erfolgreich gespeichert",
            }
        )

    except Exception as e:
        return jsonify({"error": f"Fehler beim Verarbeiten: {str(e)}"}), 500


@app.route("/api/reflection/create", methods=["POST"])
def api_create_reflection():
    """API-Endpoint für neue Reflexion mit CID"""
    if not asi_system:
        return jsonify({"error": "ASI System nicht verfügbar"}), 500

    try:
        data = request.get_json()
        cid = data.get("cid", "").strip()
        title = data.get("title", "").strip()
        tags = data.get("tags", [])
        shared = data.get("shared", False)
        timestamp = data.get("timestamp", datetime.now().isoformat())

        if not cid or not title:
            return jsonify({"error": "CID und Titel sind erforderlich"}), 400

        # Lokale Datenbank für Indexierung verwenden
        local_db = asi_system["local_db"]

        # Reflexionsdaten für lokale Speicherung vorbereiten
        reflection_data = {
            "content": title,  # Verwende Titel als Content für lokale Suche
            "timestamp": timestamp,
            "tags": tags,
            "cid": cid,
            "shared": shared,
            "privacy_level": "public" if shared else "private",
        }

        # In lokale Datenbank speichern
        reflection_id = local_db.store_reflection(reflection_data)

        print(f"✅ Reflexion erstellt: ID={reflection_id}, CID={cid}")

        return jsonify(
            {
                "success": True,
                "reflection_id": reflection_id,
                "cid": cid,
                "message": "Reflexion erfolgreich erstellt und indexiert",
            }
        )

    except Exception as e:
        print(f"❌ Fehler beim Erstellen der Reflexion: {str(e)}")
        return jsonify({"error": f"Fehler beim Erstellen: {str(e)}"}), 500


@app.route("/search")
def search():
    """Such-Seite"""
    return render_template("search.html")


@app.route("/api/search", methods=["GET"])
def api_search():
    """API-Endpoint für Suche"""
    if not asi_system:
        return jsonify({"error": "ASI System nicht verfügbar"}), 500

    try:
        query = request.args.get("q", "").strip()
        limit = int(request.args.get("limit", 10))

        if not query:
            return jsonify({"error": "Suchanfrage ist erforderlich"}), 400

        search_engine = asi_system["search_engine"]
        results = search_engine.search_by_text(query, limit=limit)

        # Ergebnisse für JSON serialisieren
        search_results = []
        for result in results:
            search_results.append(
                {
                    "hash": result.reflection_hash,
                    "preview": result.content_preview,
                    "similarity": round(result.similarity_score, 3),
                    "themes": result.matching_themes,
                    "timestamp": result.timestamp.strftime("%Y-%m-%d %H:%M"),
                    "privacy_level": result.privacy_level,
                }
            )

        return jsonify(
            {
                "success": True,
                "query": query,
                "results": search_results,
                "count": len(search_results),
            }
        )

    except Exception as e:
        print(f"Suchfehler: {e}")
        # Fallback: Einfache Textsuche
        try:
            local_db = asi_system["local_db"]
            all_reflections = local_db.get_reflections(limit=100)

            search_results = []
            query_lower = query.lower()

            for reflection in all_reflections:
                content = local_db.get_reflection_by_hash(reflection.hash).get(
                    "content", ""
                )
                content_lower = content.lower()

                # Einfache Textübereinstimmung
                if query_lower in content_lower:
                    similarity = 0.8
                else:
                    query_words = set(query_lower.split())
                    content_words = set(content_lower.split())
                    common_words = query_words.intersection(content_words)
                    similarity = (
                        len(common_words) / len(query_words) if query_words else 0
                    )

                if similarity > 0.3:
                    search_results.append(
                        {
                            "hash": reflection.hash,
                            "preview": (
                                content[:200] + "..." if len(content) > 200 else content
                            ),
                            "similarity": round(similarity, 3),
                            "themes": reflection.themes or [],
                            "timestamp": reflection.timestamp.strftime(
                                "%Y-%m-%d %H:%M"
                            ),
                            "privacy_level": reflection.privacy_level,
                        }
                    )

            search_results.sort(key=lambda x: x["similarity"], reverse=True)
            search_results = search_results[:limit]

            return jsonify(
                {
                    "success": True,
                    "query": query,
                    "results": search_results,
                    "count": len(search_results),
                    "fallback": True,
                }
            )

        except Exception as fallback_error:
            return (
                jsonify({"error": f"Fehler bei der Suche: {str(fallback_error)}"}),
                500,
            )


@app.route("/reflections")
def reflections():
    """Reflexions-Übersicht"""
    if not asi_system:
        flash("ASI System nicht verfügbar", "error")
        return redirect(url_for("index"))

    try:
        local_db = asi_system["local_db"]
        reflections = local_db.get_reflections(limit=50)

        return render_template("reflections.html", reflections=reflections)

    except Exception as e:
        flash(f"Fehler beim Laden der Reflexionen: {str(e)}", "error")
        return redirect(url_for("index"))


@app.route("/reflection/<hash_id>")
def reflection_detail(hash_id):
    """Detailansicht einer Reflexion"""
    if not asi_system:
        flash("ASI System nicht verfügbar", "error")
        return redirect(url_for("index"))

    try:
        local_db = asi_system["local_db"]
        reflection = local_db.get_reflection_by_hash(hash_id)

        if not reflection:
            flash("Reflexion nicht gefunden", "error")
            return redirect(url_for("reflections"))

        # Ähnliche Reflexionen finden
        search_engine = asi_system["search_engine"]
        similar = search_engine.get_related_reflections(hash_id, limit=5)

        return render_template(
            "reflection_detail.html", reflection=reflection, similar=similar
        )

    except Exception as e:
        flash(f"Fehler beim Laden der Reflexion: {str(e)}", "error")
        return redirect(url_for("reflections"))


@app.route("/insights")
def insights():
    """Erkenntnisse und Statistiken"""
    if not asi_system:
        flash("ASI System nicht verfügbar", "error")
        return redirect(url_for("index"))

    try:
        local_db = asi_system["local_db"]
        output_generator = asi_system["output_generator"]

        # Statistiken
        stats = local_db.get_statistics()

        # Wochenbericht
        weekly_report = output_generator.create_weekly_report()

        # Aktuelle Erkenntnisse
        recent_insights = local_db.get_recent_insights(days_back=14)

        return render_template(
            "insights.html",
            stats=stats,
            weekly_report=weekly_report,
            insights=recent_insights,
        )

    except Exception as e:
        flash(f"Fehler beim Laden der Erkenntnisse: {str(e)}", "error")
        return redirect(url_for("index"))


@app.route("/hrm")
def hrm_reflection():
    """HRM-erweiterte Reflexionsseite"""
    if not asi_system:
        flash("ASI System nicht verfügbar", "error")
        return redirect(url_for("index"))

    return render_template("hrm_reflection.html")


@app.route("/api/reflection/hrm", methods=["POST"])
def process_reflection_hrm():
    """API-Endpoint für HRM-erweiterte Reflexionsverarbeitung"""
    if not asi_system:
        return jsonify({"error": "ASI System nicht verfügbar"}), 503

    try:
        data = request.get_json()

        if not data or not data.get("content"):
            return jsonify({"error": "Reflexionsinhalt erforderlich"}), 400

        # Verarbeite mit HRM-Integration
        processor = asi_system["processor"]
        local_db = asi_system["local_db"]

        # Reflexionsdaten vorbereiten
        reflection_data = {
            "content": data["content"],
            "tags": data.get("tags", []),
            "privacy_level": data.get("privacy_level", "private"),
            "timestamp": data.get("timestamp", datetime.now().isoformat()),
            "hrm_enabled": data.get("hrm_enabled", True),
        }

        # Verarbeitung mit erweiterten HRM-Features
        processed = processor.process_reflection(reflection_data)

        # In Datenbank speichern
        reflection_id = local_db.store_reflection(
            content=processed.anonymized_content,
            tags=processed.tags,
            privacy_level=processed.privacy_level,
            metadata={
                "original_hash": processed.original_hash,
                "structured_data": processed.structured_data,
                "sentiment": processed.sentiment,
                "themes": processed.key_themes,
                "hrm_enhanced": True,
            },
        )

        # Erweiterte Antwort mit HRM-Daten
        response = {
            "status": "success",
            "message": "Reflexion erfolgreich mit HRM analysiert",
            "reflection_id": reflection_id,
            "original_hash": processed.original_hash,
            "structured_data": processed.structured_data,
            "sentiment": processed.sentiment,
            "themes": processed.key_themes,
            "hrm_available": bool(processed.structured_data.get("hrm")),
            "processing_timestamp": processed.processing_timestamp.isoformat(),
        }

        # Füge Upload-Status hinzu falls verfügbar
        hrm_data = processed.structured_data.get("hrm")
        if hrm_data and not hrm_data.get("error"):
            response["hrm_insights"] = {
                "confidence": hrm_data.get("confidence", 0.5),
                "abstract_plan_available": bool(hrm_data.get("abstract_plan")),
                "concrete_action_available": bool(hrm_data.get("concrete_action")),
                "recommendations_count": len(hrm_data.get("recommendations", [])),
            }

        return jsonify(response)

    except Exception as e:
        error_msg = f"Fehler bei HRM-Verarbeitung: {str(e)}"
        print(error_msg)  # Für Debugging
        return jsonify({"error": error_msg}), 500


@app.route("/api/hrm/analytics")
def hrm_analytics():
    """API-Endpoint für HRM-Analytics"""
    if not asi_system:
        return jsonify({"error": "ASI System nicht verfügbar"}), 503

    try:
        processor = asi_system["processor"]

        analytics = {
            "hrm_available": hasattr(processor, "hrm_planner")
            and processor.hrm_planner is not None,
            "system_status": "active" if processor.hrm_planner else "basic",
            "features": {
                "pattern_recognition": hasattr(processor, "hrm_planner"),
                "abstract_planning": hasattr(processor, "hrm_planner"),
                "concrete_execution": hasattr(processor, "hrm_executor"),
                "detail_analysis": hasattr(processor, "hrm_executor"),
            },
        }

        # Wenn HRM verfügbar ist, hole zusätzliche Analytics
        if processor.hrm_planner and hasattr(
            processor.hrm_planner, "get_planning_history"
        ):
            planning_history = processor.hrm_planner.get_planning_history()
            analytics["planning_history_count"] = len(planning_history)

            if len(planning_history) > 0:
                analytics["average_confidence"] = sum(
                    plan.get("confidence_score", 0.5) for plan in planning_history[-10:]
                ) / min(len(planning_history), 10)

        if processor.hrm_executor and hasattr(
            processor.hrm_executor, "get_action_analytics"
        ):
            action_analytics = processor.hrm_executor.get_action_analytics()
            analytics["action_analytics"] = action_analytics

        return jsonify(analytics)

    except Exception as e:
        return jsonify({"error": f"Analytics-Fehler: {str(e)}"}), 500


@app.route("/api/stats")
def api_stats():
    """API-Endpoint für Statistiken"""
    if not asi_system:
        return jsonify({"error": "ASI System nicht verfügbar"}), 500

    try:
        local_db = asi_system["local_db"]
        stats = local_db.get_statistics()

        # IPFS-Status
        ipfs_status = asi_system["ipfs_client"].is_node_running()

        # Arweave-Status
        arweave_info = asi_system["arweave_client"].get_storage_info()

        # Smart Contract-Status
        contract_stats = asi_system["smart_contract"].get_contract_stats()

        return jsonify(
            {
                "success": True,
                "database": stats,
                "ipfs_running": ipfs_status,
                "arweave_status": arweave_info["status"],
                "blockchain_connected": contract_stats.get("connected", False),
            }
        )

    except Exception as e:
        return jsonify({"error": f"Statistik-Fehler: {str(e)}"}), 500


@app.route("/settings")
def settings():
    """Einstellungen"""
    return render_template("settings.html")


@app.route("/api/export")
def api_export():
    """API-Endpoint für Daten-Export"""
    if not asi_system:
        return jsonify({"error": "ASI System nicht verfügbar"}), 500

    try:
        local_db = asi_system["local_db"]
        reflections = local_db.get_reflections(limit=1000)

        # Export-Daten vorbereiten
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "version": "1.0",
            "total_reflections": len(reflections),
            "reflections": [],
        }

        for reflection in reflections:
            full_reflection = local_db.get_reflection_by_hash(reflection.hash)
            export_data["reflections"].append(
                {
                    "hash": reflection.hash,
                    "content": full_reflection["content"],
                    "timestamp": reflection.timestamp.isoformat(),
                    "themes": reflection.themes,
                    "tags": reflection.tags,
                    "privacy_level": reflection.privacy_level,
                    "sentiment": reflection.sentiment,
                }
            )

        return jsonify(export_data)

    except Exception as e:
        return jsonify({"error": f"Export-Fehler: {str(e)}"}), 500


@app.errorhandler(404)
def not_found(error):
    """404 Error Handler"""
    return (
        render_template(
            "error.html", error_code=404, error_message="Seite nicht gefunden"
        ),
        404,
    )


@app.errorhandler(500)
def internal_error(error):
    """500 Error Handler"""
    return (
        render_template(
            "error.html", error_code=500, error_message="Interner Server-Fehler"
        ),
        500,
    )


@app.route("/api/reset", methods=["POST"])
def api_reset():
    """API-Endpoint für System-Reset (VORSICHT!)"""
    if not asi_system:
        return jsonify({"error": "ASI System nicht verfügbar"}), 500

    try:
        # WARNUNG: Das löscht alle Daten!
        # local_db = asi_system["local_db"]
        # Hier würde der Reset-Code stehen
        # local_db.clear_all_data()  # Implementierung in local_db erforderlich

        return jsonify(
            {
                "success": False,
                "message": "Reset-Funktion aus Sicherheitsgründen deaktiviert",
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/cognitive-insights", methods=["POST"])
def api_cognitive_insights():
    """API-Endpoint für kognitive Einblicke und Denkfallen-Erkennung"""
    try:
        data = request.get_json()
        if not data or "content" not in data:
            return jsonify({"error": "Kein Textinhalt bereitgestellt"}), 400

        content = data["content"]
        if not content.strip():
            return jsonify({"biases": []}), 200

        # Importiere detect_cognitive_biases aus processor
        from src.core.processor import (
            detect_cognitive_biases,
            generate_refinement_suggestions,
        )

        # Erkenne Denkfallen
        biases = detect_cognitive_biases(content)

        # Begrenze auf erste 3 Denkfallen für bessere UX
        if len(biases) > 3:
            biases = biases[:3]

        # Generiere Verbesserungsvorschläge
        suggestions = generate_refinement_suggestions(biases)

        return jsonify(
            {
                "success": True,
                "biases": biases,
                "suggestions": suggestions,
                "total_found": len(biases),
            }
        )

    except Exception as e:
        return (
            jsonify(
                {"error": f"Fehler bei kognitiver Analyse: {str(e)}", "success": False}
            ),
            500,
        )


if __name__ == "__main__":
    print("Starte ASI Core Web-Interface...")

    # Erstelle Template-Verzeichnis falls nicht vorhanden
    template_dir = Path(__file__).parent / "templates"
    template_dir.mkdir(exist_ok=True)

    static_dir = Path(__file__).parent / "static"
    static_dir.mkdir(exist_ok=True)

    # Flask App starten (Debug/Host via ENV konfigurierbar)
    debug_enabled = os.getenv("ASI_DEBUG", "true").lower() in {"1", "true", "yes"}
    host = os.getenv("ASI_HOST", "127.0.0.1" if not debug_enabled else "0.0.0.0")
    port = int(os.getenv("ASI_PORT", "8000"))
    app.run(host=host, port=port, debug=debug_enabled, threaded=True)
