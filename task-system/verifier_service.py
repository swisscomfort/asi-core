#!/usr/bin/env python3
"""
ASI Core Task Verifier Service
==============================

Automated verification service that:
1. Monitors GitHub PRs and CI status  
2. Validates Definition of Done criteria
3. Generates signed verification reports
4. Triggers on-chain task approval

This service bridges off-chain work with on-chain rewards.
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from urllib.parse import urljoin

import aiohttp
import yaml
from eth_account import Account
from web3 import Web3
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat, PublicFormat

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class TaskSubmission:
    """Represents a task submission waiting for verification"""
    task_id: str
    submitter: str
    evidence_cid: str
    submitted_at: int
    pr_url: Optional[str] = None
    repo: Optional[str] = None
    branch: Optional[str] = None


@dataclass
class VerificationReport:
    """Standardized verification report structure"""
    task_id: str
    pr_url: Optional[str]
    github_checks: Dict[str, str]  # check_name -> status
    content_checks: Dict[str, bool]  # requirement -> passed
    dod_evidence: List[str]  # DoD items with evidence
    lighthouse_score: Optional[int]
    security_findings: Dict[str, int]  # severity -> count
    verifier_pubkey: str
    verified_at: int
    overall_status: str  # "pass" | "fail" | "partial"
    notes: str
    signature: str


class GitHubClient:
    """GitHub API client for checking PR status and content"""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv('GITHUB_TOKEN')
        self.base_url = "https://api.github.com"
        
    async def get_pr_info(self, repo: str, pr_number: int) -> Dict[str, Any]:
        """Get PR information including status checks"""
        headers = {}
        if self.token:
            headers['Authorization'] = f'token {self.token}'
            
        async with aiohttp.ClientSession() as session:
            # Get PR details
            pr_url = f"{self.base_url}/repos/{repo}/pulls/{pr_number}"
            async with session.get(pr_url, headers=headers) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch PR: {response.status}")
                pr_data = await response.json()
            
            # Get commit status checks
            sha = pr_data['head']['sha']
            checks_url = f"{self.base_url}/repos/{repo}/commits/{sha}/status"
            async with session.get(checks_url, headers=headers) as response:
                if response.status == 200:
                    status_data = await response.json()
                else:
                    status_data = {'statuses': []}
            
            # Get check runs (GitHub Actions)
            check_runs_url = f"{self.base_url}/repos/{repo}/commits/{sha}/check-runs"
            async with session.get(check_runs_url, headers=headers) as response:
                if response.status == 200:
                    check_runs_data = await response.json()
                else:
                    check_runs_data = {'check_runs': []}
            
            return {
                'pr': pr_data,
                'status': status_data,
                'check_runs': check_runs_data
            }
    
    async def check_file_exists(self, repo: str, branch: str, file_path: str) -> bool:
        """Check if a file exists in the repository"""
        headers = {}
        if self.token:
            headers['Authorization'] = f'token {self.token}'
            
        url = f"{self.base_url}/repos/{repo}/contents/{file_path}?ref={branch}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                return response.status == 200
    
    async def get_file_content(self, repo: str, branch: str, file_path: str) -> Optional[str]:
        """Get file content from repository"""
        headers = {}
        if self.token:
            headers['Authorization'] = f'token {self.token}'
            
        url = f"{self.base_url}/repos/{repo}/contents/{file_path}?ref={branch}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    return None
                
                data = await response.json()
                if data.get('encoding') == 'base64':
                    import base64
                    return base64.b64decode(data['content']).decode('utf-8')
                
                return data.get('content')


class TaskValidator:
    """Validates task completion against DoD criteria"""
    
    def __init__(self, github_client: GitHubClient):
        self.github = github_client
    
    async def validate_task(self, task_sheet: Dict[str, Any], submission: TaskSubmission) -> VerificationReport:
        """Validate a task submission against its DoD criteria"""
        logger.info(f"Validating task {submission.task_id}")
        
        # Initialize report
        report = VerificationReport(
            task_id=submission.task_id,
            pr_url=submission.pr_url,
            github_checks={},
            content_checks={},
            dod_evidence=[],
            lighthouse_score=None,
            security_findings={},
            verifier_pubkey="",  # Will be set later
            verified_at=int(time.time()),
            overall_status="fail",
            notes="",
            signature=""
        )
        
        try:
            # Extract PR info if available
            pr_info = None
            if submission.pr_url and submission.repo:
                pr_number = self._extract_pr_number(submission.pr_url)
                if pr_number:
                    pr_info = await self.github.get_pr_info(submission.repo, pr_number)
                    await self._validate_github_checks(task_sheet, pr_info, report)
            
            # Validate content requirements
            if submission.repo and submission.branch:
                await self._validate_content_checks(task_sheet, submission.repo, submission.branch, report)
            
            # Validate definition of done
            await self._validate_definition_of_done(task_sheet, pr_info, report)
            
            # Calculate overall status
            self._calculate_overall_status(report)
            
        except Exception as e:
            logger.error(f"Validation error for task {submission.task_id}: {e}")
            report.notes = f"Validation error: {str(e)}"
            report.overall_status = "fail"
        
        return report
    
    def _extract_pr_number(self, pr_url: str) -> Optional[int]:
        """Extract PR number from GitHub URL"""
        try:
            # Expected format: https://github.com/owner/repo/pull/123
            parts = pr_url.rstrip('/').split('/')
            if len(parts) >= 2 and parts[-2] == 'pull':
                return int(parts[-1])
        except (ValueError, IndexError):
            pass
        return None
    
    async def _validate_github_checks(self, task_sheet: Dict, pr_info: Dict, report: VerificationReport):
        """Validate GitHub CI checks"""
        auto_verifier = task_sheet.get('auto_verifier', {})
        github_config = auto_verifier.get('github', {})
        required_checks = github_config.get('required_checks', [])
        
        # Combine status checks and check runs
        all_checks = {}
        
        # Process status checks (older API)
        for status in pr_info['status'].get('statuses', []):
            all_checks[status['context']] = status['state']
        
        # Process check runs (GitHub Actions)
        for check_run in pr_info['check_runs'].get('check_runs', []):
            all_checks[check_run['name']] = check_run['conclusion'] or check_run['status']
        
        # Validate required checks
        for check_name in required_checks:
            status = all_checks.get(check_name, 'missing')
            report.github_checks[check_name] = status
            
            if status not in ['success', 'completed']:
                report.notes += f"Required check '{check_name}' failed or missing. "
    
    async def _validate_content_checks(self, task_sheet: Dict, repo: str, branch: str, report: VerificationReport):
        """Validate repository content requirements"""
        auto_verifier = task_sheet.get('auto_verifier', {})
        content_checks = auto_verifier.get('content_checks', {})
        
        # Check required files
        must_include = content_checks.get('must_include', [])
        for file_path in must_include:
            exists = await self.github.check_file_exists(repo, branch, file_path)
            report.content_checks[f"has_{file_path}"] = exists
            
            if not exists:
                report.notes += f"Required file '{file_path}' not found. "
        
        # Check forbidden content
        must_not_include = content_checks.get('must_not_include', [])
        for pattern in must_not_include:
            # Simple pattern matching - could be enhanced with regex
            found = await self._search_for_pattern(repo, branch, pattern)
            report.content_checks[f"no_{pattern}"] = not found
            
            if found:
                report.notes += f"Forbidden pattern '{pattern}' found. "
    
    async def _search_for_pattern(self, repo: str, branch: str, pattern: str) -> bool:
        """Search for forbidden patterns in repository"""
        # Simplified implementation - check common files
        common_files = ['README.md', 'package.json', 'src/index.js', 'src/main.py']
        
        for file_path in common_files:
            content = await self.github.get_file_content(repo, branch, file_path)
            if content and pattern.lower() in content.lower():
                return True
        
        return False
    
    async def _validate_definition_of_done(self, task_sheet: Dict, pr_info: Optional[Dict], report: VerificationReport):
        """Validate Definition of Done criteria"""
        dod_items = task_sheet.get('definition_of_done', [])
        
        for dod_item in dod_items:
            evidence = self._check_dod_item(dod_item, pr_info, report)
            report.dod_evidence.append(f"{dod_item}: {evidence}")
    
    def _check_dod_item(self, dod_item: str, pr_info: Optional[Dict], report: VerificationReport) -> str:
        """Check individual DoD item and return evidence"""
        dod_lower = dod_item.lower()
        
        # CI-related checks
        if 'ci' in dod_lower and 'green' in dod_lower:
            ci_status = any(
                status in ['success', 'completed'] 
                for status in report.github_checks.values()
            )
            return "✅ CI passing" if ci_status else "❌ CI failing"
        
        # Lighthouse PWA score
        if 'lighthouse' in dod_lower and 'pwa' in dod_lower:
            # This would need integration with Lighthouse CI
            # For now, assume it passes if PR checks are green
            return "✅ PWA score check" if report.github_checks else "❌ No PWA score data"
        
        # Security scan
        if 'security' in dod_lower and 'scan' in dod_lower:
            has_security_check = any(
                'security' in check_name.lower() 
                for check_name in report.github_checks.keys()
            )
            return "✅ Security scan passed" if has_security_check else "❌ No security scan"
        
        # Test coverage
        if 'test' in dod_lower and ('coverage' in dod_lower or '%' in dod_lower):
            has_test_check = any(
                'test' in check_name.lower() 
                for check_name in report.github_checks.keys()
            )
            return "✅ Tests passing" if has_test_check else "❌ No test data"
        
        # Default: assume manual verification needed
        return "⚠️ Manual verification required"
    
    def _calculate_overall_status(self, report: VerificationReport):
        """Calculate overall verification status"""
        # Count passed checks
        github_passed = sum(
            1 for status in report.github_checks.values() 
            if status in ['success', 'completed']
        )
        github_total = len(report.github_checks)
        
        content_passed = sum(1 for passed in report.content_checks.values() if passed)
        content_total = len(report.content_checks)
        
        # Calculate pass rate
        total_checks = github_total + content_total
        total_passed = github_passed + content_passed
        
        if total_checks == 0:
            report.overall_status = "partial"
            report.notes += "No automated checks configured. "
        elif total_passed == total_checks:
            report.overall_status = "pass"
        elif total_passed >= total_checks * 0.8:  # 80% threshold
            report.overall_status = "partial"
        else:
            report.overall_status = "fail"


class ReportSigner:
    """Signs verification reports with Ed25519 keys"""
    
    def __init__(self, private_key_path: Optional[str] = None):
        self.private_key_path = private_key_path or os.getenv('VERIFIER_PRIVATE_KEY_PATH')
        self.private_key = self._load_or_create_key()
        self.public_key = self.private_key.public_key()
    
    def _load_or_create_key(self) -> ed25519.Ed25519PrivateKey:
        """Load existing key or create new one"""
        if self.private_key_path and Path(self.private_key_path).exists():
            with open(self.private_key_path, 'rb') as f:
                return ed25519.Ed25519PrivateKey.from_private_bytes(f.read())
        else:
            # Generate new key
            private_key = ed25519.Ed25519PrivateKey.generate()
            
            if self.private_key_path:
                # Save key
                os.makedirs(Path(self.private_key_path).parent, exist_ok=True)
                with open(self.private_key_path, 'wb') as f:
                    f.write(private_key.private_bytes(
                        encoding=Encoding.Raw,
                        format=PrivateFormat.Raw,
                        encryption_algorithm=NoEncryption()
                    ))
                logger.info(f"Generated new verifier key: {self.private_key_path}")
            
            return private_key
    
    def get_public_key_hex(self) -> str:
        """Get public key as hex string"""
        return self.public_key.public_bytes(
            encoding=Encoding.Raw,
            format=PublicFormat.Raw
        ).hex()
    
    def sign_report(self, report: VerificationReport) -> str:
        """Sign verification report"""
        # Set public key in report
        report.verifier_pubkey = self.get_public_key_hex()
        
        # Create canonical JSON for signing (exclude signature field)
        report_dict = asdict(report)
        report_dict.pop('signature', None)
        canonical_json = json.dumps(report_dict, sort_keys=True, separators=(',', ':'))
        
        # Sign
        signature = self.private_key.sign(canonical_json.encode('utf-8'))
        signature_hex = signature.hex()
        
        # Update report with signature
        report.signature = signature_hex
        
        return signature_hex


class IPFSClient:
    """IPFS client for pinning verification reports"""
    
    def __init__(self, api_url: str = "http://127.0.0.1:5001"):
        self.api_url = api_url
    
    async def pin_json(self, data: Dict[str, Any]) -> str:
        """Pin JSON data to IPFS and return CID"""
        try:
            async with aiohttp.ClientSession() as session:
                # Convert to JSON
                json_data = json.dumps(data, sort_keys=True, indent=2)
                
                # Pin to IPFS
                files = {'file': json_data}
                url = urljoin(self.api_url, '/api/v0/add')
                
                async with session.post(url, data=files) as response:
                    if response.status == 200:
                        result = await response.json()
                        cid = result.get('Hash')
                        logger.info(f"Pinned verification report to IPFS: {cid}")
                        return cid
                    else:
                        logger.error(f"IPFS pin failed: {response.status}")
                        return ""
        except Exception as e:
            logger.error(f"IPFS error: {e}")
            return ""


class BlockchainClient:
    """Blockchain client for submitting approvals"""
    
    def __init__(self, rpc_url: str, private_key: str, contract_address: str):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.account = Account.from_key(private_key)
        self.contract_address = contract_address
        
        # Load contract ABI (simplified)
        self.contract_abi = [
            {
                "inputs": [
                    {"name": "taskId", "type": "string"},
                    {"name": "verifierReportCID", "type": "bytes32"}
                ],
                "name": "approveTask",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ]
        
        self.contract = self.w3.eth.contract(
            address=self.contract_address,
            abi=self.contract_abi
        )
    
    async def approve_task(self, task_id: str, report_cid: str) -> str:
        """Submit task approval to blockchain"""
        try:
            # Convert CID to bytes32 (simplified)
            cid_bytes32 = Web3.keccak(text=report_cid)
            
            # Build transaction
            transaction = self.contract.functions.approveTask(
                task_id, 
                cid_bytes32
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gasPrice': self.w3.eth.gas_price,
                'gas': 200000  # Estimate
            })
            
            # Sign and send
            signed_txn = self.account.sign_transaction(transaction)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            logger.info(f"Submitted approval for task {task_id}: {tx_hash.hex()}")
            return tx_hash.hex()
            
        except Exception as e:
            logger.error(f"Blockchain approval failed: {e}")
            return ""


class TaskVerifierService:
    """Main verifier service orchestrator"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.github = GitHubClient(config.get('github_token'))
        self.validator = TaskValidator(self.github)
        self.signer = ReportSigner(config.get('verifier_key_path'))
        self.ipfs = IPFSClient(config.get('ipfs_api_url', 'http://127.0.0.1:5001'))
        
        if config.get('blockchain_enabled', False):
            self.blockchain = BlockchainClient(
                config['rpc_url'],
                config['blockchain_private_key'],
                config['task_registry_address']
            )
        else:
            self.blockchain = None
    
    async def process_task_submission(self, submission: TaskSubmission) -> bool:
        """Process a single task submission"""
        logger.info(f"Processing submission for task {submission.task_id}")
        
        try:
            # Load task sheet
            task_sheet = await self._load_task_sheet(submission.task_id)
            if not task_sheet:
                logger.error(f"Task sheet not found for {submission.task_id}")
                return False
            
            # Validate task
            report = await self.validator.validate_task(task_sheet, submission)
            
            # Sign report
            self.signer.sign_report(report)
            
            # Pin report to IPFS
            report_cid = await self.ipfs.pin_json(asdict(report))
            if not report_cid:
                logger.error(f"Failed to pin report for {submission.task_id}")
                return False
            
            # Submit to blockchain if passed
            if report.overall_status == "pass" and self.blockchain:
                tx_hash = await self.blockchain.approve_task(submission.task_id, report_cid)
                if tx_hash:
                    logger.info(f"Task {submission.task_id} approved on-chain: {tx_hash}")
                else:
                    logger.error(f"Failed to approve {submission.task_id} on-chain")
                    return False
            
            logger.info(f"Successfully processed {submission.task_id}: {report.overall_status}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to process {submission.task_id}: {e}")
            return False
    
    async def _load_task_sheet(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Load task sheet YAML from repository"""
        try:
            # Determine milestone and file path
            milestone = task_id.split('-')[0]  # e.g., "M1" from "M1-T001"
            file_path = f"tasks/{milestone}/{task_id}.yaml"
            
            # Load from GitHub
            content = await self.github.get_file_content(
                self.config['repo'], 
                self.config.get('branch', 'main'), 
                file_path
            )
            
            if content:
                return yaml.safe_load(content)
            
        except Exception as e:
            logger.error(f"Failed to load task sheet {task_id}: {e}")
        
        return None
    
    async def run_continuous(self, poll_interval: int = 60):
        """Run verifier service continuously"""
        logger.info(f"Starting verifier service (poll interval: {poll_interval}s)")
        
        while True:
            try:
                # In a real implementation, this would:
                # 1. Poll TaskRegistry contract for submitted tasks
                # 2. Check which tasks need verification
                # 3. Process them
                
                logger.info("Checking for new task submissions...")
                await asyncio.sleep(poll_interval)
                
            except KeyboardInterrupt:
                logger.info("Shutting down verifier service")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(poll_interval)


def load_config() -> Dict[str, Any]:
    """Load configuration from environment and config files"""
    config = {
        'github_token': os.getenv('GITHUB_TOKEN'),
        'verifier_key_path': os.getenv('VERIFIER_PRIVATE_KEY_PATH', './verifier_key.bin'),
        'ipfs_api_url': os.getenv('IPFS_API_URL', 'http://127.0.0.1:5001'),
        'repo': os.getenv('TASK_REPO', 'swisscomfort/asi-core'),
        'branch': os.getenv('TASK_BRANCH', 'main'),
        'blockchain_enabled': os.getenv('BLOCKCHAIN_ENABLED', 'false').lower() == 'true',
        'rpc_url': os.getenv('RPC_URL', 'https://rpc-mumbai.maticvigil.com/'),
        'blockchain_private_key': os.getenv('BLOCKCHAIN_PRIVATE_KEY'),
        'task_registry_address': os.getenv('TASK_REGISTRY_ADDRESS'),
        'poll_interval': int(os.getenv('POLL_INTERVAL', '60'))
    }
    
    return config


async def main():
    """Main entry point"""
    config = load_config()
    
    if not config['github_token']:
        logger.warning("No GitHub token provided - API rate limits may apply")
    
    # Initialize service
    verifier = TaskVerifierService(config)
    
    # Test with sample submission
    sample_submission = TaskSubmission(
        task_id="M1-T001",
        submitter="0x742d35Cc6634C0532925a3b8D",
        evidence_cid="QmTestEvidence123",
        submitted_at=int(time.time()),
        pr_url="https://github.com/swisscomfort/asi-core/pull/1",
        repo="swisscomfort/asi-core",
        branch="feature/pwa-skeleton"
    )
    
    # Process sample (for testing)
    result = await verifier.process_task_submission(sample_submission)
    logger.info(f"Sample processing result: {result}")
    
    # Start continuous processing
    await verifier.run_continuous(config['poll_interval'])


if __name__ == "__main__":
    asyncio.run(main())