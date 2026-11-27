#!/usr/bin/env bash
# ==============================================================================
# RimWorld Persian Translation & RTL Support Installer
# Native multi-platform installer for Linux, Steam Deck & macOS
# ==============================================================================

set -euo pipefail

CLR_RESET="\033[0m"
CLR_BOLD="\033[1m"
CLR_GREEN="\033[32m"
CLR_YELLOW="\033[33m"
CLR_BLUE="\033[34m"
CLR_RED="\033[31m"
CLR_CYAN="\033[36m"
CLR_MAGENTA="\033[35m"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LANG_NAME="Persian (فارسی)"
MODULES=("Core" "Royalty" "Ideology" "Biotech" "Anomaly" "Odyssey")

echo -e "${CLR_BOLD}${CLR_MAGENTA}======================================================================${CLR_RESET}"
echo -e "${CLR_BOLD}${CLR_CYAN}    RimWorld Persian (فارسی) Translation & RTL Engine Installer${CLR_RESET}"
echo -e "${CLR_BOLD}${CLR_CYAN}         Universal Linux, Steam Deck & Native Game Edition${CLR_RESET}"
echo -e "${CLR_BOLD}${CLR_MAGENTA}======================================================================${CLR_RESET}\n"

USE_LOCAL=false
INSTALL_MOD=""
EDITION=""
GAME_PATH=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --local|-l)
            USE_LOCAL=true
            shift
            ;;
        --with-mod)
            INSTALL_MOD=true
            shift
            ;;
        --no-mod)
            INSTALL_MOD=false
            shift
            ;;
        --essential|-e)
            EDITION="essential"
            shift
            ;;
        --full|-f)
            EDITION="full"
            shift
            ;;
        --mod|-m)
            EDITION="mod"
            shift
            ;;
        --edition)
            if [[ -n "${2:-}" && ( "$2" == "essential" || "$2" == "full" || "$2" == "mod" ) ]]; then
                EDITION="$2"
                shift 2
            else
                echo -e "${CLR_RED}Error:${CLR_RESET} --edition requires 'essential', 'full', or 'mod'." >&2
                exit 1
            fi
            ;;
        --edition=*)
            EDITION="${1#*=}"
            if [[ "$EDITION" != "essential" && "$EDITION" != "full" && "$EDITION" != "mod" ]]; then
                echo -e "${CLR_RED}Error:${CLR_RESET} --edition requires 'essential', 'full', or 'mod'." >&2
                exit 1
            fi
            shift
            ;;
        --help|-h)
            echo "Usage: ./install.sh [OPTIONS] [GAME_PATH]"
            echo ""
            echo "Options:"
            echo "  -l, --local            Use local repository translation files instead of downloading latest release"
            echo "  -e, --essential        Install Essential edition (Persian Keyed/DefInjected, English Strings/, standalone)"
            echo "  -f, --full             Install Full edition (complete Persian translation including Strings/, standalone)"
            echo "  -m, --mod              Install Translation + RTL Mod edition (raw UTF-8 + Vazirmatn font & Harmony RTL mod)"
            echo "      --edition <TYPE>   Explicitly choose 'essential', 'full', or 'mod'"
            echo "      --with-mod         Also install Harmony RTL support mod with standalone editions"
            echo "      --no-mod           Skip Harmony RTL support mod"
            echo "  -h, --help             Show this help message"
            exit 0
            ;;
        *)
            if [[ -z "$GAME_PATH" ]]; then
                GAME_PATH="$1"
            fi
            shift
            ;;
    esac
done

if [[ -z "$EDITION" ]]; then
    echo -e "${CLR_BOLD}Select installation option:${CLR_RESET}"
    echo -e "  ${CLR_GREEN}[1] Essential${CLR_RESET}             (Standalone — Persian UI & gameplay, English Strings/, no mod)"
    echo -e "  ${CLR_CYAN}[2] Full${CLR_RESET}                  (Standalone — Complete Persian translation incl. Strings/, no mod)"
    echo -e "  ${CLR_MAGENTA}[3] Translation + RTL Mod${CLR_RESET} (Recommended with Mods — Vazirmatn font & dynamic RTL engine)"
    read -r -p "Enter choice [1/2/3] (default: 1): " EDITION_CHOICE
    case "${EDITION_CHOICE:-1}" in
        1|essential|Essential|e|E)
            EDITION="essential"
            ;;
        2|full|Full|f|F)
            EDITION="full"
            ;;
        3|mod|Mod|m|M|rtl|RTL)
            EDITION="mod"
            ;;
        *)
            echo -e "${CLR_RED}Error:${CLR_RESET} Invalid choice '${EDITION_CHOICE}'. Please enter 1, 2, or 3." >&2
            exit 1
            ;;
    esac
    echo ""
fi

if [[ -z "$INSTALL_MOD" ]]; then
    if [[ "$EDITION" == "mod" ]]; then
        INSTALL_MOD=true
    else
        INSTALL_MOD=false
    fi
fi

echo -e "Selected option: ${CLR_BOLD}${EDITION}${CLR_RESET} (RTL Mod: ${CLR_BOLD}${INSTALL_MOD}${CLR_RESET})"

# Comprehensive candidate search list for Linux, Steam Deck & Flatpak
CANDIDATE_PATHS=(
    "$(pwd)"
    "${SCRIPT_DIR}"
    # Standard Steam Linux
    "${HOME}/.steam/steam/steamapps/common/RimWorld"
    "${HOME}/.local/share/Steam/steamapps/common/RimWorld"
    # Flatpak Steam (Default on immutable distros like SteamOS / Fedora Silverblue)
    "${HOME}/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common/RimWorld"
    "${HOME}/.var/app/com.valvesoftware.Steam/data/Steam/steamapps/common/RimWorld"
    # DRM-free / Standalone / GOG / Heroic / Lutris
    "${HOME}/Games/RimWorld"
    "${HOME}/Games/Heroic/RimWorld"
    "${HOME}/Documents/games/RimWorld"
    "${HOME}/GOG Games/RimWorld"
    "${HOME}/.wine/drive_c/GOG Games/RimWorld"
    "${HOME}/.wine/drive_c/Program Files (x86)/Steam/steamapps/common/RimWorld"
)

# Detect MicroSD and external storage paths on Steam Deck
for sd in /run/media/*/*/steamapps/common/RimWorld /run/media/deck/*/steamapps/common/RimWorld /media/"${USER:-deck}"/*/steamapps/common/RimWorld; do
    if [[ -d "$sd" ]]; then
        CANDIDATE_PATHS+=("$sd")
    fi
done

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

echo -e "Detected RimWorld installation at: ${CLR_BLUE}${GAME_PATH}${CLR_RESET}\n"

TEMP_DIR=""
cleanup() {
    if [[ -n "$TEMP_DIR" && -d "$TEMP_DIR" ]]; then
        rm -rf "$TEMP_DIR"
    fi
}
trap cleanup EXIT

SRC_BASE=""
MOD_SRC=""

# Option 3 ('mod') prefers local raw UTF-8 repository + compiled RTL mod if available,
# otherwise downloads the repository archive from GitHub so both raw UTF-8 XMLs and the mod are fetched.
if [[ "$EDITION" == "mod" ]]; then
    if [[ -d "${SCRIPT_DIR}/Core" && -d "${SCRIPT_DIR}/mods/RTL_Persian_Support" ]]; then
        echo -e "${CLR_CYAN}Using local raw UTF-8 translation files and RTL Support mod from: ${SCRIPT_DIR}${CLR_RESET}\n"
        SRC_BASE="${SCRIPT_DIR}"
        MOD_SRC="${SCRIPT_DIR}/mods/RTL_Persian_Support"
        USED_LOCAL_SOURCE=true
    elif [[ "$USE_LOCAL" != true ]]; then
        echo -e "${CLR_CYAN}Downloading raw translation & RTL Support mod package from GitHub...${CLR_RESET}"
        TEMP_DIR="$(mktemp -d /tmp/rimworld_farsi_XXXXXX)"
        ARCHIVE_URL="https://github.com/Ludeon/RimWorld-Farsi/archive/refs/heads/beta.zip"
        DOWNLOADED=false
        if command -v curl &>/dev/null; then
            curl -sSL "$ARCHIVE_URL" -o "${TEMP_DIR}/repo.zip" && DOWNLOADED=true || true
        elif command -v wget &>/dev/null; then
            wget -qO "${TEMP_DIR}/repo.zip" "$ARCHIVE_URL" && DOWNLOADED=true || true
        fi
        if [[ "$DOWNLOADED" == true && -f "${TEMP_DIR}/repo.zip" ]]; then
            if command -v unzip &>/dev/null; then
                unzip -q "${TEMP_DIR}/repo.zip" -d "${TEMP_DIR}/extracted" || true
            elif command -v python3 &>/dev/null; then
                python3 -m zipfile -e "${TEMP_DIR}/repo.zip" "${TEMP_DIR}/extracted" || true
            fi
            REPO_SUBDIR=$(find "${TEMP_DIR}/extracted" -mindepth 1 -maxdepth 1 -type d | head -n 1 || true)
            if [[ -n "$REPO_SUBDIR" && -d "${REPO_SUBDIR}/Core" ]]; then
                SRC_BASE="$REPO_SUBDIR"
                MOD_SRC="${REPO_SUBDIR}/mods/RTL_Persian_Support"
                USED_LOCAL_SOURCE=true
                echo -e "${CLR_GREEN}Downloaded raw translation and RTL Support mod package.${CLR_RESET}\n"
            fi
        fi
    fi
fi

# Standalone editions ('essential' / 'full'): download latest pre-processed release ZIP from GitHub unless --local
if [[ -z "$SRC_BASE" && "$USE_LOCAL" != true ]]; then
    echo -e "${CLR_CYAN}Checking for latest Persian translation release on GitHub...${CLR_RESET}"

    RELEASE_JSON=""
    if command -v curl &>/dev/null; then
        RELEASE_JSON=$(curl -sSL -H "User-Agent: RimWorld-Farsi-Installer" "https://api.github.com/repos/Ludeon/RimWorld-Farsi/releases/latest" 2>/dev/null || true)
    elif command -v wget &>/dev/null; then
        RELEASE_JSON=$(wget -qO- --user-agent="RimWorld-Farsi-Installer" "https://api.github.com/repos/Ludeon/RimWorld-Farsi/releases/latest" 2>/dev/null || true)
    fi

    if [[ "$EDITION" == "essential" ]]; then
        ZIP_URL=$(echo "$RELEASE_JSON" | grep -o 'https://[^"]*persian-language-essential-[^"]*\.zip' | head -n 1 || true)
    else
        ZIP_URL=$(echo "$RELEASE_JSON" | grep -o 'https://[^"]*persian-language-full-[^"]*\.zip' | head -n 1 || true)
        if [[ -z "$ZIP_URL" ]]; then
            ZIP_URL=$(echo "$RELEASE_JSON" | grep -o 'https://[^"]*persian-language-[0-9][^"]*\.zip' | head -n 1 || true)
        fi
    fi

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
USED_LOCAL_SOURCE="${USED_LOCAL_SOURCE:-false}"
if [[ -z "$SRC_BASE" ]]; then
    if [[ -d "${SCRIPT_DIR}/Core" ]]; then
        echo -e "${CLR_YELLOW}Using local repository translation files from: ${SCRIPT_DIR}${CLR_RESET}\n"
        SRC_BASE="${SCRIPT_DIR}"
        USED_LOCAL_SOURCE=true
    else
        echo -e "${CLR_RED}Error:${CLR_RESET} Failed to fetch release from GitHub and no local translation files found in: ${SCRIPT_DIR}" >&2
        echo -e "Please check your internet connection or download manually from: https://github.com/Ludeon/RimWorld-Farsi/releases" >&2
        exit 1
    fi
fi
if [[ -z "$MOD_SRC" && -d "${SCRIPT_DIR}/mods/RTL_Persian_Support" ]]; then
    MOD_SRC="${SCRIPT_DIR}/mods/RTL_Persian_Support"
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

            # In Essential or Mod mode from repo/archive, swap Strings/ with original English Strings/
            if [[ ( "$EDITION" == "essential" || "$EDITION" == "mod" ) && "$USED_LOCAL_SOURCE" == true ]]; then
                rm -rf "${DEST_DIR}/Strings"
                if [[ -d "${SRC_BASE}/src/english/${MOD}/Strings" ]]; then
                    cp -r "${SRC_BASE}/src/english/${MOD}/Strings" "${DEST_DIR}/Strings"
                fi
            fi

            # Purge cached .tar files so RimWorld reloads fresh XML assets
            rm -f "${GAME_PATH}/Data/${MOD}/Languages/${LANG_NAME}.tar"
            rm -f "${GAME_PATH}/Data/${MOD}/Languages/Persian.tar"
            rm -f "${GAME_PATH}/Data/${MOD}/Languages/Persian (فارسی).tar"
            rm -f "${GAME_PATH}/Data/${MOD}/Languages/Farsi.tar"

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

# Install Harmony RTL Mod into Mods/ folder if requested
if [[ "$INSTALL_MOD" == true && -n "$MOD_SRC" && -d "$MOD_SRC" ]]; then
    echo -e "\n${CLR_CYAN}Installing RTL Persian Support mod (Vazirmatn font & Harmony engine)...${CLR_RESET}"
    MOD_DEST="${GAME_PATH}/Mods/RTL_Persian_Support"
    rm -rf "$MOD_DEST"
    mkdir -p "$MOD_DEST"
    cp -r "${MOD_SRC}/"* "$MOD_DEST/"
    echo -e "  ${CLR_GREEN}[OK]${CLR_RESET} RTL Persian Support mod installed to: ${CLR_BLUE}${MOD_DEST}${CLR_RESET}"
fi

echo -e "\n${CLR_BOLD}${CLR_MAGENTA}======================================================================${CLR_RESET}"
echo -e "${CLR_BOLD}${CLR_GREEN}   Installation completed successfully! (${INSTALLED_COUNT} modules, edition: ${EDITION})${CLR_RESET}"
echo -e "   1. Launch RimWorld."
echo -e "   2. Navigate to: Options -> Language -> Select 'Persian (فارسی)'."
if [[ "$INSTALL_MOD" == true ]]; then
    echo -e "   3. (Recommended) Under 'Mods', enable 'Persian RTL Support' for Vazirmatn font and RTL alignment."
fi
echo -e "${CLR_BOLD}${CLR_MAGENTA}======================================================================${CLR_RESET}\n"
