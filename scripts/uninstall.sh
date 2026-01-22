#!/usr/bin/env bash
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
WAYBAR_MODULES_DIR="$HOME/.config/waybar/modules"
WAYBAR_CONFIG="$HOME/.config/waybar/config.jsonc"
WAYBAR_STYLE="$HOME/.config/waybar/style.css"
MODULE_NAME="waybar-mpris-enhanced"
INSTALL_PATH="$WAYBAR_MODULES_DIR/$MODULE_NAME"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       Waybar MPRIS Enhanced - Uninstall Script             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo

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

# Remove module files/symlink
remove_module() {
    if [[ ! -e "$INSTALL_PATH" ]]; then
        echo -e "${YELLOW}Module not found at $INSTALL_PATH${NC}"
        return 0
    fi

    if [[ -L "$INSTALL_PATH" ]]; then
        echo "Found symlink at $INSTALL_PATH"
        rm "$INSTALL_PATH"
        echo -e "${GREEN}✓${NC} Removed symlink"
    elif [[ -d "$INSTALL_PATH" ]]; then
        echo "Found directory at $INSTALL_PATH"
        rm -rf "$INSTALL_PATH"
        echo -e "${GREEN}✓${NC} Removed directory"
    else
        echo -e "${RED}Error: $INSTALL_PATH exists but is neither a symlink nor directory${NC}"
        return 1
    fi
}

# Remove module from waybar config
remove_from_config() {
    if [[ ! -f "$WAYBAR_CONFIG" ]]; then
        echo -e "${YELLOW}Waybar config not found at $WAYBAR_CONFIG${NC}"
        return 0
    fi

    local needs_update=false

    # Check if module is referenced
    if grep -q "group/enhanced-mpris" "$WAYBAR_CONFIG"; then
        needs_update=true
    fi

    if grep -q "$MODULE_NAME/mpris-enhanced.jsonc" "$WAYBAR_CONFIG"; then
        needs_update=true
    fi

    if [[ "$needs_update" == "false" ]]; then
        echo -e "${GREEN}✓${NC} Module not found in waybar config"
        return 0
    fi

    # Warn about comments
    if grep -q '//' "$WAYBAR_CONFIG"; then
        echo -e "${YELLOW}Warning: Your config contains comments which will be removed.${NC}"
        if ! ask_yes_no "Continue anyway?" "y"; then
            echo -e "${YELLOW}Skipped.${NC} Remove module references from config manually."
            return 0
        fi
    fi

    # Check for json5 Python module
    if ! python3 -c "import json5" &> /dev/null; then
        echo -e "${RED}Error: python3-json5 is required to modify config${NC}"
        echo "Install it with: pip install json5"
        echo "Or remove module references manually."
        return 1
    fi

    # Use Python with json5 to modify the config
    if python3 << PYTHON
import json5
import sys

config_path = "$WAYBAR_CONFIG"
module_name = "group/enhanced-mpris"
include_pattern = "$MODULE_NAME/mpris-enhanced.jsonc"

try:
    with open(config_path, 'r') as f:
        config = json5.load(f)

    modified = False

    # Remove from modules arrays
    for array_name in ["modules-left", "modules-center", "modules-right"]:
        if array_name in config and module_name in config[array_name]:
            config[array_name].remove(module_name)
            modified = True
            print(f"Removed from {array_name}")

    # Remove from include array
    if "include" in config:
        original_len = len(config["include"])
        config["include"] = [
            inc for inc in config["include"]
            if include_pattern not in inc
        ]
        if len(config["include"]) < original_len:
            modified = True
            print("Removed from include array")

        # Remove empty include array
        if not config["include"]:
            del config["include"]

    if modified:
        with open(config_path, 'w') as f:
            json5.dump(config, f, indent=2, quote_keys=True, trailing_commas=False)

    sys.exit(0)
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
PYTHON
    then
        echo -e "${GREEN}✓${NC} Removed module references from waybar config"
    else
        echo -e "${RED}Error: Failed to update config${NC}"
        return 1
    fi
}

# Remove CSS import from waybar style
remove_css_import() {
    if [[ ! -f "$WAYBAR_STYLE" ]]; then
        echo -e "${YELLOW}Waybar style.css not found at $WAYBAR_STYLE${NC}"
        return 0
    fi

    if ! grep -q "$MODULE_NAME/mpris-enhanced.css" "$WAYBAR_STYLE"; then
        echo -e "${GREEN}✓${NC} CSS import not found in waybar style.css"
        return 0
    fi

    # Remove the import line
    sed -i "/$MODULE_NAME\/mpris-enhanced.css/d" "$WAYBAR_STYLE"
    echo -e "${GREEN}✓${NC} Removed CSS import from waybar style.css"
}

# Main uninstall flow
main() {
    if ! ask_yes_no "Uninstall Waybar MPRIS Enhanced?" "n"; then
        echo "Uninstall cancelled."
        exit 0
    fi

    echo
    echo -e "${YELLOW}Removing module files...${NC}"
    remove_module

    echo
    echo -e "${YELLOW}Cleaning waybar config...${NC}"
    remove_from_config

    echo
    echo -e "${YELLOW}Cleaning waybar style...${NC}"
    remove_css_import

    echo
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║              Uninstall Complete!                           ║${NC}"
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
