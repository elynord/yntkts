#!/bin/bash

# Function to check and fix scripts
check_and_fix_script() {
    script_file="$1"

# Function to check syntax using ShellCheck
check_syntax() {
    if ! shellcheck "$1"; then
        echo "⚠️ Syntax errors detected:"
        shellcheck "$1"  # Show ShellCheck output
    else
        echo "✅ Syntax is valid."
    fi
}

# Function to check for dangerous patterns
check_patterns() {
    if grep -E "(eval|exec|rm -rf|curl -s|wget -qO-)" "$1"; then
        echo "⚠️ Warning: Dangerous patterns found (eval, exec, rm -rf, suspicious downloads)."
    fi
}

# Function to check for uninitialized variables
check_uninitialized_vars() {
    if shellcheck -e SC2154 "$1"; then
        echo "⚠️ Warning: Uninitialized variables found."
        shellcheck -e SC2154 "$1"  # Show ShellCheck output
    fi
}

# Function to check for invalid shebang
check_shebang() {
    shebang_line=$(head -n 1 "$1")
    if [[ ! $shebang_line =~ ^#!(/usr/bin/env|/bin/bash|/bin/sh) ]]; then
        echo "⚠️ Warning: Invalid or missing shebang."
    fi
}

# Function to fix syntax errors (using ShellCheck)
fix_syntax() {
    if shellcheck -f diff "$1" | patch "$1" &> /dev/null; then  # Redirect output to /dev/null
        echo "✅ Syntax errors fixed successfully."
    else
        echo "❌ Could not fix all syntax errors."
    fi
}

# Function to fix other issues by searching for solutions online (using DuckDuckGo)
fix_with_internet() {
    error_message="$1"
    search_query="shell script $error_message"
    search_results=$(ddg -j "$search_query" | jq -r '.RelatedTopics[].Text')

    if [[ -n "$search_results" ]]; then
        echo "🔍 Searching for solutions online..."
        echo "$search_results"  # Show search results to the user

        # Example logic for fixing uninitialized variables
        if [[ "$error_message" =~ "uninitialized variable" ]]; then
            variable_name=$(echo "$error_message" | grep -oP "'[^']+'")  # Extract variable name
            if [[ -n "$variable_name" ]]; then
                sed -i "s/^\($variable_name\s*=\s*\)/\1\"\"/g" "$script_file"  # Add empty quotes
                echo "🔧 Trying to fix uninitialized variable: $variable_name"
            fi
        fi

        # Add more automatic fix logic here
        # ...
    else
        echo "🤷 No solutions found online."
    fi
}

    # Main logic
    if [[ -f "$script_file" ]]; then
        # ... (function calls for checks and fixes same as before)
    else
        echo "❌ Script file not found."
    fi
}

# Function to run Telegram bot
run_telegram_bot() {
    python3 telegram_bot.py &  # Run bot in the background
}

# Function to install dependencies and run bot
setup_and_run() {
    # Update and upgrade system
    sudo apt update && sudo apt upgrade -y

    # Install dependencies (with error handling)
    required_packages=(python3 python3-pip jq shellcheck curl) 
    for package in "${required_packages[@]}"; do
        if ! dpkg -l | grep -q "^ii  $package "; then
            echo "⚙️ Installing $package..."
            sudo apt install "$package" -y || {
                echo "❌ Failed to install $package. Please check your internet connection and try again." >&2
                exit 1
            }
        fi
    done

    # Install python-telegram-bot (with latest version handling)
    pip3 install --upgrade python-telegram-bot

    echo "✅ Installation complete. Telegram bot is running..."
    run_telegram_bot
}

# Main script logic
if [[ "$1" == "setup" ]]; then
    setup_and_run
elif [[ -f "$1" ]]; then
    check_and_fix_script "$1"
else
    echo "Usage: $0 [setup | script_file.sh]"
fi
