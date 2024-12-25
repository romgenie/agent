#!/usr/bin/env python3

import subprocess
import sys
import time
import socket
import os
import re

DOCKER_IMAGE = "trufflesuite/ganache:latest"
GANACHE_PORT = 8545
GANACHE_CONTAINER_NAME = "local-ganache"

def prompt_for_env_values() -> list[tuple[str, str]]:
    """
    Prompt the user for some environment variables in a specific order.
    Returns a list of (key, value) tuples in that exact order.
    (NEXT_PUBLIC_ETHEREUM_CONTRACT_ADDRESS will be populated from Ganache logs.)
    """
    variables_in_order = [
        ("ETHEREUM_RPC_URL", "http://127.0.0.1:8545"),
        ("ETHEREUM_CHAIN_ID", "8453 #11155111"),
        ("ETHEREUM_CHAIN_NAME", "base #sepolia"),
    ]

    print("Please provide the following environment variables.")
    print("Press Enter to accept the default value shown in brackets:\n")

    user_inputs = []
    for key, default_value in variables_in_order:
        user_val = input(f"{key} [{default_value}]: ").strip()
        if not user_val:  # If user pressed Enter (empty), use default
            user_val = default_value
        user_inputs.append((key, user_val))

    return user_inputs

def is_docker_installed() -> bool:
    """
    Checks if Docker is installed by running 'docker --version'.
    Returns True if installed, False otherwise.
    """
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            return True
    except FileNotFoundError:
        pass
    return False

def is_port_open(host="127.0.0.1", port=8545) -> bool:
    """
    Checks if a given TCP port is open by attempting to connect.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1.0)
        try:
            s.connect((host, port))
            return True
        except (ConnectionRefusedError, OSError):
            return False

def remove_existing_container_if_any(container_name: str):
    """
    Checks if a container with the given name exists. 
    If it does, stop and remove it automatically.
    """
    # Check if it exists with `docker ps -a --filter "name=..." --format "{{.ID}}"`
    check_cmd = ["docker", "ps", "-a", "--filter", f"name={container_name}", "--format", "{{.ID}}"]
    check_process = subprocess.run(check_cmd, capture_output=True, text=True)
    container_id = check_process.stdout.strip()

    if container_id:
        print(f"[WARNING] A container named '{container_name}' already exists. Stopping and removing it now...")
        stop_cmd = ["docker", "stop", container_name]
        rm_cmd = ["docker", "rm", container_name]
        
        subprocess.run(stop_cmd, capture_output=True, text=True)  # stop container
        subprocess.run(rm_cmd, capture_output=True, text=True)    # remove container

def run_local_ganache(container_name=GANACHE_CONTAINER_NAME, port=GANACHE_PORT) -> str:
    """
    Runs a Ganache container in detached mode on the specified port.
    Returns the container ID if successful. Raises an Exception on failure.
    Automatically stops & removes any existing container with the same name.
    """
    # First, ensure no leftover container with the same name
    remove_existing_container_if_any(container_name)

    command = [
        "docker", "run", "-d",
        "-p", f"{port}:{port}",
        "--name", container_name,
        DOCKER_IMAGE,
    ]

    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Failed to start Ganache container.\n{result.stderr}")

    container_id = result.stdout.strip()
    return container_id

def get_first_wallet_address(container_name=GANACHE_CONTAINER_NAME) -> str:
    """
    Fetches the Ganache logs and extracts the first (index 0) wallet address.
    Returns the wallet address as a hex string (e.g., 0xabc123...).
    If not found, raises an exception.
    """
    # Retrieve logs
    result = subprocess.run(["docker", "logs", container_name], capture_output=True, text=True)
    logs = result.stdout

    # Example lines we look for:
    # (0) 0x59Cc23812345C02B54e466E802CfAF1b8738C779 (100 ETH)
    # We'll look for: "(0) 0x<40 hex chars>"
    match = re.search(r"^\(0\)\s+(0x[a-fA-F0-9]{40})", logs, re.MULTILINE)
    if not match:
        raise Exception("Could not find the first Ganache wallet address in the logs.")
    return match.group(1)

def update_env_values(env_path: str, env_pairs: list[tuple[str, str]]) -> None:
    """
    Updates or inserts multiple key-value pairs in the .env file in the given order.
    
    :param env_path: The path to the .env file.
    :param env_pairs: A list of (key, value) tuples in the order they should appear.
    """
    # Read existing lines if .env exists
    env_lines = []
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            env_lines = f.readlines()
    
    # Build a map of existing keys to their line indices
    line_map = {}
    for index, line in enumerate(env_lines):
        stripped_line = line.strip()
        # Ignore empty or comment lines
        if not stripped_line or stripped_line.startswith('#'):
            continue
        if '=' not in stripped_line:
            continue
        
        existing_key, _ = stripped_line.split('=', 1)
        existing_key = existing_key.strip()
        line_map[existing_key] = index

    # Update or append lines in the order we received them
    for key, value in env_pairs:
        formatted_line = f"{key}={value}\n"
        if key in line_map:
            # Replace the existing line with this new one
            env_lines[line_map[key]] = formatted_line
        else:
            # Append if the key wasn't found
            env_lines.append(formatted_line)
    
    # Write everything back
    with open(env_path, 'w') as f:
        f.writelines(env_lines)

def main():
    # 1) Prompt user for environment variables (except the contract address, which we get from Ganache)
    user_env_pairs = prompt_for_env_values()
    print()

    # 2) Check Docker
    print("[INFO] Checking if Docker is installed and running...")
    if not is_docker_installed():
        print("[ERROR] Docker not found. Please install Docker Desktop or Docker Engine.")
        sys.exit(1)
    
    # 3) Pull Ganache image
    print(f"[INFO] Pulling Docker image '{DOCKER_IMAGE}' (if not already present)...")
    pull_result = subprocess.run(["docker", "pull", DOCKER_IMAGE], capture_output=True, text=True)
    if pull_result.returncode != 0:
        print("[ERROR] Docker pull failed:")
        print(pull_result.stderr)
        sys.exit(1)

    # 4) Run Ganache container (automatically remove any existing container with the same name)
    print("[INFO] Starting Ganache container on port 8545...")
    try:
        container_id = run_local_ganache()
        print(f"[INFO] Container started. ID: {container_id}")
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

    # 5) Wait for Ganache to listen on port 8545
    print("[INFO] Waiting for Ganache to listen on port 8545...")
    max_wait_seconds = 10
    waited = 0
    while waited < max_wait_seconds:
        if is_port_open("127.0.0.1", GANACHE_PORT):
            print("[INFO] Ganache is running and port 8545 is open.")
            break
        time.sleep(1)
        waited += 1
    
    if not is_port_open("127.0.0.1", GANACHE_PORT):
        print("[WARNING] Port 8545 is still not open after waiting. "
              "Ganache might be starting slowly, or there might be an issue.")
        print("You can check logs with:")
        print(f"  docker logs {GANACHE_CONTAINER_NAME}")
        print("And check port usage with netstat or equivalent.")
    else:
        print("[INFO] Ganache node should now be accessible at http://127.0.0.1:8545")

    # Gather the address from Ganache logs
    print("[INFO] Fetching the first Ganache wallet address from logs...")
    try:
        first_address = get_first_wallet_address()
        print(f"[INFO] First Ganache wallet address: {first_address}")
    except Exception as err:
        print(f"[ERROR] Failed to retrieve Ganache wallet address: {err}")
        print("Continuing without populating NEXT_PUBLIC_ETHEREUM_CONTRACT_ADDRESS...")
        first_address = "your_ethereum_contract_address_here"  # fallback
    
    # 6) Update .env file
    print("[INFO] Updating the .env file with required environment variables...")
    # Insert the user values in order, then the contract address
    env_pairs_in_order = user_env_pairs + [
        ("NEXT_PUBLIC_ETHEREUM_CONTRACT_ADDRESS", first_address)
    ]
    env_file = ".env"  # Adjust path if needed
    update_env_values(env_file, env_pairs_in_order)
    print("[INFO] .env file updated successfully.")

    # 7) Output final instructions
    print("\n=== Ganache Setup Complete ===")
    print("To stop Ganache, run:")
    print(f"  docker stop {GANACHE_CONTAINER_NAME}")
    print("To remove Ganache container, run:")
    print(f"  docker rm {GANACHE_CONTAINER_NAME}")

if __name__ == "__main__":
    main()
