#!/usr/bin/env python3
"""
ASI-Core Progressive Web App Starter
Startet die PWA-Version mit Service Worker Registration
"""

import os
import sys
import json
import webbrowser
from pathlib import Path
from flask import Flask, render_template_string, send_from_directory, jsonify
import threading
import time

# PWA Template
PWA_TEMPLATE = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ASI-Core PWA</title>
    
    <!-- PWA Meta Tags -->
    <meta name="theme-color" content="#764ba2">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <meta name="apple-mobile-web-app-title" content="ASI-Core">
    <meta name="description" content="Advanced Structured Intelligence - Core System">
    
    <!-- PWA Links -->
    <link rel="manifest" href="/manifest.json">
    <link rel="icon" type="image/png" sizes="32x32" href="/icon-32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/icon-16.png">
    <link rel="apple-touch-icon" href="/icon-192.png">
    
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .header {
            text-align: center;
            margin-bottom: 3rem;
        }
        
        .header h1 {
            font-size: 3rem;
            font-weight: 300;
            margin-bottom: 1rem;
        }
        
        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        
        .cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin-bottom: 3rem;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 2rem;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
        }
        
        .card h3 {
            font-size: 1.5rem;
            margin-bottom: 1rem;
            color: #fff;
        }
        
        .card p {
            opacity: 0.9;
            line-height: 1.6;
            margin-bottom: 1.5rem;
        }
        
        .btn {
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1rem;
            transition: background-color 0.3s;
            text-decoration: none;
            display: inline-block;
        }
        
        .btn:hover {
            background: rgba(255, 255, 255, 0.3);
        }
        
        .btn.primary {
            background: #4CAF50;
        }
        
        .btn.primary:hover {
            background: #45a049;
        }
        
        .status {
            background: rgba(0, 0, 0, 0.2);
            border-radius: 10px;
            padding: 1rem;
            margin-top: 2rem;
        }
        
        .status-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.5rem;
        }
        
        .status-item:last-child {
            margin-bottom: 0;
        }
        
        .online {
            color: #4CAF50;
        }
        
        .offline {
            color: #f44336;
        }
        
        .install-prompt {
            background: rgba(76, 175, 80, 0.2);
            border: 1px solid #4CAF50;
            border-radius: 10px;
            padding: 1rem;
            margin-top: 2rem;
            text-align: center;
            display: none;
        }
        
        @media (max-width: 768px) {
            .header h1 {
                font-size: 2rem;
            }
            
            .container {
                padding: 1rem;
            }
            
            .cards {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 ASI-Core</h1>
            <p>Advanced Structured Intelligence - Progressive Web App</p>
        </div>
        
        <div class="cards">
            <div class="card">
                <h3>📝 Neue Reflexion</h3>
                <p>Erstelle eine neue Reflexion und beginne deinen Erkenntnisprozess.</p>
                <button class="btn primary" onclick="navigateTo('/new-reflection')">
                    Reflexion erstellen
                </button>
            </div>
            
            <div class="card">
                <h3>🔍 Suche</h3>
                <p>Durchsuche deine bestehenden Reflexionen und finde Verbindungen.</p>
                <button class="btn" onclick="navigateTo('/search')">
                    Durchsuchen
                </button>
            </div>
            
            <div class="card">
                <h3>📊 Dashboard</h3>
                <p>Übersicht über deine Reflexionen, Statistiken und Erkenntnisse.</p>
                <button class="btn" onclick="navigateTo('/dashboard')">
                    Dashboard öffnen
                </button>
            </div>
            
            <div class="card">
                <h3>⚙️ Einstellungen</h3>
                <p>Konfiguriere ASI-Core nach deinen Bedürfnissen.</p>
                <button class="btn" onclick="navigateTo('/settings')">
                    Einstellungen
                </button>
            </div>
        </div>
        
        <div class="status">
            <h3>📡 System Status</h3>
            <div class="status-item">
                <span>Verbindung:</span>
                <span id="connection-status" class="online">Online</span>
            </div>
            <div class="status-item">
                <span>Service Worker:</span>
                <span id="sw-status">Wird geladen...</span>
            </div>
            <div class="status-item">
                <span>Offline-Modus:</span>
                <span id="offline-status">Verfügbar</span>
            </div>
            <div class="status-item">
                <span>Synchronisation:</span>
                <span id="sync-status">Aktuell</span>
            </div>
        </div>
        
        <div id="install-prompt" class="install-prompt">
            <h3>📱 App installieren</h3>
            <p>Installiere ASI-Core auf deinem Gerät für die beste Erfahrung.</p>
            <button class="btn primary" onclick="installPWA()">
                Jetzt installieren
            </button>
        </div>
    </div>

    <script>
        let deferredPrompt;
        
        // Service Worker Registration
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', () => {
                navigator.serviceWorker.register('/service-worker.js')
                    .then(registration => {
                        console.log('SW registered: ', registration);
                        updateSWStatus('Aktiv');
                        
                        // Listen for updates
                        registration.addEventListener('updatefound', () => {
                            updateSWStatus('Update verfügbar');
                        });
                    })
                    .catch(registrationError => {
                        console.log('SW registration failed: ', registrationError);
                        updateSWStatus('Fehler');
                    });
            });
        } else {
            updateSWStatus('Nicht unterstützt');
        }
        
        // PWA Install Prompt
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
            document.getElementById('install-prompt').style.display = 'block';
        });
        
        function installPWA() {
            if (deferredPrompt) {
                deferredPrompt.prompt();
                deferredPrompt.userChoice.then((choiceResult) => {
                    if (choiceResult.outcome === 'accepted') {
                        console.log('User accepted the install prompt');
                        document.getElementById('install-prompt').style.display = 'none';
                    }
                    deferredPrompt = null;
                });
            }
        }
        
        // Connection Status
        function updateConnectionStatus() {
            const statusEl = document.getElementById('connection-status');
            if (navigator.onLine) {
                statusEl.textContent = 'Online';
                statusEl.className = 'online';
            } else {
                statusEl.textContent = 'Offline';
                statusEl.className = 'offline';
            }
        }
        
        function updateSWStatus(status) {
            document.getElementById('sw-status').textContent = status;
        }
        
        // Navigation
        function navigateTo(path) {
            // Check if API is available
            fetch('/api/health')
                .then(response => {
                    if (response.ok) {
                        window.location.href = path;
                    } else {
                        alert('API nicht verfügbar. Bitte starte den ASI-Core Server.');
                    }
                })
                .catch(error => {
                    alert('Keine Verbindung zum Server. Bitte starte ASI-Core mit: python main.py serve');
                });
        }
        
        // Initialize
        updateConnectionStatus();
        
        // Listen for online/offline events
        window.addEventListener('online', updateConnectionStatus);
        window.addEventListener('offline', updateConnectionStatus);
        
        // Periodic API health check
        setInterval(() => {
            fetch('/api/health', { mode: 'no-cors' })
                .then(() => {
                    document.getElementById('sync-status').textContent = 'Aktuell';
                })
                .catch(() => {
                    document.getElementById('sync-status').textContent = 'Offline';
                });
        }, 30000);
    </script>
</body>
</html>
"""

class PWAServer:
    def __init__(self, port=8000):
        self.app = Flask(__name__)
        self.port = port
        self.setup_routes()
    
    def setup_routes(self):
        @self.app.route('/')
        def index():
            return render_template_string(PWA_TEMPLATE)
        
        @self.app.route('/manifest.json')
        def manifest():
            # Check if manifest exists in web directory
            manifest_path = Path('web/manifest.json')
            if manifest_path.exists():
                return send_from_directory('web', 'manifest.json')
            
            # Fallback manifest
            return jsonify({
                "name": "ASI-Core",
                "short_name": "ASI-Core",
                "start_url": "/",
                "display": "standalone",
                "background_color": "#667eea",
                "theme_color": "#764ba2",
                "icons": [
                    {
                        "src": "/icon-192.png",
                        "sizes": "192x192",
                        "type": "image/png"
                    }
                ]
            })
        
        @self.app.route('/service-worker.js')
        def service_worker():
            sw_path = Path('web/src/service-worker.js')
            if sw_path.exists():
                return send_from_directory('web/src', 'service-worker.js')
            
            # Fallback basic service worker
            return """
const CACHE_NAME = 'asi-core-basic';
self.addEventListener('install', (event) => {
    console.log('Service Worker installing...');
    self.skipWaiting();
});
self.addEventListener('activate', (event) => {
    console.log('Service Worker activating...');
    self.clients.claim();
});
            """, 200, {'Content-Type': 'application/javascript'}
        
        @self.app.route('/offline.html')
        def offline():
            offline_path = Path('web/offline.html')
            if offline_path.exists():
                return send_from_directory('web', 'offline.html')
            
            return "<h1>Offline</h1><p>Sie sind offline.</p>"
        
        # Proxy routes to main ASI-Core API
        @self.app.route('/api/<path:path>')
        def proxy_api(path):
            import requests
            try:
                resp = requests.get(f'http://localhost:5000/api/{path}')
                return resp.content, resp.status_code
            except:
                return jsonify({"error": "API not available"}), 503
        
        # Static file serving
        @self.app.route('/<path:filename>')
        def static_files(filename):
            # Try web directory first
            web_path = Path('web')
            if (web_path / filename).exists():
                return send_from_directory('web', filename)
            
            # Fallback for missing files
            return f"File not found: {filename}", 404
    
    def run(self):
        print(f"🚀 Starting ASI-Core PWA Server on port {self.port}")
        print(f"📱 Open: http://localhost:{self.port}")
        print("🔄 Service Worker will be registered automatically")
        print("📦 App can be installed as PWA")
        print("\nPress Ctrl+C to stop the server")
        
        self.app.run(host='0.0.0.0', port=self.port, debug=False)

def main():
    """Start PWA server"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ASI-Core PWA Starter')
    parser.add_argument('--port', type=int, default=8000, help='Port for PWA server')
    parser.add_argument('--open', action='store_true', help='Open browser automatically')
    args = parser.parse_args()
    
    server = PWAServer(port=args.port)
    
    # Open browser if requested
    if args.open:
        def open_browser():
            time.sleep(1)  # Wait for server to start
            webbrowser.open(f'http://localhost:{args.port}')
        
        threading.Thread(target=open_browser, daemon=True).start()
    
    try:
        server.run()
    except KeyboardInterrupt:
        print("\n👋 PWA Server stopped")

if __name__ == "__main__":
    main()
