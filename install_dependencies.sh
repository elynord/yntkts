#!/bin/bash

echo "Starting dependency installation..."

# Check if pip is installed
if ! command -v pip &> /dev/null
then
    echo "pip could not be found. Installing pip..."

    # Detect Operating System
    OS=$(uname -s)

    case "$OS" in
        Linux*)     # Linux Distros (Debian/Ubuntu, CentOS/RHEL, etc.)
            if command -v apt-get &> /dev/null
            then
                echo "Installing pip using apt-get..."
                sudo apt-get update
                sudo apt-get install -y python3-pip
            elif command -v yum &> /dev/null
            then
                echo "Installing pip using yum..."
                sudo yum install -y python3-pip
            elif command -v dnf &> /dev/null  # Fedora
            then
                echo "Installing pip using dnf..."
                sudo dnf install -y python3-pip
            elif command -v zypper &> /dev/null  # openSUSE
            then
                echo "Installing pip using zypper..."
                sudo zypper install -y python3-pip
            else
                echo "Error: Could not find a supported package manager (apt-get, yum, dnf, or zypper)."
                exit 1
            fi
            ;;
        Darwin*)    # macOS
            if command -v brew &> /dev/null  # Check for Homebrew
            then
                echo "Installing pip using Homebrew..."
                brew install python3
            else
                echo "Error: Homebrew is not installed. Please install it first: /bin/bash -c '$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)'"
                exit 1
            fi
            ;;
        *)          # Other Operating Systems (not explicitly supported)
            echo "Error: Unsupported operating system. Please install pip manually."
            exit 1
            ;;
    esac
fi

# Check if virtual environment is desired
read -p "Do you want to create a virtual environment (recommended)? (y/n): " CREATE_VENV
if [[ "$CREATE_VENV" =~ ^[Yy]$ ]]
then
    # Create and activate virtual environment
    python3 -m venv venv
    source venv/bin/activate
fi

# Install Python dependencies
echo "Installing Python dependencies from requirements.txt..."
pip install -r requirements.txt

echo "Installation of dependencies completed successfully!"

# Check if script_file.sh exists
if [ -f "script_file.sh" ]; then
    echo "Executing script_file.sh..."
    # Activate virtual environment if it was created
    if [[ "$CREATE_VENV" =~ ^[Yy]$ ]]
    then
        source venv/bin/activate
    fi
    
    ./script_file.sh
    deactivate # Deactivate the virtual environment after execution
else
    echo "Warning: script_file.sh not found. Skipping execution."
fi
