#!/usr/bin/env python3
"""
ASI Core Workflow Manager
Complete workflow for contributors: claim → work → submit → payout
"""

import os
import sys
import subprocess
import pathlib
from typing import Optional

# Import our modules
sys.path.append(str(pathlib.Path(__file__).parent))
from register_tasks import TaskRegistrar
from submit_evidence import EvidenceSubmitter
from pin_to_ipfs import IPFSManager

class WorkflowManager:
    def __init__(self):
        self.registrar = TaskRegistrar()
        self.submitter = EvidenceSubmitter()
        self.ipfs = IPFSManager()
    
    def contributor_workflow(self, task_id: str):
        """Complete workflow for a contributor"""
        print(f"🚀 Starting workflow for task: {task_id}")
        print("=" * 50)
        
        # Step 1: Check task status
        print("\n1️⃣ Checking task status...")
        status = self.submitter.get_task_status(task_id)
        
        if not status:
            print("❌ Task not found or contract not available")
            return False
        
        print(f"   Status: {status['status']}")
        print(f"   Bounty: {status['bounty_amount']} wei")
        
        if status['status'] != "Open":
            print(f"❌ Task is not available for claiming")
            return False
        
        # Step 2: Claim task
        print("\n2️⃣ Claiming task...")
        if not self.submitter.claim_task(task_id):
            print("❌ Failed to claim task")
            return False
        
        # Step 3: Work instructions
        print("\n3️⃣ Work on the task:")
        print("   • Check the task YAML file for requirements")
        print("   • Create your PR with the deliverables")
        print("   • Ensure all tests pass")
        print("   • Take screenshots if needed")
        print("   • Gather all artifacts")
        print("\n   When ready, run:")
        print(f"   python workflow_manager.py submit {task_id} <pr_url> [artifacts...]")
        
        return True
    
    def submit_workflow(self, task_id: str, pr_url: str, artifacts: list):
        """Submit evidence workflow"""
        print(f"📤 Submitting evidence for task: {task_id}")
        print("=" * 50)
        
        # Step 1: Check if we own this task
        print("\n1️⃣ Verifying task ownership...")
        status = self.submitter.get_task_status(task_id)
        
        if not status:
            print("❌ Task not found")
            return False
        
        if not status['is_mine']:
            print("❌ You don't own this task")
            return False
        
        if status['status'] != "Claimed":
            print(f"❌ Task is not in 'Claimed' status: {status['status']}")
            return False
        
        # Step 2: Create evidence package
        print("\n2️⃣ Creating evidence package...")
        package_path = self.submitter.create_evidence_package(
            task_id, pr_url, artifacts
        )
        
        if not package_path:
            print("❌ Failed to create evidence package")
            return False
        
        # Step 3: Pin to IPFS
        print("\n3️⃣ Pinning evidence to IPFS...")
        evidence_cid = self.ipfs.pin_file(package_path, f"evidence-{task_id}")
        
        if not evidence_cid:
            print("❌ Failed to pin evidence to IPFS")
            return False
        
        # Step 4: Submit on-chain
        print("\n4️⃣ Submitting evidence on-chain...")
        if not self.submitter.submit_evidence(task_id, evidence_cid):
            print("❌ Failed to submit evidence on-chain")
            return False
        
        print("\n✅ Evidence submitted successfully!")
        print("   Now wait for the verifier to approve your submission")
        print(f"   Check status with: python workflow_manager.py status {task_id}")
        
        return True
    
    def payout_workflow(self, task_id: str):
        """Claim payout workflow"""
        print(f"💰 Claiming payout for task: {task_id}")
        print("=" * 50)
        
        # Step 1: Check if approved
        print("\n1️⃣ Checking approval status...")
        status = self.submitter.get_task_status(task_id)
        
        if not status:
            print("❌ Task not found")
            return False
        
        if not status['is_mine']:
            print("❌ You don't own this task")
            return False
        
        if status['status'] != "Approved":
            print(f"❌ Task is not approved yet: {status['status']}")
            if status['status'] == "Submitted":
                print("   Wait for the verifier to approve your submission")
            return False
        
        # Step 2: Claim payout
        print("\n2️⃣ Claiming payout...")
        if not self.submitter.claim_payout(task_id):
            print("❌ Failed to claim payout")
            return False
        
        print("\n🎉 Payout claimed successfully!")
        print("   Check your wallet for the bounty tokens")
        print("   You should also receive an SBT badge as proof of contribution")
        
        return True
    
    def setup_workflow(self):
        """Setup workflow for new contributors"""
        print("🔧 ASI Core Contributor Setup")
        print("=" * 50)
        
        # Step 1: Check IPFS
        print("\n1️⃣ Checking IPFS daemon...")
        if not self.ipfs.check_ipfs_daemon():
            print("   Starting IPFS daemon...")
            if not self.ipfs.start_ipfs_daemon():
                print("❌ IPFS setup failed. Install IPFS first:")
                print("   https://docs.ipfs.tech/install/")
                return False
        
        # Step 2: Check environment
        print("\n2️⃣ Checking environment...")
        
        required_env = ["CONTRIBUTOR_PRIVATE_KEY"]
        missing_env = []
        
        for env_var in required_env:
            if not os.getenv(env_var):
                missing_env.append(env_var)
        
        if missing_env:
            print("⚠️  Missing environment variables:")
            for var in missing_env:
                print(f"   export {var}=your_value_here")
            print("\n   Create a wallet and export your private key (without 0x prefix)")
        
        # Step 3: Check contracts
        print("\n3️⃣ Checking smart contracts...")
        if self.submitter.registry_contract:
            print("✅ TaskRegistry contract connected")
        else:
            print("⚠️  TaskRegistry contract not available")
            print("   Update REGISTRY_ADDRESS in submit_evidence.py")
        
        # Step 4: Test workflow
        print("\n4️⃣ Test workflow:")
        print("   • List available tasks: python workflow_manager.py list")
        print("   • Start a task: python workflow_manager.py start <task_id>")
        print("   • Submit evidence: python workflow_manager.py submit <task_id> <pr_url>")
        print("   • Claim payout: python workflow_manager.py payout <task_id>")
        
        print("\n✅ Setup complete!")
        return True

def main():
    """Main CLI interface"""
    manager = WorkflowManager()
    
    if len(sys.argv) < 2:
        print("ASI Core Workflow Manager")
        print("Usage: python workflow_manager.py <command> [args]")
        print("\nCommands:")
        print("  setup                                     - Setup environment for contributors")
        print("  list [milestone]                          - List available tasks")
        print("  start <task_id>                           - Start working on a task (claim it)")
        print("  submit <task_id> <pr_url> [artifacts...]  - Submit evidence for completed task")
        print("  payout <task_id>                          - Claim payout after approval")
        print("  status <task_id>                          - Check task status")
        print("\nExample workflow:")
        print("  1. python workflow_manager.py list")
        print("  2. python workflow_manager.py start M1-T001")
        print("  3. # Work on the task, create PR")
        print("  4. python workflow_manager.py submit M1-T001 https://github.com/org/repo/pull/123")
        print("  5. # Wait for approval")
        print("  6. python workflow_manager.py payout M1-T001")
        return
    
    command = sys.argv[1]
    
    if command == "setup":
        manager.setup_workflow()
        
    elif command == "list":
        milestone = sys.argv[2] if len(sys.argv) > 2 else None
        manager.registrar.list_tasks(milestone)
        
    elif command == "start" and len(sys.argv) >= 3:
        task_id = sys.argv[2]
        manager.contributor_workflow(task_id)
        
    elif command == "submit" and len(sys.argv) >= 4:
        task_id = sys.argv[2]
        pr_url = sys.argv[3]
        artifacts = sys.argv[4:] if len(sys.argv) > 4 else []
        manager.submit_workflow(task_id, pr_url, artifacts)
        
    elif command == "payout" and len(sys.argv) >= 3:
        task_id = sys.argv[2]
        manager.payout_workflow(task_id)
        
    elif command == "status" and len(sys.argv) >= 3:
        task_id = sys.argv[2]
        status = manager.submitter.get_task_status(task_id)
        
        if status:
            print(f"📋 Task: {status['task_id']}")
            print(f"   Status: {status['status']}")
            print(f"   Bounty: {status['bounty_amount']} wei")
            print(f"   Your task: {status['is_mine']}")
        else:
            print("❌ Task not found or contract not available")
        
    else:
        print(f"❌ Invalid command: {command}")

if __name__ == "__main__":
    main()