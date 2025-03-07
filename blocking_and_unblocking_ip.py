from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import platform
from supabase import create_client, Client

# Supabase Credentials (Replace with your actual values)
SUPABASE_URL = "https://ehpxbrdnnfzeyvhtizwq.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVocHhicmRubmZ6ZXl2aHRpendxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzc3NzI5NjAsImV4cCI6MjA1MzM0ODk2MH0.To1EcmSMUJrXMWJZDfu6CjMdRNuiINLXR8pTXaaAEsI"

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)
CORS(app)

# Check if OS is Windows or Linux
def is_windows():
    return platform.system().lower() == "windows"

# Function to block an IP address
def block_ip(ip):
    try:
        if is_windows():
            os.system(f'netsh advfirewall firewall add rule name="Block_{ip}" dir=in action=block remoteip={ip}')
            i = 0
        else:
            #os.system(f'sudo iptables -A INPUT -s {ip} -j DROP')
            #os.system(f'sudo ufw deny from {ip}')
            i = 2

        # Save the IP in Supabase only when the user clicks "Block IP"
        supabase.table("blocked_ips").insert({"ip_address": ip, "status": "blocked"}).execute()
        print(f"Blocked & Saved IP: {ip}")
        return f"Blocked IP: {ip}"
    except Exception as e:
        return f"Error blocking IP {ip}: {str(e)}"

# Function to unblock an IP address
def unblock_ip(ip):
    try:
        if is_windows():
            #os.system(f'netsh advfirewall firewall delete rule name="Block_{ip}"')
            i = 0
        else:
            #os.system(f'sudo iptables -D INPUT -s {ip} -j DROP')
            #os.system(f'sudo ufw delete deny from {ip}')
            i = 2

        # Remove the IP from Supabase when unblocked
        supabase.table("blocked_ips").delete().eq("ip_address", ip).execute()
        print(f"✅ Unblocked & Removed IP: {ip}")
        return f"Unblocked IP: {ip}"
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

# API to list all blocked IPs
@app.route('/blocked_ips', methods=['GET'])
def api_list_blocked_ips():
    try:
        response = supabase.table("blocked_ips").select("ip_address", "status").execute()
        return jsonify({"blocked_ips": response.data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5001, debug=True)
