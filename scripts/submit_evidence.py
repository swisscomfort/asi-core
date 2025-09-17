#!/usr/bin/env python3
"""
ASI Core Evidence Submission Script
Submit evidence for completed tasks and claim bounties
"""

import json
import os
import sys
import pathlib
import subprocess
import requests
import zipfile
from datetime import datetime
from web3 import Web3
from eth_account import Account
from typing import Dict, List, Optional

# Configuration
EVIDENCE_DIR = "/workspaces/asi-core/evidence"
RPC_URL = "https://rpc.ankr.com/polygon_mumbai"
REGISTRY_ADDRESS = "0x"  # TaskRegistry contract
PRIVATE_KEY = os.getenv("CONTRIBUTOR_PRIVATE_KEY", "")
IPFS_API = "http://127.0.0.1:5001"

# Contract ABI
TASK_REGISTRY_ABI = [
    {
        "inputs": [
            {"name": "taskId", "type": "string"},
            {"name": "evidenceCid", "type": "bytes32"}
        ],
        "name": "submitTask",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"name": "taskId", "type": "string"}],
        "name": "claimTask",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"name": "taskId", "type": "string"}],
        "name": "payout",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"name": "taskId", "type": "bytes32"}],
        "name": "tasks",
        "outputs": [
            {"name": "ipfsHash", "type": "bytes32"},
            {"name": "bountyToken", "type": "address"},
            {"name": "bountyAmount", "type": "uint256"},
            {"name": "status", "type": "uint8"},
            {"name": "claimer", "type": "address"},
            {"name": "payer", "type": "address"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

class EvidenceSubmitter:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(RPC_URL))
        
        if PRIVATE_KEY:
            self.account = Account.from_key(PRIVATE_KEY)
            print(f"🔑 Using account: {self.account.address}")
        else:
            print("⚠️  No PRIVATE_KEY found. Set CONTRIBUTOR_PRIVATE_KEY env var.")
            self.account = None
            
        self.registry_contract = None
        if REGISTRY_ADDRESS and REGISTRY_ADDRESS != "0x":
            self.registry_contract = self.w3.eth.contract(
                address=REGISTRY_ADDRESS,
                abi=TASK_REGISTRY_ABI
            )
    
    def create_evidence_package(self, task_id: str, 
                              pr_url: str = "",
                              artifacts: List[str] = [],
                              screenshots: List[str] = [],
                              notes: str = "") -> Optional[str]:
        """Create evidence package and return local path"""
        
        # Create evidence directory
        evidence_path = pathlib.Path(EVIDENCE_DIR) / task_id
        evidence_path.mkdir(parents=True, exist_ok=True)
        
        # Create evidence metadata
        evidence_meta = {
            "task_id": task_id,
            "contributor": self.account.address if self.account else "unknown",
            "timestamp": datetime.now().isoformat(),
            "pr_url": pr_url,
            "artifacts": artifacts,
            "screenshots": screenshots,
            "notes": notes,
            "version": "1.0"
        }
        
        # Write metadata
        meta_file = evidence_path / "evidence.json"
        with open(meta_file, 'w') as f:
            json.dump(evidence_meta, f, indent=2)
        
        # Copy artifacts
        artifacts_dir = evidence_path / "artifacts"
        artifacts_dir.mkdir(exist_ok=True)
        
        for artifact in artifacts:
            if os.path.exists(artifact):
                dest = artifacts_dir / os.path.basename(artifact)
                if os.path.isdir(artifact):
                    subprocess.run(["cp", "-r", artifact, str(dest)])
                else:
                    subprocess.run(["cp", artifact, str(dest)])
                print(f"📁 Copied artifact: {artifact}")
            else:
                print(f"⚠️  Artifact not found: {artifact}")
        
        # Copy screenshots
        screenshots_dir = evidence_path / "screenshots"
        screenshots_dir.mkdir(exist_ok=True)
        
        for screenshot in screenshots:
            if os.path.exists(screenshot):
                dest = screenshots_dir / os.path.basename(screenshot)
                subprocess.run(["cp", screenshot, str(dest)])
                print(f"🖼️  Copied screenshot: {screenshot}")
            else:
                print(f"⚠️  Screenshot not found: {screenshot}")
        
        # Create ZIP package
        zip_path = evidence_path.parent / f"{task_id}_evidence.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(evidence_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_path = os.path.relpath(file_path, evidence_path)
                    zipf.write(file_path, arc_path)
        
        print(f"📦 Evidence package created: {zip_path}")
        return str(zip_path)
    
    def pin_to_ipfs(self, file_path: str) -> Optional[str]:
        """Pin evidence package to IPFS"""
        try:
            # Try local IPFS daemon
            with open(file_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(f"{IPFS_API}/api/v0/add", files=files)
                
            if response.status_code == 200:
                result = response.json()
                cid = result['Hash']
                print(f"📌 Evidence pinned to IPFS: {cid}")
                
                # Pin it permanently
                pin_response = requests.post(
                    f"{IPFS_API}/api/v0/pin/add",
                    params={'arg': cid}
                )
                
                if pin_response.status_code == 200:
                    print(f"📍 Evidence permanently pinned")
                else:
                    print(f"⚠️  Permanent pinning failed: {pin_response.text}")
                
                return cid
            else:
                print(f"❌ IPFS upload failed: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ IPFS error: {e}")
            # Fallback to CLI
            try:
                result = subprocess.check_output(
                    ["ipfs", "add", "-Q", file_path],
                    text=True
                ).strip()
                print(f"📌 Pinned via CLI: {result}")
                return result
            except subprocess.CalledProcessError:
                print("❌ IPFS CLI also failed")
                return None
    
    def claim_task(self, task_id: str) -> bool:
        """Claim a task before working on it"""
        if not self.registry_contract or not self.account:
            print("❌ Contract or account not available")
            return False
        
        try:
            # Check if task exists and is available
            task_hash = Web3.keccak(text=task_id)
            task_data = self.registry_contract.functions.tasks(task_hash).call()
            
            status = task_data[3]  # status field
            if status != 0:  # 0 = Open
                print(f"❌ Task {task_id} is not available (status: {status})")
                return False
            
            # Build claim transaction
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            
            tx = self.registry_contract.functions.claimTask(task_id).build_transaction({
                'from': self.account.address,
                'nonce': nonce,
                'gas': 150000,
                'gasPrice': self.w3.to_wei('30', 'gwei')
            })
            
            # Sign and send
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            print(f"🚀 Claim transaction sent: {tx_hash.hex()}")
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt['status'] == 1:
                print(f"✅ Task {task_id} claimed successfully!")
                return True
            else:
                print(f"❌ Claim transaction failed")
                return False
                
        except Exception as e:
            print(f"❌ Claim failed: {e}")
            return False
    
    def submit_evidence(self, task_id: str, evidence_cid: str) -> bool:
        """Submit evidence for a claimed task"""
        if not self.registry_contract or not self.account:
            print("❌ Contract or account not available")
            return False
        
        try:
            # Convert CID to bytes32
            evidence_hash = Web3.keccak(text=evidence_cid)
            
            # Build submission transaction
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            
            tx = self.registry_contract.functions.submitTask(
                task_id, 
                evidence_hash
            ).build_transaction({
                'from': self.account.address,
                'nonce': nonce,
                'gas': 200000,
                'gasPrice': self.w3.to_wei('30', 'gwei')
            })
            
            # Sign and send
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            print(f"🚀 Submission transaction sent: {tx_hash.hex()}")
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt['status'] == 1:
                print(f"✅ Evidence submitted for task {task_id}!")
                print(f"   Evidence CID: {evidence_cid}")
                print(f"   Block: {receipt['blockNumber']}")
                return True
            else:
                print(f"❌ Submission transaction failed")
                return False
                
        except Exception as e:
            print(f"❌ Submission failed: {e}")
            return False
    
    def claim_payout(self, task_id: str) -> bool:
        """Claim payout after task approval"""
        if not self.registry_contract or not self.account:
            print("❌ Contract or account not available")
            return False
        
        try:
            # Check task status
            task_hash = Web3.keccak(text=task_id)
            task_data = self.registry_contract.functions.tasks(task_hash).call()
            
            status = task_data[3]  # status field
            if status != 3:  # 3 = Approved
                print(f"❌ Task {task_id} is not approved yet (status: {status})")
                return False
            
            # Build payout transaction
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            
            tx = self.registry_contract.functions.payout(task_id).build_transaction({
                'from': self.account.address,
                'nonce': nonce,
                'gas': 200000,
                'gasPrice': self.w3.to_wei('30', 'gwei')
            })
            
            # Sign and send
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            print(f"🚀 Payout transaction sent: {tx_hash.hex()}")
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt['status'] == 1:
                print(f"💰 Payout claimed for task {task_id}!")
                print(f"   Block: {receipt['blockNumber']}")
                return True
            else:
                print(f"❌ Payout transaction failed")
                return False
                
        except Exception as e:
            print(f"❌ Payout failed: {e}")
            return False
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Get current status of a task"""
        if not self.registry_contract:
            print("❌ Contract not available")
            return None
        
        try:
            task_hash = Web3.keccak(text=task_id)
            task_data = self.registry_contract.functions.tasks(task_hash).call()
            
            status_names = ["Open", "Claimed", "Submitted", "Approved", "Paid", "Reopened"]
            status = task_data[3]
            
            return {
                "task_id": task_id,
                "status": status_names[status] if status < len(status_names) else "Unknown",
                "status_code": status,
                "bounty_amount": task_data[2],
                "claimer": task_data[4],
                "is_mine": task_data[4].lower() == self.account.address.lower() if self.account else False
            }
            
        except Exception as e:
            print(f"❌ Status check failed: {e}")
            return None

def main():
    """Main CLI interface"""
    submitter = EvidenceSubmitter()
    
    if len(sys.argv) < 2:
        print("Usage: python submit_evidence.py <command> [args]")
        print("Commands:")
        print("  claim <task_id>                           - Claim a task")
        print("  submit <task_id> <pr_url> [artifacts...]  - Submit evidence")
        print("  payout <task_id>                          - Claim payout")
        print("  status <task_id>                          - Check task status")
        print("  package <task_id> <pr_url> [artifacts...] - Create evidence package only")
        return
    
    command = sys.argv[1]
    
    if command == "claim" and len(sys.argv) >= 3:
        task_id = sys.argv[2]
        submitter.claim_task(task_id)
        
    elif command == "submit" and len(sys.argv) >= 4:
        task_id = sys.argv[2]
        pr_url = sys.argv[3]
        artifacts = sys.argv[4:] if len(sys.argv) > 4 else []
        
        # Create evidence package
        package_path = submitter.create_evidence_package(
            task_id, pr_url, artifacts
        )
        
        if package_path:
            # Pin to IPFS
            evidence_cid = submitter.pin_to_ipfs(package_path)
            
            if evidence_cid:
                # Submit on-chain
                submitter.submit_evidence(task_id, evidence_cid)
        
    elif command == "package" and len(sys.argv) >= 4:
        task_id = sys.argv[2]
        pr_url = sys.argv[3]
        artifacts = sys.argv[4:] if len(sys.argv) > 4 else []
        
        package_path = submitter.create_evidence_package(
            task_id, pr_url, artifacts
        )
        
        if package_path:
            print(f"📦 Evidence package ready: {package_path}")
            print("   Use 'submit' command to upload and submit on-chain")
        
    elif command == "payout" and len(sys.argv) >= 3:
        task_id = sys.argv[2]
        submitter.claim_payout(task_id)
        
    elif command == "status" and len(sys.argv) >= 3:
        task_id = sys.argv[2]
        status = submitter.get_task_status(task_id)
        
        if status:
            print(f"📋 Task: {status['task_id']}")
            print(f"   Status: {status['status']}")
            print(f"   Bounty: {status['bounty_amount']} wei")
            print(f"   Claimer: {status['claimer']}")
            print(f"   Is mine: {status['is_mine']}")
        
    else:
        print(f"❌ Invalid command or missing arguments")

if __name__ == "__main__":
    main()