#!/usr/bin/env bash

print_green() {
    BOLD_GREEN=$(tput bold ; tput setaf 2)
    NORMAL=$(tput sgr0)
    echo "${BOLD_GREEN}$1${NORMAL}"
}

print_yellow() {
    BOLD_YELLOW=$(tput bold ; tput setaf 3)
    NORMAL=$(tput sgr0)
    echo "${BOLD_YELLOW}$1${NORMAL}"
}

print_red() {
    BOLD_RED=$(tput bold ; tput setaf 1)
    NORMAL=$(tput sgr0)
    echo "${BOLD_RED}$1${NORMAL}"
}

print_blue() {
    BOLD_BLUE=$(tput bold ; tput setaf 4)
    NORMAL=$(tput sgr0)
    echo "${BOLD_BLUE}$1${NORMAL}"
}

print_delimiter() {
    echo
    echo "-------------------------------------------------------------------------------"
    echo
}

# Counter for failed installations
failed_counter=0

echo
echo
print_blue "================================"
print_blue " Hellsing - Installation Script "
print_blue "================================"
echo
echo

# Make sure we are root!
if [ "$EUID" -ne 0 ]; then 
    print_red "[!] Must be run as root"
    exit 1
fi

# -----------------------------------------------------------------------------

print_blue "[~] Running dependencies install script..."
./install-dependencies.sh
if [ $? -eq 0 ]; then
    print_green "[+] Dependencies install script exited with success returncode"
else
    print_red "[!] Dependencies install script exited with error returncode"
    ((failed_counter++))
fi
print_delimiter

# -----------------------------------------------------------------------------

print_blue "[~] Running Hellsing full toolbox install (in non-interactive mode)..."
python3 hellsing.py toolbox --install-all --auto
if [ $? -eq 0 ]; then
    print_green "[+] Hellsing toolbox install exited with success returncode"
else
    print_red "[!] Hellsing toolbox install exited with error returncode"
    ((failed_counter++))
fi
print_delimiter

# -----------------------------------------------------------------------------

print_blue "[~] Running automatic check of all installed tools (based on returncodes)..."
python3 hellsing.py toolbox --check
if [ $? -eq 0 ]; then
    print_green "[+] Toolbox automatic check exited with success returncode"
else
    print_red "[!] Toolbox automatic check exited with error returncode"
    ((failed_counter++))
fi
print_delimiter

# -----------------------------------------------------------------------------

print_blue "[~] Print toolbox content"
python3 hellsing.py toolbox --show-all

# -----------------------------------------------------------------------------

# Check if there were any failed installations
if [ $failed_counter -eq 0 ]; then
    print_green "[+] Install script finished with success"
else
    print_red "[!] Install script finished, but $failed_counter tool(s) failed to install"
fi
