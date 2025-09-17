# ASI-Core Copilot Instructions

## System Overview
ASI-Core is a **hybrid AI reflection system** combining local privacy with decentralized storage. The architecture features dual Python entry points (`main.py` for legacy, `src/asi_core.py` for enhanced) and a Vite-based PWA frontend.

## Key Architectural Patterns

### Hybrid Model Architecture
- **Local**: `src/core/` (input, processing, output) for privacy-first operations
- **ASI Core**: `asi_core/` package with blockchain, state management, and agent integration
- **Web Frontend**: `web/` Vite+React PWA with offline capabilities
- **State Management**: `ASIStateManager` tracks user emotional/cognitive states (0-10 scale)

### Module Organization
```
asi_core/          # Core package (blockchain, agents, search)
src/ai/            # Embedding and semantic search
src/blockchain/    # Smart contracts and wallet integration
src/storage/       # Local DB, IPFS, Arweave clients
web/src/           # React PWA frontend
```

### Entry Points & Workflows
- **Development**: `python src/asi_core.py` (enhanced system with state management)
- **Legacy**: `python main.py` (Flask API for compatibility)
- **Web**: `cd web && npm run dev` (Vite dev server on port 5173)
- **Production**: `./start-pwa.sh` (builds and serves PWA)

## Development Conventions

### Python Patterns
- **ASI prefix**: All core classes use `ASI` prefix (`ASIBlockchainClient`, `ASIStateManager`)
- **Config pattern**: JSON configs in `config/` with example files (`.example.json`)
- **Error handling**: Custom exceptions like `ASIBlockchainError`
- **State management**: 0-10 integer states with auto-detection from text

### Frontend Architecture
- **PWA-first**: Offline-capable with service worker and manifest
- **Component structure**: Feature-based organization in `web/src/components/`
- **TypeScript**: Preferred for new components
- **Vite + React**: Modern build tooling with HMR

### Integration Points
- **Blockchain**: Polygon/Mumbai testnet with custom ASI smart contracts
- **Storage**: Three-tier (local SQLite → IPFS → Arweave for permanence)
- **AI**: Sentence transformers for embeddings, semantic search with similarity thresholds
- **Privacy**: K-anonymity (k≥5) with local anonymization before any external storage

## Key Configuration Files
- `config/settings.json`: Feature flags, storage paths, AI parameters
- `config/secrets.json`: API keys, blockchain private keys (gitignored)
- `web/vite.config.js`: PWA configuration, build settings
- `docker-compose.yml`: IPFS and PostgreSQL services

## Testing & Build Patterns
- **Python**: `pytest` for unit tests, configuration in `requirements.txt`
- **Frontend**: Vitest for testing, `npm run build` for production
- **Docker**: Multi-service setup with ASI core, IPFS, and database
- **Setup**: `./setup.sh` for initial configuration, environment generation

## Critical Commands
```bash
# Initial setup
./setup.sh

# Development (dual system)
python src/asi_core.py        # Enhanced ASI system
python main.py               # Legacy Flask API

# Frontend development
cd web && npm run dev        # Development server
./start-pwa.sh              # Production PWA build

# Docker deployment
docker-compose up -d         # Full stack with IPFS
```

## Integration Guidelines
- **State transitions**: Use `suggest_state_from_text()` for automatic state detection
- **Blockchain**: Check `features.blockchain_enabled` before web3 operations
- **Privacy**: Always anonymize before external storage (IPFS/Arweave)
- **Search**: Combine ASI semantic search with traditional local database queries
- **PWA**: Ensure offline functionality and proper caching strategies

## Important File Relationships
- `asi_core/__init__.py` exports all core classes for clean imports
- `main.py` integrates both legacy and ASI systems for backward compatibility
- `web/src/App.jsx` manages PWA installation and offline state
- `contracts/ASIStateTracker.sol` handles blockchain state persistence