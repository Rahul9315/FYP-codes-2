import psutil

interfaces = psutil.net_if_addrs()
print("Available Network Interfaces:")
for interface in interfaces:
    print(interface)

