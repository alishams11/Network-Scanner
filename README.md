# 🌐 network-scanner

A lightweight Python-based network scanner tool that performs live host discovery (ping sweep) and TCP port scanning. Ideal for SOC analysts, pentesters, and security learners.

---

## 🎯 Features

- ✅ Ping sweep across a local subnet to detect active hosts
- ✅ TCP port scanning on discovered or specified IP addresses
- ✅ Simple and modular CLI interface
- ✅ Easy to expand with SSH modules or other protocols
- ✅ Clean codebase for educational and operational use

---

## 🧠 Skills Demonstrated

- Python socket programming
- Subnet scanning
- TCP connection testing
- Modular code structure
- Command-line interface design

---

## 🚀 How to Use

```bash
python3 main.py



#You’ll be prompted to enter an IP address:

Enter target IP address: 192.168.1.10

The scanner will return open ports on the specified host.

#🖥️ Sample Output

[+] Open ports on 192.168.1.10: [22, 80, 443]

#📁 Project Structure

network-scanner/
├── scanner/
│   ├── ping_sweep.py       # Scans subnet for live hosts
│   └── port_scanner.py     # TCP port scanner
├── ssh_module/
│   └── ssh_client_env.py   # (Optional) SSH automation module
├── output/                 # Stores future scan results
├── main.py                 # CLI entry point
├── README.md
├── requirements.txt
└── LICENSE

#📸 Demo Screenshot
![demo](screenshots.demo.png)

#⚙️ Installation

pip install -r requirements.txt

    No external dependencies currently required.

#💡 Future Improvements

    Save scan results in JSON or CSV

    Add multithreaded port scanning

    Integrate banner grabbing or version detection

    Add auto-SSH connect feature

#👨‍💻 Author

Ali Shams

#📝 License

This project is licensed under the MIT License.
