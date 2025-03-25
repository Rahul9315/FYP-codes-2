import platform
import socket

def get_system_info():
    os_name = platform.system().lower()
    device_name = socket.gethostname()
    return os_name, device_name

# Example usage
os_name, device_name = get_system_info()
print(f"Operating System: {os_name}")
print(f"Device Name: {device_name}")

