"""
ASI Core - Admin API Endpoints
Erweiterte API-Endpoints für das zentrale Admin-Dashboard
"""

import os
import psutil
import time
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request, send_file
from pathlib import Path
import sqlite3
import json

# Blueprint für Admin-APIs
admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# Hilfsfunktionen
def get_system_stats():
    """Sammelt Systemstatistiken"""
    try:
        return {
            "cpu_usage": psutil.cpu_percent(interval=1),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "uptime": time.time() - psutil.boot_time(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}

def get_asi_core_stats():
    """Sammelt ASI-Core spezifische Statistiken"""
    try:
        # Reflexionen zählen
        db_path = "data/asi_local.db"
        total_reflections = 0
        total_agents = 0
        
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Reflexionen zählen (angenommen es gibt eine reflections Tabelle)
            try:
                cursor.execute("SELECT COUNT(*) FROM reflections")
                total_reflections = cursor.fetchone()[0]
            except:
                pass
            
            conn.close()
        
        # Agenten zählen
        agents_file = "data/agents/agents.json"
        if os.path.exists(agents_file):
            with open(agents_file, 'r') as f:
                agents_data = json.load(f)
                total_agents = len(agents_data)
        
        return {
            "total_reflections": total_reflections,
            "active_agents": total_agents,
            "database_size": os.path.getsize(db_path) if os.path.exists(db_path) else 0,
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}

def get_service_status():
    """Überprüft den Status verschiedener Services"""
    services = {
        "flask_app": {
            "status": "running",
            "description": "Flask Web Server",
            "port": 8000,
            "pid": os.getpid()
        },
        "asi_core": {
            "status": "running" if os.path.exists("data/asi_local.db") else "stopped",
            "description": "ASI Core System",
            "last_activity": datetime.now().isoformat()
        },
        "blockchain": {
            "status": "unknown",
            "description": "Blockchain Connection",
            "network": "polygon"
        },
        "ipfs": {
            "status": "unknown", 
            "description": "IPFS Storage Node",
            "gateway": "local"
        }
    }
    
    return services

def get_system_alerts():
    """Generiert System-Alerts basierend auf aktuellen Bedingungen"""
    alerts = []
    
    # CPU-Check
    cpu_usage = psutil.cpu_percent()
    if cpu_usage > 80:
        alerts.append({
            "level": "warning",
            "message": f"Hohe CPU-Auslastung: {cpu_usage:.1f}%",
            "timestamp": datetime.now().isoformat()
        })
    
    # Memory-Check
    memory_usage = psutil.virtual_memory().percent
    if memory_usage > 85:
        alerts.append({
            "level": "error",
            "message": f"Kritische Speicherauslastung: {memory_usage:.1f}%",
            "timestamp": datetime.now().isoformat()
        })
    
    # Disk-Check
    disk_usage = psutil.disk_usage('/').percent
    if disk_usage > 90:
        alerts.append({
            "level": "error",
            "message": f"Kritischer Speicherplatz: {disk_usage:.1f}% belegt",
            "timestamp": datetime.now().isoformat()
        })
    
    return alerts

def get_recent_logs(limit=50):
    """Sammelt aktuelle Log-Einträge"""
    logs = []
    
    # Simulierte Logs (in Produktion würde man echte Log-Dateien lesen)
    log_levels = ["INFO", "WARNING", "ERROR", "DEBUG"]
    messages = [
        "Agent system initialized successfully",
        "New reflection processed",
        "Blockchain connection established", 
        "IPFS node connected",
        "State transition recorded",
        "Embedding cache updated",
        "User session started",
        "Database query executed"
    ]
    
    for i in range(min(limit, 20)):  # Max 20 simulierte Logs
        logs.append({
            "timestamp": (datetime.now() - timedelta(minutes=i*5)).isoformat(),
            "level": log_levels[i % len(log_levels)],
            "message": messages[i % len(messages)],
            "source": "asi-core"
        })
    
    return logs

# Admin API Endpoints

@admin_bp.route('/stats')
def admin_stats():
    """Kombinierte Systemstatistiken für das Admin-Dashboard"""
    try:
        system_stats = get_system_stats()
        asi_stats = get_asi_core_stats()
        
        combined_stats = {
            **system_stats,
            **asi_stats,
            "success": True
        }
        
        return jsonify(combined_stats)
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

@admin_bp.route('/services')
def admin_services():
    """Status aller System-Services"""
    try:
        services = get_service_status()
        return jsonify(services)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/alerts')
def admin_alerts():
    """Aktuelle System-Alerts"""
    try:
        alerts = get_system_alerts()
        return jsonify(alerts)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/logs')
def admin_logs():
    """Recent System Logs"""
    try:
        limit = request.args.get('limit', 50, type=int)
        logs = get_recent_logs(limit)
        return jsonify(logs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/logs', methods=['DELETE'])
def clear_logs():
    """Löscht System-Logs"""
    try:
        # In Produktion würde hier echte Log-Datei geleert werden
        return jsonify({"success": True, "message": "Logs cleared"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/services/<service_name>/restart', methods=['POST'])
def restart_service(service_name):
    """Startet einen Service neu"""
    try:
        # Simulierter Service-Neustart
        # In Produktion würde hier echter Service-Neustart stattfinden
        return jsonify({
            "success": True, 
            "message": f"Service {service_name} restart initiated"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/export/<data_type>')
def export_data(data_type):
    """Exportiert verschiedene Datentypen"""
    try:
        export_data = {}
        
        if data_type == "full":
            # Vollständiger Datenexport
            export_data = {
                "system_stats": get_system_stats(),
                "asi_stats": get_asi_core_stats(),
                "services": get_service_status(),
                "export_timestamp": datetime.now().isoformat()
            }
        elif data_type == "reflections":
            # Nur Reflexionen exportieren
            # Hier würde die Datenbank abgefragt werden
            export_data = {"reflections": [], "count": 0}
        elif data_type == "agents":
            # Agent-Daten exportieren
            agents_file = "data/agents/agents.json"
            if os.path.exists(agents_file):
                with open(agents_file, 'r') as f:
                    export_data = json.load(f)
        
        # JSON-Response als Download
        filename = f"asi-export-{data_type}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        
        # Temporäre Datei erstellen
        temp_path = f"/tmp/{filename}"
        with open(temp_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return send_file(temp_path, as_attachment=True, download_name=filename)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/config')
def get_config():
    """Aktuelle Systemkonfiguration"""
    try:
        config_data = {
            "database_path": "data/asi_local.db",
            "agents_path": "data/agents/",
            "blockchain_network": "polygon",
            "ipfs_gateway": "local",
            "debug_mode": True,
            "auto_backup": False,
            "max_reflections": 10000,
            "cache_size": "100MB"
        }
        return jsonify(config_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/config', methods=['POST'])
def update_config():
    """Aktualisiert Systemkonfiguration"""
    try:
        config_updates = request.get_json()
        # In Produktion würde hier die Konfiguration persistiert werden
        return jsonify({
            "success": True, 
            "message": "Configuration updated",
            "updated_fields": list(config_updates.keys())
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route('/health')
def admin_health():
    """Erweiterte Health-Check für Admin"""
    try:
        health_data = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "uptime": time.time() - psutil.boot_time(),
            "components": {
                "database": os.path.exists("data/asi_local.db"),
                "agents": os.path.exists("data/agents/agents.json"),
                "web_server": True,
                "file_system": os.access("data/", os.W_OK)
            }
        }
        return jsonify(health_data)
    except Exception as e:
        return jsonify({"error": str(e), "status": "unhealthy"}), 500