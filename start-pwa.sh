#!/bin/bash

# 🚀 ASI-Core Local PWA Server
# Startet die PWA lokal für sofortigen Zugriff

echo "🚀 Starting ASI-Core PWA Server..."
echo "📱 Building PWA..."

cd web

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Build PWA
echo "🏗️ Building production PWA..."
npm run build

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo "🌐 Starting local server..."
    echo ""
    echo "🎯 Your ASI-Core PWA will be available at:"
    echo "   http://localhost:3000"
    echo ""
    echo "📱 Features available:"
    echo "   ✅ Progressive Web App"
    echo "   ✅ Offline functionality"
    echo "   ✅ Installable"
    echo "   ✅ Service Worker"
    echo ""
    echo "🛑 Press Ctrl+C to stop the server"
    echo ""
    
    # Start local server
    npx serve dist -p 3000 -s
else
    echo "❌ Build failed!"
    exit 1
fi
