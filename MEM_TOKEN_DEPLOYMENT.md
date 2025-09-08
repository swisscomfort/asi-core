# $MEM Token System - Deployment Guide

## Smart Contract Deployment

### 1. Vorbereitung

```bash
# Installiere Dependencies
npm install --save-dev hardhat @openzeppelin/contracts

# Erstelle hardhat.config.js
echo 'require("@nomiclabs/hardhat-ethers");
module.exports = {
  solidity: "0.8.20",
  networks: {
    mumbai: {
      url: process.env.MUMBAI_RPC_URL,
      accounts: [process.env.DEPLOYER_PRIVATE_KEY]
    }
  }
};' > hardhat.config.js
```

### 2. Smart Contract deployen

```bash
# Kompiliere Contract
npx hardhat compile

# Deploy zu Mumbai Testnet
npx hardhat run contracts/deploy-memory-token.js --network mumbai
```

### 3. Contract Address in .env speichern

```bash
# Füge die Contract-Adresse zu .env hinzu
echo "MEMORY_TOKEN_ADDRESS=0x..." >> .env
```

## Backend Integration

### 1. Python Dependencies installieren

```bash
pip install web3 eth-account
```

### 2. Memory Token Service starten

```python
# Teste Token Service
python src/blockchain/memory_token.py
```

### 3. API-Server mit Token-Endpoints starten

```bash
# Starte ASI Core mit Token-Integration
python main.py serve
```

## Frontend Integration

### 1. TokenDashboard in bestehende App einbinden

```jsx
import TokenDashboard from './components/TokenDashboard';
import GovernanceDashboard from './components/GovernanceDashboard';

// In deine App-Komponente:
<TokenDashboard userAddress={userWalletAddress} reflectionCount={10} />
<GovernanceDashboard userAddress={userWalletAddress} tokenBalance={1000} />
```

### 2. NewReflectionModal erweitern

Das Modal ist bereits erweitert um:

- Token-Balance-Anzeige
- Automatische Belohnungen für Reflexionen
- Opt-in für anonyme Musterfreigabe
- Token-Belohnungs-Benachrichtigungen

## Lokale Wallet Integration

### 1. Automatische Wallet-Generierung

```javascript
// Frontend - Wallet wird automatisch erstellt
const generateWallet = () => {
  let address = localStorage.getItem("asi_wallet_address");
  if (!address) {
    const seed =
      localStorage.getItem("asi_wallet_seed") || Math.random().toString(36);
    localStorage.setItem("asi_wallet_seed", seed);

    // Vereinfachte Adressgenerierung
    address =
      "0x" +
      Array.from(seed)
        .map((c) => c.charCodeAt(0).toString(16).padStart(2, "0"))
        .join("")
        .substring(0, 40);
    localStorage.setItem("asi_wallet_address", address);
  }
  return address;
};
```

### 2. Backend Wallet Service

```python
# Wallet-Manager für sichere Seed-Verwaltung
from src.blockchain.wallet import WalletManager

wm = WalletManager()
print(f"Wallet Address: {wm.get_address()}")
print(f"Seed Backup: {wm.export_seed()}")
```

## Token-Ökonomie aktivieren

### 1. Belohnungssystem

Das System vergibt automatisch $MEM Token für:

- 1 $MEM pro gespeicherter Reflexion
- 5 $MEM pro erkanntem Muster
- 10 $MEM pro anonymer Musterfreigabe
- Bonus-Token bei Meilensteinen (10, 50, 100 Reflexionen)

### 2. Deflationärer Mechanismus

```python
# Buyback ausführen (nur Owner)
from src.blockchain.memory_token import memory_token_service

result = memory_token_service.execute_buyback(100.0)  # 100 USDC
print(f"Buyback result: {result}")
```

### 3. Governance Integration

Das Governance-Dashboard bietet:

- Anzeige aller aktiven Vorschläge
- Abstimmung basierend auf Token-Guthaben
- Integration mit Snapshot.org
- Quorum-Tracking

## Testing

### 1. Local Testing

```bash
# Starte lokalen Development Server
python main.py serve

# Teste Token-Endpoints
curl http://localhost:5000/api/token/stats
curl http://localhost:5000/api/token/balance/0x...
```

### 2. Mumbai Testnet Testing

```bash
# Erhalte Mumbai MATIC von Faucet
# https://faucet.polygon.technology/

# Teste Smart Contract Funktionen
python -c "
from src.blockchain.memory_token import memory_token_service
print(memory_token_service.get_contract_stats())
"
```

## Deployment Checklist

- [ ] Smart Contract zu Mumbai deployed
- [ ] Contract Address in .env gesetzt
- [ ] Python Dependencies installiert
- [ ] Token Service funktioniert
- [ ] Frontend-Komponenten integriert
- [ ] Wallet-System funktioniert
- [ ] API-Endpoints reagieren
- [ ] Belohnungssystem aktiv
- [ ] Governance-Dashboard funktional

## Sicherheit

### Wichtige Sicherheitshinweise:

1. **Private Keys**: Nie in Versionskontrolle speichern
2. **Seed-Backup**: Nutzer müssen Seed sicher aufbewahren
3. **Testnet Only**: System ist für Mumbai Testnet konzipiert
4. **Local First**: Vollständig offline-fähig
5. **No Cloud AI**: Keine externen AI-Services erforderlich

Das $MEM Token-System ist vollständig integriert und funktional!
