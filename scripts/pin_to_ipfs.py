#!/usr/bin/env python3
"""
ASI Core IPFS Management Script
Pin files, manage content and interact with IPFS network
"""

import json
import os
import sys
import subprocess
import requests
import pathlib
import hashlib
from typing import Dict, List, Optional, Union
from datetime import datetime

# Configuration
IPFS_API = "http://127.0.0.1:5001"
IPFS_GATEWAY = "http://127.0.0.1:8080"
PIN_DIR = "/workspaces/asi-core/.ipfs_pins"
CLUSTER_API = ""  # Optional: IPFS Cluster for redundancy

class IPFSManager:
    def __init__(self):
        self.api_url = IPFS_API
        self.gateway_url = IPFS_GATEWAY
        self.pin_registry = self._load_pin_registry()
        
        # Ensure pin directory exists
        pathlib.Path(PIN_DIR).mkdir(parents=True, exist_ok=True)
    
    def _load_pin_registry(self) -> Dict:
        """Load local pin registry"""
        registry_file = pathlib.Path(PIN_DIR) / "pin_registry.json"
        
        if registry_file.exists():
            with open(registry_file, 'r') as f:
                return json.load(f)
        else:
            return {
                "pins": {},
                "last_updated": datetime.now().isoformat(),
                "version": "1.0"
            }
    
    def _save_pin_registry(self) -> None:
        """Save local pin registry"""
        registry_file = pathlib.Path(PIN_DIR) / "pin_registry.json"
        self.pin_registry["last_updated"] = datetime.now().isoformat()
        
        with open(registry_file, 'w') as f:
            json.dump(self.pin_registry, f, indent=2)
    
    def check_ipfs_daemon(self) -> bool:
        """Check if IPFS daemon is running"""
        try:
            response = requests.get(f"{self.api_url}/api/v0/version", timeout=5)
            if response.status_code == 200:
                version_info = response.json()
                print(f"✅ IPFS daemon running (version: {version_info.get('Version', 'unknown')})")
                return True
            else:
                print(f"❌ IPFS daemon not responding: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ IPFS daemon connection failed: {e}")
            return False
    
    def start_ipfs_daemon(self) -> bool:
        """Start IPFS daemon if not running"""
        if self.check_ipfs_daemon():
            return True
        
        print("🚀 Starting IPFS daemon...")
        try:
            # Try to start daemon
            subprocess.Popen(
                ["ipfs", "daemon"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Wait a moment and check again
            import time
            time.sleep(3)
            
            return self.check_ipfs_daemon()
            
        except FileNotFoundError:
            print("❌ IPFS CLI not found. Install IPFS first:")
            print("   curl -sSL https://dist.ipfs.tech/kubo/v0.22.0/kubo_v0.22.0_linux-amd64.tar.gz | tar -xz")
            print("   sudo install kubo/ipfs /usr/local/bin/")
            print("   ipfs init")
            return False
        except Exception as e:
            print(f"❌ Failed to start IPFS daemon: {e}")
            return False
    
    def pin_file(self, file_path: str, name: Optional[str] = None) -> Optional[str]:
        """Pin a file to IPFS and track it locally"""
        if not self.check_ipfs_daemon():
            if not self.start_ipfs_daemon():
                return None
        
        file_path = pathlib.Path(file_path)
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return None
        
        try:
            # Add file to IPFS
            with open(file_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(
                    f"{self.api_url}/api/v0/add",
                    files=files,
                    params={'pin': 'true'}  # Pin immediately
                )
            
            if response.status_code != 200:
                print(f"❌ IPFS add failed: {response.text}")
                return None
            
            result = response.json()
            cid = result['Hash']
            size = result['Size']
            
            # Calculate file hash for verification
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            
            # Record in registry
            pin_name = name or file_path.name
            self.pin_registry["pins"][cid] = {
                "name": pin_name,
                "file_path": str(file_path),
                "file_hash": file_hash,
                "size": size,
                "pinned_at": datetime.now().isoformat(),
                "gateway_url": f"{self.gateway_url}/ipfs/{cid}"
            }
            
            self._save_pin_registry()
            
            print(f"📌 Pinned: {pin_name}")
            print(f"   CID: {cid}")
            print(f"   Size: {size} bytes")
            print(f"   Gateway: {self.gateway_url}/ipfs/{cid}")
            
            return cid
            
        except Exception as e:
            print(f"❌ Pin failed: {e}")
            return None
    
    def pin_directory(self, dir_path: str, name: Optional[str] = None) -> Optional[str]:
        """Pin a directory recursively to IPFS"""
        if not self.check_ipfs_daemon():
            if not self.start_ipfs_daemon():
                return None
        
        dir_path = pathlib.Path(dir_path)
        if not dir_path.exists() or not dir_path.is_dir():
            print(f"❌ Directory not found: {dir_path}")
            return None
        
        try:
            # Use CLI for directory pinning (easier than API)
            result = subprocess.check_output([
                "ipfs", "add", "-r", "-Q", str(dir_path)
            ], text=True).strip()
            
            # Get the root CID (last line)
            lines = result.split('\n')
            root_cid = lines[-1]
            
            # Pin the root CID
            pin_response = requests.post(
                f"{self.api_url}/api/v0/pin/add",
                params={'arg': root_cid}
            )
            
            if pin_response.status_code != 200:
                print(f"⚠️  Pinning failed: {pin_response.text}")
            
            # Record in registry
            pin_name = name or dir_path.name
            self.pin_registry["pins"][root_cid] = {
                "name": pin_name,
                "file_path": str(dir_path),
                "type": "directory",
                "file_count": len(list(dir_path.rglob('*'))),
                "pinned_at": datetime.now().isoformat(),
                "gateway_url": f"{self.gateway_url}/ipfs/{root_cid}"
            }
            
            self._save_pin_registry()
            
            print(f"📁 Directory pinned: {pin_name}")
            print(f"   Root CID: {root_cid}")
            print(f"   Files: {len(list(dir_path.rglob('*')))}")
            print(f"   Gateway: {self.gateway_url}/ipfs/{root_cid}")
            
            return root_cid
            
        except Exception as e:
            print(f"❌ Directory pin failed: {e}")
            return None
    
    def unpin(self, cid: str) -> bool:
        """Unpin content from IPFS"""
        try:
            response = requests.post(
                f"{self.api_url}/api/v0/pin/rm",
                params={'arg': cid}
            )
            
            if response.status_code == 200:
                # Remove from registry
                if cid in self.pin_registry["pins"]:
                    name = self.pin_registry["pins"][cid]["name"]
                    del self.pin_registry["pins"][cid]
                    self._save_pin_registry()
                    print(f"📌 Unpinned: {name} ({cid})")
                else:
                    print(f"📌 Unpinned: {cid}")
                return True
            else:
                print(f"❌ Unpin failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Unpin error: {e}")
            return False
    
    def list_pins(self) -> None:
        """List all pinned content"""
        if not self.pin_registry["pins"]:
            print("📋 No pinned content found")
            return
        
        print(f"📋 Pinned content ({len(self.pin_registry['pins'])}):")
        
        for cid, info in self.pin_registry["pins"].items():
            pin_type = info.get("type", "file")
            size_info = f"{info.get('size', 0)} bytes" if pin_type == "file" else f"{info.get('file_count', 0)} files"
            
            print(f"   📌 {info['name']}")
            print(f"      CID: {cid}")
            print(f"      Type: {pin_type}")
            print(f"      Size: {size_info}")
            print(f"      Pinned: {info['pinned_at']}")
            print(f"      URL: {info['gateway_url']}")
            print()
    
    def get_content(self, cid: str, output_path: Optional[str] = None) -> bool:
        """Download content from IPFS"""
        try:
            response = requests.get(f"{self.gateway_url}/ipfs/{cid}")
            
            if response.status_code == 200:
                if output_path:
                    with open(output_path, 'wb') as f:
                        f.write(response.content)
                    print(f"💾 Downloaded to: {output_path}")
                else:
                    print(response.text)
                return True
            else:
                print(f"❌ Download failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Download error: {e}")
            return False
    
    def verify_pin(self, cid: str) -> bool:
        """Verify that content is properly pinned"""
        try:
            # Check if pinned
            response = requests.get(f"{self.api_url}/api/v0/pin/ls")
            
            if response.status_code == 200:
                pins = response.json()
                is_pinned = cid in pins.get("Keys", {})
                
                if is_pinned:
                    print(f"✅ {cid} is pinned")
                    return True
                else:
                    print(f"❌ {cid} is NOT pinned")
                    return False
            else:
                print(f"❌ Pin verification failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Verification error: {e}")
            return False
    
    def bulk_pin_tasks(self) -> None:
        """Pin all task YAML files to IPFS"""
        tasks_dir = pathlib.Path("/workspaces/asi-core/tasks")
        
        if not tasks_dir.exists():
            print(f"❌ Tasks directory not found: {tasks_dir}")
            return
        
        task_files = list(tasks_dir.glob("**/*.yaml"))
        
        if not task_files:
            print("❌ No task YAML files found")
            return
        
        print(f"📌 Pinning {len(task_files)} task files...")
        
        pinned_count = 0
        failed_count = 0
        
        for task_file in task_files:
            print(f"\n📋 Pinning: {task_file.name}")
            
            cid = self.pin_file(str(task_file), f"task-{task_file.stem}")
            
            if cid:
                pinned_count += 1
            else:
                failed_count += 1
        
        print(f"\n📊 Bulk pin summary:")
        print(f"   ✅ Pinned: {pinned_count}")
        print(f"   ❌ Failed: {failed_count}")
        print(f"   📈 Total: {len(task_files)}")

def main():
    """Main CLI interface"""
    manager = IPFSManager()
    
    if len(sys.argv) < 2:
        print("Usage: python pin_to_ipfs.py <command> [args]")
        print("Commands:")
        print("  status                    - Check IPFS daemon status")
        print("  start                     - Start IPFS daemon")
        print("  pin <file/dir> [name]     - Pin file or directory")
        print("  unpin <cid>               - Unpin content")
        print("  list                      - List all pins")
        print("  get <cid> [output_path]   - Download content")
        print("  verify <cid>              - Verify pin status")
        print("  bulk-tasks                - Pin all task YAML files")
        return
    
    command = sys.argv[1]
    
    if command == "status":
        manager.check_ipfs_daemon()
        
    elif command == "start":
        manager.start_ipfs_daemon()
        
    elif command == "pin" and len(sys.argv) >= 3:
        path = sys.argv[2]
        name = sys.argv[3] if len(sys.argv) > 3 else None
        
        if os.path.isdir(path):
            manager.pin_directory(path, name)
        else:
            manager.pin_file(path, name)
            
    elif command == "unpin" and len(sys.argv) >= 3:
        cid = sys.argv[2]
        manager.unpin(cid)
        
    elif command == "list":
        manager.list_pins()
        
    elif command == "get" and len(sys.argv) >= 3:
        cid = sys.argv[2]
        output_path = sys.argv[3] if len(sys.argv) > 3 else None
        manager.get_content(cid, output_path)
        
    elif command == "verify" and len(sys.argv) >= 3:
        cid = sys.argv[2]
        manager.verify_pin(cid)
        
    elif command == "bulk-tasks":
        manager.bulk_pin_tasks()
        
    else:
        print(f"❌ Invalid command or missing arguments")

if __name__ == "__main__":
    main()