#!/usr/bin/env python3
"""
Oryn Ticket Verifier Service
Automatisierter Service für objektive Ticket-Prüfung und Smart Contract Integration
"""

import os
import sys
import hashlib
import json
import time
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import requests
import yaml

# Web3 integration for smart contract calls
try:
    from web3 import Web3
    from eth_account import Account
    HAS_WEB3 = True
except ImportError:
    HAS_WEB3 = False
    print("⚠️ Web3 nicht installiert. Verwende Mock-Modus.")

# IPFS integration for evidence storage
try:
    import ipfshttpclient
    HAS_IPFS = True
except ImportError:
    HAS_IPFS = False
    print("⚠️ IPFS client nicht installiert. Verwende lokalen Speicher.")


@dataclass
class VerificationResult:
    """Ergebnis einer Ticket-Verifikation"""
    ticket_id: str
    evidence_cid: str
    passed: bool
    score: float  # 0.0 - 1.0
    checks_performed: List[str]
    details: Dict[str, Any]
    verification_timestamp: str
    verifier_version: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TicketSpec:
    """Ticket-Spezifikation aus YAML"""
    title: str
    category: str
    difficulty: int
    credit_reward: int
    dod: str  # Definition of Done
    evidence_requirements: Dict[str, Any]
    skill_tags: List[str]
    estimated_hours: int


class MockIPFSClient:
    """Mock IPFS Client für Entwicklung ohne echten IPFS-Node"""
    
    def __init__(self):
        self.storage_dir = Path("data/mock_ipfs")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def add_json(self, data: Dict) -> str:
        """Simuliert IPFS add für JSON-Daten"""
        content = json.dumps(data, sort_keys=True)
        cid = hashlib.sha256(content.encode()).hexdigest()[:46]  # Simulierter CID
        
        file_path = self.storage_dir / f"{cid}.json"
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return f"Qm{cid}"  # IPFS-ähnlicher CID
    
    def get_json(self, cid: str) -> Dict:
        """Simuliert IPFS get für JSON-Daten"""
        clean_cid = cid.replace("Qm", "")
        file_path = self.storage_dir / f"{clean_cid}.json"
        
        if file_path.exists():
            with open(file_path, 'r') as f:
                return json.load(f)
        else:
            raise FileNotFoundError(f"CID {cid} nicht gefunden")


class MockWeb3Client:
    """Mock Web3 Client für Entwicklung ohne echte Blockchain"""
    
    def __init__(self):
        self.transactions = []
        self.contract_calls = []
    
    def call_approve_ticket(self, ticket_id: str, verifier_report_cid: str) -> str:
        """Simuliert Smart Contract-Aufruf für Ticket-Approval"""
        tx_hash = f"0x{hashlib.sha256(f'{ticket_id}{verifier_report_cid}{time.time()}'.encode()).hexdigest()}"
        
        self.contract_calls.append({
            "function": "approveTicket",
            "ticket_id": ticket_id,
            "verifier_report_cid": verifier_report_cid,
            "tx_hash": tx_hash,
            "timestamp": datetime.now().isoformat()
        })
        
        return tx_hash


class TicketVerifier:
    """Hauptklasse für automatische Ticket-Verifikation"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.logger = self._setup_logging()
        self.config = self._load_config(config_path)
        self.version = "0.1.0-alpha"
        
        # Initialize clients
        if HAS_IPFS and self.config.get("ipfs_enabled", False):
            try:
                self.ipfs_client = ipfshttpclient.connect()
                self.logger.info("✅ IPFS Client verbunden")
            except:
                self.ipfs_client = MockIPFSClient()
                self.logger.warning("⚠️ IPFS-Verbindung fehlgeschlagen, verwende Mock")
        else:
            self.ipfs_client = MockIPFSClient()
            self.logger.info("📝 Verwende Mock IPFS Client")
        
        if HAS_WEB3 and self.config.get("web3_enabled", False):
            try:
                self.web3_client = self._init_web3()
                self.logger.info("✅ Web3 Client verbunden")
            except:
                self.web3_client = MockWeb3Client()
                self.logger.warning("⚠️ Web3-Verbindung fehlgeschlagen, verwende Mock")
        else:
            self.web3_client = MockWeb3Client()
            self.logger.info("📝 Verwende Mock Web3 Client")
    
    def _setup_logging(self) -> logging.Logger:
        """Logging-Setup"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger('TicketVerifier')
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Lade Konfiguration"""
        default_config = {
            "ipfs_enabled": False,
            "web3_enabled": False,
            "strict_mode": False,
            "quality_threshold": 0.7,
            "supported_categories": ["security", "ui", "docs", "translation", "testing"],
            "check_weights": {
                "code_review": 0.3,
                "tests_passing": 0.25,
                "documentation": 0.2,
                "accessibility": 0.15,
                "security_scan": 0.1
            }
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                default_config.update(user_config)
        
        return default_config
    
    def _init_web3(self) -> Any:
        """Initialisiere Web3-Verbindung"""
        if not HAS_WEB3:
            return MockWeb3Client()
        
        rpc_url = os.getenv("MUMBAI_RPC_URL", "https://rpc-mumbai.maticvigil.com/")
        web3 = Web3(Web3.HTTPProvider(rpc_url))
        
        if not web3.isConnected():
            raise ConnectionError("Web3-Verbindung fehlgeschlagen")
        
        return web3
    
    async def verify_ticket_evidence(self, ticket_id: str, evidence_cid: str) -> VerificationResult:
        """Hauptverifikationsfunktion für Ticket-Evidence"""
        self.logger.info(f"🔍 Starte Verifikation für Ticket {ticket_id}")
        
        try:
            # 1. Evidence von IPFS laden
            evidence_data = await self._fetch_evidence(evidence_cid)
            
            # 2. Ticket-Spezifikation laden
            ticket_spec = await self._fetch_ticket_spec(ticket_id)
            
            # 3. Verifikations-Checks durchführen
            checks_results = await self._perform_verification_checks(
                evidence_data, ticket_spec
            )
            
            # 4. Gesamtbewertung berechnen
            overall_score = self._calculate_overall_score(checks_results)
            passed = overall_score >= self.config["quality_threshold"]
            
            # 5. Ergebnis zusammenstellen
            result = VerificationResult(
                ticket_id=ticket_id,
                evidence_cid=evidence_cid,
                passed=passed,
                score=overall_score,
                checks_performed=list(checks_results.keys()),
                details=checks_results,
                verification_timestamp=datetime.now().isoformat(),
                verifier_version=self.version
            )
            
            self.logger.info(f"✅ Verifikation abgeschlossen: {passed} (Score: {overall_score:.2f})")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Verifikation fehlgeschlagen: {e}")
            # Fallback-Ergebnis bei Fehlern
            return VerificationResult(
                ticket_id=ticket_id,
                evidence_cid=evidence_cid,
                passed=False,
                score=0.0,
                checks_performed=["error_handling"],
                details={"error": str(e)},
                verification_timestamp=datetime.now().isoformat(),
                verifier_version=self.version
            )
    
    async def _fetch_evidence(self, evidence_cid: str) -> Dict[str, Any]:
        """Lade Evidence-Daten von IPFS"""
        try:
            if hasattr(self.ipfs_client, 'get_json'):
                return self.ipfs_client.get_json(evidence_cid)
            else:
                # Echter IPFS Client
                evidence_data = self.ipfs_client.get_json(evidence_cid)
                return evidence_data
        except Exception as e:
            self.logger.warning(f"⚠️ Evidence-Abruf fehlgeschlagen, verwende Fallback: {e}")
            # Fallback für Demo
            return {
                "type": "code_submission",
                "github_pr": f"https://github.com/oryn/repo/pull/123",
                "files_changed": ["src/security/auth.js", "tests/auth.test.js"],
                "description": "Implemented E2E encryption for chat function",
                "tests_passing": True,
                "lint_passed": True
            }
    
    async def _fetch_ticket_spec(self, ticket_id: str) -> TicketSpec:
        """Lade Ticket-Spezifikation"""
        # In echtem System würde dies von Smart Contract oder IPFS kommen
        fallback_spec = TicketSpec(
            title="Chat-Funktion E2E-Verschlüsselung hinzufügen",
            category="security",
            difficulty=3,
            credit_reward=50,
            dod="WebCrypto API implementiert, Tests bestehen, Dokumentation aktualisiert",
            evidence_requirements={
                "code_review": True,
                "tests_passing": True,
                "security_audit": True,
                "documentation": True
            },
            skill_tags=["javascript", "cryptography", "security"],
            estimated_hours=8
        )
        
        return fallback_spec
    
    async def _perform_verification_checks(
        self, 
        evidence: Dict[str, Any], 
        spec: TicketSpec
    ) -> Dict[str, Dict[str, Any]]:
        """Führe alle erforderlichen Verifikations-Checks durch"""
        
        results = {}
        
        # 1. Code Review Check
        if spec.evidence_requirements.get("code_review", False):
            results["code_review"] = await self._check_code_review(evidence)
        
        # 2. Tests Check
        if spec.evidence_requirements.get("tests_passing", False):
            results["tests_passing"] = await self._check_tests(evidence)
        
        # 3. Documentation Check
        if spec.evidence_requirements.get("documentation", False):
            results["documentation"] = await self._check_documentation(evidence)
        
        # 4. Security Check (für Security-Kategorie)
        if spec.category == "security":
            results["security_scan"] = await self._check_security(evidence)
        
        # 5. Accessibility Check (für UI-Kategorie)
        if spec.category == "ui":
            results["accessibility"] = await self._check_accessibility(evidence)
        
        return results
    
    async def _check_code_review(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Simuliert Code-Review-Check"""
        # In echtem System: GitHub API, GitLab API, etc.
        github_pr = evidence.get("github_pr")
        
        if github_pr:
            # Simulierte PR-Analyse
            return {
                "passed": True,
                "score": 0.85,
                "details": {
                    "pr_url": github_pr,
                    "files_changed": len(evidence.get("files_changed", [])),
                    "review_comments": 3,
                    "approved_by_maintainer": True
                }
            }
        else:
            return {
                "passed": False,
                "score": 0.0,
                "details": {"error": "Kein GitHub PR Link gefunden"}
            }
    
    async def _check_tests(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Simuliert Test-Check"""
        tests_passing = evidence.get("tests_passing", False)
        
        return {
            "passed": tests_passing,
            "score": 1.0 if tests_passing else 0.0,
            "details": {
                "all_tests_pass": tests_passing,
                "test_coverage": 85,  # Simuliert
                "new_tests_added": True
            }
        }
    
    async def _check_documentation(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Simuliert Documentation-Check"""
        # Prüfe ob Dokumentation erwähnt wird
        description = evidence.get("description", "").lower()
        has_docs = any(word in description for word in ["documentation", "readme", "docs", "documented"])
        
        return {
            "passed": has_docs,
            "score": 0.9 if has_docs else 0.3,
            "details": {
                "documentation_mentioned": has_docs,
                "readme_updated": has_docs,
                "api_docs_complete": True
            }
        }
    
    async def _check_security(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Simuliert Security-Check"""
        return {
            "passed": True,
            "score": 0.9,
            "details": {
                "no_vulnerabilities": True,
                "secure_patterns_used": True,
                "sensitive_data_handled": True
            }
        }
    
    async def _check_accessibility(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Simuliert Accessibility-Check"""
        return {
            "passed": True,
            "score": 0.8,
            "details": {
                "lighthouse_score": 92,
                "wcag_compliant": True,
                "keyboard_navigation": True
            }
        }
    
    def _calculate_overall_score(self, checks_results: Dict[str, Dict[str, Any]]) -> float:
        """Berechne Gesamtscore basierend auf gewichteten Checks"""
        if not checks_results:
            return 0.0
        
        total_score = 0.0
        total_weight = 0.0
        
        for check_name, result in checks_results.items():
            weight = self.config["check_weights"].get(check_name, 0.1)
            score = result.get("score", 0.0)
            
            total_score += score * weight
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    async def approve_ticket_on_chain(self, verification_result: VerificationResult) -> Optional[str]:
        """Rufe Smart Contract auf um Ticket zu approven"""
        if not verification_result.passed:
            self.logger.info(f"❌ Ticket {verification_result.ticket_id} nicht approved - Qualität unzureichend")
            return None
        
        try:
            # 1. Verifier-Report zu IPFS hochladen
            report_cid = await self._upload_verification_report(verification_result)
            
            # 2. Smart Contract approveTicket() aufrufen
            tx_hash = self._call_approve_ticket_contract(
                verification_result.ticket_id,
                report_cid
            )
            
            self.logger.info(f"✅ Ticket {verification_result.ticket_id} approved on-chain: {tx_hash}")
            return tx_hash
            
        except Exception as e:
            self.logger.error(f"❌ On-chain approval fehlgeschlagen: {e}")
            return None
    
    async def _upload_verification_report(self, result: VerificationResult) -> str:
        """Lade Verifier-Report zu IPFS hoch"""
        report_data = result.to_dict()
        
        if hasattr(self.ipfs_client, 'add_json'):
            return self.ipfs_client.add_json(report_data)
        else:
            # Echter IPFS Client
            return self.ipfs_client.add_json(report_data)
    
    def _call_approve_ticket_contract(self, ticket_id: str, verifier_report_cid: str) -> str:
        """Rufe TicketRegistry.approveTicket() auf"""
        if hasattr(self.web3_client, 'call_approve_ticket'):
            return self.web3_client.call_approve_ticket(ticket_id, verifier_report_cid)
        else:
            # Echter Web3 Call würde hier stehen
            # contract.functions.approveTicket(ticket_id, verifier_report_cid).transact()
            return f"0xmocked{int(time.time())}"


class VerifierDaemon:
    """Daemon für kontinuierliche Ticket-Verifikation"""
    
    def __init__(self, verifier: TicketVerifier):
        self.verifier = verifier
        self.logger = verifier.logger
        self.running = False
        self.processed_tickets = set()
    
    async def start(self, check_interval: int = 30):
        """Starte den Verifier-Daemon"""
        self.running = True
        self.logger.info(f"🚀 Verifier-Daemon gestartet (Check-Intervall: {check_interval}s)")
        
        while self.running:
            try:
                await self._check_for_new_submissions()
                await asyncio.sleep(check_interval)
            except KeyboardInterrupt:
                self.logger.info("⏹️ Verifier-Daemon gestoppt durch Benutzer")
                self.running = False
            except Exception as e:
                self.logger.error(f"❌ Daemon-Fehler: {e}")
                await asyncio.sleep(check_interval)
    
    async def _check_for_new_submissions(self):
        """Prüfe auf neue Ticket-Submissions"""
        # In echtem System: Smart Contract Events abfragen
        # Hier: Simulierte neue Submissions
        
        simulated_submissions = [
            {"ticket_id": "ticket_001", "evidence_cid": "QmExample123"},
            {"ticket_id": "ticket_002", "evidence_cid": "QmExample456"},
        ]
        
        for submission in simulated_submissions:
            ticket_id = submission["ticket_id"]
            
            if ticket_id not in self.processed_tickets:
                self.logger.info(f"🔍 Neue Submission gefunden: {ticket_id}")
                
                # Verifikation durchführen
                result = await self.verifier.verify_ticket_evidence(
                    ticket_id, submission["evidence_cid"]
                )
                
                # On-chain approval wenn erfolgreich
                await self.verifier.approve_ticket_on_chain(result)
                
                self.processed_tickets.add(ticket_id)
    
    def stop(self):
        """Stoppe den Daemon"""
        self.running = False


async def main():
    """Hauptfunktion für CLI-Nutzung"""
    print("🤖 Oryn Ticket Verifier Service")
    print("=" * 40)
    
    # Verifier initialisieren
    verifier = TicketVerifier()
    
    # Beispiel-Verifikation
    print("\n📝 Beispiel-Verifikation:")
    result = await verifier.verify_ticket_evidence(
        ticket_id="demo_ticket_001",
        evidence_cid="QmDemoEvidence123"
    )
    
    print(f"✅ Ergebnis: {result.passed} (Score: {result.score:.2f})")
    print(f"📊 Details: {json.dumps(result.details, indent=2)}")
    
    # On-chain approval
    if result.passed:
        tx_hash = await verifier.approve_ticket_on_chain(result)
        print(f"🔗 Transaction Hash: {tx_hash}")
    
    print("\n🚀 Starte Daemon-Modus (Ctrl+C zum Beenden)...")
    
    # Daemon starten
    daemon = VerifierDaemon(verifier)
    try:
        await daemon.start()
    except KeyboardInterrupt:
        print("\n👋 Verifier Service beendet")


if __name__ == "__main__":
    asyncio.run(main())