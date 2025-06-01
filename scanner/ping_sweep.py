<<<<<<< HEAD
# scanner/ping_sweep.py
=======
>>>>>>> 58583b0 (Add port scanner module and CLI test for network-scanner)
import subprocess
import platform

def ping_ip(ip):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "1", ip]
<<<<<<< HEAD
    return subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

def scan_range(base_ip="192.168.1", start=1, end=254):
    active_hosts = []
    for i in range(start, end+1):
        ip = f"{base_ip}.{i}"
        if ping_ip(ip):
            active_hosts.append(ip)
            print(f"[+] Active: {ip}")

