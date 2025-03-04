import subprocess
import time

# Define the scripts to run
scripts = ["blocking_and_unblocking_ip.py", "Live_NIDs_v4_1.py"]

# Store process objects
processes = []

try:
    for script in scripts:
        print(f"Starting {script}...")
        # Start each script in a new process
        process = subprocess.Popen(["python", script], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        processes.append((script, process))
        time.sleep(2)  # Give some time for each process to start

    print("✅ Both scripts are running!")

    # Keep running until user interrupts
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\n🛑 Stopping all processes...")
    for script, process in processes:
        print(f"Stopping {script}...")
        process.terminate()  # Stop the process

    print("🚀 All scripts stopped!")

except Exception as e:
    print(f"⚠ Error: {e}")

