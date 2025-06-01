from scanner.port_scanner import scan_ports

if __name__ == "__main__":
    ip = input("Enter target IP address: ").strip()
    result = scan_ports(ip)
    if result:
        print(f"[+] Open ports on {ip}: {result}")
    else:
        print(f"[-] No open ports found on {ip}.")
