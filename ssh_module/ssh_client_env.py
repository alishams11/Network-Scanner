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
        sys.exit(1) # Exit if config file is not found
    except Exception as e:
        print(f"Error reading config file {config_file}: {e}")
        sys.exit(1) # Exit for other config file read errors

    if server_name not in config:
        print(f"Error: Server '{server_name}' not found in '{config_file}'.")
        print("Please check the server name or config file content.")
        sys.exit(1) # Exit if server section not found

    # IMPORTANT: Return the specific server section, not the whole config
    return config[server_name]

# --- Argument Parsing ---
parser = argparse.ArgumentParser(description="SSH Client to connect to remote servers via environment variables or a config file.")
parser.add_argument('--config', '-c', type=str,
                    help="Specify server name from config.ini (e.g., server_1). If not provided, environment variables are used.")
parser.add_argument('--config-file', '-f', type=str, default='config.ini',
                    help="Path to the config file (default: config.ini).")
parser.add_argument('--command', '-cmd', type=str,
                    help="Command to execute on the remote server (overrides config file/default).")
args = parser.parse_args()

# --- Configuration & Input Validation ---
hostname = None
port = None
username = None
password = None
command = None # Initialize command variable

if args.config: # If --config or -c is provided, read from config file
    print(f"Reading configuration for server '{args.config}' from '{args.config_file}'...")
    # Get configuration from file using the new function
    config_section = get_config_from_file(args.config_file, args.config)
    
    # Extract details from the config section
    # Use .get() with a default value for optional fields
    hostname = config_section.get('Hostname')
    port = int(config_section.get('Port', 22)) # Default to 22 if not specified in config
    username = config_section.get('Username')
    password = config_section.get('Password')
    # Command can be specified in the config, if not, it will be None
    command = config_section.get('Command')
    
    # Validate essential config details
    if not all([hostname, username, password]):
        print(f"Error: Missing Hostname, Username, or Password for server '{args.config}' in '{args.config_file}'.")
        sys.exit(1)

else: # If --config is not provided, use environment variables
    print("No --config specified. Attempting to use environment variables for connection details...")
    hostname = os.getenv('SSH_HOSTNAME')
    port = int(os.getenv('SSH_PORT', 22))
    username = os.getenv('SSH_USERNAME')
    password = os.getenv('SSH_PASSWORD')
    # Default command for environment variables if not overridden by --command
    command = os.getenv('SSH_COMMAND', 'ls -l') # Also check for SSH_COMMAND environment variable

    # Validate essential environment variables
    if not all([hostname, username, password]):
        print("Error: One or more of SSH_HOSTNAME, SSH_USERNAME, or SSH_PASSWORD environment variables are not set.")
        print("Please set them before running the script or use --config to specify a server from config.ini.")
        print("\nExample for Linux/macOS:")
        print("  export SSH_HOSTNAME='your_host'")
        print("  export SSH_PORT='22'")
        print("  export SSH_USERNAME='your_username'")
        print("  export SSH_PASSWORD='your_password'")
        sys.exit(1)

# Override command if --command is provided in command line
if args.command:
    command = args.command
    print(f"Command line --command '{args.command}' overrides any other command source.")

# Final check for command
if not command:
    print("Error: No command specified. Please provide a command via --command, config file, or SSH_COMMAND environment variable.")
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
    print("Error: Authentication failed. Incorrect username or password. Please check your configuration.")
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