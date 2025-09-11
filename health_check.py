#!/usr/bin/env python3
"""
ASI-Core Health Check and System Monitor
Prüft die Systemgesundheit und zeigt wichtige Metriken an
"""

import json
import psutil
import sqlite3
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess
import sys

class ASIHealthMonitor:
    def __init__(self, config_path: str = "config/settings.json"):
        self.config_path = Path(config_path)
        self.data_dir = Path("data")
        self.logs_dir = Path("logs")
        
    def load_config(self) -> Dict[str, Any]:
        """Load system configuration"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            return {"error": f"Config load error: {e}"}
    
    def check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_gb = memory.available / (1024**3)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            disk_free_gb = disk.free / (1024**3)
            
            return {
                "status": "healthy" if cpu_percent < 80 and memory_percent < 80 and disk_percent < 80 else "warning",
                "cpu": {
                    "usage_percent": round(cpu_percent, 1),
                    "cores": cpu_count,
                    "status": "normal" if cpu_percent < 80 else "high"
                },
                "memory": {
                    "usage_percent": round(memory_percent, 1),
                    "available_gb": round(memory_available_gb, 2),
                    "total_gb": round(memory.total / (1024**3), 2),
                    "status": "normal" if memory_percent < 80 else "high"
                },
                "disk": {
                    "usage_percent": round(disk_percent, 1),
                    "free_gb": round(disk_free_gb, 2),
                    "total_gb": round(disk.total / (1024**3), 2),
                    "status": "normal" if disk_percent < 80 else "high"
                }
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def check_database(self) -> Dict[str, Any]:
        """Check database health and statistics"""
        try:
            db_path = self.data_dir / "asi_local.db"
            if not db_path.exists():
                return {"status": "missing", "error": "Database file not found"}
            
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Get database size
            db_size_mb = db_path.stat().st_size / (1024**2)
            
            # Count reflections (if table exists)
            try:
                cursor.execute("SELECT COUNT(*) FROM reflections")
                reflection_count = cursor.fetchone()[0]
            except sqlite3.OperationalError:
                reflection_count = 0
            
            # Check database integrity
            cursor.execute("PRAGMA integrity_check")
            integrity_result = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "status": "healthy" if integrity_result == "ok" else "error",
                "size_mb": round(db_size_mb, 2),
                "reflection_count": reflection_count,
                "integrity": integrity_result,
                "path": str(db_path)
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def check_data_directories(self) -> Dict[str, Any]:
        """Check data directory structure and content"""
        required_dirs = [
            "reflections",
            "backups", 
            "states",
            "search",
            "local"
        ]
        
        results = {}
        total_files = 0
        total_size_mb = 0
        
        for dir_name in required_dirs:
            dir_path = self.data_dir / dir_name
            
            if dir_path.exists():
                files = list(dir_path.glob("*"))
                file_count = len([f for f in files if f.is_file()])
                
                # Calculate directory size
                dir_size = 0
                for file_path in dir_path.rglob("*"):
                    if file_path.is_file():
                        dir_size += file_path.stat().st_size
                
                dir_size_mb = dir_size / (1024**2)
                
                results[dir_name] = {
                    "status": "exists",
                    "file_count": file_count,
                    "size_mb": round(dir_size_mb, 2)
                }
                
                total_files += file_count
                total_size_mb += dir_size_mb
            else:
                results[dir_name] = {
                    "status": "missing",
                    "file_count": 0,
                    "size_mb": 0
                }
        
        return {
            "status": "healthy" if all(r["status"] == "exists" for r in results.values()) else "warning",
            "directories": results,
            "total_files": total_files,
            "total_size_mb": round(total_size_mb, 2)
        }
    
    def check_services(self) -> Dict[str, Any]:
        """Check external services availability"""
        services = {}
        
        # Check IPFS (if enabled)
        try:
            response = requests.get("http://localhost:5001/api/v0/version", timeout=5)
            if response.status_code == 200:
                ipfs_version = response.json().get("Version", "unknown")
                services["ipfs"] = {
                    "status": "running",
                    "version": ipfs_version,
                    "endpoint": "http://localhost:5001"
                }
            else:
                services["ipfs"] = {"status": "error", "error": "API not responding"}
        except requests.exceptions.RequestException:
            services["ipfs"] = {"status": "not_available", "error": "Connection failed"}
        
        # Check ASI-Core API (if running)
        try:
            response = requests.get("http://localhost:5000/api/health", timeout=5)
            if response.status_code == 200:
                services["asi_api"] = {
                    "status": "running",
                    "endpoint": "http://localhost:5000"
                }
            else:
                services["asi_api"] = {"status": "error", "error": "API not responding"}
        except requests.exceptions.RequestException:
            services["asi_api"] = {"status": "not_running", "error": "API not available"}
        
        return services
    
    def check_logs(self) -> Dict[str, Any]:
        """Check log files and recent errors"""
        if not self.logs_dir.exists():
            return {"status": "no_logs", "error": "Logs directory not found"}
        
        log_files = list(self.logs_dir.glob("*.log"))
        
        if not log_files:
            return {"status": "no_logs", "files": []}
        
        results = {
            "status": "available",
            "files": [],
            "recent_errors": [],
            "total_size_mb": 0
        }
        
        total_size = 0
        
        for log_file in log_files[-5:]:  # Check last 5 log files
            size = log_file.stat().st_size
            total_size += size
            
            # Check for recent errors (last 100 lines)
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    recent_lines = lines[-100:] if len(lines) > 100 else lines
                    
                    errors = [line.strip() for line in recent_lines 
                             if "ERROR" in line or "CRITICAL" in line]
                    
                    results["files"].append({
                        "name": log_file.name,
                        "size_mb": round(size / (1024**2), 2),
                        "recent_errors": len(errors)
                    })
                    
                    results["recent_errors"].extend(errors[-5:])  # Last 5 errors
            except Exception as e:
                results["files"].append({
                    "name": log_file.name,
                    "size_mb": round(size / (1024**2), 2),
                    "error": f"Could not read: {e}"
                })
        
        results["total_size_mb"] = round(total_size / (1024**2), 2)
        results["recent_errors"] = results["recent_errors"][-10:]  # Keep last 10 errors
        
        return results
    
    def check_python_environment(self) -> Dict[str, Any]:
        """Check Python environment and dependencies"""
        try:
            python_version = sys.version
            
            # Check if in virtual environment
            in_venv = hasattr(sys, 'real_prefix') or (
                hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
            )
            
            # Try to import key dependencies
            dependencies = {}
            key_packages = [
                'flask', 'sqlite3', 'json', 'pathlib', 
                'requests', 'psutil', 'web3', 'ipfshttpclient'
            ]
            
            for package in key_packages:
                try:
                    __import__(package)
                    dependencies[package] = "available"
                except ImportError:
                    dependencies[package] = "missing"
            
            return {
                "status": "healthy",
                "python_version": python_version.split()[0],
                "virtual_environment": in_venv,
                "dependencies": dependencies,
                "missing_packages": [pkg for pkg, status in dependencies.items() if status == "missing"]
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get general system information"""
        try:
            return {
                "timestamp": datetime.now().isoformat(),
                "platform": psutil.platform,
                "hostname": psutil.hostname(),
                "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
                "asi_core_path": str(Path.cwd().absolute()),
                "python_executable": sys.executable
            }
        except Exception as e:
            return {"error": str(e)}
    
    def run_full_health_check(self) -> Dict[str, Any]:
        """Run complete health check"""
        print("🏥 ASI-Core Health Check")
        print("=" * 40)
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "unknown",
            "checks": {}
        }
        
        # Run all checks
        checks = [
            ("system_info", self.get_system_info),
            ("system_resources", self.check_system_resources),
            ("python_environment", self.check_python_environment),
            ("database", self.check_database),
            ("data_directories", self.check_data_directories),
            ("services", self.check_services),
            ("logs", self.check_logs)
        ]
        
        error_count = 0
        warning_count = 0
        
        for check_name, check_func in checks:
            print(f"Running {check_name}...")
            try:
                result = check_func()
                results["checks"][check_name] = result
                
                status = result.get("status", "unknown")
                if status == "error":
                    error_count += 1
                    print(f"  ❌ {check_name}: ERROR")
                elif status == "warning":
                    warning_count += 1
                    print(f"  ⚠️  {check_name}: WARNING")
                elif status in ["healthy", "running", "available"]:
                    print(f"  ✅ {check_name}: OK")
                else:
                    print(f"  ℹ️  {check_name}: {status}")
                    
            except Exception as e:
                error_count += 1
                results["checks"][check_name] = {"status": "error", "error": str(e)}
                print(f"  ❌ {check_name}: FAILED - {e}")
        
        # Determine overall status
        if error_count > 0:
            results["overall_status"] = "critical"
        elif warning_count > 0:
            results["overall_status"] = "warning"
        else:
            results["overall_status"] = "healthy"
        
        results["summary"] = {
            "total_checks": len(checks),
            "errors": error_count,
            "warnings": warning_count,
            "passed": len(checks) - error_count - warning_count
        }
        
        return results
    
    def print_summary(self, results: Dict[str, Any]):
        """Print formatted health check summary"""
        print("\n" + "=" * 40)
        print("📊 HEALTH CHECK SUMMARY")
        print("=" * 40)
        
        overall = results["overall_status"]
        summary = results["summary"]
        
        status_emoji = {
            "healthy": "🟢",
            "warning": "🟡", 
            "critical": "🔴"
        }
        
        print(f"Overall Status: {status_emoji.get(overall, '⚪')} {overall.upper()}")
        print(f"Checks: {summary['passed']} passed, {summary['warnings']} warnings, {summary['errors']} errors")
        
        # Key metrics
        if "system_resources" in results["checks"]:
            resources = results["checks"]["system_resources"]
            if "cpu" in resources:
                print(f"CPU Usage: {resources['cpu']['usage_percent']}%")
                print(f"Memory Usage: {resources['memory']['usage_percent']}%")
                print(f"Disk Usage: {resources['disk']['usage_percent']}%")
        
        if "database" in results["checks"]:
            db = results["checks"]["database"]
            if "reflection_count" in db:
                print(f"Reflections: {db['reflection_count']}")
                print(f"Database Size: {db['size_mb']} MB")
        
        if "data_directories" in results["checks"]:
            dirs = results["checks"]["data_directories"]
            if "total_files" in dirs:
                print(f"Data Files: {dirs['total_files']}")
                print(f"Data Size: {dirs['total_size_mb']} MB")
        
        print("\n🔧 To fix issues, run: python health_check.py --fix")
        print("📖 For details, run: python health_check.py --verbose")

def main():
    """Main health check execution"""
    monitor = ASIHealthMonitor()
    results = monitor.run_full_health_check()
    monitor.print_summary(results)
    
    # Save results
    health_file = Path("logs/health_check.json")
    health_file.parent.mkdir(exist_ok=True)
    
    with open(health_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: {health_file}")
    
    # Exit with appropriate code
    if results["overall_status"] == "critical":
        sys.exit(1)
    elif results["overall_status"] == "warning":
        sys.exit(2)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
