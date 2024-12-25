#!/usr/bin/env python3

import subprocess
import sys
import platform
import shutil

def is_command_available(command):
    """
    Check if a given command is available on the system.
    Returns True if found in PATH, False otherwise.
    """
    return shutil.which(command) is not None

def run_command(command, shell=False):
    """
    Run a system command. Raises an exception if the command fails.
    If shell=True, the command is run through the shell (e.g. Bash on Linux).
    """
    print(f"Running command: {' '.join(command) if isinstance(command, list) else command}")
    result = subprocess.run(command, shell=shell, check=True, text=True)
    return result

def install_yarn_windows():
    """
    Attempt to install Yarn on Windows using one of:
      - Chocolatey
      - npm
    """
    # 1. Try Chocolatey
    if is_command_available("choco"):
        try:
            run_command(["choco", "install", "yarn", "-y"])
            return
        except subprocess.CalledProcessError:
            print("Failed to install Yarn with Chocolatey.")

    # 2. Fallback: npm -g (requires Node.js and npm installed)
    if is_command_available("npm"):
        try:
            run_command(["npm", "install", "-g", "yarn"])
            return
        except subprocess.CalledProcessError:
            print("Failed to install Yarn with npm.")
    else:
        print("npm not found. Please install Node.js/npm or Chocolatey and try again.")

    print("Could not install Yarn on Windows with available methods.")

def install_yarn_macos():
    """
    Attempt to install Yarn on macOS using one of:
      - Homebrew
      - npm -g (requires Node.js)
    """
    # 1. Try Homebrew
    if is_command_available("brew"):
        try:
            run_command(["brew", "update"])
            run_command(["brew", "install", "yarn"])
            return
        except subprocess.CalledProcessError:
            print("Failed to install Yarn with Homebrew.")
    
    # 2. Fallback: npm -g
    if is_command_available("npm"):
        try:
            run_command(["npm", "install", "-g", "yarn"])
            return
        except subprocess.CalledProcessError:
            print("Failed to install Yarn with npm.")
    else:
        print("npm not found. Please install Node.js/npm or Homebrew and try again.")

    print("Could not install Yarn on macOS with available methods.")

def install_yarn_linux():
    """
    Attempt to install Yarn on Linux (primarily Debian/Ubuntu-based).
    Fallback to npm -g if apt is not available or fails.
    """
    # 1. If apt-get is available, assume Debian/Ubuntu-based
    if is_command_available("apt-get"):
        try:
            # Add Yarn’s GPG key and repo
            run_command(["curl", "-sS", "https://dl.yarnpkg.com/debian/pubkey.gpg", 
                         "|", "sudo", "apt-key", "add", "-"], shell=True)
            run_command(["sudo", "apt-get", "update"])
            # On newer versions of Ubuntu, Yarn is typically available via the official repository
            # The Yarn package from the repos can conflict with cmdtest, so we install with official Yarn repo
            run_command(["sudo", "apt-get", "install", "-y", "yarn"])
            return
        except subprocess.CalledProcessError:
            print("Failed to install Yarn with apt-get, or your distribution is not supported by this method.")
    
    # 2. Fallback: npm -g (requires Node.js and npm installed)
    if is_command_available("npm"):
        try:
            run_command(["npm", "install", "-g", "yarn"])
            return
        except subprocess.CalledProcessError:
            print("Failed to install Yarn with npm.")
    else:
        print("npm not found. Please install Node.js/npm or use your distribution's package manager to install Yarn.")

    print("Could not install Yarn on Linux with available methods.")

def main():
    # Check if Yarn is already installed
    if is_command_available("yarn"):
        print("Yarn is already installed.")
        sys.exit(0)

    system_name = platform.system().lower()

    try:
        if "windows" in system_name:
            install_yarn_windows()
        elif "darwin" in system_name:
            install_yarn_macos()
        elif "linux" in system_name:
            install_yarn_linux()
        else:
            print(f"Unsupported platform: {system_name}. Please install Yarn manually.")
            sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)

    # Final check if Yarn was installed successfully
    if is_command_available("yarn"):
        print("Yarn installed successfully!")
    else:
        print("Yarn installation failed. Please try installing manually.")
        sys.exit(1)

if __name__ == "__main__":
    main()
