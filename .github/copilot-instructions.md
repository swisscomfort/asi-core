# ASI-Core Copilot Instructions

## System Overview
ASI-Core is a **hybrid AI reflection system** combining local privacy with decentralized storage. The architecture features dual Python entry points (`main.py` for legacy, `src/asi_core.py` for enhanced) and a Vite-based PWA frontend designed for lifelong personal memory storage.

## Critical Architecture Patterns

### Dual Entry Points
- **Enhanced**: `python src/asi_core.py` (modern ASI system with state management)
- **Legacy**: `python main.py` (Flask API integration, 1000+ lines with backward compatibility)
- **Hybrid Integration**: Both systems share core `asi_core/` package but serve different purposes

### Module Organization (Key Distinction)
```
asi_core/          # Core package: blockchain, search, state_management, agent_manager
src/asi_core/      # Enhanced entry point with ASICore class
src/ai/hrm/        # High-Level Reasoning Module (pattern recognition, planning)
src/blockchain/    # Smart contracts, wallet integration, memory tokens
src/storage/       # Multi-tier: SQLite → IPFS → Arweave
web/src/           # React PWA with offline-first architecture
```

### State Management Architecture (0-255 Scale)
- **State Manager**: `ASIStateManager` tracks emotional/cognitive states with 255-value precision
- **Auto-detection**: `suggest_state_from_text()` analyzes content for automatic state assignment
- **State Categories**: Emotional (0-99), Cognitive (100-149), Social (150-199), Special (200-255)
- **Integration**: Both entry points use same state system via `asi_core.state_management`

## Development Conventions

### ASI Naming Pattern
**CRITICAL**: All core classes use `ASI` prefix:
- `ASIStateManager`, `ASIBlockchainClient`, `ASIEmbeddingGenerator`, `ASISemanticSearch`
- Custom exceptions: `ASIStateError`, `ASIBlockchainError`
- Functions: `suggest_state_from_text()`, `create_blockchain_client_from_config()`

### Configuration Architecture
- **Feature flags**: `config/settings.json` controls blockchain_enabled, ipfs_enabled, hrm_enabled
- **Secrets**: `config/secrets.json` (gitignored) for API keys, private keys
- **Example pattern**: All configs have `.example.json` templates for setup

### Error Handling Patterns
```python
class ASIStateError(Exception):
    """Custom Exception für State Management Operationen"""
    pass

# Usage in methods
def create_state_reflection(self, reflection_text: str, state_value: int):
    if not self.validate_state(state_value):
        raise ASIStateError(f"Ungültiger Zustandswert: {state_value}")
```

### HRM (High-Level Reasoning Module)
- **Pattern Recognition**: `src/ai/hrm/high_level/pattern_recognition.py` analyzes temporal/thematic patterns
- **Planning**: `src/ai/hrm/high_level/planner.py` derives goals from recognized patterns
- **Fallback Logic**: When no historical data exists, generates baseline patterns from current content

## Critical Workflows

### Development Setup
```bash
# Initial setup (creates configs, directories, dependencies)
./setup.sh

# Development modes
python src/asi_core.py              # Enhanced system with full feature set
python main.py                      # Legacy Flask API (1000+ lines)

# Web development
cd web && npm run dev               # Vite dev server (port 5173)
./start-pwa.sh                      # Production PWA build + serve
```

### State Management Integration
```python
# Automatic state detection pattern
from asi_core.state_management import ASIStateManager, suggest_state_from_text

state_manager = ASIStateManager()
suggested_state = suggest_state_from_text("Feeling focused today")  # Returns integer 0-255
reflection = state_manager.create_state_reflection(text, suggested_state, tags)
```

### Blockchain Integration Pattern
```python
# Feature-flag controlled integration
if self.config.get("features", {}).get("blockchain_enabled", False):
    self.blockchain_client = create_blockchain_client_from_config(config)
    # Proceed with blockchain operations
```

## Privacy & Storage Architecture

### Three-Tier Storage Pattern
1. **Local**: SQLite database (`data/asi_local.db`) for immediate access
2. **IPFS**: Distributed storage for sharing (feature-flag controlled)
3. **Arweave**: Permanent archival storage (long-term persistence)

### Anonymization Requirements
- **K-anonymity**: Minimum k≥5 before external storage
- **No personal data**: Content anonymized before IPFS/Arweave upload
- **Local encryption**: Sensitive data encrypted in local storage

## PWA Frontend Patterns

### Offline-First Architecture
- **Service Worker**: `sw.js` and `workbox` for caching strategies
- **PWA Manifest**: `manifest.json` for installability
- **IndexedDB**: Local storage via `idb` library for offline functionality

### Component Organization
- **Feature-based**: Components organized by functionality, not type
- **TypeScript preferred**: New components should use `.tsx` extension
- **Tailwind CSS**: Utility-first styling throughout frontend

## Integration Points & Dependencies

### Blockchain Smart Contracts
- **ASI State Tracker**: `contracts/ASIStateTracker.sol` stores anonymized state data
- **Memory Tokens**: `contracts/MemoryToken.sol` for reflection ownership
- **Polygon/Mumbai**: Testnet deployment for development

### External Service Integration
- **IPFS**: `docker-compose.yml` includes local IPFS node (port 5001)
- **PostgreSQL**: Optional database backend for enhanced storage
- **Embedding Models**: Sentence transformers for semantic search

## Key Files to Understanding System
- `asi_core/__init__.py`: Clean exports of all core classes
- `src/asi_core.py`: Enhanced system entry point with `ASICore` class
- `main.py`: Legacy integration with Flask API and backward compatibility
- `config/settings.json`: Master feature configuration
- `web/vite.config.js`: PWA build configuration and service worker setup

## Testing Patterns
- **Python**: `pytest` with tests in `tests/` directory
- **Frontend**: Vitest for component testing
- **Integration**: Docker compose for full stack testing