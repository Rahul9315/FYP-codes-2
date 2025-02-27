# source my_venv_env/bi0ctivate  # to open the python environment
# python file_name.py   #to run the file
# deactivate  # when done with the python environment

import pyshark
import csv
from datetime import datetime

# Define the network interface (Change accordingly)
INTERFACE = "WiFi"  # Example: Use "eth0" for wired, "wlan0" for Wi-Fi

# Capture only UDP packets
capture = pyshark.LiveCapture(interface=INTERFACE, bpf_filter="udp or tcp or icmp")

# Define CSV file name with timestamp
csv_filename = f"captured_packets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

print(f"🔍 Capturing Live Packets and Saving to {csv_filename}...\n")

# Open CSV file and define header
with open(csv_filename, mode="w", newline="") as file:
    csv_writer = csv.writer(file)
    headers = ["Ethernet Type", "Packet Length", "Service", "Source IP", "Destination IP",
               "Source Port", "Destination Port", "Protocol", "TCP Flags", "Checksum", "TCP Window Size", "ICMP Type"]
    csv_writer.writerow(headers)

    # Capture and process packets
    for packet in capture.sniff_continuously(packet_count=2000):  # Capture 20 packets
        try:
            
            # Get Ethernet Type (IPv4 or IPv6)
            eth_type = "Unknown"
            if hasattr(packet, 'eth'):
                eth_type = "IPv4" if packet.eth.type == "0x0800" else "IPv6"

            # Get Source & Destination IP Addresses
            src_ip = packet.ip.src if hasattr(packet, 'ip') else (packet.ipv6.src if hasattr(packet, 'ipv6') else "0")
            dst_ip = packet.ip.dst if hasattr(packet, 'ip') else (packet.ipv6.dst if hasattr(packet, 'ipv6') else "0")

            # Get Packet Length
            packet_length = packet.length if hasattr(packet, "length") else "Unknown"

            # Initialize variables
            service, src_port, dst_port, tcp_flags, checksum, tcp_window_size , icmp_type = "Unknown", "0", "0", "0", "0","0", "0"

            # Check if it's a TCP or UDP packet
            if hasattr(packet, 'tcp'):
                service = "TCP"
                src_port = packet.tcp.srcport
                dst_port = packet.tcp.dstport

                # Extract TCP Flags
                tcp_flags = f"{packet.tcp.flags}" if hasattr(packet.tcp, "flags") else "0"

                # Extract TCP Checksum
                checksum = f"{packet.tcp.checksum}" if hasattr(packet.tcp, "checksum") else "0"

                # Extract TCP Window Size
                tcp_window_size = packet.tcp.window_size if hasattr(packet.tcp, "window_size") else "0"

            elif hasattr(packet, 'udp'):
                service = "UDP"
                src_port = packet.udp.srcport
                dst_port = packet.udp.dstport
                tcp_flags = "0"  # No flags for UDP
                tcp_window_size = "0"

                # Extract UDP Checksum
                checksum = f"{packet.udp.checksum}" if hasattr(packet.udp, "checksum") else "0"
            
            elif hasattr(packet,'icmp'):
                service = "ICMP"
                src_port, dst_port = "0", "0" # ICMP does not have src and dest port as its part of layer 3 not the part of transport layer
                tcp_window_size = "0"

                # Extract ICMP Fields
                icmp_type = packet.icmp.type if hasattr(packet, 'icmp') else "Unknown"
                icmp_code = packet.icmp.code if hasattr(packet, 'icmp') else "Unknown"
                checksum = f"{packet.icmp.checksum}" if hasattr(packet.icmp, 'checksum') else "Unknown"

                # Identify ICMP message type
                icmp_description = "Unknown"
                if icmp_type == "0":
                    icmp_description = "Echo Reply (Ping Response)"
                elif icmp_type == "8":
                    icmp_description = "Echo Request (Ping)"
                elif icmp_type == "3":
                    icmp_description = "Destination Unreachable"
                elif icmp_type == "11":
                    icmp_description = "Time Exceeded"
                elif icmp_type == "5":
                    icmp_description = "Redirect Message"


            # Detect Application Protocol (DNS, MDNS, QUIC, etc.)
            protocol_name = "Unknown"
            if hasattr(packet, 'dns'):
                protocol_name = "DNS"
            elif hasattr(packet, 'mdns'):
                protocol_name = "MDNS"
            elif hasattr(packet, 'quic'):
                protocol_name = "QUIC"
            elif hasattr(packet, 'http'):
                protocol_name = "HTTP"
            elif hasattr(packet, 'tls'):
                protocol_name = "TLS"
            elif hasattr(packet, 'dhcp'):
                protocol_name = "DHCP"
            elif hasattr(packet, 'tcp'):
                protocol_name = "TCP"
            elif hasattr(packet, 'udp'):
                protocol_name = "UDP"
            elif hasattr(packet, 'icmp'):
                protocol_name = "ICMP"

            # Write packet data to CSV
            csv_writer.writerow([ eth_type, packet_length, service, src_ip, dst_ip, src_port,
                                 dst_port, protocol_name, tcp_flags, checksum, tcp_window_size, icmp_type])

            # Print live updates
            print(f"✔ Packet Captured: {src_ip}:{src_port} → {dst_ip}:{dst_port} | Protocol: {protocol_name}")

        except Exception as e:
            print(f"⚠️ Error processing packet: {e}\n")

print(f"\n✅ Capture complete! Packets saved in {csv_filename}")
