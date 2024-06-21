import socket

def get_local_ip():
    try:
        # Create a socket object
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Connect to a server within China
        s.connect(("223.5.5.5", 80))  # This IP is one of the DNS servers operated by China Telecom
        # Get the local IP address
        local_ip = s.getsockname()[0]
        # Close the socket
        s.close()
        return str(local_ip)
    except Exception as e:
        print("Error:", e)
        return "127.0.0.1"

# Get and print the local IP address
local_ip = get_local_ip()
if local_ip:
    print("Local IP Address:", local_ip)
else:
    print("Failed to retrieve local IP address.")
