import pytest
from unittest.mock import patch, MagicMock
from flask import json
import sys
import os

# Add the parent directory to sys.path so Python can find your main script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from blocking_and_unblocking_ip import app  

@pytest.fixture
def client():
    app.testing = True
    return app.test_client()

def test_block_ip_success(client):
    test_ip = "192.168.1.100"
    test_status = "anomaly"

    with patch("blocking_and_unblocking_ip.block_ip") as mock_block_ip:
        mock_block_ip.return_value = f"Blocked IP: {test_ip} (Device: TEST-HOST)"

        response = client.post("/block_ip", json={"ip": test_ip, "status": test_status})
        data = response.get_json()

        assert response.status_code == 200
        assert data["success"] is True
        assert "Blocked IP" in data["message"]

def test_block_ip_missing_params(client):
    response = client.post("/block_ip", json={"ip": "192.168.1.100"})  # No status
    data = response.get_json()
    assert response.status_code == 400
    assert data["success"] is False

def test_unblock_ip_success(client):
    test_ip = "192.168.1.100"

    with patch("blocking_and_unblocking_ip.unblock_ip") as mock_unblock_ip:
        mock_unblock_ip.return_value = f"Unblocked IP: {test_ip} (Device: TEST-HOST)"

        response = client.post("/unblock_ip", json={"ip": test_ip})
        data = response.get_json()

        assert response.status_code == 200
        assert data["success"] is True
        assert "Unblocked IP" in data["message"]

def test_unblock_ip_no_ip(client):
    response = client.post("/unblock_ip", json={})
    data = response.get_json()
    assert response.status_code == 400
    assert data["success"] is False

def test_list_blocked_ips_success(client):
    mock_data = [{"ip_address": "192.168.1.100", "hostname": "TEST-HOST", "status": "anomaly"}]

    with patch("blocking_and_unblocking_ip.supabase") as mock_supabase:
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = mock_data

        response = client.get("/blocked_ips")
        data = response.get_json()

        assert response.status_code == 200
        assert "blocked_ips" in data
        assert isinstance(data["blocked_ips"], list)
        assert data["blocked_ips"][0]["ip_address"] == "192.168.1.100"
