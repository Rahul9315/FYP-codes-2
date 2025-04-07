import subprocess
import time
import webbrowser
import requests
import signal
import sys

def is_flask_up():
    """Check if Flask server is up by sending a GET request."""
    try:
        response = requests.get("http://127.0.0.1:5000")
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def terminate_processes(processes):
    """Terminate all running processes."""
    for process in processes:
        print(f"Terminating process {process.pid}...")
        process.terminate()

def main():
    # Start the Blocking and Unblocking service
    print("Starting Blocking and Unblocking Service...")
    process1 = subprocess.Popen(["python", "blocking_and_unblocking_ip.py"])

    time.sleep(5)
    # Start the Flask Application
    print("Starting Flask Application...")
    process2 = subprocess.Popen(["python", "Live_NIDs_v4_1.py"])

    processes = [process1, process2]

    try:
        print("Waiting for Flask server to start...")
        while not is_flask_up():
            time.sleep(20)  # Wait for Flask to be ready

        print("Opening Flask Web App...")
        webbrowser.open("http://127.0.0.1:5000")

        # Wait for user to terminate with Ctrl+C or another interrupt
        print("Press Ctrl+C to quit and terminate processes.")

        # Keep the script running until interrupted
        signal.pause()

    except KeyboardInterrupt:
        print("\nDetected interruption, terminating processes...")
        terminate_processes(processes)
        sys.exit(0)

if __name__ == "__main__":
    main()
