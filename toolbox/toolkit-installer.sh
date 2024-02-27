#!/bin/bash

# Colors
blue=$(tput setaf 4)
yellow=$(tput setaf 3)
magenta=$(tput setaf 5)
green=$(tput setaf 2)
red=$(tput setaf 1)
reset=$(tput sgr0)

# Function to clone tool
clone_repo() {
    local repo=$1
    local repo_name=$2
    local tool_number=$3
    local total_number=$4
    
    if [ -d "$repo_name" ]; then
        echo $'\n'"Tool #${yellow}$tool_number${reset}/${yellow}$total_number${reset} already ${magenta}exists${reset} : '${blue}$repo_name${reset}'"
    else
        echo ""
        git clone "$repo"
        if [ $? -eq 0 ]; then
            echo "Tool #${yellow}$tool_number${reset}/${yellow}$total_number${reset} cloned ${green}successfully.${reset} : '${blue}$repo_name${reset}'"
        else
            echo "Tool #${yellow}$tool_number${reset}/${yellow}$total_number${reset} cloning ${red}error${reset}  : '${blue}$repo_name${reset}'"
        fi
    fi
}

# Function to remove tool
remove_repo() {
    local repo_name=$1
    
    if [ -d "$repo_name" ]; then
        echo ""
        echo "Removing tool '${blue}$repo_name${reset}'..."
        rm -rf "$repo_name"
        echo "Tool ${green}removed${reset} : '${blue}$repo_name${reset}' "
    else
        echo ""
        echo "Tool ${red}does not exist${reset} : '${blue}$repo_name${reset}'"
    fi
}

# Function to check if tool exists
check_repo() {
    local repo_name=$1
    
    if [ -d "$repo_name" ]; then
        echo "Tool already ${magenta}exists${reset} : '${blue}$repo_name${reset}'"
    else
        echo "Tool ${red}does not exist${reset} : '${blue}$repo_name${reset}'"
    fi
}

# Help message
show_help() {
    echo "Usage: $0 [OPTION]"
    echo "Clones, removes, or checks tools according to the specified option."
    echo
    echo "Options:"
    echo "  --clone-all                  Clone all tools listed in 'toolkit.txt'."
    echo "  --remove-all                 Remove all tools listed in 'toolkit.txt'."
    echo "  --check-all                  Check if all tools listed in 'toolkit.txt' exist."
    echo "  --update-all                 Remove all the existing repositories and clone them again."
    echo "  --clone 'tool1,tool2,...'   Clone the specified tool(s) (comma-separated)."
    echo "  --remove 'tool1,tool2,...'   Remove the specified tool(s) (comma-separated)."
    echo "  --check 'tool1,tool2,...'    Check if the specified tool(s) exist(s) (comma-separated)."
    echo "  --update 'tool1,tool2,...'   Remove the specific repositories and clone them again (comma-separated)."
    echo "  -h, --help                   Display this help message."
    echo
}

# Check for command-line options
case "$1" in
    --clone-all)
        # Check if toolkit.txt exists
        if [ ! -f "toolkit.txt" ]; then
            echo "${red}Error: toolkit.txt not found.${reset}"
            exit 1
        fi
        
        # Remove any trailing whitespace or newline characters from each line
        sed -i 's/[[:space:]]*$//' toolkit.txt
        
        # Count the number of lines in toolkit.txt to get the total tool count
        total_tools=$(wc -l < toolkit.txt)
        
        # Loop through each line in toolkit.txt
        tool_number=1
        while IFS= read -r repo; do
            repo_name=$(basename "$repo" .git)
            clone_repo "$repo" "$repo_name" "$tool_number" "$total_tools"
            ((tool_number++))
        done < toolkit.txt
        
        echo $'\n'"${green}Cloning completed.${reset}"
        ;;
    --remove-all)
        # Loop through each line in toolkit.txt
        while IFS= read -r repo; do
            repo_name=$(basename "$repo" .git)
            remove_repo "$repo_name"
        done < toolkit.txt
        
        echo "${green}Removal completed.${reset}"
        ;;
    --check-all)
        # Loop through each line in toolkit.txt
        while IFS= read -r repo; do
            repo_name=$(basename "$repo" .git)
            check_repo "$repo_name"
        done < toolkit.txt

        echo $'\n'"${green}Check completed.${reset}"
        ;;
    --clone)
        if [ -n "$2" ]; then
            IFS=',' read -r -a tools <<< "$2"
            for tool in "${tools[@]}"; do
                clone_repo "$tool" "$tool" "N/A" "N/A"
            done
        else
            echo $'\n'"${red}Error: Missing tool name.${reset}"
            exit 1
        fi
        ;;
    --remove)
        if [ -n "$2" ]; then
            IFS=',' read -r -a tools <<< "$2"
            for tool in "${tools[@]}"; do
                remove_repo "$tool"
            done
        else
            echo $'\n'"${red}Error: Missing tool name.${reset}"
            exit 1
        fi
        ;;
    --check)
        if [ -n "$2" ]; then
            IFS=',' read -r -a tools <<< "$2"
            for tool in "${tools[@]}"; do
                check_repo "$tool"
            done
        else
            echo $'\n'"${red}Error: Missing tool name.${reset}"
            exit 1
        fi
        ;;
    -h|--help)
        show_help
        ;;
    *)
        echo $'\n'"${red}Error: Invalid option. Use -h or --help for usage information.${reset}"
        exit 1
        ;;
esac
