import numpy as np
import pandas as pd
import time
import keyboard
import pyshark
from sklearn.feature_selection import VarianceThreshold
from sklearn.model_selection import train_test_split ,cross_val_score
from sklearn.preprocessing import MinMaxScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report



def preprocess_network_data(file_path):

    # Load dataset
    df = pd.read_csv(file_path)

    ## Step 1: Convert Categorical to Numeric ##
    df['Service'] = df['Service'].map({'TCP': 0, 'UDP': 1, 'ICMP': 2})

    # Encode Protocol column
    protocol_map = {protocol: i for i, protocol in enumerate(df['Protocol'].unique())}
    df['Protocol'] = df['Protocol'].map({'QUIC' : 1,'UDP' : 3,'ICMP' : 3,'TCP' : 4,'DNS' : 5,'TLS' : 6,'HTTP' : 7,'MDNS' : 8,'Unknown' : 9})

    # Convert hexadecimal Checksum to decimal
    df['Checksum'] = df['Checksum'].apply(lambda x: int(x, 16))

    # Encode TCP Flags column
    #tcp_flags_map = {flag: i for i, flag in enumerate(df['TCP Flags'].unique())}
    df['TCP Flags'] = df['TCP Flags'].apply(lambda x: int(x ,16))

    # Encode Class and Ethernet Type
    
    df['Ethernet Type'] = df['Ethernet Type'].map({'IPv4': 4, 'IPv6': 6})

    ## Step 2: Drop Unnecessary Columns ##
    df.drop(columns=["Source IP", "Destination IP"], inplace=True)

    

    
    #print(df.head())

    return df


def live_data_preprocessing_and_pridiction(df):
    ## Step 1: Convert Categorical to Numeric ##
    df['Service'] = df['Service'].map({'TCP': 0, 'UDP': 1, 'ICMP': 2})

    # Encode Protocol column
    df['Protocol'] = df['Protocol'].map({'QUIC' : 1,'UDP' : 3,'ICMP' : 3,'TCP' : 4,'DNS' : 5,'TLS' : 6,'HTTP' : 7,'MDNS' : 8,'Unknown' : 9})

    # Convert hexadecimal Checksum to decimal
    df['Checksum'] = df['Checksum'].apply(lambda x: int(x, 16))

    # Encode TCP Flags column
    #tcp_flags_map = {flag: i for i, flag in enumerate(df['TCP Flags'].unique())}
    df['TCP Flags'] = df['TCP Flags'].apply(lambda x: int(x ,16))

    # Encode Class and Ethernet Type
    
    df['Ethernet Type'] = df['Ethernet Type'].map({'IPv4': 4, 'IPv6': 6})

    ## Step 2: Drop Unnecessary Columns ##
    df.drop(columns=["Source IP", "Destination IP"], inplace=True)

    df.drop(columns=dropped_cols, axis=1, inplace=True)    
    df = scaler.transform(df)

    prediction = dec_classifier.predict(df)

    return prediction


def preprocess_network_data_2(file_p, scaler , dropped_cols):

    # Load dataset
    df = pd.read_csv(file_p)

    ## Step 1: Convert Categorical to Numeric ##
    df['Service'] = df['Service'].map({'TCP': 0, 'UDP': 1, 'ICMP': 2})

    # Encode Protocol column
    protocol_map = {protocol: i for i, protocol in enumerate(df['Protocol'].unique())}
    df['Protocol'] = df['Protocol'].map({'QUIC' : 1,'UDP' : 3,'ICMP' : 3,'TCP' : 4,'DNS' : 5,'TLS' : 6,'HTTP' : 7,'MDNS' : 8,'Unknown' : 9})

    # Convert hexadecimal Checksum to decimal
    df['Checksum'] = df['Checksum'].apply(lambda x: int(x, 16))

    # Encode TCP Flags column
    #tcp_flags_map = {flag: i for i, flag in enumerate(df['TCP Flags'].unique())}
    df['TCP Flags'] = df['TCP Flags'].apply(lambda x: int(x ,16))

    # Encode Class and Ethernet Type
    
    df['Ethernet Type'] = df['Ethernet Type'].map({'IPv4': 4, 'IPv6': 6})

    ## Step 2: Drop Unnecessary Columns ##
    df.drop(columns=["Source IP", "Destination IP"], inplace=True)

    df.drop(columns=dropped_cols, axis=1, inplace=True)


    
    df = scaler.transform(df)

    #dec_classifier.fit(df.values.ravel())

    
    #print(df.head())

    return df


# Provide the path to your dataset
file_path = "Network_kali_dataset.csv"

# Call the function to preprocess the data
df = preprocess_network_data(file_path)

df['class'] = df['class'].map({'normal': 0, 'anomaly': 1})


## Step 3: Remove Duplicates and Null Values ##
df.drop_duplicates(inplace=True)
df.dropna(how='any', inplace=True)


## Step 4: Feature Selection - Remove Low Variance Features ##
filter_cols = VarianceThreshold(threshold=0.01)
filter_cols.fit(df)
col_ids = np.where(filter_cols.variances_ <= 0.01)[0]
dropped_cols = [df.columns[i] for i in col_ids] 
df.drop(columns=dropped_cols, axis=1, inplace=True)



#print(df.shape)

# Splitting the model
y = df[['class']]
X = df.drop(columns=['class',], axis=1)

scaler = MinMaxScaler()
X = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)


#print("Input Training Set Shape:", X_train.shape)
#print("Input Testing Set Shape:", X_test.shape)
#print("Output Training Set Shape:", y_train.shape)
#print("Output Testing Set Shape:", y_test.shape)

## Decision Tree algorithm

dec_classifier = DecisionTreeClassifier(ccp_alpha=0.01, random_state=42) # ccp 0.01 for prunning and and less overfitting
start_time = time.time()
dec_classifier.fit(X_train, y_train.values.ravel()) ## values = coverting dataframe values into numpy array ; ravel = it converts the numpy array to 1D array
end_time = time.time()
#print("Total training time: ", end_time - start_time)


start_time = time.time()
y_test_pred = dec_classifier.predict(X_train)
end_time = time.time()
y_test_pred2 = dec_classifier.predict(X_test)
#print("Total testing time: ", end_time - start_time)


#print("Training accuracy is:", str(round(100 * dec_classifier.score(X_train, y_train), 2)) + str("%"))
#print("Testing accuracy is:", str(round(100 * dec_classifier.score(X_test, y_test), 2)) + str("%"))
dec_tree_train_accuracy = 100 * dec_classifier.score(X_train, y_train)
dec_tree_test_accuracy = 100 * dec_classifier.score(X_test, y_test)

#print("1 = Anomaly\n0 = Normal")
#print(y_test['class'].value_counts())

# Compute confusion matrix
cm = confusion_matrix(y_test, y_test_pred2)
#print(cm)
#print("Decision Tree Prediction::::")
#print(f"Correct Guess :: {cm[0][0] + cm[1][1]}\nWrong Guess :: {cm[0][1] + cm [1][0]}\nTotal Guess :: {cm[0][0] + cm[1][1] + cm[0][1] + cm [1][0]}\n\n  ")


# Accuracy
accuracy2 = (accuracy_score(y_test, y_test_pred2)) 
#print(f"Accuracy : {accuracy2* 100:.2f} %")


# Generate classification report
dec_report = classification_report(y_test, y_test_pred2, target_names=['Normal', 'Anomaly'])
#print("Decision tree Classification Report:")
#print(dec_report)

from sklearn.model_selection import cross_val_score

scores = cross_val_score(dec_classifier, X_train, y_train, cv=5)
#print(f"Cross-Validation Accuracy: {scores.mean():.4f} ± {scores.std():.4f}")


"""
#prediction in new dataset 

new23 ="testing.csv"
new_data_test = preprocess_network_data_2(new23, scaler, dropped_cols)

df_original = pd.read_csv(new23)

new_data_test_pridiction = dec_classifier.predict(new_data_test)

df_original["Predicted Class"] = new_data_test_pridiction
df_original['Predicted Class'] = df_original['Predicted Class'].map({0 : 'normal', 1: 'anomaly'})
df_original.to_csv("predicted_results.csv", index=False)

print("Predictions saved in 'predicted_results.csv'")


"""








# ✅ Network Interface (Change accordingly)
INTERFACE = "WiFi"  # Use "eth0" for wired, "wlan0" for Wi-Fi

# ✅ Capture TCP, UDP, ICMP Packets
capture = pyshark.LiveCapture(interface=INTERFACE, bpf_filter="tcp or udp or icmp")

print("🔍 Capturing Live Packets & Predicting Anomalies...\n")

# Store captured packet details
packet_data = []

def capture_live_packets():

    # Capture and process packets
    for packet in capture.sniff_continuously():  # Adjust packet count as needed
        try:

            if keyboard.is_pressed("q"):  # Stop when 'q' is pressed
                print("\nStopping Live Capture... Exiting!\n")
                break

            # Get Ethernet Type
            eth_type = "Unknown"
            if hasattr(packet, 'eth'):
                eth_type = "IPv4" if packet.eth.type == "0x0800" else "IPv6"

            # Get Source & Destination IP
            src_ip = packet.ip.src if hasattr(packet, 'ip') else (packet.ipv6.src if hasattr(packet, 'ipv6') else "0")
            dst_ip = packet.ip.dst if hasattr(packet, 'ip') else (packet.ipv6.dst if hasattr(packet, 'ipv6') else "0")

            # Get Packet Length
            packet_length = packet.length if hasattr(packet, "length") else "Unknown"

            # Initialize variables
            service, src_port, dst_port, tcp_flags, checksum, tcp_window_size, icmp_type = "Unknown", "0", "0", "0", "0", "0", "0"

            # Check Packet Type (TCP, UDP, ICMP)
            if hasattr(packet, 'tcp'):
                service = "TCP"
                src_port = packet.tcp.srcport
                dst_port = packet.tcp.dstport
                tcp_flags = f"{packet.tcp.flags}" if hasattr(packet.tcp, "flags") else "0"
                checksum = f"{packet.tcp.checksum}" if hasattr(packet.tcp, "checksum") else "0"
                tcp_window_size = packet.tcp.window_size if hasattr(packet.tcp, "window_size") else "0"

            elif hasattr(packet, 'udp'):
                service = "UDP"
                src_port = packet.udp.srcport
                dst_port = packet.udp.dstport
                tcp_flags = "0"  # No flags for UDP
                tcp_window_size = "0"
                checksum = f"{packet.udp.checksum}" if hasattr(packet.udp, "checksum") else "0"

            elif hasattr(packet, 'icmp'):
                service = "ICMP"
                src_port, dst_port = "0", "0"  # ICMP doesn't use ports
                icmp_type = packet.icmp.type if hasattr(packet, 'icmp') else "Unknown"
                checksum = f"{packet.icmp.checksum}" if hasattr(packet.icmp, 'checksum') else "Unknown"

            # Detect Protocol (DNS, HTTP, TLS, etc.)
            protocol_name = "Unknown"
            if hasattr(packet, 'dns'):
                protocol_name = "DNS"
            elif hasattr(packet, 'http'):
                protocol_name = "HTTP"
            elif hasattr(packet, 'tls'):
                protocol_name = "TLS"
            elif hasattr(packet, 'tcp'):
                protocol_name = "TCP"
            elif hasattr(packet, 'udp'):
                protocol_name = "UDP"
            elif hasattr(packet, 'icmp'):
                protocol_name = "ICMP"

            # Append data to the list
            
            packet_data = [[eth_type, packet_length, service, src_ip, dst_ip, src_port, dst_port, protocol_name, tcp_flags, checksum, tcp_window_size , icmp_type ]]
            headers = ["Ethernet Type", "Packet Length", "Service", "Source IP", "Destination IP", "Source Port", "Destination Port", "Protocol", "TCP Flags", "Checksum", "TCP Window Size", "ICMP Type"]

            Live_data = pd.DataFrame(packet_data,columns=headers)
            #print(Live_data)

            predictiom = live_data_preprocessing_and_pridiction(Live_data)

            #prediction = dec_classifier.predict(Live_data)
            if predictiom == 0 :
                predictiom = "Normal"
            else:
                predictiom = "Anomaly"


            # Display Real-Time Results
            print(f"Packet: {src_ip} → {dst_ip} | Service: {service} | Protocol: {protocol_name} | Network Satatus: {predictiom}")

            # Store Packet Data for CSV
            #packet_data.append([eth_type, packet_length, service, src_ip, dst_ip, src_port, dst_port, protocol_name, tcp_flags, checksum, tcp_window_size, icmp_type, predicted_class])

        except Exception as e:
            print(f"Error processing packet: {e}\n")


capture_live_packets()