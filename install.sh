#!/usr/bin/env bash
# ==============================================================================
# RimWorld Persian Translation Installer for Linux & Steam Deck
# ==============================================================================

set -euo pipefail

CLR_RESET="\033[0m"
CLR_BOLD="\033[1m"
CLR_GREEN="\033[32m"
CLR_YELLOW="\033[33m"
CLR_BLUE="\033[34m"
CLR_RED="\033[31m"
CLR_CYAN="\033[36m"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LANG_NAME="Persian (فارسی)"
MODULES=("Core" "Royalty" "Ideology" "Biotech" "Anomaly" "Odyssey")

echo -e "${CLR_BOLD}======================================================================${CLR_RESET}"
echo -e "${CLR_BOLD}${CLR_CYAN}    RimWorld Persian (فارسی) Translation Installer (Linux/Steam Deck)${CLR_RESET}"
echo -e "${CLR_BOLD}======================================================================${CLR_RESET}\n"

GAME_PATH=""

# Auto-detect common Linux Steam paths
CANDIDATE_PATHS=(
    "${HOME}/.steam/steam/steamapps/common/RimWorld"
    "${HOME}/.local/share/Steam/steamapps/common/RimWorld"
    "${HOME}/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common/RimWorld"
)

if [[ $# -gt 0 ]]; then
    GAME_PATH="$1"
else
    for CANDIDATE in "${CANDIDATE_PATHS[@]}"; do
        if [[ -d "${CANDIDATE}/Data/Core" ]]; then
            GAME_PATH="${CANDIDATE}"
            break
        fi
    done
fi

if [[ -z "$GAME_PATH" || ! -d "${GAME_PATH}/Data/Core" ]]; then
    echo -e "${CLR_YELLOW}Could not automatically detect your RimWorld installation.${CLR_RESET}"
    read -r -p "Please enter the path to your RimWorld directory: " GAME_PATH
fi

if [[ ! -d "${GAME_PATH}/Data/Core" ]]; then
    echo -e "${CLR_RED}Error:${CLR_RESET} Invalid RimWorld folder. 'Data/Core' was not found in: ${GAME_PATH}" >&2
    exit 1
fi

echo -e "Installing to: ${CLR_BLUE}${GAME_PATH}${CLR_RESET}\n"

for MOD in "${MODULES[@]}"; do
    SRC_DIR="${SCRIPT_DIR}/${MOD}"
    DEST_DIR="${GAME_PATH}/Data/${MOD}/Languages/${LANG_NAME}"

    if [[ -d "$SRC_DIR" ]]; then
        if [[ -d "${GAME_PATH}/Data/${MOD}" ]]; then
            echo -e "Installing module: ${CLR_CYAN}${MOD}${CLR_RESET}..."
            rm -rf "$DEST_DIR"
            mkdir -p "$DEST_DIR"
            cp -r "${SRC_DIR}/"* "$DEST_DIR/"
            rm -f "${GAME_PATH}/Data/${MOD}/Languages/${LANG_NAME}.tar"
            rm -f "${GAME_PATH}/Data/${MOD}/Languages/Persian.tar"
            echo -e "  ${CLR_GREEN}[OK]${CLR_RESET} ${MOD} installed."
        else
            echo -e "  ${CLR_YELLOW}[SKIPPED]${CLR_RESET} ${MOD} DLC not found in game."
        fi
    fi
done

echo -e "\n${CLR_BOLD}======================================================================${CLR_RESET}"
echo -e "${CLR_BOLD}${CLR_GREEN}Installation completed successfully!${CLR_RESET}"
echo -e "Launch RimWorld, navigate to Options -> Language, and choose 'Persian (فارسی)'."
echo -e "${CLR_BOLD}======================================================================${CLR_RESET}\n"
