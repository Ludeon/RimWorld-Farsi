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

USE_LOCAL=false
GAME_PATH=""

for arg in "$@"; do
    case "$arg" in
        --local|-l)
            USE_LOCAL=true
            ;;
        --help|-h)
            echo "Usage: ./install.sh [OPTIONS] [GAME_PATH]"
            echo ""
            echo "Options:"
            echo "  -l, --local    Use local repository translation files instead of downloading latest release"
            echo "  -h, --help     Show this help message"
            exit 0
            ;;
        *)
            if [[ -z "$GAME_PATH" ]]; then
                GAME_PATH="$arg"
            fi
            ;;
    esac
done

# Auto-detect common Linux Steam / Game paths
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

if [[ -z "$GAME_PATH" ]]; then
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

SRC_BASE=""

# If not forced to use local files, download latest processed release package from GitHub
if [[ "$USE_LOCAL" != true ]]; then
    echo -e "${CLR_CYAN}Checking for latest Persian translation release on GitHub...${CLR_RESET}"

    RELEASE_JSON=""
    if command -v curl &>/dev/null; then
        RELEASE_JSON=$(curl -sSL -H "User-Agent: RimWorld-Farsi-Installer" "https://api.github.com/repos/Ludeon/RimWorld-Farsi/releases/latest" 2>/dev/null || true)
    elif command -v wget &>/dev/null; then
        RELEASE_JSON=$(wget -qO- --user-agent="RimWorld-Farsi-Installer" "https://api.github.com/repos/Ludeon/RimWorld-Farsi/releases/latest" 2>/dev/null || true)
    fi

    ZIP_URL=$(echo "$RELEASE_JSON" | grep -o 'https://[^"]*persian-language-[^"]*\.zip' | head -n 1 || true)

    if [[ -n "$ZIP_URL" ]]; then
        TEMP_DIR="$(mktemp -d /tmp/rimworld_farsi_XXXXXX)"
        echo -e "Downloading latest release package: ${CLR_BLUE}${ZIP_URL}${CLR_RESET}"

        DOWNLOADED=false
        if command -v curl &>/dev/null; then
            if curl -sSL "$ZIP_URL" -o "${TEMP_DIR}/release.zip"; then
                DOWNLOADED=true
            fi
        elif command -v wget &>/dev/null; then
            if wget -qO "${TEMP_DIR}/release.zip" "$ZIP_URL"; then
                DOWNLOADED=true
            fi
        fi

        if [[ "$DOWNLOADED" == true && -f "${TEMP_DIR}/release.zip" ]]; then
            echo -e "Extracting translation files..."
            EXTRACTED=false
            if command -v unzip &>/dev/null; then
                if unzip -q "${TEMP_DIR}/release.zip" -d "${TEMP_DIR}/extracted"; then
                    EXTRACTED=true
                fi
            elif command -v python3 &>/dev/null; then
                if python3 -m zipfile -e "${TEMP_DIR}/release.zip" "${TEMP_DIR}/extracted"; then
                    EXTRACTED=true
                fi
            fi

            if [[ "$EXTRACTED" == true && -d "${TEMP_DIR}/extracted" ]]; then
                SRC_BASE="${TEMP_DIR}/extracted"
                echo -e "${CLR_GREEN}Latest processed translation package downloaded and ready.${CLR_RESET}\n"
            fi
        fi
    fi
fi

# Fallback to local translation repository if download was skipped or failed
if [[ -z "$SRC_BASE" ]]; then
    if [[ -d "${SCRIPT_DIR}/Core" ]]; then
        echo -e "${CLR_YELLOW}Using local repository translation files from: ${SCRIPT_DIR}${CLR_RESET}\n"
        SRC_BASE="${SCRIPT_DIR}"
    else
        echo -e "${CLR_RED}Error:${CLR_RESET} Failed to fetch release from GitHub and no local translation files found in: ${SCRIPT_DIR}" >&2
        echo -e "Please check your internet connection or download manually from: https://github.com/Ludeon/RimWorld-Farsi/releases" >&2
        exit 1
    fi
fi

INSTALLED_COUNT=0

for MOD in "${MODULES[@]}"; do
    SRC_DIR="${SRC_BASE}/${MOD}"

    # Handle nested module directories from build artifacts (e.g. Core/Core/DefInjected)
    if [[ -d "${SRC_DIR}/${MOD}" && ( -d "${SRC_DIR}/${MOD}/DefInjected" || -d "${SRC_DIR}/${MOD}/Keyed" || -f "${SRC_DIR}/${MOD}/LanguageInfo.xml" ) ]]; then
        SRC_DIR="${SRC_DIR}/${MOD}"
    fi

    DEST_DIR="${GAME_PATH}/Data/${MOD}/Languages/${LANG_NAME}"
    OLD_DEST_DIR="${GAME_PATH}/Data/${MOD}/Languages/Persian"

    if [[ -d "$SRC_DIR" ]]; then
        if [[ -d "${GAME_PATH}/Data/${MOD}" ]]; then
            echo -e "Installing module: ${CLR_CYAN}${MOD}${CLR_RESET}..."

            # Overwrite previous installation completely
            rm -rf "$DEST_DIR"
            rm -rf "$OLD_DEST_DIR"
            mkdir -p "$DEST_DIR"

            cp -r "${SRC_DIR}/"* "$DEST_DIR/"

            # Purge cached .tar files so RimWorld loads the fresh XMLs
            rm -f "${GAME_PATH}/Data/${MOD}/Languages/${LANG_NAME}.tar"
            rm -f "${GAME_PATH}/Data/${MOD}/Languages/Persian.tar"
            rm -f "${GAME_PATH}/Data/${MOD}/Languages/Persian (فارسی).tar"

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
