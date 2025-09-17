#!/usr/bin/env python3
"""
ASI Core Evidence Submission Tool
=================================

Tool für Contributors zum Einreichen von Arbeitsnachweisen (Evidence) für geclaimte Tasks.
Lädt Evidence Files auf IPFS hoch und submitted sie an den TaskRegistry Contract.

Usage:
    python submit_evidence.py --task M1-T001 --github-pr 42 --demo-url https://my-demo.com
    python submit_evidence.py --task M1-T001 --files evidence/ --description "Completed MVP"
    python submit_evidence.py --task M1-T001 --auto-package --message "Final submission"
"""

import argparse
import json
import os
import sys
import time
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

import requests
import yaml
from eth_account import Account
from web3 import Web3

# Configure paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
CONFIG_DIR = PROJECT_ROOT / "config"
EVIDENCE_DIR = PROJECT_ROOT / "evidence"


class EvidencePackager:
    """Package evidence files into IPFS-ready structure"""
    
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.evidence_dir = EVIDENCE_DIR / task_id
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
    
    def create_evidence_package(self, 
                              files: Optional[List[str]] = None,
                              github_pr: Optional[int] = None,
                              demo_url: Optional[str] = None,
                              description: Optional[str] = None,
                              auto_package: bool = False) -> Dict[str, Any]:
        """Create standardized evidence package"""
        
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        evidence = {
            "task_id": self.task_id,
            "submission_type": "evidence_package",
            "submitted_at": timestamp,
            "contributor": {
                "wallet_address": None,  # Will be filled by submission tool
                "github_username": os.getenv('GITHUB_USERNAME'),
                "contact": os.getenv('CONTRIBUTOR_EMAIL')
            },
            "evidence": {},
            "deliverables": []
        }
        
        # Add GitHub PR reference
        if github_pr:
            evidence["evidence"]["github_pr"] = {
                "number": github_pr,
                "url": f"https://github.com/{os.getenv('GITHUB_REPO', 'asi-org/asi-core')}/pull/{github_pr}",
                "branch": os.getenv('GITHUB_BRANCH'),
                "commit_hash": self._get_git_commit()
            }
        
        # Add demo URL
        if demo_url:
            evidence["evidence"]["demo"] = {
                "url": demo_url,
                "type": "live_demo",
                "verified_at": timestamp
            }
        
        # Add description
        if description:
            evidence["evidence"]["description"] = description
        
        # Package files
        if auto_package:
            files = self._auto_discover_files()
        
        if files:
            evidence["evidence"]["files"] = self._package_files(files)
        
        # Load task sheet for deliverable checking
        task_sheet = self._load_task_sheet()
        if task_sheet:
            evidence["deliverables"] = self._check_deliverables(task_sheet, evidence)
        
        return evidence
    
    def _get_git_commit(self) -> Optional[str]:
        """Get current git commit hash"""
        try:
            import subprocess
            result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                                  capture_output=True, text=True, cwd=PROJECT_ROOT)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return None
    
    def _auto_discover_files(self) -> List[str]:
        """Auto-discover evidence files in common locations"""
        file_patterns = [
            'README.md',
            'IMPLEMENTATION.md',
            '*.py',
            '*.js',
            '*.sol',
            '*.yaml',
            '*.json',
            'docs/**/*',
            'src/**/*',
            'contracts/**/*',
            'screenshots/**/*',
            'videos/**/*'
        ]
        
        discovered_files = []
        
        # Check project root and task-specific directories
        search_dirs = [PROJECT_ROOT, self.evidence_dir]
        
        for search_dir in search_dirs:
            if search_dir.exists():
                for pattern in file_patterns:
                    for file_path in search_dir.glob(pattern):
                        if file_path.is_file():
                            relative_path = str(file_path.relative_to(PROJECT_ROOT))
                            discovered_files.append(relative_path)
        
        return discovered_files[:50]  # Limit to 50 files
    
    def _package_files(self, files: List[str]) -> Dict[str, Any]:
        """Package files into evidence structure"""
        packaged_files = {
            "count": 0,
            "total_size": 0,
            "files": []
        }
        
        for file_path in files:
            full_path = PROJECT_ROOT / file_path
            if full_path.exists() and full_path.is_file():
                try:
                    file_size = full_path.stat().st_size
                    if file_size > 10 * 1024 * 1024:  # Skip files > 10MB
                        continue
                    
                    # Read file content (text files only)
                    content = None
                    if full_path.suffix in ['.md', '.py', '.js', '.sol', '.yaml', '.json', '.txt']:
                        try:
                            with open(full_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                        except:
                            content = "<binary_file>"
                    
                    file_info = {
                        "path": file_path,
                        "size": file_size,
                        "modified": datetime.fromtimestamp(full_path.stat().st_mtime).isoformat(),
                        "content": content
                    }
                    
                    packaged_files["files"].append(file_info)
                    packaged_files["count"] += 1
                    packaged_files["total_size"] += file_size
                    
                except Exception as e:
                    print(f"⚠️ Skipping file {file_path}: {e}")
        
        return packaged_files
    
    def _load_task_sheet(self) -> Optional[Dict[str, Any]]:
        """Load task sheet for deliverable validation"""
        milestone = self.task_id.split('-')[0]
        task_file = PROJECT_ROOT / "tasks" / milestone / f"{self.task_id}.yaml"
        
        if task_file.exists():
            try:
                with open(task_file) as f:
                    return yaml.safe_load(f)
            except:
                pass
        return None
    
    def _check_deliverables(self, task_sheet: Dict[str, Any], evidence: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check deliverables against task requirements"""
        deliverables = []
        
        task_deliverables = task_sheet.get('deliverables', [])
        
        for i, deliverable in enumerate(task_deliverables):
            deliverable_check = {
                "index": i,
                "description": deliverable,
                "status": "unknown",
                "evidence_reference": None,
                "notes": []
            }
            
            # Simple keyword matching for deliverable validation
            deliverable_lower = deliverable.lower()
            
            # Check GitHub PR
            if 'github' in deliverable_lower or 'pr' in deliverable_lower or 'pull request' in deliverable_lower:
                if evidence["evidence"].get("github_pr"):
                    deliverable_check["status"] = "provided"
                    deliverable_check["evidence_reference"] = "github_pr"
                    deliverable_check["notes"].append("GitHub PR linked")
                else:
                    deliverable_check["status"] = "missing"
                    deliverable_check["notes"].append("No GitHub PR provided")
            
            # Check demo
            elif 'demo' in deliverable_lower or 'url' in deliverable_lower:
                if evidence["evidence"].get("demo"):
                    deliverable_check["status"] = "provided"
                    deliverable_check["evidence_reference"] = "demo"
                    deliverable_check["notes"].append("Demo URL provided")
                else:
                    deliverable_check["status"] = "missing"
                    deliverable_check["notes"].append("No demo URL provided")
            
            # Check documentation
            elif 'documentation' in deliverable_lower or 'readme' in deliverable_lower or 'docs' in deliverable_lower:
                files = evidence["evidence"].get("files", {}).get("files", [])
                doc_files = [f for f in files if f["path"].lower().endswith(('.md', '.rst', '.txt')) or 'doc' in f["path"].lower()]
                if doc_files:
                    deliverable_check["status"] = "provided"
                    deliverable_check["evidence_reference"] = "files"
                    deliverable_check["notes"].append(f"Found {len(doc_files)} documentation files")
                else:
                    deliverable_check["status"] = "missing"
                    deliverable_check["notes"].append("No documentation files found")
            
            # Check code/implementation
            elif 'code' in deliverable_lower or 'implementation' in deliverable_lower or 'script' in deliverable_lower:
                files = evidence["evidence"].get("files", {}).get("files", [])
                code_files = [f for f in files if f["path"].lower().endswith(('.py', '.js', '.sol', '.go', '.rs', '.java', '.cpp'))]
                if code_files:
                    deliverable_check["status"] = "provided"
                    deliverable_check["evidence_reference"] = "files"
                    deliverable_check["notes"].append(f"Found {len(code_files)} code files")
                else:
                    deliverable_check["status"] = "missing"
                    deliverable_check["notes"].append("No code files found")
            
            else:
                # Generic check - assume provided if any evidence exists
                if any(evidence["evidence"].values()):
                    deliverable_check["status"] = "provided"
                    deliverable_check["notes"].append("General evidence provided")
                else:
                    deliverable_check["status"] = "missing"
                    deliverable_check["notes"].append("No evidence provided")
            
            deliverables.append(deliverable_check)
        
        return deliverables
    
    def save_evidence_package(self, evidence: Dict[str, Any]) -> str:
        """Save evidence package to file"""
        filename = f"{self.task_id}_evidence_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.evidence_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(evidence, f, indent=2, ensure_ascii=False)
        
        return str(filepath)


class IPFSClient:
    """IPFS client for uploading evidence"""
    
    def __init__(self, api_url: str = "http://127.0.0.1:5001"):
        self.api_url = api_url.rstrip('/')
    
    def pin_json(self, data: Dict[str, Any]) -> Optional[str]:
        """Pin JSON data to IPFS"""
        try:
            json_str = json.dumps(data, indent=2, ensure_ascii=False)
            files = {'file': ('evidence.json', json_str)}
            response = requests.post(f"{self.api_url}/api/v0/add", files=files)
            
            if response.status_code == 200:
                result = response.json()
                cid = result.get('Hash')
                print(f"✅ Evidence pinned to IPFS: {cid}")
                return cid
            else:
                print(f"❌ IPFS pin failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ IPFS error: {e}")
            return None


class TaskRegistryClient:
    """Web3 client for submitting evidence to TaskRegistry"""
    
    def __init__(self, config: Dict[str, Any]):
        self.w3 = Web3(Web3.HTTPProvider(config['rpc_url']))
        self.account = Account.from_key(config['private_key'])
        self.contract_address = config['task_registry_address']
        
        # Load contract ABI (simplified)
        self.contract_abi = [
            {
                "inputs": [
                    {"name": "taskId", "type": "string"},
                    {"name": "evidenceCID", "type": "bytes32"}
                ],
                "name": "submitEvidence",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [{"name": "taskId", "type": "string"}],
                "name": "getTask",
                "outputs": [
                    {"name": "taskSheetCID", "type": "bytes32"},
                    {"name": "bountyToken", "type": "address"},
                    {"name": "bountyAmount", "type": "uint256"},
                    {"name": "status", "type": "uint8"},
                    {"name": "claimer", "type": "address"},
                    {"name": "payoutVault", "type": "address"},
                    {"name": "claimDeadline", "type": "uint256"},
                    {"name": "submitDeadline", "type": "uint256"},
                    {"name": "evidenceCID", "type": "bytes32"},
                    {"name": "verifierReportCID", "type": "bytes32"},
                    {"name": "createdAt", "type": "uint256"},
                    {"name": "claimedAt", "type": "uint256"},
                    {"name": "submittedAt", "type": "uint256"},
                    {"name": "approvedAt", "type": "uint256"}
                ],
                "stateMutability": "view",
                "type": "function"
            }
        ]
        
        self.contract = self.w3.eth.contract(
            address=self.contract_address,
            abi=self.contract_abi
        )
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get current task status"""
        try:
            result = self.contract.functions.getTask(task_id).call()
            
            # Status mapping: 0=Available, 1=Claimed, 2=Submitted, 3=Approved, 4=Rejected
            status_names = ['Available', 'Claimed', 'Submitted', 'Approved', 'Rejected']
            
            return {
                'task_sheet_cid': result[0].hex(),
                'bounty_token': result[1],
                'bounty_amount': result[2],
                'status': status_names[result[3]] if result[3] < len(status_names) else 'Unknown',
                'status_code': result[3],
                'claimer': result[4],
                'payout_vault': result[5],
                'claim_deadline': result[6],
                'submit_deadline': result[7],
                'evidence_cid': result[8].hex() if result[8] != b'\x00' * 32 else None,
                'verifier_report_cid': result[9].hex() if result[9] != b'\x00' * 32 else None,
                'created_at': result[10],
                'claimed_at': result[11],
                'submitted_at': result[12],
                'approved_at': result[13]
            }
        except Exception as e:
            print(f"❌ Failed to get task status: {e}")
            return None
    
    def submit_evidence(self, task_id: str, evidence_cid: str, dry_run: bool = False) -> bool:
        """Submit evidence to blockchain"""
        try:
            # Check task status
            task_status = self.get_task_status(task_id)
            if not task_status:
                print(f"❌ Task {task_id} not found")
                return False
            
            if task_status['claimer'].lower() != self.account.address.lower():
                print(f"❌ Task {task_id} not claimed by current account")
                print(f"   Claimer: {task_status['claimer']}")
                print(f"   Current: {self.account.address}")
                return False
            
            if task_status['status_code'] != 1:  # Not in Claimed state
                print(f"❌ Task {task_id} not in claimable state (status: {task_status['status']})")
                return False
            
            # Check deadline
            current_time = int(time.time())
            if task_status['submit_deadline'] > 0 and current_time > task_status['submit_deadline']:
                print(f"❌ Task {task_id} submission deadline has passed")
                return False
            
            # Convert IPFS CID to bytes32
            cid_bytes32 = Web3.keccak(text=evidence_cid)
            
            print(f"📤 Submitting evidence for task {task_id}:")
            print(f"   Evidence CID: {evidence_cid}")
            print(f"   Current status: {task_status['status']}")
            
            if dry_run:
                print("🧪 DRY RUN - Not executing transaction")
                return True
            
            # Build transaction
            transaction = self.contract.functions.submitEvidence(
                task_id,
                cid_bytes32
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gasPrice': self.w3.eth.gas_price,
            })
            
            # Estimate gas
            try:
                gas_estimate = self.w3.eth.estimate_gas(transaction)
                transaction['gas'] = int(gas_estimate * 1.2)
            except Exception as e:
                print(f"⚠️ Gas estimation failed: {e}")
                transaction['gas'] = 200000
            
            # Sign and send
            signed_txn = self.account.sign_transaction(transaction)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            print(f"⏳ Transaction sent: {tx_hash.hex()}")
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            if receipt.status == 1:
                print(f"✅ Evidence submitted successfully!")
                print(f"   Gas used: {receipt.gasUsed}")
                return True
            else:
                print(f"❌ Transaction failed")
                return False
                
        except Exception as e:
            print(f"❌ Failed to submit evidence: {e}")
            return False


class EvidenceSubmissionTool:
    """Main tool for evidence submission"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.ipfs = IPFSClient(self.config.get('ipfs_api_url', 'http://127.0.0.1:5001'))
        self.registry = TaskRegistryClient(self.config)
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration"""
        config = {}
        
        if config_path:
            config_file = Path(config_path)
        else:
            config_file = CONFIG_DIR / "task-registry.json"
        
        if config_file.exists():
            with open(config_file) as f:
                config = json.load(f)
        
        # Override with environment variables
        config.update({
            'rpc_url': os.getenv('RPC_URL', config.get('rpc_url', 'https://rpc-mumbai.maticvigil.com/')),
            'private_key': os.getenv('PRIVATE_KEY', config.get('private_key')),
            'task_registry_address': os.getenv('TASK_REGISTRY_ADDRESS', config.get('task_registry_address')),
            'ipfs_api_url': os.getenv('IPFS_API_URL', config.get('ipfs_api_url', 'http://127.0.0.1:5001'))
        })
        
        return config
    
    def submit_evidence(self, task_id: str, 
                       files: Optional[List[str]] = None,
                       github_pr: Optional[int] = None,
                       demo_url: Optional[str] = None,
                       description: Optional[str] = None,
                       auto_package: bool = False,
                       dry_run: bool = False) -> bool:
        """Submit evidence for a task"""
        print(f"\n📤 Submitting evidence for task: {task_id}")
        
        # Create evidence package
        packager = EvidencePackager(task_id)
        evidence = packager.create_evidence_package(
            files=files,
            github_pr=github_pr,
            demo_url=demo_url,
            description=description,
            auto_package=auto_package
        )
        
        # Set contributor wallet address
        evidence["contributor"]["wallet_address"] = self.registry.account.address
        
        # Save evidence package locally
        evidence_file = packager.save_evidence_package(evidence)
        print(f"💾 Evidence package saved: {evidence_file}")
        
        # Show deliverables status
        print(f"\n📋 Deliverables check:")
        for deliverable in evidence.get("deliverables", []):
            status_icon = "✅" if deliverable["status"] == "provided" else "❌"
            print(f"   {status_icon} {deliverable['description']}")
            for note in deliverable.get("notes", []):
                print(f"      └─ {note}")
        
        # Upload to IPFS
        evidence_cid = self.ipfs.pin_json(evidence)
        if not evidence_cid:
            return False
        
        # Submit to blockchain
        return self.registry.submit_evidence(task_id, evidence_cid, dry_run)
    
    def check_task_status(self, task_id: str) -> None:
        """Check current task status"""
        print(f"\n🔍 Checking status for task: {task_id}")
        
        status = self.registry.get_task_status(task_id)
        if not status:
            print(f"❌ Task {task_id} not found")
            return
        
        print(f"📊 Task Status:")
        print(f"   Status: {status['status']}")
        print(f"   Claimer: {status['claimer']}")
        print(f"   Bounty: {Web3.from_wei(status['bounty_amount'], 'ether')} tokens")
        
        if status['claim_deadline'] > 0:
            deadline = datetime.fromtimestamp(status['claim_deadline'])
            print(f"   Claim Deadline: {deadline}")
        
        if status['submit_deadline'] > 0:
            deadline = datetime.fromtimestamp(status['submit_deadline'])
            print(f"   Submit Deadline: {deadline}")
        
        if status['evidence_cid']:
            print(f"   Evidence CID: {status['evidence_cid']}")
        
        if status['verifier_report_cid']:
            print(f"   Verifier Report CID: {status['verifier_report_cid']}")


def main():
    parser = argparse.ArgumentParser(description="ASI Core Evidence Submission Tool")
    parser.add_argument('--config', help='Config file path')
    parser.add_argument('--dry-run', action='store_true', help='Simulate without executing')
    parser.add_argument('--task', required=True, help='Task ID (e.g., M1-T001)')
    parser.add_argument('--files', nargs='*', help='Evidence files to include')
    parser.add_argument('--github-pr', type=int, help='GitHub Pull Request number')
    parser.add_argument('--demo-url', help='Demo URL')
    parser.add_argument('--description', help='Evidence description')
    parser.add_argument('--auto-package', action='store_true', help='Auto-discover evidence files')
    parser.add_argument('--status', action='store_true', help='Check task status only')
    
    args = parser.parse_args()
    
    # Initialize tool
    tool = EvidenceSubmissionTool(args.config)
    
    if args.status:
        tool.check_task_status(args.task)
    else:
        if not tool.submit_evidence(
            task_id=args.task,
            files=args.files,
            github_pr=args.github_pr,
            demo_url=args.demo_url,
            description=args.description,
            auto_package=args.auto_package,
            dry_run=args.dry_run
        ):
            sys.exit(1)


if __name__ == "__main__":
    main()