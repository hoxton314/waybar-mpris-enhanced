#!/usr/bin/env bash
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
REPO_NAME="$(basename "$REPO_DIR")"
WAYBAR_MODULES_DIR="$HOME/.config/waybar/modules"
WAYBAR_CONFIG="$HOME/.config/waybar/config.jsonc"
WAYBAR_STYLE="$HOME/.config/waybar/style.css"
MODULE_NAME="$REPO_NAME"
INSTALL_PATH="$WAYBAR_MODULES_DIR/$MODULE_NAME"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       Waybar MPRIS Enhanced - Installation Script          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo

# Check dependencies
check_dependencies() {
    local missing=()

    if ! command -v playerctl &> /dev/null; then
        missing+=("playerctl")
    fi

    if ! command -v python3 &> /dev/null; then
        missing+=("python3")
    fi

    if [[ ${#missing[@]} -gt 0 ]]; then
        echo -e "${RED}Error: Missing dependencies: ${missing[*]}${NC}"
        echo "Please install them before continuing."
        exit 1
    fi

    echo -e "${GREEN}✓${NC} Dependencies check passed (python3, playerctl)"
}

# Ask yes/no question
ask_yes_no() {
    local prompt="$1"
    local default="${2:-}"
    local answer

    while true; do
        if [[ "$default" == "y" ]]; then
            read -rp "$prompt [Y/n]: " answer
            answer="${answer:-y}"
        elif [[ "$default" == "n" ]]; then
            read -rp "$prompt [y/N]: " answer
            answer="${answer:-n}"
        else
            read -rp "$prompt [y/n]: " answer
        fi

        case "${answer,,}" in
            y|yes) return 0 ;;
            n|no) return 1 ;;
            *) echo "Please answer y or n." ;;
        esac
    done
}

# Install module files
install_module() {
    echo
    echo -e "${YELLOW}Installation Method${NC}"
    echo "1) Symlink (recommended) - Links to this repository location"
    echo "   Allows easy updates by pulling the latest changes with git"
    echo "2) Copy - Copies all files to waybar modules directory"
    echo "   Files are independent but won't receive updates automatically"
    echo

    local choice
    while true; do
        read -rp "Choose installation method [1/2]: " choice
        case "$choice" in
            1) install_symlink; break ;;
            2) install_copy; break ;;
            *) echo "Please enter 1 or 2." ;;
        esac
    done
}

install_symlink() {
    echo
    echo -e "${BLUE}Installing via symlink...${NC}"

    # Create modules directory if it doesn't exist
    mkdir -p "$WAYBAR_MODULES_DIR"

    # Remove existing installation if present
    if [[ -e "$INSTALL_PATH" ]]; then
        if [[ -L "$INSTALL_PATH" ]]; then
            echo "Removing existing symlink at $INSTALL_PATH"
            rm "$INSTALL_PATH"
        else
            echo -e "${RED}Error: $INSTALL_PATH exists and is not a symlink.${NC}"
            echo "Please remove it manually and run the installer again."
            exit 1
        fi
    fi

    # Create symlink
    ln -s "$REPO_DIR" "$INSTALL_PATH"
    echo -e "${GREEN}✓${NC} Created symlink: $INSTALL_PATH -> $REPO_DIR"
}

install_copy() {
    echo
    echo -e "${BLUE}Installing via copy...${NC}"

    # Create modules directory if it doesn't exist
    mkdir -p "$WAYBAR_MODULES_DIR"

    # Remove existing installation if present
    if [[ -e "$INSTALL_PATH" ]]; then
        if [[ -L "$INSTALL_PATH" ]]; then
            echo "Removing existing symlink at $INSTALL_PATH"
            rm "$INSTALL_PATH"
        elif [[ -d "$INSTALL_PATH" ]]; then
            echo "Removing existing directory at $INSTALL_PATH"
            rm -rf "$INSTALL_PATH"
        fi
    fi

    # Create destination directory
    mkdir -p "$INSTALL_PATH"

    # Copy required files
    cp "$REPO_DIR/mpris_enhanced.py" "$INSTALL_PATH/"
    cp -r "$REPO_DIR/mpris_enhanced" "$INSTALL_PATH/"
    cp "$REPO_DIR/mpris-enhanced.jsonc" "$INSTALL_PATH/"
    cp "$REPO_DIR/mpris-enhanced.css" "$INSTALL_PATH/"

    echo -e "${GREEN}✓${NC} Copied files to $INSTALL_PATH"
}

# Configure waybar imports
configure_waybar() {
    local include_line="\"./modules/$MODULE_NAME/mpris-enhanced.jsonc\""
    local css_import="@import './modules/$MODULE_NAME/mpris-enhanced.css';"

    echo
    echo -e "${YELLOW}Waybar Configuration${NC}"

    if ask_yes_no "Auto-add imports to waybar config.jsonc and style.css?" "y"; then
        add_waybar_include "$include_line"
        add_waybar_css_import "$css_import"
    else
        show_manual_instructions "$include_line" "$css_import"
    fi
}

show_manual_instructions() {
    local include_line="$1"
    local css_import="$2"

    echo
    echo -e "${YELLOW}Manual configuration required:${NC}"
    echo
    echo -e "${BLUE}1. config.jsonc${NC} ($WAYBAR_CONFIG)"
    echo
    echo "   Add to your \"include\" array (create one if it doesn't exist):"
    echo -e "   ${GREEN}$include_line${NC}"
    echo
    echo "   Add \"group/enhanced-mpris\" to your modules-left/center/right array"
    echo
    echo -e "${BLUE}2. style.css${NC} ($WAYBAR_STYLE)"
    echo
    echo "   Add this import at the top of the file:"
    echo -e "   ${GREEN}$css_import${NC}"
    echo
}

add_waybar_include() {
    local include_line="$1"

    if [[ ! -f "$WAYBAR_CONFIG" ]]; then
        echo -e "${RED}Error: Waybar config not found at $WAYBAR_CONFIG${NC}"
        return 1
    fi

    # Check if already included
    if grep -q "$MODULE_NAME/mpris-enhanced.jsonc" "$WAYBAR_CONFIG"; then
        echo -e "${GREEN}✓${NC} Module already included in waybar config"
        return 0
    fi

    # Check if include array exists
    if grep -q '"include"' "$WAYBAR_CONFIG"; then
        # Add to existing include array using sed
        # Find the include line and append our module
        if grep -q '"include": \[\]' "$WAYBAR_CONFIG"; then
            # Empty include array
            sed -i "s|\"include\": \[\]|\"include\": [$include_line]|" "$WAYBAR_CONFIG"
        else
            # Non-empty include array - add after the opening bracket
            sed -i "s|\"include\": \[|\"include\": [$include_line, |" "$WAYBAR_CONFIG"
        fi
        echo -e "${GREEN}✓${NC} Added module to existing include array"
    else
        # No include array - add one after the opening brace
        sed -i "s|^{|{\n  \"include\": [$include_line],|" "$WAYBAR_CONFIG"
        echo -e "${GREEN}✓${NC} Created include array and added module"
    fi

    echo
    echo -e "${YELLOW}Note:${NC} Don't forget to add ${GREEN}\"group/enhanced-mpris\"${NC} to your"
    echo "modules-left, modules-center, or modules-right array if not already present."
}

add_waybar_css_import() {
    local css_import="$1"

    if [[ ! -f "$WAYBAR_STYLE" ]]; then
        echo -e "${RED}Error: Waybar style.css not found at $WAYBAR_STYLE${NC}"
        return 1
    fi

    # Check if already imported
    if grep -q "$MODULE_NAME/mpris-enhanced.css" "$WAYBAR_STYLE"; then
        echo -e "${GREEN}✓${NC} CSS already imported in waybar style.css"
        return 0
    fi

    # Add import at the top of the file (after any existing @imports)
    if grep -q '^@import' "$WAYBAR_STYLE"; then
        # Add after the last @import line
        local last_import_line
        last_import_line=$(grep -n '^@import' "$WAYBAR_STYLE" | tail -1 | cut -d: -f1)
        sed -i "${last_import_line}a\\$css_import" "$WAYBAR_STYLE"
    else
        # No existing imports - add at the very top
        sed -i "1i\\$css_import" "$WAYBAR_STYLE"
    fi

    echo -e "${GREEN}✓${NC} Added CSS import to waybar style.css"
}

# Main installation flow
main() {
    check_dependencies
    install_module
    configure_waybar

    echo
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║              Installation Complete!                        ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo
    echo "Restart waybar to apply changes:"
    echo -e "  ${BLUE}killall waybar && waybar &${NC}"
    echo
    echo "Or if using hyprland:"
    echo -e "  ${BLUE}hyprctl reload${NC}"
    echo
}

main "$@"
