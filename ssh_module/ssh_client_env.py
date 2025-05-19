import paramiko
import configparser
import os
import argparse
import sys # Added for sys.exit()
# --- Argument Parsing ---
parser = argparse.ArgumentParser(description="SSH Client to connect to remote servers via environment variables or a config file.")
parser.add_argument('--config', '-c', type=str,
                    help="Specify server name from config.ini (e.g., server_1). If not provided, environment variables are used.")
parser.add_argument('--config-file', '-f', type=str, default='config.ini',
                    help="Path to the config file (default: config.ini).")
parser.add_argument('--command', '-cmd', type=str,
                    help="Command to execute on the remote server (overrides config file/default).")
args = parser.parse_args()
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

# --- Configuration ---
# Server connection details are read from environment variables for security.
# Make sure these environment variables are set before running the script.
# Example for Linux/macOS:
# export SSH_HOSTNAME='your_host_ip_or_hostname'
# export SSH_PORT='22'
# export SSH_USERNAME='your_username'
# export SSH_PASSWORD='your_password'

# Get connection details from environment variables
hostname = os.getenv('SSH_HOSTNAME')
# Default to port 22 if SSH_PORT environment variable is not set
port = int(os.getenv('SSH_PORT', 22))
username = os.getenv('SSH_USERNAME')
password = os.getenv('SSH_PASSWORD')

# --- Input Validation ---
# Check if all necessary environment variables are set
if not all([hostname, username, password]):
    print("Error: One or more of SSH_HOSTNAME, SSH_USERNAME, or SSH_PASSWORD environment variables are not set.")
    print("Please set them before running the script.")
    print("\nExample for Linux/macOS:")
    print("  export SSH_HOSTNAME='your_host'")
    print("  export SSH_PORT='22'")
    print("  export SSH_USERNAME='your_username'")
    print("  export SSH_PASSWORD='your_password'")
    # Exit the script if critical variables are missing
    sys.exit(1)

# --- SSH Client Initialization ---
ssh_client = paramiko.SSHClient()

# Set missing host key policy to automatically add host keys.
# In a production environment, it's safer to load known hosts explicitly
# (e.g., ssh_client.load_system_host_keys()) or prompt for confirmation.
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# --- Connection and Command Execution ---
try:
    print(f"Attempting to connect to {hostname}:{port} with username {username}...")
    # Establish the SSH connection
    ssh_client.connect(hostname, port, username, password)
    print("Connection to server successful!")

    # Command to execute on the remote server
    command = 'ls -l'
    print(f"Executing command: '{command}'")
    
    # Execute the command and get stdin, stdout, stderr streams
    stdin, stdout, stderr = ssh_client.exec_command(command)

    # Read and decode the output and errors
    output = stdout.read().decode().strip()
    errors = stderr.read().decode().strip()

    # Print command output if available
    if output:
        print("\nCommand Output:")
        print(output)
    # Print errors if available
    if errors:
        print("\nErrors:")
        print(errors)

except paramiko.ssh_exception.AuthenticationException:
    print("Error: Authentication failed. Incorrect username or password. Please check your environment variables.")
except paramiko.ssh_exception.NoValidConnectionsError:
    print(f"Error: Unable to connect to {hostname}:{port}. Ensure the SSH server is running and reachable, and the port is correct.")
except Exception as e:
    # Catch any other unexpected errors during connection or command execution
    print(f"An unexpected error occurred: {e}")
finally:
    # --- Close Connection ---
    # Ensure the SSH connection is closed whether successful or not
    if ssh_client:
        ssh_client.close()
        print("\nSSH connection closed.")