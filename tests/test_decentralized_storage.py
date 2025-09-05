#!/usr/bin/env python3
"""
Tests für die dezentrale Speicherfunktionalität des ASI-Systems
"""

from unittest.mock import MagicMock, patch

import pytest

from asi_core.processing import process_reflection
from asi_core.storage import (
    create_metadata,
    persist_metadata_on_arweave,
    upload_to_ipfs,
)


class TestProcessing:
    """Tests für die Reflexionsverarbeitung"""

    def test_process_reflection_basic(self):
        """Test der grundlegenden Reflexionsverarbeitung"""
        text = "Test-Reflexion für das ASI-System"
        result = process_reflection(text)

        assert result["type"] == "reflection"
        assert result["text_content_anonymized"] == text
        assert "timestamp" in result
        assert isinstance(result["tags"], list)
        assert result["context"]["device"] == "simulated"

    def test_process_reflection_empty_string(self):
        """Test mit leerem String"""
        result = process_reflection("")

        assert result["type"] == "reflection"
        assert result["text_content_anonymized"] == ""
        assert "timestamp" in result


class TestMetadata:
    """Tests für Metadaten-Funktionen"""

    def test_create_metadata_basic(self):
        """Test der Metadaten-Erstellung"""
        cid = "QmTest123456789"
        original_data = {
            "type": "reflection",
            "timestamp": "2023-01-01T00:00:00",
            "tags": ["#test", "#demo"],
            "context": {"device": "test"},
        }

        metadata = create_metadata(cid, original_data)

        assert metadata["ipfs_cid"] == cid
        assert metadata["content_type"] == "application/json"
        assert metadata["data_type"] == "reflection"
        assert metadata["timestamp"] == "2023-01-01T00:00:00"
        assert metadata["tags"] == ["#test", "#demo"]
        assert metadata["storage_layer"] == "ipfs"
        assert metadata["metadata_layer"] == "arweave"

    def test_create_metadata_missing_fields(self):
        """Test mit fehlenden Feldern in den ursprünglichen Daten"""
        cid = "QmTest789"
        original_data = {"type": "reflection"}

        metadata = create_metadata(cid, original_data)

        assert metadata["ipfs_cid"] == cid
        assert metadata["data_type"] == "reflection"
        assert metadata["tags"] == []
        assert metadata["context"] == {}


class TestArweaveStorage:
    """Tests für Arweave-Speicherung (simuliert)"""

    def test_persist_metadata_on_arweave_success(self, capsys):
        """Test erfolgreiche Metadaten-Persistierung"""
        cid = "QmTestCID"
        metadata = {"test": "data"}

        result = persist_metadata_on_arweave(cid, metadata)

        assert result is True

        captured = capsys.readouterr()
        assert "Persisting metadata for CID QmTestCID on Arweave" in (captured.out)
        assert "erfolgreich" in captured.out


class TestIPFSStorage:
    """Tests für IPFS-Speicherung"""

    @patch("asi_core.storage.ipfshttpclient.connect")
    def test_upload_to_ipfs_success(self, mock_connect, capsys):
        """Test erfolgreicher IPFS-Upload mit Mock"""
        # Mock IPFS-Client
        mock_client = MagicMock()
        mock_client.add_json.return_value = "QmMockCID123"
        mock_connect.return_value = mock_client

        test_data = {
            "type": "reflection",
            "timestamp": "2023-01-01T00:00:00",
            "text_content_anonymized": "Test-Text",
        }

        result = upload_to_ipfs(test_data)

        assert result == "QmMockCID123"
        mock_connect.assert_called_once_with("/ip4/127.0.0.1/tcp/5001")
        mock_client.add_json.assert_called_once_with(test_data)

        captured = capsys.readouterr()
        assert "Erfolgreich auf IPFS hochgeladen" in captured.out

    @patch("asi_core.storage.ipfshttpclient.connect")
    def test_upload_to_ipfs_connection_error(self, mock_connect):
        """Test IPFS-Upload mit Verbindungsfehler"""
        # Mock Connection Error
        mock_connect.side_effect = ConnectionError("Connection failed")

        test_data = {"test": "data"}

        with pytest.raises(RuntimeError) as exc_info:
            upload_to_ipfs(test_data)

        assert "Connection failed" in str(exc_info.value)


class TestIntegration:
    """Integrationstests für den gesamten Workflow"""

    @patch("asi_core.storage.ipfshttpclient.connect")
    def test_full_workflow_mock(self, mock_connect, capsys):
        """Test des gesamten Workflows mit IPFS-Mock"""
        # Mock IPFS-Client
        mock_client = MagicMock()
        mock_client.add_json.return_value = "QmIntegrationTest123"
        mock_connect.return_value = mock_client

        # 1. Reflexion verarbeiten
        text = "Integrations-Test für dezentrale Speicherung"
        processed_data = process_reflection(text)

        # 2. IPFS-Upload
        cid = upload_to_ipfs(processed_data)

        # 3. Metadaten erstellen
        metadata = create_metadata(cid, processed_data)

        # 4. Arweave-Persistierung
        arweave_success = persist_metadata_on_arweave(cid, metadata)

        # Assertions
        assert processed_data["type"] == "reflection"
        assert cid == "QmIntegrationTest123"
        assert metadata["ipfs_cid"] == cid
        assert arweave_success is True

        # Prüfe Console-Output
        captured = capsys.readouterr()
        assert "Erfolgreich auf IPFS hochgeladen" in captured.out
        assert "erfolgreich auf Arweave gespeichert" in captured.out


if __name__ == "__main__":
    # Tests ausführen
    pytest.main([__file__, "-v"])
