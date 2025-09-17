#!/usr/bin/env python3
"""
ASI Core Task Registration Tool
===============================

Tool für Maintainer zum Registrieren von Tasks auf der Blockchain.
Liest YAML Task-Sheets, pinnt sie auf IPFS und registriert sie im TaskRegistry Contract.

Usage:
    python register_tasks.py --milestone M1 --dry-run
    python register_tasks.py --task M1-T001 --deploy
    python register_tasks.py --all --fund-vault 10000
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

import requests
import yaml
from eth_account import Account
from web3 import Web3

# Configure paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
TASKS_DIR = PROJECT_ROOT / "tasks"
CONFIG_DIR = PROJECT_ROOT / "config"


class IPFSClient:
    """IPFS client for pinning task sheets"""
    
    def __init__(self, api_url: str = "http://127.0.0.1:5001"):
        self.api_url = api_url.rstrip('/')
    
    def pin_file(self, content: str) -> Optional[str]:
        """Pin content to IPFS and return CID"""
        try:
            files = {'file': ('task.yaml', content)}
            response = requests.post(f"{self.api_url}/api/v0/add", files=files)
            
            if response.status_code == 200:
                result = response.json()
                cid = result.get('Hash')
                print(f"✅ Pinned to IPFS: {cid}")
                return cid
            else:
                print(f"❌ IPFS pin failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ IPFS error: {e}")
            return None


class TaskRegistryClient:
    """Web3 client for TaskRegistry contract"""
    
    def __init__(self, config: Dict[str, Any]):
        self.w3 = Web3(Web3.HTTPProvider(config['rpc_url']))
        self.account = Account.from_key(config['private_key'])
        self.contract_address = config['task_registry_address']
        self.vault_address = config['reward_vault_address']
        
        # Load contract ABI
        abi_path = PROJECT_ROOT / "contracts" / "task-system" / "TaskRegistry.abi.json"
        if abi_path.exists():
            with open(abi_path) as f:
                self.contract_abi = json.load(f)
        else:
            # Minimal ABI for basic functions
            self.contract_abi = [
                {
                    "inputs": [
                        {"name": "taskId", "type": "string"},
                        {"name": "taskSheetCID", "type": "bytes32"},
                        {"name": "bountyToken", "type": "address"},
                        {"name": "bountyAmount", "type": "uint256"},
                        {"name": "payoutVault", "type": "address"}
                    ],
                    "name": "createTask",
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
        
        # Token addresses
        self.token_addresses = {
            'ASI': config.get('asi_token_address', '0x' + '0' * 40),
            'USDC': config.get('usdc_token_address', '0x' + '0' * 40),
            'MATIC': '0x0000000000000000000000000000000000000000'  # Native token
        }
    
    def check_connection(self) -> bool:
        """Check blockchain connection"""
        try:
            latest_block = self.w3.eth.block_number
            balance = self.w3.eth.get_balance(self.account.address)
            
            print(f"🔗 Connected to blockchain (block: {latest_block})")
            print(f"💰 Account: {self.account.address}")
            print(f"💰 Balance: {Web3.from_wei(balance, 'ether')} MATIC")
            
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def task_exists(self, task_id: str) -> bool:
        """Check if task already exists on-chain"""
        try:
            result = self.contract.functions.getTask(task_id).call()
            # If createdAt is 0, task doesn't exist
            return result[10] != 0  # createdAt field
        except:
            return False
    
    def create_task(self, task_id: str, task_sheet: Dict[str, Any], ipfs_cid: str, dry_run: bool = False) -> bool:
        """Create task on blockchain"""
        try:
            # Parse bounty info
            bounty = task_sheet.get('bounty', {})
            token_symbol = bounty.get('token', 'ASI')
            bounty_amount = bounty.get('amount', 0)
            
            token_address = self.token_addresses.get(token_symbol)
            if not token_address:
                print(f"❌ Unknown token: {token_symbol}")
                return False
            
            # Convert IPFS CID to bytes32 (simplified)
            cid_bytes32 = Web3.keccak(text=ipfs_cid)
            
            # Convert bounty amount (assuming 18 decimals for ASI)
            bounty_wei = Web3.to_wei(bounty_amount, 'ether')
            
            print(f"📝 Creating task {task_id}:")
            print(f"   Token: {token_symbol} ({token_address})")
            print(f"   Amount: {bounty_amount} tokens")
            print(f"   IPFS CID: {ipfs_cid}")
            print(f"   Vault: {self.vault_address}")
            
            if dry_run:
                print("🧪 DRY RUN - Not executing transaction")
                return True
            
            # Build transaction
            transaction = self.contract.functions.createTask(
                task_id,
                cid_bytes32,
                token_address,
                bounty_wei,
                self.vault_address
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gasPrice': self.w3.eth.gas_price,
            })
            
            # Estimate gas
            try:
                gas_estimate = self.w3.eth.estimate_gas(transaction)
                transaction['gas'] = int(gas_estimate * 1.2)  # 20% buffer
            except Exception as e:
                print(f"⚠️ Gas estimation failed: {e}")
                transaction['gas'] = 300000  # Fallback
            
            # Sign and send
            signed_txn = self.account.sign_transaction(transaction)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            print(f"⏳ Transaction sent: {tx_hash.hex()}")
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            if receipt.status == 1:
                print(f"✅ Task {task_id} created successfully!")
                print(f"   Gas used: {receipt.gasUsed}")
                return True
            else:
                print(f"❌ Transaction failed")
                return False
                
        except Exception as e:
            print(f"❌ Failed to create task {task_id}: {e}")
            return False


class TaskRegistrationTool:
    """Main tool for task registration"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.ipfs = IPFSClient(self.config.get('ipfs_api_url', 'http://127.0.0.1:5001'))
        self.registry = TaskRegistryClient(self.config)
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file and environment"""
        config = {}
        
        # Try to load from config file
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
            'reward_vault_address': os.getenv('REWARD_VAULT_ADDRESS', config.get('reward_vault_address')),
            'asi_token_address': os.getenv('ASI_TOKEN_ADDRESS', config.get('asi_token_address')),
            'ipfs_api_url': os.getenv('IPFS_API_URL', config.get('ipfs_api_url', 'http://127.0.0.1:5001'))
        })
        
        return config
    
    def load_task_sheet(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Load task YAML sheet"""
        milestone = task_id.split('-')[0]  # e.g., "M1" from "M1-T001"
        task_file = TASKS_DIR / milestone / f"{task_id}.yaml"
        
        if not task_file.exists():
            print(f"❌ Task file not found: {task_file}")
            return None
        
        try:
            with open(task_file) as f:
                task_sheet = yaml.safe_load(f)
            
            # Validate required fields
            required_fields = ['task_id', 'title', 'bounty', 'deliverables', 'definition_of_done']
            for field in required_fields:
                if field not in task_sheet:
                    print(f"❌ Missing required field in {task_id}: {field}")
                    return None
            
            return task_sheet
            
        except Exception as e:
            print(f"❌ Failed to load {task_file}: {e}")
            return None
    
    def register_task(self, task_id: str, dry_run: bool = False) -> bool:
        """Register a single task"""
        print(f"\n🚀 Registering task: {task_id}")
        
        # Check if already exists
        if self.registry.task_exists(task_id):
            print(f"⚠️ Task {task_id} already exists on-chain")
            return False
        
        # Load task sheet
        task_sheet = self.load_task_sheet(task_id)
        if not task_sheet:
            return False
        
        # Pin to IPFS
        yaml_content = yaml.dump(task_sheet, default_flow_style=False, sort_keys=False)
        ipfs_cid = self.ipfs.pin_file(yaml_content)
        if not ipfs_cid:
            return False
        
        # Create on blockchain
        return self.registry.create_task(task_id, task_sheet, ipfs_cid, dry_run)
    
    def register_milestone(self, milestone: str, dry_run: bool = False) -> bool:
        """Register all tasks in a milestone"""
        milestone_dir = TASKS_DIR / milestone
        if not milestone_dir.exists():
            print(f"❌ Milestone directory not found: {milestone_dir}")
            return False
        
        # Find all task files
        task_files = list(milestone_dir.glob("*.yaml"))
        if not task_files:
            print(f"❌ No task files found in {milestone_dir}")
            return False
        
        print(f"\n🎯 Registering milestone {milestone} ({len(task_files)} tasks)")
        
        success_count = 0
        for task_file in sorted(task_files):
            task_id = task_file.stem  # Remove .yaml extension
            if self.register_task(task_id, dry_run):
                success_count += 1
            time.sleep(2)  # Rate limiting
        
        print(f"\n📊 Milestone {milestone} registration complete: {success_count}/{len(task_files)} tasks")
        return success_count == len(task_files)
    
    def register_all(self, dry_run: bool = False) -> bool:
        """Register all available tasks"""
        milestones = []
        for milestone_dir in TASKS_DIR.iterdir():
            if milestone_dir.is_dir() and milestone_dir.name.startswith('M'):
                milestones.append(milestone_dir.name)
        
        if not milestones:
            print("❌ No milestone directories found")
            return False
        
        milestones.sort()  # M0, M1, M2, etc.
        
        print(f"\n🌍 Registering all tasks from milestones: {', '.join(milestones)}")
        
        total_success = 0
        total_tasks = 0
        
        for milestone in milestones:
            if self.register_milestone(milestone, dry_run):
                print(f"✅ Milestone {milestone} completed successfully")
            else:
                print(f"⚠️ Milestone {milestone} had some failures")
            time.sleep(5)  # Rate limiting between milestones
        
        return True
    
    def list_tasks(self, milestone: Optional[str] = None) -> None:
        """List available tasks"""
        if milestone:
            milestone_dir = TASKS_DIR / milestone
            if not milestone_dir.exists():
                print(f"❌ Milestone {milestone} not found")
                return
            
            task_files = list(milestone_dir.glob("*.yaml"))
            print(f"\n📋 Tasks in {milestone}:")
            for task_file in sorted(task_files):
                task_sheet = self.load_task_sheet(task_file.stem)
                if task_sheet:
                    bounty = task_sheet.get('bounty', {})
                    status = "✅ EXISTS" if self.registry.task_exists(task_file.stem) else "⏳ NEW"
                    print(f"   {task_file.stem}: {task_sheet['title']} ({bounty.get('amount', 0)} {bounty.get('token', 'ASI')}) {status}")
        else:
            # List all milestones
            print("\n📋 Available milestones:")
            for milestone_dir in sorted(TASKS_DIR.iterdir()):
                if milestone_dir.is_dir() and milestone_dir.name.startswith('M'):
                    task_count = len(list(milestone_dir.glob("*.yaml")))
                    print(f"   {milestone_dir.name}: {task_count} tasks")
    
    def validate_setup(self) -> bool:
        """Validate that everything is set up correctly"""
        print("🔍 Validating setup...")
        
        # Check config
        required_config = ['private_key', 'task_registry_address', 'reward_vault_address']
        for key in required_config:
            if not self.config.get(key):
                print(f"❌ Missing config: {key}")
                return False
        
        # Check blockchain connection
        if not self.registry.check_connection():
            return False
        
        # Check IPFS connection
        try:
            response = requests.get(f"{self.config['ipfs_api_url']}/api/v0/version")
            if response.status_code == 200:
                version = response.json().get('Version', 'unknown')
                print(f"📦 IPFS connected (version: {version})")
            else:
                print("⚠️ IPFS connection failed")
                return False
        except:
            print("⚠️ IPFS not reachable")
            return False
        
        # Check task directory
        if not TASKS_DIR.exists():
            print(f"❌ Tasks directory not found: {TASKS_DIR}")
            return False
        
        print("✅ Setup validation complete!")
        return True


def main():
    parser = argparse.ArgumentParser(description="ASI Core Task Registration Tool")
    parser.add_argument('--config', help='Config file path')
    parser.add_argument('--dry-run', action='store_true', help='Simulate without executing')
    parser.add_argument('--task', help='Register specific task (e.g., M1-T001)')
    parser.add_argument('--milestone', help='Register all tasks in milestone (e.g., M1)')
    parser.add_argument('--all', action='store_true', help='Register all available tasks')
    parser.add_argument('--list', help='List tasks (specify milestone or "all")')
    parser.add_argument('--validate', action='store_true', help='Validate setup')
    
    args = parser.parse_args()
    
    # Initialize tool
    tool = TaskRegistrationTool(args.config)
    
    # Validate setup
    if args.validate or not any([args.task, args.milestone, args.all, args.list]):
        if not tool.validate_setup():
            sys.exit(1)
        if args.validate:
            return
    
    # Execute commands
    if args.list:
        milestone = None if args.list == 'all' else args.list
        tool.list_tasks(milestone)
    elif args.task:
        if not tool.register_task(args.task, args.dry_run):
            sys.exit(1)
    elif args.milestone:
        if not tool.register_milestone(args.milestone, args.dry_run):
            sys.exit(1)
    elif args.all:
        if not tool.register_all(args.dry_run):
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()