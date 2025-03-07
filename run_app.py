import subprocess
import time
import webbrowser

print("Starting Blocking and Unblocking Service...")
subprocess.Popen(["python", "blocking_and_unblocking_ip.py"])

time.sleep(2)

print("Starting Flask Application...")
subprocess.Popen(["python", "Live_NIDs_v4_1.py"])

time.sleep(3)

print("Opening Flask Web App...")
webbrowser.open("http://127.0.0.1:5000")
