#!/usr/bin/env python3
"""
ASI Core Task Registration Script
Register YAML task sheets on-chain via TaskRegistry smart contract
"""

import json
import os
import sys
import pathlib
import subprocess
import yaml
import requests
from web3 import Web3
from eth_account import Account
from typing import Dict, List, Optional

# Configuration
TASKS_DIR = "/workspaces/asi-core/tasks"
RPC_URL = "https://rpc.ankr.com/polygon_mumbai"  # Testnet
REGISTRY_ADDRESS = "0x"  # To be deployed
VAULT_ADDRESS = "0x"      # To be deployed
PRIVATE_KEY = os.getenv("DEPLOYER_PRIVATE_KEY", "")
IPFS_API = "http://127.0.0.1:5001"  # Local IPFS node

# Contract ABIs (minimal interface)
TASK_REGISTRY_ABI = [
    {
        "inputs": [
            {"name": "taskId", "type": "string"},
            {"name": "ipfsHash", "type": "bytes32"},
            {"name": "bountyToken", "type": "address"},
            {"name": "bountyAmount", "type": "uint256"},
            {"name": "payer", "type": "address"}
        ],
        "name": "createTask",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "taskId", "type": "bytes32"},
            {"indexed": False, "name": "ipfsHash", "type": "bytes32"},
            {"indexed": False, "name": "bountyAmount", "type": "uint256"}
        ],
        "name": "TaskCreated",
        "type": "event"
    }
]

class TaskRegistrar:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(RPC_URL))
        
        if PRIVATE_KEY:
            self.account = Account.from_key(PRIVATE_KEY)
        else:
            print("⚠️  No PRIVATE_KEY found. Running in read-only mode.")
            self.account = None
            
        self.registry_contract = None
        if REGISTRY_ADDRESS and REGISTRY_ADDRESS != "0x":
            self.registry_contract = self.w3.eth.contract(
                address=REGISTRY_ADDRESS,
                abi=TASK_REGISTRY_ABI
            )
    
    def pin_to_ipfs(self, file_path: str) -> Optional[str]:
        """Pin file to IPFS and return CID"""
        try:
            # Try local IPFS daemon first
            with open(file_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(f"{IPFS_API}/api/v0/add", files=files)
                
            if response.status_code == 200:
                result = response.json()
                cid = result['Hash']
                print(f"📌 Pinned to IPFS: {cid}")
                return cid
            else:
                print(f"❌ IPFS pin failed: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ IPFS error: {e}")
            # Fallback: use ipfs CLI if available
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
    
    def load_task_sheet(self, yaml_path: str) -> Optional[Dict]:
        """Load and validate task sheet"""
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                task = yaml.safe_load(f)
            
            # Validate required fields
            required = ['task_id', 'title', 'bounty', 'deliverables', 'definition_of_done']
            for field in required:
                if field not in task:
                    print(f"❌ Missing field '{field}' in {yaml_path}")
                    return None
            
            # Validate bounty structure
            bounty = task['bounty']
            if not isinstance(bounty, dict) or 'token' not in bounty or 'amount' not in bounty:
                print(f"❌ Invalid bounty format in {yaml_path}")
                return None
            
            return task
            
        except Exception as e:
            print(f"❌ Error loading {yaml_path}: {e}")
            return None
    
    def register_task_onchain(self, task: Dict, ipfs_cid: str) -> bool:
        """Register task on-chain via TaskRegistry"""
        if not self.registry_contract or not self.account:
            print("❌ Contract or account not available")
            return False
        
        try:
            task_id = task['task_id']
            bounty = task['bounty']
            
            # Convert IPFS CID to bytes32 (simplified)
            ipfs_hash = Web3.keccak(text=ipfs_cid)
            
            # Token mapping (simplified - in production use actual addresses)
            token_addresses = {
                'ASI': '0x7D1AfA7B718fb893dB30A3aBc0Cfc608AaCfeBB0',  # Mock ASI token
                'USDT': '0xc2132D05D31c914a87C6611C10748AEb04B58e8F',  # Polygon USDT
                'MATIC': '0x0000000000000000000000000000000000000000'  # Native token
            }
            
            token_address = token_addresses.get(bounty['token'], token_addresses['ASI'])
            bounty_amount = int(bounty['amount'] * 10**18)  # Convert to wei
            
            # Build transaction
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            
            tx = self.registry_contract.functions.createTask(
                task_id,
                ipfs_hash,
                token_address,
                bounty_amount,
                VAULT_ADDRESS
            ).build_transaction({
                'from': self.account.address,
                'nonce': nonce,
                'gas': 300000,
                'gasPrice': self.w3.to_wei('30', 'gwei')
            })
            
            # Sign and send
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            print(f"🚀 Transaction sent: {tx_hash.hex()}")
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt['status'] == 1:
                print(f"✅ Task {task_id} registered successfully!")
                print(f"   Block: {receipt['blockNumber']}")
                print(f"   Gas used: {receipt['gasUsed']}")
                return True
            else:
                print(f"❌ Transaction failed: {receipt}")
                return False
                
        except Exception as e:
            print(f"❌ Registration failed: {e}")
            return False
    
    def register_all_tasks(self, milestone: Optional[str] = None) -> None:
        """Register all tasks or tasks from specific milestone"""
        tasks_path = pathlib.Path(TASKS_DIR)
        
        if not tasks_path.exists():
            print(f"❌ Tasks directory not found: {TASKS_DIR}")
            return
        
        # Find task files
        pattern = f"**/{milestone}-*.yaml" if milestone else "**/*.yaml"
        task_files = list(tasks_path.glob(pattern))
        
        if not task_files:
            print(f"❌ No task files found with pattern: {pattern}")
            return
        
        print(f"🔍 Found {len(task_files)} task files")
        
        successful = 0
        failed = 0
        
        for task_file in sorted(task_files):
            print(f"\n📋 Processing: {task_file.name}")
            
            # Load task
            task = self.load_task_sheet(str(task_file))
            if not task:
                failed += 1
                continue
            
            # Pin to IPFS
            ipfs_cid = self.pin_to_ipfs(str(task_file))
            if not ipfs_cid:
                failed += 1
                continue
            
            # Register on-chain
            if self.register_task_onchain(task, ipfs_cid):
                successful += 1
            else:
                failed += 1
        
        print(f"\n📊 Summary:")
        print(f"   ✅ Successful: {successful}")
        print(f"   ❌ Failed: {failed}")
        print(f"   📈 Total: {len(task_files)}")
    
    def list_tasks(self, milestone: Optional[str] = None) -> None:
        """List available tasks"""
        tasks_path = pathlib.Path(TASKS_DIR)
        
        if not tasks_path.exists():
            print(f"❌ Tasks directory not found: {TASKS_DIR}")
            return
        
        pattern = f"**/{milestone}-*.yaml" if milestone else "**/*.yaml"
        task_files = list(tasks_path.glob(pattern))
        
        print(f"📋 Available tasks ({len(task_files)}):")
        
        for task_file in sorted(task_files):
            task = self.load_task_sheet(str(task_file))
            if task:
                bounty = task['bounty']
                print(f"   • {task['task_id']}: {task['title']}")
                print(f"     💰 {bounty['amount']} {bounty['token']}")
                print(f"     📁 {task_file.relative_to(tasks_path)}")
            else:
                print(f"   ❌ {task_file.name} (invalid)")

def main():
    """Main CLI interface"""
    registrar = TaskRegistrar()
    
    if len(sys.argv) < 2:
        print("Usage: python register_tasks.py <command> [args]")
        print("Commands:")
        print("  list [milestone]     - List available tasks")
        print("  register [milestone] - Register tasks on-chain")
        print("  setup               - Setup contracts and configuration")
        return
    
    command = sys.argv[1]
    milestone = sys.argv[2] if len(sys.argv) > 2 else None
    
    if command == "list":
        registrar.list_tasks(milestone)
    elif command == "register":
        registrar.register_all_tasks(milestone)
    elif command == "setup":
        print("🔧 Contract setup not implemented yet")
        print("   Deploy contracts first, then update addresses in this script")
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()