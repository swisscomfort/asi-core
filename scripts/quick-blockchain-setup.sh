#!/bin/bash

# 🚀 ASI-Core Blockchain Quick Setup Script
# Führt komplettes Setup mit Ihren API Keys durch

echo "🚀 ASI-Core Blockchain Quick Setup"
echo "===================================="

# Environment Check
echo "📋 Checking Environment Variables..."

if [ -z "$ALCHEMY_API_KEY" ]; then
    echo "❌ ALCHEMY_API_KEY fehlt!"
    echo "   Exportieren Sie: export ALCHEMY_API_KEY='your_key_here'"
    exit 1
fi

if [ -z "$PRIVATE_KEY" ]; then
    echo "❌ PRIVATE_KEY fehlt!"
    echo "   Exportieren Sie: export PRIVATE_KEY='your_private_key_without_0x'"
    exit 1
fi

echo "✅ Environment Variables OK"

# Update Config Files
echo "🔧 Updating Configuration Files..."

# Update secrets.json
cat > config/secrets.json << EOF
{
  "alchemy": {
    "api_key": "$ALCHEMY_API_KEY",
    "mumbai_url": "https://polygon-mumbai.g.alchemy.com/v2/$ALCHEMY_API_KEY"
  },
  "wallet": {
    "private_key": "$PRIVATE_KEY"
  },
  "polygonscan": {
    "api_key": "${POLYGONSCAN_API_KEY:-placeholder_polygonscan_api_key}"
  }
}
EOF

# Update web/.env
mkdir -p web
cat > web/.env << EOF
VITE_ALCHEMY_API_KEY=$ALCHEMY_API_KEY
VITE_POLYGON_RPC_URL=https://polygon-mumbai.g.alchemy.com/v2/$ALCHEMY_API_KEY
VITE_CHAIN_ID=80001
VITE_NETWORK_NAME=Mumbai
EOF

echo "✅ Configuration Files updated"

# Test Connection
echo "🔍 Testing Blockchain Connection..."

python3 << 'EOF'
import requests
import json
import os

api_key = os.environ.get('ALCHEMY_API_KEY')
rpc_url = f"https://polygon-mumbai.g.alchemy.com/v2/{api_key}"

try:
    response = requests.post(rpc_url, 
        headers={'Content-Type': 'application/json'},
        data=json.dumps({
            "jsonrpc": "2.0",
            "method": "eth_blockNumber",
            "params": [],
            "id": 1
        })
    )
    
    if response.status_code == 200:
        data = response.json()
        if 'result' in data:
            block_number = int(data['result'], 16)
            print(f"✅ Blockchain Connection SUCCESS!")
            print(f"📊 Current Block: {block_number:,}")
        else:
            print(f"❌ API Error: {data}")
    else:
        print(f"❌ HTTP Error: {response.status_code}")

except Exception as e:
    print(f"❌ Connection Error: {e}")
EOF

# Deploy Smart Contracts
echo "🔨 Deploying Smart Contracts..."

cd contracts

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Deploy contracts
echo "🚀 Deploying to Mumbai..."
npx hardhat run scripts/deploy.js --network mumbai

cd ..

echo "🎉 Setup Complete!"
echo ""
echo "📄 Configuration files updated:"
echo "   - config/secrets.json ✅"
echo "   - web/.env ✅"
echo ""
echo "🔧 Next steps:"
echo "   1. Test with: python3 scripts/test_blockchain_live.py"
echo "   2. Start Web UI: cd web && npm run dev"
echo "   3. Check PolygonScan for deployed contracts"
echo ""
echo "🎯 Your ASI-Core Blockchain is now LIVE!"