import pytest
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.tree import DecisionTreeClassifier
import sys
import os

# Add the parent directory to sys.path so Python can find your main script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Live_NIDs_v4_1 import (
    preprocess_network_data,
    preprocess_network_data_2,
    live_data_preprocessing_and_pridiction,
    get_system_ip
)

# Sample dataframe fixture
@pytest.fixture
def sample_df():
    data = {
        "Ethernet Type": ["IPv4", "IPv6"],
        "Packet Length": [64, 128],
        "Service": ["TCP", "UDP"],
        "Source IP": ["192.168.0.1", "10.0.0.1"],
        "Destination IP": ["192.168.0.2", "10.0.0.2"],
        "Source Port": [1234, 443],
        "Destination Port": [80, 53],
        "Protocol": ["TCP", "UDP"],
        "TCP Flags": ["0x02", "0x10"],
        "Checksum": ["0x1a2b", "0x3c4d"],
        "TCP Window Size": [8192, 4096],
        "ICMP Type": [0, 0],
        "class": ["normal", "anomaly"]
    }
    return pd.DataFrame(data)

def test_preprocess_network_data(tmp_path, sample_df):
    test_file = tmp_path / "test.csv"
    sample_df.to_csv(test_file, index=False)
    df_processed = preprocess_network_data(str(test_file))

    assert not df_processed.isnull().values.any()
    assert "Service" in df_processed.columns
    assert df_processed["Service"].isin([0, 1, 2]).all()

def test_get_system_ip_returns_string():
    ip = get_system_ip()
    assert isinstance(ip, str)
    assert "." in ip or "Error" in ip

def test_preprocess_network_data_2_scaling(sample_df):
    df = sample_df.copy()
    df["Service"] = df["Service"].map({"TCP": 0, "UDP": 1})
    df["Protocol"] = df["Protocol"].map({"TCP": 4, "UDP": 3})
    df["Checksum"] = df["Checksum"].apply(lambda x: int(x, 16))
    df["TCP Flags"] = df["TCP Flags"].apply(lambda x: int(x, 16))
    df["Ethernet Type"] = df["Ethernet Type"].map({"IPv4": 4, "IPv6": 6})
    df = df.drop(["Source IP", "Destination IP", "class"], axis=1)

    dropped_cols = ["Source Port"]
    df.drop(columns=dropped_cols, inplace=True)
    scaler = MinMaxScaler()
    scaler.fit(df)

    df_scaled = preprocess_network_data_2(str("mocked.csv"), scaler, dropped_cols)
    assert isinstance(df_scaled, np.ndarray)

def test_live_data_prediction(sample_df):
    df = sample_df.drop(columns=["class"])
    df["Service"] = df["Service"].map({"TCP": 0, "UDP": 1})
    df["Protocol"] = df["Protocol"].map({"TCP": 4, "UDP": 3})
    df["Checksum"] = df["Checksum"].apply(lambda x: int(x, 16))
    df["TCP Flags"] = df["TCP Flags"].apply(lambda x: int(x, 16))
    df["Ethernet Type"] = df["Ethernet Type"].map({"IPv4": 4, "IPv6": 6})
    df.drop(columns=["Source IP", "Destination IP"], inplace=True)

    X = df.copy()
    y = [0, 1]
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)

    clf = DecisionTreeClassifier()
    clf.fit(X_scaled, y)

    # Inject model and globals for test
    from Live_NIDs_v4_1 import dec_classifier, dropped_cols
    dec_classifier = clf
    dropped_cols = []

    from Live_NIDs_v4_1 import scaler as global_scaler
    global_scaler = scaler

    prediction = live_data_preprocessing_and_pridiction(df)
    assert prediction[0] in [0, 1]
