#!/usr/bin/env bash
echo "=== ASI-Core Setup Reparatur ==="

# 1. Clean slate - alles neu
rm -rf .venv/
echo "✅ Alte venv entfernt"

# 2. Virtual Environment korrekt erstellen
python3 -m venv .venv
source .venv/bin/activate
echo "✅ Neue venv aktiviert"

# 3. Pip upgrade
pip install --upgrade pip
echo "✅ Pip aktualisiert"

# 4. Requirements installieren (falls vorhanden)
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
    echo "✅ Requirements installiert"
else
    echo "⚠️  Keine requirements.txt gefunden"
fi

# 5. Web dependencies
cd web && npm install && cd ..
echo "✅ Web dependencies installiert"

# 6. Test der Installation
source .venv/bin/activate
python3 -c "print('✅ Python läuft in venv')"
echo "🚀 Setup erfolgreich!"