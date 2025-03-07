from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import platform
import socket
from supabase import create_client, Client

# Supabase Credentials (Replace with your actual values)
SUPABASE_URL = "https://ehpxbrdnnfzeyvhtizwq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVocHhicmRubmZ6ZXl2aHRpendxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzc3NzI5NjAsImV4cCI6MjA1MzM0ODk2MH0.To1EcmSMUJrXMWJZDfu6CjMdRNuiINLXR8pTXaaAEsI"

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)
CORS(app)

# Get current device (hostname)
def get_device_name():
    return socket.gethostname()

# Check if OS is Windows or Linux
def is_windows():
    return platform.system().lower() == "windows"

# Function to block an IP address
def block_ip(ip):
    try:
        device_name = get_device_name()  # Get device hostname

        if is_windows():
            os.system(f'netsh advfirewall firewall add rule name="Block_{ip}" dir=in action=block remoteip={ip}')
        else:
            os.system(f'sudo iptables -A INPUT -s {ip} -j DROP')
            os.system(f'sudo ufw deny from {ip}')

        # Save IP & Hostname to Supabase
        supabase.table("blocked_ips").insert({
            "ip_address": ip,
            "hostname": device_name,  # Save hostname
            "status": "blocked"
        }).execute()

        print(f"Blocked & Saved IP: {ip} (Device: {device_name})")
        return f"Blocked IP: {ip} (Device: {device_name})"
    except Exception as e:
        return f"Error blocking IP {ip}: {str(e)}"

# Function to unblock an IP address (Matching hostname)
def unblock_ip(ip):
    try:
        device_name = get_device_name()  # Get current hostname

        if is_windows():
            os.system(f'netsh advfirewall firewall delete rule name="Block_{ip}"')
        else:
            os.system(f'sudo iptables -D INPUT -s {ip} -j DROP')
            os.system(f'sudo ufw delete deny from {ip}')

        # Remove the IP from Supabase if it matches the current hostname
        supabase.table("blocked_ips").delete().match({
            "ip_address": ip,
            "hostname": device_name  # Ensure it only removes entries from this device
        }).execute()

        print(f"✅ Unblocked & Removed IP: {ip} (Device: {device_name})")
        return f"Unblocked IP: {ip} (Device: {device_name})"
    except Exception as e:
        return f"Error unblocking IP {ip}: {str(e)}"

# API to block a specific IP (Called when "Block IP" button is clicked)
@app.route('/block_ip', methods=['POST'])
def api_block_ip():
    try:
        ip = request.json.get("ip")
        if ip:
            message = block_ip(ip)
            return jsonify({"message": message, "success": True})
        return jsonify({"error": "No IP provided", "success": False}), 400
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

# API to unblock a specific IP (Called when "Unblock IP" button is clicked)
@app.route('/unblock_ip', methods=['POST'])
def api_unblock_ip():
    try:
        ip = request.json.get("ip")
        if ip:
            message = unblock_ip(ip)
            return jsonify({"message": message, "success": True})
        return jsonify({"error": "No IP provided", "success": False}), 400
    except Exception as e:
        return jsonify({"error": str(e), "success": False}), 500

# API to list blocked IPs for the current device only
@app.route('/blocked_ips', methods=['GET'])
def api_list_blocked_ips():
    try:
        device_name = get_device_name()  # Get the current device's hostname

        # Fetch only IPs associated with this hostname
        response = supabase.table("blocked_ips").select("ip_address", "hostname", "status") \
            .eq("hostname", device_name) \
            .execute()

        return jsonify({"blocked_ips": response.data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(port=5001, debug=True)
