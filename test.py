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


SUPABASE_URL = "https://ehpxbrdnnfzeyvhtizwq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVocHhicmRubmZ6ZXl2aHRpendxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzc3NzI5NjAsImV4cCI6MjA1MzM0ODk2MH0.To1EcmSMUJrXMWJZDfu6CjMdRNuiINLXR8pTXaaAEsI"
