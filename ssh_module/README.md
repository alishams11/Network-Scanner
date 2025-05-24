# SSH Module - Network Scanner 🔐

This module is a component of a broader network reconnaissance toolkit. It focuses on scanning IP addresses for active SSH services and performing brute-force login attempts using predefined username and password lists.

---

## 🧩 Description

The SSH module allows penetration testers and security researchers to:

- Identify hosts with open SSH ports
- Attempt to authenticate to SSH servers using dictionary attacks
- Test login access using the `paramiko` SSH library in Python

It is intended to be integrated into larger network scanning and auditing workflows.

---

## 🚀 Features

- Scan specified IP addresses for open SSH ports (default port 22)
- Brute-force SSH login using custom username and password lists
- Modular structure for ease of use and integration
- Uses Python’s `paramiko` library for secure SSH communication

---

## 📂 Project Structure

ssh_module/
├── init.py
├── ssh_scanner.py # Scans hosts for open SSH ports
├── ssh_bruteforce.py # Performs SSH brute-force login attempts


---

## ⚙️ Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/alishams11/Network-Scanner.git
   cd Network-Scanner/ssh_module

    Install required dependencies:

    pip install paramiko

    You can also create a requirements.txt file with paramiko for easier setup in the future.

🧪 Usage
SSH Scanner:

python ssh_scanner.py

SSH Brute-force:

python ssh_bruteforce.py

    Make sure the files usernames.txt and passwords.txt are in the correct location, or update the script accordingly.

📌 Requirements

    Python 3.x

    paramiko library

📈 Future Improvements / TODO

Add multithreading for faster scanning

Add CLI argument parsing (e.g., IP range, credentials)

Export scan results to CSV or JSON

Integrate with main network scanner

Add logging and better error handling
