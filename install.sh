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
    "$(pwd)"
    "${SCRIPT_DIR}"
    "${HOME}/.steam/steam/steamapps/common/RimWorld"
    "${HOME}/.local/share/Steam/steamapps/common/RimWorld"
    "${HOME}/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common/RimWorld"
    "${HOME}/Games/RimWorld"
    "${HOME}/Documents/games/RimWorld"
    "${HOME}/GOG Games/RimWorld"
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

TEMP_DIR=""
cleanup() {
    if [[ -n "$TEMP_DIR" && -d "$TEMP_DIR" ]]; then
        rm -rf "$TEMP_DIR"
    fi
}
trap cleanup EXIT

SRC_BASE="${SCRIPT_DIR}"

# Check if local translation files exist, or download them from GitHub
if [[ ! -d "${SRC_BASE}/Core" ]]; then
    echo -e "${CLR_YELLOW}Translation files not found in: ${SRC_BASE}${CLR_RESET}"
    echo -e "${CLR_CYAN}Downloading latest translation pack from GitHub...${CLR_RESET}"

    TEMP_DIR="$(mktemp -d /tmp/rimworld_farsi_XXXXXX)"
    DOWNLOAD_SUCCESS=false

    DOWNLOAD_URLS=(
        "https://github.com/Ludeon/RimWorld-Farsi/archive/refs/heads/beta.tar.gz"
        "https://github.com/Ludeon/RimWorld-Farsi/archive/refs/heads/master.tar.gz"
    )

    if command -v curl &>/dev/null; then
        for URL in "${DOWNLOAD_URLS[@]}"; do
            if curl -sSL "$URL" | tar -xz -C "$TEMP_DIR" --strip-components=1 2>/dev/null; then
                DOWNLOAD_SUCCESS=true
                break
            fi
        done
    elif command -v wget &>/dev/null; then
        for URL in "${DOWNLOAD_URLS[@]}"; do
            if wget -qO- "$URL" | tar -xz -C "$TEMP_DIR" --strip-components=1 2>/dev/null; then
                DOWNLOAD_SUCCESS=true
                break
            fi
        done
    fi

    if [[ "$DOWNLOAD_SUCCESS" != true ]] && command -v git &>/dev/null; then
        if git clone --depth 1 -b beta https://github.com/Ludeon/RimWorld-Farsi.git "$TEMP_DIR" 2>/dev/null || \
           git clone --depth 1 https://github.com/Ludeon/RimWorld-Farsi.git "$TEMP_DIR" 2>/dev/null; then
            DOWNLOAD_SUCCESS=true
        fi
    fi

    if [[ "$DOWNLOAD_SUCCESS" != true || ! -d "${TEMP_DIR}/Core" ]]; then
        echo -e "${CLR_RED}Error:${CLR_RESET} Failed to download translation files from GitHub." >&2
        echo -e "Please ensure you have an active internet connection (curl, wget, or git), or" >&2
        echo -e "download the full repository manually from: https://github.com/Ludeon/RimWorld-Farsi" >&2
        exit 1
    fi

    SRC_BASE="$TEMP_DIR"
    echo -e "${CLR_GREEN}Download completed successfully.${CLR_RESET}\n"
fi

INSTALLED_COUNT=0

for MOD in "${MODULES[@]}"; do
    SRC_DIR="${SRC_BASE}/${MOD}"
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
            INSTALLED_COUNT=$((INSTALLED_COUNT + 1))
        else
            echo -e "  ${CLR_YELLOW}[SKIPPED]${CLR_RESET} ${MOD} DLC not found in game."
        fi
    fi
done

if [[ "$INSTALLED_COUNT" -eq 0 ]]; then
    echo -e "\n${CLR_RED}Error:${CLR_RESET} No translation modules could be installed." >&2
    echo -e "Please check that your RimWorld folder contains 'Data/Core'." >&2
    exit 1
fi

echo -e "\n${CLR_BOLD}======================================================================${CLR_RESET}"
echo -e "${CLR_BOLD}${CLR_GREEN}Installation completed successfully! (${INSTALLED_COUNT} modules installed)${CLR_RESET}"
echo -e "Launch RimWorld, navigate to Options -> Language, and choose 'Persian (فارسی)'."
echo -e "${CLR_BOLD}======================================================================${CLR_RESET}\n"
