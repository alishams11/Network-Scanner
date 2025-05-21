import paramiko
import configparser
import os
import argparse
import sys

# Function to read configuration from a .ini file
def get_config_from_file(config_file='config.ini', server_name='server_1'):
    config = configparser.ConfigParser()
    try:
        # config.read() returns a list of successfully parsed filenames
        if not config.read(config_file):
            raise FileNotFoundError(f"Config file '{config_file}' not found or could not be read.")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading config file {config_file}: {e}")
        sys.exit(1)

    if server_name not in config:
        print(f"Error: Server '{server_name}' not found in '{config_file}'.")
        print("Please check the server name or config file content.")
        sys.exit(1)

    # IMPORTANT: Return the specific server section, not the whole config
    return config[server_name]

# --- Argument Parsing ---
parser = argparse.ArgumentParser(description="SSH Client to connect to remote servers via environment variables, a config file, or SSH key.")
parser.add_argument('--config', '-c', type=str,
                    help="Specify server name from config.ini (e.g., server_1). If not provided, environment variables are used.")
parser.add_argument('--config-file', '-f', type=str, default='config.ini',
                    help="Path to the config file (default: config.ini).")
parser.add_argument('--command', '-cmd', type=str,
                    help="Command to execute on the remote server (overrides config file/default).")
parser.add_argument('--key-file', '-k', type=str,
                    help="Path to the SSH private key file (e.g., ~/.ssh/id_rsa).")
parser.add_argument('--passphrase', '-p', type=str,
                    help="Passphrase for the SSH private key, if it's encrypted.")
args = parser.parse_args()

# --- Configuration & Input Validation ---
hostname = None
port = None
username = None
password = None # Password will be None if using key-based auth
key_file = None
passphrase = None
command = None

if args.config: # If --config or -c is provided, read from config file
    print(f"Reading configuration for server '{args.config}' from '{args.config_file}'...")
    config_section = get_config_from_file(args.config_file, args.config)
    
    hostname = config_section.get('Hostname')
    port = int(config_section.get('Port', 22))
    username = config_section.get('Username')
    password = config_section.get('Password') # This can be None
    key_file = config_section.get('KeyFile') # New: Read KeyFile from config
    passphrase = config_section.get('Passphrase') # New: Read Passphrase from config
    command = config_section.get('Command')
    
    if not all([hostname, username]) or (not password and not key_file):
        print(f"Error: Missing Hostname, Username, and either Password or KeyFile for server '{args.config}' in '{args.config_file}'.")
        sys.exit(1)

else: # If --config is not provided, use environment variables
    print("No --config specified. Attempting to use environment variables for connection details...")
    hostname = os.getenv('SSH_HOSTNAME')
    port = int(os.getenv('SSH_PORT', 22))
    username = os.getenv('SSH_USERNAME')
    password = os.getenv('SSH_PASSWORD')
    key_file = os.getenv('SSH_KEY_FILE') # New: Read KeyFile from env var
    passphrase = os.getenv('SSH_PASSPHRASE') # New: Read Passphrase from env var
    command = os.getenv('SSH_COMMAND', 'ls -l')

    if not all([hostname, username]) or (not password and not key_file):
        print("Error: One or more of SSH_HOSTNAME, SSH_USERNAME, and either SSH_PASSWORD or SSH_KEY_FILE environment variables are not set.")
        print("Please set them before running the script or use --config to specify a server from config.ini.")
        print("\nExample for Linux/macOS:")
        print("  export SSH_HOSTNAME='your_host'")
        print("  export SSH_PORT='22'")
        print("  export SSH_USERNAME='your_username'")
        print("  export SSH_PASSWORD='your_password'")
        print("  # OR for key-based authentication:")
        print("  export SSH_KEY_FILE='~/.ssh/id_rsa'")
        print("  export SSH_PASSPHRASE='your_key_passphrase' # if applicable")
        sys.exit(1)

# Override with command-line arguments if provided (highest priority)
if args.key_file:
    key_file = args.key_file
    passphrase = args.passphrase # CLI passphrase overrides any other
    print(f"Command line --key-file '{args.key_file}' will be used for authentication.")
    password = None # Ensure password is not used if key is specified via CLI

if args.command:
    command = args.command
    print(f"Command line --command '{args.command}' overrides any other command source.")

# Final check for authentication method and command
if not (password or key_file):
    print("Error: No authentication method specified. Please provide a password (via env var or config) or a key file (via env var, config, or --key-file).")
    sys.exit(1)

if not command:
    print("Error: No command specified. Please provide a command via --command, config file, or SSH_COMMAND environment variable.")
    sys.exit(1)

# --- SSH Client Initialization ---
ssh_client = paramiko.SSHClient()

ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# --- Connection and Command Execution ---
try:
    print(f"Attempting to connect to {hostname}:{port} with username {username}...")
    
    # New connection logic: Try key-based auth first, then password
    if key_file:
        try:
            # Expand user home directory for key file path
            expanded_key_file = os.path.expanduser(key_file)
            print(f"Attempting key-based authentication with key: {expanded_key_file}")
            
            # Auto-detect key type (RSA, EdDSA, etc.)
            key = paramiko.AutoAddPolicy()
            try:
                # Try to load key as RSA
                key = paramiko.RSAKey.from_private_key_file(expanded_key_file, password=passphrase)
            except paramiko.ssh_exception.SSHException:
                try:
                    # Try to load key as EdDSA (for newer keys)
                    key = paramiko.EdDSAKey.from_private_key_file(expanded_key_file, password=passphrase)
                except paramiko.ssh_exception.SSHException:
                     try:
                        # Try to load key as ECDSA (common newer key type)
                        key = paramiko.ECDSAKey.from_private_key_file(expanded_key_file, password=passphrase)
                     except paramiko.ssh_exception.SSHException as e:
                        print(f"Error loading key file {expanded_key_file}: {e}")
                        sys.exit(1)
            
            ssh_client.connect(hostname, port, username, pkey=key)
            print("Connection to server successful using SSH key!")
        except FileNotFoundError:
            print(f"Error: SSH key file '{expanded_key_file}' not found.")
            sys.exit(1)
        except paramiko.ssh_exception.BadHostKeyException as e:
            print(f"Error: Bad host key for {hostname}: {e}")
            sys.exit(1)
        except paramiko.ssh_exception.AuthenticationException:
            print("Error: Authentication failed with SSH key. Incorrect key, username, or passphrase. Please check your configuration.")
            sys.exit(1)
        except Exception as e:
            print(f"An unexpected error occurred during key-based authentication: {e}")
            sys.exit(1)
    else:
        # Fallback to password authentication if no key file is specified
        if not password:
            print("Error: No SSH key file provided and no password found. Please specify an authentication method.")
            sys.exit(1)
        
        print("Attempting password-based authentication...")
        ssh_client.connect(hostname, port, username, password)
        print("Connection to server successful using password!")

    print(f"Executing command: '{command}'")
    
    stdin, stdout, stderr = ssh_client.exec_command(command)

    output = stdout.read().decode().strip()
    errors = stderr.read().decode().strip()

    if output:
        print("\nCommand Output:")
        print(output)
    if errors:
        print("\nErrors:")
        print(errors)

except paramiko.ssh_exception.AuthenticationException:
    print("Error: Authentication failed. Incorrect username or password. Please check your configuration.")
except paramiko.ssh_exception.NoValidConnectionsError:
    print(f"Error: Unable to connect to {hostname}:{port}. Ensure the SSH server is running and reachable, and the port is correct.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
finally:
    if ssh_client:
        ssh_client.close()
        print("\nSSH connection closed.")