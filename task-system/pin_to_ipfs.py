#!/usr/bin/env python3
"""
ASI Core IPFS Pinning Tool
==========================

Tool zum Pinning von Dateien und Daten auf IPFS für das ASI Core System.
Unterstützt lokale IPFS Nodes und externe IPFS Services (Pinata, Infura, etc.).

Usage:
    python pin_to_ipfs.py --file evidence.json
    python pin_to_ipfs.py --directory evidence/ --recursive
    python pin_to_ipfs.py --json '{"task": "M1-T001", "status": "complete"}'
    python pin_to_ipfs.py --url https://example.com/file.pdf --name "task-reference.pdf"
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import hashlib
import mimetypes
import time

import requests

# Configure paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
CONFIG_DIR = PROJECT_ROOT / "config"
CACHE_DIR = PROJECT_ROOT / ".ipfs_cache"


class IPFSPinningService:
    """Interface for different IPFS pinning services"""
    
    def pin_content(self, content: Union[str, bytes], name: Optional[str] = None) -> Optional[str]:
        """Pin content and return CID"""
        raise NotImplementedError
    
    def pin_file(self, file_path: Path, name: Optional[str] = None) -> Optional[str]:
        """Pin file and return CID"""
        raise NotImplementedError
    
    def unpin_content(self, cid: str) -> bool:
        """Unpin content by CID"""
        raise NotImplementedError
    
    def list_pins(self) -> List[Dict[str, Any]]:
        """List all pinned content"""
        raise NotImplementedError
    
    def get_pin_status(self, cid: str) -> Optional[Dict[str, Any]]:
        """Get pin status for CID"""
        raise NotImplementedError


class LocalIPFSService(IPFSPinningService):
    """Local IPFS node service"""
    
    def __init__(self, api_url: str = "http://127.0.0.1:5001"):
        self.api_url = api_url.rstrip('/')
        self.session = requests.Session()
    
    def _make_request(self, endpoint: str, **kwargs) -> Optional[requests.Response]:
        """Make request to IPFS API"""
        try:
            url = f"{self.api_url}/api/v0/{endpoint}"
            response = self.session.post(url, **kwargs)
            return response if response.status_code == 200 else None
        except Exception as e:
            print(f"❌ IPFS API error: {e}")
            return None
    
    def pin_content(self, content: Union[str, bytes], name: Optional[str] = None) -> Optional[str]:
        """Pin content to IPFS"""
        if isinstance(content, str):
            content = content.encode('utf-8')
        
        filename = name or "content"
        files = {'file': (filename, content)}
        
        response = self._make_request("add", files=files)
        if response:
            result = response.json()
            cid = result.get('Hash')
            if cid:
                # Explicitly pin the content
                pin_response = self._make_request("pin/add", params={'arg': cid})
                if pin_response:
                    print(f"✅ Content pinned: {cid}")
                    return cid
                else:
                    print(f"⚠️ Content added but pinning failed: {cid}")
                    return cid
        
        print("❌ Failed to pin content")
        return None
    
    def pin_file(self, file_path: Path, name: Optional[str] = None) -> Optional[str]:
        """Pin file to IPFS"""
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return None
        
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            filename = name or file_path.name
            return self.pin_content(content, filename)
        
        except Exception as e:
            print(f"❌ Failed to read file {file_path}: {e}")
            return None
    
    def unpin_content(self, cid: str) -> bool:
        """Unpin content from IPFS"""
        response = self._make_request("pin/rm", params={'arg': cid})
        if response:
            print(f"✅ Content unpinned: {cid}")
            return True
        
        print(f"❌ Failed to unpin: {cid}")
        return False
    
    def list_pins(self) -> List[Dict[str, Any]]:
        """List all pinned content"""
        response = self._make_request("pin/ls", params={'type': 'recursive'})
        if response:
            try:
                result = response.json()
                pins = []
                for cid, info in result.get('Keys', {}).items():
                    pins.append({
                        'cid': cid,
                        'type': info.get('Type', 'unknown'),
                        'size': None  # Local IPFS doesn't provide size in pin/ls
                    })
                return pins
            except:
                pass
        
        return []
    
    def get_pin_status(self, cid: str) -> Optional[Dict[str, Any]]:
        """Get pin status for CID"""
        response = self._make_request("pin/ls", params={'arg': cid})
        if response:
            try:
                result = response.json()
                if cid in result.get('Keys', {}):
                    return {
                        'cid': cid,
                        'status': 'pinned',
                        'service': 'local'
                    }
            except:
                pass
        
        return {
            'cid': cid,
            'status': 'unpinned',
            'service': 'local'
        }
    
    def get_node_info(self) -> Optional[Dict[str, Any]]:
        """Get IPFS node information"""
        version_response = self._make_request("version")
        id_response = self._make_request("id")
        
        info = {}
        
        if version_response:
            try:
                version_data = version_response.json()
                info['version'] = version_data.get('Version')
            except:
                pass
        
        if id_response:
            try:
                id_data = id_response.json()
                info['peer_id'] = id_data.get('ID')
                info['addresses'] = id_data.get('Addresses', [])
            except:
                pass
        
        return info if info else None


class PinataService(IPFSPinningService):
    """Pinata IPFS pinning service"""
    
    def __init__(self, api_key: str, secret_key: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = "https://api.pinata.cloud"
        self.session = requests.Session()
        self.session.headers.update({
            'pinata_api_key': api_key,
            'pinata_secret_api_key': secret_key
        })
    
    def pin_content(self, content: Union[str, bytes], name: Optional[str] = None) -> Optional[str]:
        """Pin content to Pinata"""
        if isinstance(content, str):
            content = content.encode('utf-8')
        
        filename = name or "content"
        files = {'file': (filename, content)}
        
        metadata = {
            'name': filename,
            'keyvalues': {
                'source': 'asi-core',
                'timestamp': str(int(time.time()))
            }
        }
        
        data = {
            'pinataMetadata': json.dumps(metadata),
            'pinataOptions': json.dumps({'cidVersion': 1})
        }
        
        try:
            response = self.session.post(f"{self.base_url}/pinning/pinFileToIPFS", 
                                       files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                cid = result.get('IpfsHash')
                print(f"✅ Content pinned to Pinata: {cid}")
                return cid
            else:
                print(f"❌ Pinata error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Pinata error: {e}")
            return None
    
    def pin_file(self, file_path: Path, name: Optional[str] = None) -> Optional[str]:
        """Pin file to Pinata"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            filename = name or file_path.name
            return self.pin_content(content, filename)
        
        except Exception as e:
            print(f"❌ Failed to read file {file_path}: {e}")
            return None
    
    def unpin_content(self, cid: str) -> bool:
        """Unpin content from Pinata"""
        try:
            response = self.session.delete(f"{self.base_url}/pinning/unpin/{cid}")
            if response.status_code == 200:
                print(f"✅ Content unpinned from Pinata: {cid}")
                return True
            else:
                print(f"❌ Pinata unpin error: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Pinata unpin error: {e}")
            return False
    
    def list_pins(self) -> List[Dict[str, Any]]:
        """List pinned content on Pinata"""
        try:
            response = self.session.get(f"{self.base_url}/data/pinList")
            if response.status_code == 200:
                result = response.json()
                pins = []
                for item in result.get('rows', []):
                    pins.append({
                        'cid': item.get('ipfs_pin_hash'),
                        'name': item.get('metadata', {}).get('name'),
                        'size': item.get('size'),
                        'date_pinned': item.get('date_pinned')
                    })
                return pins
        except Exception as e:
            print(f"❌ Pinata list error: {e}")
        
        return []
    
    def get_pin_status(self, cid: str) -> Optional[Dict[str, Any]]:
        """Get pin status from Pinata"""
        try:
            response = self.session.get(f"{self.base_url}/data/pinList", 
                                      params={'hashContains': cid})
            if response.status_code == 200:
                result = response.json()
                if result.get('rows'):
                    item = result['rows'][0]
                    return {
                        'cid': cid,
                        'status': 'pinned',
                        'service': 'pinata',
                        'name': item.get('metadata', {}).get('name'),
                        'size': item.get('size'),
                        'date_pinned': item.get('date_pinned')
                    }
        except Exception as e:
            print(f"❌ Pinata status error: {e}")
        
        return {
            'cid': cid,
            'status': 'unknown',
            'service': 'pinata'
        }


class IPFSPinningTool:
    """Main IPFS pinning tool"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.services = self._initialize_services()
        self.cache_dir = CACHE_DIR
        self.cache_dir.mkdir(exist_ok=True)
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration"""
        config = {
            'local_ipfs_url': 'http://127.0.0.1:5001',
            'use_pinata': False,
            'pinata_api_key': None,
            'pinata_secret_key': None
        }
        
        # Load from config file
        if config_path:
            config_file = Path(config_path)
        else:
            config_file = CONFIG_DIR / "ipfs-config.json"
        
        if config_file.exists():
            try:
                with open(config_file) as f:
                    file_config = json.load(f)
                config.update(file_config)
            except Exception as e:
                print(f"⚠️ Failed to load config: {e}")
        
        # Override with environment variables
        config.update({
            'local_ipfs_url': os.getenv('IPFS_API_URL', config['local_ipfs_url']),
            'use_pinata': os.getenv('USE_PINATA', '').lower() == 'true',
            'pinata_api_key': os.getenv('PINATA_API_KEY', config['pinata_api_key']),
            'pinata_secret_key': os.getenv('PINATA_SECRET_KEY', config['pinata_secret_key'])
        })
        
        return config
    
    def _initialize_services(self) -> List[IPFSPinningService]:
        """Initialize available IPFS services"""
        services = []
        
        # Local IPFS
        local_service = LocalIPFSService(self.config['local_ipfs_url'])
        services.append(('local', local_service))
        
        # Pinata
        if (self.config['use_pinata'] and 
            self.config['pinata_api_key'] and 
            self.config['pinata_secret_key']):
            pinata_service = PinataService(
                self.config['pinata_api_key'],
                self.config['pinata_secret_key']
            )
            services.append(('pinata', pinata_service))
        
        return services
    
    def _save_pin_cache(self, cid: str, service: str, metadata: Dict[str, Any]) -> None:
        """Save pin information to cache"""
        cache_file = self.cache_dir / f"{cid}.json"
        cache_data = {
            'cid': cid,
            'service': service,
            'pinned_at': time.time(),
            'metadata': metadata
        }
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            print(f"⚠️ Failed to save cache: {e}")
    
    def _load_pin_cache(self, cid: str) -> Optional[Dict[str, Any]]:
        """Load pin information from cache"""
        cache_file = self.cache_dir / f"{cid}.json"
        if cache_file.exists():
            try:
                with open(cache_file) as f:
                    return json.load(f)
            except:
                pass
        return None
    
    def pin_content(self, content: Union[str, bytes], name: Optional[str] = None, 
                   service: Optional[str] = None) -> Optional[str]:
        """Pin content using specified or all available services"""
        if service:
            # Use specific service
            for svc_name, svc_obj in self.services:
                if svc_name == service:
                    cid = svc_obj.pin_content(content, name)
                    if cid:
                        self._save_pin_cache(cid, service, {'name': name})
                    return cid
            print(f"❌ Service '{service}' not available")
            return None
        else:
            # Use first available service
            for svc_name, svc_obj in self.services:
                print(f"🔄 Trying service: {svc_name}")
                cid = svc_obj.pin_content(content, name)
                if cid:
                    self._save_pin_cache(cid, svc_name, {'name': name})
                    return cid
            
            print("❌ All services failed")
            return None
    
    def pin_file(self, file_path: Union[str, Path], name: Optional[str] = None,
                service: Optional[str] = None) -> Optional[str]:
        """Pin file using specified or all available services"""
        file_path = Path(file_path)
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return None
        
        # Calculate file hash for deduplication
        file_hash = self._calculate_file_hash(file_path)
        
        print(f"📁 Pinning file: {file_path.name} ({file_path.stat().st_size} bytes)")
        
        if service:
            # Use specific service
            for svc_name, svc_obj in self.services:
                if svc_name == service:
                    cid = svc_obj.pin_file(file_path, name)
                    if cid:
                        self._save_pin_cache(cid, service, {
                            'name': name or file_path.name,
                            'file_path': str(file_path),
                            'file_hash': file_hash,
                            'file_size': file_path.stat().st_size
                        })
                    return cid
            print(f"❌ Service '{service}' not available")
            return None
        else:
            # Use first available service
            for svc_name, svc_obj in self.services:
                print(f"🔄 Trying service: {svc_name}")
                cid = svc_obj.pin_file(file_path, name)
                if cid:
                    self._save_pin_cache(cid, svc_name, {
                        'name': name or file_path.name,
                        'file_path': str(file_path),
                        'file_hash': file_hash,
                        'file_size': file_path.stat().st_size
                    })
                    return cid
            
            print("❌ All services failed")
            return None
    
    def pin_directory(self, directory_path: Union[str, Path], recursive: bool = True) -> List[str]:
        """Pin all files in a directory"""
        directory_path = Path(directory_path)
        if not directory_path.exists() or not directory_path.is_dir():
            print(f"❌ Directory not found: {directory_path}")
            return []
        
        pattern = "**/*" if recursive else "*"
        files = [f for f in directory_path.glob(pattern) if f.is_file()]
        
        print(f"📂 Pinning directory: {directory_path} ({len(files)} files)")
        
        cids = []
        for file_path in files:
            relative_name = str(file_path.relative_to(directory_path))
            cid = self.pin_file(file_path, relative_name)
            if cid:
                cids.append(cid)
        
        print(f"✅ Pinned {len(cids)}/{len(files)} files from directory")
        return cids
    
    def pin_json(self, data: Dict[str, Any], name: Optional[str] = None) -> Optional[str]:
        """Pin JSON data"""
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        return self.pin_content(json_str, name or "data.json")
    
    def pin_url(self, url: str, name: Optional[str] = None) -> Optional[str]:
        """Download and pin content from URL"""
        try:
            print(f"🌐 Downloading from: {url}")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            content = response.content
            if not name:
                # Try to get filename from URL or Content-Disposition
                name = url.split('/')[-1] or "downloaded_file"
                if 'Content-Disposition' in response.headers:
                    try:
                        disposition = response.headers['Content-Disposition']
                        if 'filename=' in disposition:
                            name = disposition.split('filename=')[1].strip('"')
                    except:
                        pass
            
            return self.pin_content(content, name)
            
        except Exception as e:
            print(f"❌ Failed to download from {url}: {e}")
            return None
    
    def unpin_content(self, cid: str, service: Optional[str] = None) -> bool:
        """Unpin content from specified or all services"""
        success = False
        
        if service:
            for svc_name, svc_obj in self.services:
                if svc_name == service:
                    if svc_obj.unpin_content(cid):
                        success = True
                    break
        else:
            # Try all services
            for svc_name, svc_obj in self.services:
                if svc_obj.unpin_content(cid):
                    success = True
        
        # Remove from cache
        cache_file = self.cache_dir / f"{cid}.json"
        if cache_file.exists():
            try:
                cache_file.unlink()
            except:
                pass
        
        return success
    
    def list_pins(self, service: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """List pins from specified or all services"""
        results = {}
        
        if service:
            for svc_name, svc_obj in self.services:
                if svc_name == service:
                    results[svc_name] = svc_obj.list_pins()
                    break
        else:
            for svc_name, svc_obj in self.services:
                results[svc_name] = svc_obj.list_pins()
        
        return results
    
    def get_pin_status(self, cid: str) -> Dict[str, Any]:
        """Get pin status across all services"""
        status = {
            'cid': cid,
            'services': {}
        }
        
        for svc_name, svc_obj in self.services:
            status['services'][svc_name] = svc_obj.get_pin_status(cid)
        
        # Check cache
        cache_data = self._load_pin_cache(cid)
        if cache_data:
            status['cache'] = cache_data
        
        return status
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except:
            return ""
    
    def check_services(self) -> None:
        """Check status of all configured services"""
        print("🔍 Checking IPFS services:")
        
        for svc_name, svc_obj in self.services:
            print(f"\n📡 Service: {svc_name}")
            
            if isinstance(svc_obj, LocalIPFSService):
                info = svc_obj.get_node_info()
                if info:
                    print(f"   Version: {info.get('version', 'unknown')}")
                    print(f"   Peer ID: {info.get('peer_id', 'unknown')}")
                    print(f"   Status: ✅ Connected")
                else:
                    print(f"   Status: ❌ Disconnected")
            
            elif isinstance(svc_obj, PinataService):
                # Test Pinata by listing pins
                try:
                    pins = svc_obj.list_pins()
                    print(f"   Pins: {len(pins)}")
                    print(f"   Status: ✅ Connected")
                except:
                    print(f"   Status: ❌ Authentication failed")


def main():
    parser = argparse.ArgumentParser(description="ASI Core IPFS Pinning Tool")
    parser.add_argument('--config', help='Config file path')
    parser.add_argument('--service', choices=['local', 'pinata'], help='Specific service to use')
    
    # Content sources
    parser.add_argument('--file', type=Path, help='File to pin')
    parser.add_argument('--directory', type=Path, help='Directory to pin')
    parser.add_argument('--recursive', action='store_true', help='Pin directory recursively')
    parser.add_argument('--json', help='JSON data to pin (as string)')
    parser.add_argument('--url', help='URL to download and pin')
    parser.add_argument('--content', help='Text content to pin')
    
    # Options
    parser.add_argument('--name', help='Name for pinned content')
    
    # Actions
    parser.add_argument('--unpin', help='CID to unpin')
    parser.add_argument('--list', action='store_true', help='List all pins')
    parser.add_argument('--status', help='Get status for CID')
    parser.add_argument('--check-services', action='store_true', help='Check service status')
    
    args = parser.parse_args()
    
    # Initialize tool
    tool = IPFSPinningTool(args.config)
    
    # Execute actions
    if args.check_services:
        tool.check_services()
    elif args.unpin:
        if tool.unpin_content(args.unpin, args.service):
            print(f"✅ Successfully unpinned: {args.unpin}")
        else:
            print(f"❌ Failed to unpin: {args.unpin}")
            sys.exit(1)
    elif args.list:
        results = tool.list_pins(args.service)
        print("📋 Pinned content:")
        for service, pins in results.items():
            print(f"\n🔧 Service: {service}")
            for pin in pins:
                print(f"   {pin['cid']} - {pin.get('name', 'unnamed')}")
    elif args.status:
        status = tool.get_pin_status(args.status)
        print(f"📊 Pin status for {args.status}:")
        for service, svc_status in status['services'].items():
            print(f"   {service}: {svc_status['status']}")
    elif args.file:
        cid = tool.pin_file(args.file, args.name, args.service)
        if cid:
            print(f"✅ File pinned successfully: {cid}")
        else:
            sys.exit(1)
    elif args.directory:
        cids = tool.pin_directory(args.directory, args.recursive)
        if cids:
            print(f"✅ Directory pinned successfully: {len(cids)} files")
            for cid in cids:
                print(f"   {cid}")
        else:
            sys.exit(1)
    elif args.json:
        try:
            data = json.loads(args.json)
            cid = tool.pin_json(data, args.name)
            if cid:
                print(f"✅ JSON pinned successfully: {cid}")
            else:
                sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON: {e}")
            sys.exit(1)
    elif args.url:
        cid = tool.pin_url(args.url, args.name)
        if cid:
            print(f"✅ URL content pinned successfully: {cid}")
        else:
            sys.exit(1)
    elif args.content:
        cid = tool.pin_content(args.content, args.name, args.service)
        if cid:
            print(f"✅ Content pinned successfully: {cid}")
        else:
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()