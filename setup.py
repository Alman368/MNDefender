#!/usr/bin/env python3
import os
import subprocess
import sys

def install_requirements(folder):
    """Install requirements for a specific folder."""
    requirements_file = os.path.join(folder, 'requirements.txt')
    if os.path.exists(requirements_file):
        print(f"Installing requirements for {folder}...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', requirements_file])
        print(f"Requirements for {folder} installed successfully.")
    else:
        print(f"No requirements.txt file found in {folder}.")

def main():
    """Main function to set up all microservices."""
    # Install requirements for each service
    services = ['api', 'chat', 'web']

    for service in services:
        install_requirements(service)

    print("\nSetup completed successfully!")
    print("\nTo start the application, run the following commands in separate terminals:")
    print("\nTerminal 1 (API service): python run_api.py")
    print("Terminal 2 (Chat service): python run_chat.py")
    print("Terminal 3 (Web service): python run.py")

    print("\nThen access the application at http://localhost:5000")

if __name__ == "__main__":
    main()
