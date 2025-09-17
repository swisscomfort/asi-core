# ASI Core – Distributed Task System Architecture

## 🎯 Vision in einem Satz

Viele kleine, klar definierte Arbeitsblätter/Tasks werden on-chain registriert, von Freiwilligen geclaimt, geliefert und durch einen prüfbaren Verifier-Prozess bestätigt; der Smart Contract zahlt automatisch aus, vergibt Reputation und schaltet die nächsten Aufgaben frei. So wächst das System modulweise – von 1–10 Leuten bis Millionen.

## 🧩 System-Komponenten

### 1. Off-Chain (Developer & Human-Friendly)
```
/tasks/
  M0/          # Foundation Milestone  
    M0-T001.yaml  # Individual task sheet
    M0-T002.yaml
  M1/          # PWA MVP Milestone
    M1-T001.yaml
    ...
/evidence/     # IPFS-pinned deliverables
/scripts/      # Python automation tools
```

### 2. On-Chain (Automated Rules Engine)
```solidity
TaskRegistry     // Task lifecycle: create/claim/submit/approve/payout
RewardVault      // Token management & automatic payouts  
MilestoneOrchestrator // Unlocks next task waves when dependencies complete
ContributorSBT   // Non-transferable reputation badges
```

### 3. Verifier Service (Bridge)
```python
verifier_service.py  // Reads PR/CI status, validates DoD, signs reports
```

## 🔄 Task Lifecycle (7 Steps)

1. **Create**: Maintainer → pushes `tasks/M1/M1-T004.yaml` → pins CID to IPFS → calls `createTask()`
2. **Claim**: Contributor → calls `claimTask("M1-T004")` (locks for X days)  
3. **Deliver**: Creates PR → tests green → artifacts to IPFS → calls `submitTask(taskId, evidenceCID)`
4. **Verify**: Auto-verifier → reads PR/CI → validates DoD → creates `verifierReport.json` → signs → pins to IPFS
5. **Approve**: Verifier → calls `approveTask(taskId, reportCID)`
6. **Payout**: Contributor → calls `payout(taskId)` → RewardVault sends bounty + mints SBT badge
7. **Scale**: Orchestrator → sees all M1 tasks "Approved" → calls `unlockNext(M2)`

## 📜 Task Sheet Standard

```yaml
task_id: "M1-T004"
title: "Minimal P2P Chat (UI + send/receive)"
bounty: 
  token: "ASI"
  amount: 2500
deadline: "2025-10-20"
dependencies: ["M1-T001", "M1-T003"]
deliverables:
  - "PR with Chat UI (send/receive), libp2p/Matrix bridge"
  - "README: Start instructions, key generation, local test"
definition_of_done:
  - "CI: build+unit+e2e green"
  - "Manual test: 2 browser tabs can chat locally"
  - "Lighthouse PWA >= 90"
evidence:
  - "ipfs://"  # Will be filled by contributor
  - "ipfs://"
reviewers: ["0xReviewerA...", "0xReviewerB..."]
license: "AGPL-3.0"
notes: "UX simple, focus on function"
```

## 🧠 Smart Contracts (Minimal Interfaces)

### TaskRegistry.sol
```solidity
function createTask(string taskId, bytes32 taskSheetCID, address token, uint256 amount, address vault)
function claimTask(string taskId) // locks task for claimTimeout
function submitTask(string taskId, bytes32 evidenceCID)  
function approveTask(string taskId, bytes32 reportCID) // onlyVerifier
function payout(string taskId) // triggers vault transfer + SBT mint

Events: TaskCreated/Claimed/Submitted/Approved/Paid
```

### RewardVault.sol
```solidity
function payout(address token, address to, uint256 amount) // onlyRegistry
```

### MilestoneOrchestrator.sol  
```solidity
function activateMilestone(uint256 milestone) // when all tasks approved
function unlockNext(uint256 nextMilestone)
```

### ContributorSBT.sol
```solidity
function mintTaskCompletion(address contributor, string taskId) // onlyRegistry
```

## 🛡️ Security & Fairness

- **Role-based access**: Only verifier can approve, only registry can trigger payouts
- **Timeouts**: Claimed tasks auto-release after deadline
- **Dispute mechanism**: Contributor can challenge → DAO snapshot vote → binding decision
- **Anti-spam**: Optional small collateral on claim (returned on submission)
- **Transparency**: All reports and evidence on IPFS with content hashes

## 📈 Growth Mechanics

### $10 Micro-Funding
- Small donations flow to RewardVault
- Maintainers create micro-tasks (1-4h work)
- Every donation = immediately visible task activation

### Viral Referral System
- Optional referral tag in task sheets
- Successful completion = 2-5% bonus to referrer  
- Community recruits community organically

### SBT Reputation Cascade
- More completed tasks = higher trust level
- Higher trust = bigger tasks, less collateral required
- Gamified progression encourages continued participation

## 🧪 MVP Demo Flow (10 Minutes)

1. **Deploy** (Polygon testnet): RewardVault → TaskRegistry → ContributorSBT → MilestoneOrchestrator
2. **Fund**: Add test tokens to RewardVault
3. **Create**: YAML → IPFS → `createTask("M1-T001", cid, ASI, 1500, vault)`
4. **Work**: Contributor claims → builds PR → CI green → artifacts to IPFS → submits
5. **Verify**: Auto-verifier validates DoD → signs report → approves on-chain
6. **Complete**: Contributor gets payout → SBT badge → milestone potentially unlocks

Result: Transparent, automated, trustless task completion with built-in growth mechanics.

## 🚀 Why This Changes Everything

- **No gatekeeping**: Rules in task sheet, verification is technical not political
- **Exponential scaling**: More contributors = more parallel tasks = faster milestone unlocks  
- **Unstoppable**: Fork-resistant, no single point of failure
- **Economically aligned**: Contributors earn immediately, maintainers get results
- **Reputation-based**: SBT system creates long-term incentives for quality work

This architecture transforms ASI Core from a project into a **self-reinforcing movement** where every contribution strengthens the whole system.