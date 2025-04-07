# NIDPS - Network Intrusion Detection and Prevention System 

NIDPS is a python based network intrusion detection and prevention system that features:
- Real-time packet capturing with **PyShark**
- A UI built with **Flask**
- IP blocking and Unblocking with both Automatic and manual

---

## Features 

- Live network monitoring
- Detection dashboard via web interface
- Simple IP block/unblock logic
- Cross-platform support (Both Windows and Linux)
- Recommended to use on Linux VM
  
---
## SetUp Intrusctions

follow the steps below to get the project up and running

### Clone the Repository

```bash
git clone https://github.com/Rahul9315/FYP-codes-2.git
```

## For Linux And Linux VM ( Optional Settings But Recommended )

While using VM try using Network : **Briged network Adapter** and Promicious Mode : **Allow All** ( this will allow to to capture network traffic of all VMs as well as host PC )
like as in the Screenshot below:

![image](https://github.com/user-attachments/assets/b273db11-4639-4259-b44f-3a8653f7db51)

### Install Required Tools

```bash
sudo apt install wireshark tshark
```

### Adding current user to WireShark group

```bash
sudo usermod -aG wireshark $USER
```

**Note : You must restart the your System or log out/log back in for the group chnages to apply.**

### Verify Tshark working

Run this Command 
```bash
tshark -D
```

if you see a list of interfaces like below then TShark is set up correctly:

![image](https://github.com/user-attachments/assets/1b8899d1-5f5a-42fc-8d3c-111c8efc80fc)


### Set up Python Virtual Environment

```bash
python3 -m venv myvenv
source myvenv/bin/activate
```

You can change your Virtual Environment name to the name of your choice 

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the application

```bash
python run_app.py
```

![image](https://github.com/user-attachments/assets/15846e11-f3c0-4aa5-9bbf-bf8d587d7226)

once started it will automatically open the dashboard at http://127.0.0.1:5000

## For Windows

To run the NIDPS on Windows we have to download WireShark 
https://www.wireshark.org/download.html

NIDPS Uses PyShark which is Python Wrapper of Wireshark that helps in capturing packets in Real-time.

### Set up Python Virtual Environment

```bash
python3 -m venv myvenv
source myvenv/bin/activate
```

You can change your Virtual Environment name to the name of your choice 

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the application

```bash
python run_app.py
```

once started it will automatically open the dashboard at http://127.0.0.1:5000



