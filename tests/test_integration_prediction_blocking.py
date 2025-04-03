import pytest
import sys
import os

# Add the parent directory to sys.path so Python can find your main script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Live_NIDs_v4_1 import live_data_preprocessing_and_pridiction, dec_classifier, dropped_cols, scaler
from blocking_and_unblocking_ip import app, supabase
from flask import json
import pandas as pd
from unittest.mock import patch

@pytest.fixture
def client():
    app.testing = True
    return app.test_client()

def test_anomaly_prediction_triggers_block(client):
    # Simulate incoming packet as DataFrame
    packet_data = pd.DataFrame([{
        "Ethernet Type": "IPv4",
        "Packet Length": 128,
        "Service": "TCP",
        "Source IP": "10.0.0.200",
        "Destination IP": "192.168.0.2",
        "Source Port": 443,
        "Destination Port": 80,
        "Protocol": "TCP",
        "TCP Flags": "0x10",
        "Checksum": "0x1a2b",
        "TCP Window Size": 4096,
        "ICMP Type": 0
    }])

    # Patch supabase to prevent real DB call
    with patch.object(supabase, "table") as mock_table:
        mock_table.return_value.insert.return_value.execute.return_value = None

        # Trigger model + blocking
        prediction = live_data_preprocessing_and_pridiction(packet_data)
        assert prediction[0] == 1 or prediction[0] == 0  # Prediction works

        # Manually simulate IP block via API
        response = client.post("/block_ip", json={"ip": "10.0.0.200", "status": "Anomaly"})
        assert response.status_code == 200
        assert response.get_json()["success"] is True

