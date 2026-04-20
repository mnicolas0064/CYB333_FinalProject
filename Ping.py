import subprocess
import ipaddress
import socket


def ping_network(subnet):

    print(f"--- Scanning Network: {subnet} ---")
    network = ipaddress.ip_network(subnet)
    active_hosts = []

    for ip in network.hosts():
        res = subprocess.call(['ping', '-n', '1', '-w', '100', str(ip)],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if res == 0:
            print(f"{ip}")
            active_hosts.append(str(ip))
    return active_hosts




if __name__ == "__main__":

    my_subnet = "10.12.12.0/24"

    ping_network(my_subnet)
