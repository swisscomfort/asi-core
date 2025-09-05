"""
ASI Core - IPFS Client
Upload zu IPFS für dezentrale Speicherung
"""

import hashlib
import json
from datetime import datetime
from typing import Dict, List, Optional

import requests


class IPFSClient:
    """Client für IPFS-Operationen"""

    def __init__(self, api_url: str = "http://localhost:5001/api/v0"):
        self.api_url = api_url
        self.session = requests.Session()

    def is_node_running(self) -> bool:
        """
        Prüft, ob ein IPFS-Node erreichbar ist

        Returns:
            bool: True wenn Node erreichbar
        """
        try:
            # Kubo HTTP API erwartet POST für die meisten Endpunkte
            response = self.session.post(f"{self.api_url}/version", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def upload_json(self, data: Dict) -> Optional[str]:
        """
        Lädt JSON-Daten zu IPFS hoch

        Args:
            data: Zu uploadende Daten

        Returns:
            Optional[str]: IPFS-Hash bei Erfolg
        """
        if not self.is_node_running():
            print("IPFS-Node nicht erreichbar. Verwende lokale Simulation.")
            return self._simulate_upload(data)

        try:
            # JSON zu String konvertieren
            json_string = json.dumps(data, ensure_ascii=False)

            # Upload zu IPFS
            files = {"file": ("data.json", json_string, "application/json")}
            response = self.session.post(
                f"{self.api_url}/add",
                files=files,
                params={"pin": "true"},  # Pin für Persistenz
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("Hash")
            else:
                print(f"IPFS Upload Fehler: {response.status_code}")
                return None

        except (requests.RequestException, TypeError, ValueError) as e:
            print(f"IPFS Upload Fehler/Exception: {e}")
            return self._simulate_upload(data)

    def _simulate_upload(self, data: Dict) -> str:
        """
        Simuliert IPFS-Upload für Entwicklung/Testing

        Args:
            data: Daten

        Returns:
            str: Simulierter Hash
        """
        # Generiere determinierten Hash basierend auf Daten
        content = json.dumps(data, sort_keys=True, ensure_ascii=False)
        hash_obj = hashlib.sha256(content.encode("utf-8"))

        # IPFS-ähnlicher Hash (vereinfacht)
        simulated_hash = f"Qm{hash_obj.hexdigest()[:44]}"

        print(f"Simulierter IPFS-Upload: {simulated_hash}")
        return simulated_hash

    def download_json(self, ipfs_hash: str) -> Optional[Dict]:
        """
        Lädt JSON-Daten von IPFS herunter

        Args:
            ipfs_hash: IPFS-Hash der Daten

        Returns:
            Optional[Dict]: Heruntergeladene Daten
        """
        if not self.is_node_running():
            print("IPFS-Node nicht erreichbar. Download nicht möglich.")
            return None

        try:
            # Kubo erwartet POST für /cat
            response = self.session.post(
                f"{self.api_url}/cat", params={"arg": ipfs_hash}
            )

            if response.status_code == 200:
                # Inhalt ist roher JSON-Text (wir haben zuvor JSON hochgeladen)
                try:
                    return response.json()
                except ValueError:
                    return json.loads(response.text)
            else:
                print(f"IPFS Download Fehler: {response.status_code}")
                return None

        except requests.RequestException as e:
            print(f"IPFS Download Exception: {e}")
            return None

    def pin_hash(self, ipfs_hash: str) -> bool:
        """
        Pinnt einen Hash für Persistenz

        Args:
            ipfs_hash: Zu pinnender Hash

        Returns:
            bool: Erfolg des Pinning
        """
        if not self.is_node_running():
            return False

        try:
            response = self.session.post(
                f"{self.api_url}/pin/add", params={"arg": ipfs_hash}
            )
            return response.status_code == 200
        except requests.RequestException as e:
            print(f"IPFS Pin Exception: {e}")
            return False

    def list_pins(self) -> List[str]:
        """
        Listet alle gepinnten Hashes auf

        Returns:
            List[str]: Liste gepinnter Hashes
        """
        if not self.is_node_running():
            return []

        try:
            # Kubo erwartet POST für /pin/ls
            response = self.session.post(f"{self.api_url}/pin/ls")
            if response.status_code == 200:
                data = response.json()
                return list(data.get("Keys", {}).keys())
            return []
        except requests.RequestException as e:
            print(f"IPFS List Pins Exception: {e}")
            return []

    def get_node_info(self) -> Optional[Dict]:
        """
        Ruft Informationen über den IPFS-Node ab

        Returns:
            Optional[Dict]: Node-Informationen
        """
        if not self.is_node_running():
            return None

        try:
            # Version
            version_resp = self.session.post(f"{self.api_url}/version")
            version_data = (
                version_resp.json() if version_resp.status_code == 200 else {}
            )

            # ID
            id_resp = self.session.post(f"{self.api_url}/id")
            id_data = id_resp.json() if id_resp.status_code == 200 else {}

            return {
                "version": version_data.get("Version", "unknown"),
                "peer_id": id_data.get("ID", "unknown"),
                "addresses": id_data.get("Addresses", []),
                "status": "running",
            }
        except requests.RequestException as e:
            print(f"IPFS Node Info Exception: {e}")
            return None

    def upload_reflection(self, processed_reflection: Dict) -> Optional[str]:
        """
        Lädt eine verarbeitete Reflexion zu IPFS hoch

        Args:
            processed_reflection: Verarbeitete Reflexionsdaten

        Returns:
            Optional[str]: IPFS-Hash bei Erfolg
        """
        # Metadaten hinzufügen
        upload_data = {
            "asi_version": "1.0",
            "upload_timestamp": datetime.now().isoformat(),
            "data_type": "reflection",
            "reflection": processed_reflection,
        }

        return self.upload_json(upload_data)

    def create_manifest(self, reflection_hashes: List[str]) -> Optional[str]:
        """
        Erstellt ein Manifest mit mehreren Reflexions-Hashes

        Args:
            reflection_hashes: Liste von IPFS-Hashes

        Returns:
            Optional[str]: Hash des Manifests
        """
        manifest = {
            "asi_manifest_version": "1.0",
            "created": datetime.now().isoformat(),
            "type": "reflection_collection",
            "count": len(reflection_hashes),
            "reflections": reflection_hashes,
        }

        return self.upload_json(manifest)


class IPFSGateway:
    """Gateway für öffentlichen IPFS-Zugriff"""

    def __init__(self, gateway_url: str = "https://ipfs.io/ipfs/"):
        self.gateway_url = gateway_url

    def get_public_url(self, ipfs_hash: str) -> str:
        """
        Erstellt eine öffentliche URL für einen IPFS-Hash

        Args:
            ipfs_hash: IPFS-Hash

        Returns:
            str: Öffentliche URL
        """
        return f"{self.gateway_url}{ipfs_hash}"

    def verify_accessibility(self, ipfs_hash: str) -> bool:
        """
        Prüft, ob ein Hash über das Gateway erreichbar ist

        Args:
            ipfs_hash: Zu prüfender Hash

        Returns:
            bool: True wenn erreichbar
        """
        try:
            url = self.get_public_url(ipfs_hash)
            response = requests.head(url, timeout=10)
            return response.status_code == 200
        except requests.RequestException:
            return False


if __name__ == "__main__":
    # Beispiel-Nutzung
    client = IPFSClient()

    print("=== IPFS Client Test ===")

    # Node-Status prüfen
    if client.is_node_running():
        print("✓ IPFS-Node läuft")
        info = client.get_node_info()
        if info:
            print(f"Version: {info['version']}")
            print(f"Peer ID: {info['peer_id'][:20]}...")
    else:
        print("⚠ IPFS-Node nicht erreichbar (Simulation aktiv)")

    # Test-Upload
    test_data = {
        "content": "Test-Reflexion für IPFS",
        "timestamp": datetime.now().isoformat(),
        "privacy": "anonymous",
    }

    hash_result = client.upload_json(test_data)
    if hash_result:
        print(f"Upload erfolgreich: {hash_result}")

        # Gateway-URL
        gateway = IPFSGateway()
        public_url = gateway.get_public_url(hash_result)
        print(f"Öffentliche URL: {public_url}")
    else:
        print("Upload fehlgeschlagen")
