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
IS_PACKAGED_BUNDLE=false

if [[ -f "${SCRIPT_DIR}/.release-edition" ]]; then
    BUNDLED_EDITION=$(tr -d '[:space:]' < "${SCRIPT_DIR}/.release-edition")
    if [[ "$BUNDLED_EDITION" == "essential" || "$BUNDLED_EDITION" == "full" || "$BUNDLED_EDITION" == "mod" ]]; then
        EDITION="$BUNDLED_EDITION"
        USE_LOCAL=true
        IS_PACKAGED_BUNDLE=true
    fi
fi

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
            echo "Usage: ./$(basename "$0") [OPTIONS] [GAME_PATH]"
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
        -*)
            echo -e "${CLR_RED}Error:${CLR_RESET} Unknown option '$1'. Run with --help for usage." >&2
            exit 1
            ;;
        *)
            if [[ -z "$GAME_PATH" ]]; then
                GAME_PATH="$1"
            else
                echo -e "${CLR_RED}Error:${CLR_RESET} Unexpected positional argument '$1'." >&2
                exit 1
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
    read -r -p "Enter choice [1/2/3] (default: 3): " EDITION_CHOICE
    case "${EDITION_CHOICE:-3}" in
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

# Comprehensive candidate search list for Linux, Steam Deck & macOS
CANDIDATE_PATHS=(
    "$(pwd)"
    "${SCRIPT_DIR}"
    # Standard Steam Linux
    "${HOME}/.steam/steam/steamapps/common/RimWorld"
    "${HOME}/.local/share/Steam/steamapps/common/RimWorld"
    # Flatpak Steam (Default on immutable distros like SteamOS / Fedora Silverblue)
    "${HOME}/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common/RimWorld"
    "${HOME}/.var/app/com.valvesoftware.Steam/data/Steam/steamapps/common/RimWorld"
    # macOS Steam & Standalone / GOG
    "${HOME}/Library/Application Support/Steam/steamapps/common/RimWorld/RimWorldMac.app"
    "/Applications/RimWorld.app"
    "${HOME}/Applications/RimWorld.app"
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

fetch_url() {
    local url="$1"
    local out="${2:-}"
    if command -v curl &>/dev/null; then
        if [[ -n "$out" ]]; then
            curl -fsSL -H "User-Agent: RimWorld-Farsi-Installer" "$url" -o "$out"
        else
            curl -fsSL -H "User-Agent: RimWorld-Farsi-Installer" "$url"
        fi
    elif command -v wget &>/dev/null; then
        if [[ -n "$out" ]]; then
            wget -qO "$out" --user-agent="RimWorld-Farsi-Installer" "$url"
        else
            wget -qO- --user-agent="RimWorld-Farsi-Installer" "$url"
        fi
    else
        return 1
    fi
}

extract_zip() {
    local zip_file="$1"
    local dest_dir="$2"
    mkdir -p "$dest_dir"
    if command -v unzip &>/dev/null; then
        unzip -q "$zip_file" -d "$dest_dir"
    elif command -v python3 &>/dev/null; then
        python3 -m zipfile -e "$zip_file" "$dest_dir"
    else
        return 1
    fi
}

verify_sha256() {
    local zip_file="$1"
    local sum_file="$2"
    local asset_name="$3"
    local expected=""
    local actual=""

    expected=$(awk -v target="$asset_name" '$2 == target || $2 == "*" target {print $1; exit}' "$sum_file" || true)
    [[ -z "$expected" ]] && expected=$(awk 'NF>=1 {print $1; exit}' "$sum_file" || true)
    if [[ -z "$expected" ]]; then
        echo -e "${CLR_RED}Error:${CLR_RESET} Could not find SHA-256 entry for '${asset_name}'." >&2
        return 1
    fi

    if command -v sha256sum &>/dev/null; then
        actual=$(sha256sum "$zip_file" | awk '{print $1}')
    elif command -v shasum &>/dev/null; then
        actual=$(shasum -a 256 "$zip_file" | awk '{print $1}')
    elif command -v python3 &>/dev/null; then
        actual=$(python3 -c 'import hashlib, sys; print(hashlib.sha256(open(sys.argv[1], "rb").read()).hexdigest())' "$zip_file")
    else
        echo -e "${CLR_YELLOW}Warning:${CLR_RESET} No SHA-256 tool found; skipping checksum verification."
        return 0
    fi

    if [[ "${actual,,}" != "${expected,,}" ]]; then
        echo -e "${CLR_RED}Error:${CLR_RESET} SHA-256 checksum mismatch for '${asset_name}'!" >&2
        echo -e "  Expected: ${expected}" >&2
        echo -e "  Actual:   ${actual}" >&2
        return 1
    fi
    echo -e "${CLR_GREEN}[OK]${CLR_RESET} Verified SHA-256 checksum for ${asset_name}."
}

find_release_assets() {
    local edition="$1"
    local rel_json
    rel_json=$(fetch_url "https://api.github.com/repos/Ludeon/RimWorld-Farsi/releases?per_page=10" 2>/dev/null || true)
    [[ -z "$rel_json" ]] && return 0

    if command -v python3 &>/dev/null; then
        EDITION="$edition" python3 -c '
import json, os, sys
ed = os.environ["EDITION"]
releases = json.loads(sys.stdin.read())
for rel in releases:
    assets = {a.get("name", ""): a.get("browser_download_url", "") for a in rel.get("assets", [])}
    chosen_name = ""
    if ed == "mod":
        for name in assets:
            if "With-RTL-Mod-" in name and name.endswith("-linux.zip"):
                chosen_name = name; break
    elif ed == "essential":
        for pat in [("RimWorld-Farsi-Essential-", "-linux.zip"), ("persian-language-essential-", ".zip")]:
            for name in assets:
                if name.startswith(pat[0]) and name.endswith(pat[1]):
                    chosen_name = name; break
            if chosen_name:
                break
    else:
        for name in assets:
            if name.startswith("RimWorld-Farsi-Full-") and name.endswith("-linux.zip"):
                chosen_name = name; break
        if not chosen_name:
            for name in assets:
                if name.startswith("persian-language-full-") and name.endswith(".zip"):
                    chosen_name = name; break
        if not chosen_name:
            for name in assets:
                if name.startswith("persian-language-") and "essential" not in name and name.endswith(".zip"):
                    chosen_name = name; break
    if chosen_name:
        sum_url = assets.get("SHA256SUMS.txt") or assets.get(f"{chosen_name}.sha256") or ""
        print(f"{assets[chosen_name]}\t{sum_url}")
        sys.exit(0)
' <<< "$rel_json" 2>/dev/null || true
    else
        local zurl=""
        if [[ "$edition" == "mod" ]]; then
            zurl=$(echo "$rel_json" | grep -o 'https://[^"]*RimWorld-Farsi-With-RTL-Mod-[^"]*-linux\.zip' | head -n 1 || true)
        elif [[ "$edition" == "essential" ]]; then
            zurl=$(echo "$rel_json" | grep -o 'https://[^"]*RimWorld-Farsi-Essential-[^"]*-linux\.zip' | head -n 1 || true)
        else
            zurl=$(echo "$rel_json" | grep -o 'https://[^"]*RimWorld-Farsi-Full-[^"]*-linux\.zip' | head -n 1 || true)
        fi
        if [[ -n "$zurl" ]]; then
            local sumurl
            sumurl=$(echo "$rel_json" | grep -o 'https://[^"]*SHA256SUMS\.txt' | head -n 1 || true)
            [[ -z "$sumurl" ]] && sumurl="${zurl}.sha256"
            printf '%s\t%s\n' "$zurl" "$sumurl"
        fi
    fi
}

SRC_BASE=""
MOD_SRC=""
USED_LOCAL_SOURCE=false

if [[ "$IS_PACKAGED_BUNDLE" == true ]]; then
    echo -e "${CLR_GREEN}Detected pre-packaged '${EDITION}' release bundle at: ${SCRIPT_DIR}${CLR_RESET}\n"
    SRC_BASE="${SCRIPT_DIR}"
    USED_LOCAL_SOURCE=true
    if [[ -d "${SCRIPT_DIR}/mods/RTL_Persian_Support" ]]; then
        MOD_SRC="${SCRIPT_DIR}/mods/RTL_Persian_Support"
    fi
elif [[ "$EDITION" == "mod" && -d "${SCRIPT_DIR}/Core" && -d "${SCRIPT_DIR}/mods/RTL_Persian_Support" ]]; then
    echo -e "${CLR_CYAN}Using local raw UTF-8 translation files and RTL Support mod from: ${SCRIPT_DIR}${CLR_RESET}\n"
    SRC_BASE="${SCRIPT_DIR}"
    MOD_SRC="${SCRIPT_DIR}/mods/RTL_Persian_Support"
    USED_LOCAL_SOURCE=true
elif [[ "$USE_LOCAL" != true ]]; then
    echo -e "${CLR_CYAN}Checking GitHub Releases for '${EDITION}' (-linux) package...${CLR_RESET}"
    ASSET_INFO=$(find_release_assets "$EDITION")
    ZIP_URL="${ASSET_INFO%%$'\t'*}"
    SUM_URL=""
    if [[ "$ASSET_INFO" == *$'\t'* ]]; then
        SUM_URL="${ASSET_INFO#*$'\t'}"
    fi

    if [[ -z "$ZIP_URL" && "$EDITION" == "mod" ]]; then
        echo -e "${CLR_YELLOW}Warning:${CLR_RESET} No pre-built release asset found; falling back to master source archive."
        ZIP_URL="https://github.com/Ludeon/RimWorld-Farsi/archive/refs/heads/master.zip"
    fi

    if [[ -n "$ZIP_URL" ]]; then
        TEMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/rimworld_farsi_XXXXXX")"
        ZIP_PATH="${TEMP_DIR}/release.zip"
        ASSET_NAME="$(basename "$ZIP_URL")"
        echo -e "Downloading package: ${CLR_BLUE}${ZIP_URL}${CLR_RESET}"
        if fetch_url "$ZIP_URL" "$ZIP_PATH"; then
            SUM_OK=true
            if [[ -n "$SUM_URL" ]]; then
                SUM_PATH="${TEMP_DIR}/checksum.txt"
                if fetch_url "$SUM_URL" "$SUM_PATH"; then
                    if ! verify_sha256 "$ZIP_PATH" "$SUM_PATH" "$ASSET_NAME"; then
                        SUM_OK=false
                    fi
                else
                    echo -e "${CLR_RED}Error:${CLR_RESET} Failed to download checksum manifest '${SUM_URL}'." >&2
                    SUM_OK=false
                fi
            fi

            if [[ "$SUM_OK" == true ]] && extract_zip "$ZIP_PATH" "${TEMP_DIR}/extracted"; then
                if [[ -d "${TEMP_DIR}/extracted/Core" ]]; then
                    SRC_BASE="${TEMP_DIR}/extracted"
                else
                    REPO_SUBDIR=$(find "${TEMP_DIR}/extracted" -mindepth 1 -maxdepth 1 -type d | head -n 1 || true)
                    if [[ -n "$REPO_SUBDIR" && -d "${REPO_SUBDIR}/Core" ]]; then
                        SRC_BASE="$REPO_SUBDIR"
                        USED_LOCAL_SOURCE=true
                    fi
                fi

                if [[ -n "$SRC_BASE" ]]; then
                    if [[ -f "${SRC_BASE}/.release-edition" ]]; then
                        IS_PACKAGED_BUNDLE=true
                    fi
                    if [[ -d "${SRC_BASE}/mods/RTL_Persian_Support" ]]; then
                        MOD_SRC="${SRC_BASE}/mods/RTL_Persian_Support"
                    fi
                    echo -e "${CLR_GREEN}Package downloaded and ready.${CLR_RESET}\n"
                fi
            fi
        fi
    fi
fi

# Fallback to local translation repository if download was skipped or failed
if [[ -z "$SRC_BASE" ]]; then
    if [[ -d "${SCRIPT_DIR}/Core" ]]; then
        echo -e "${CLR_YELLOW}Using local repository translation files from: ${SCRIPT_DIR}${CLR_RESET}\n"
        SRC_BASE="${SCRIPT_DIR}"
        USED_LOCAL_SOURCE=true
    else
        echo -e "${CLR_RED}Error:${CLR_RESET} Failed to fetch release from GitHub and no local translation files found in: ${SCRIPT_DIR}" >&2
        echo -e "Please download manually from: https://github.com/Ludeon/RimWorld-Farsi/releases" >&2
        exit 1
    fi
fi

if [[ -z "$MOD_SRC" && -d "${SCRIPT_DIR}/mods/RTL_Persian_Support" ]]; then
    MOD_SRC="${SCRIPT_DIR}/mods/RTL_Persian_Support"
fi

INSTALLED_COUNT=0

for MOD in "${MODULES[@]}"; do
    SRC_DIR="${SRC_BASE}/${MOD}"

    # Handle nested module directories from legacy build artifacts
    if [[ -d "${SRC_DIR}/${MOD}" && ( -d "${SRC_DIR}/${MOD}/DefInjected" || -d "${SRC_DIR}/${MOD}/Keyed" || -f "${SRC_DIR}/${MOD}/LanguageInfo.xml" ) ]]; then
        SRC_DIR="${SRC_DIR}/${MOD}"
    fi

    DEST_DIR="${GAME_PATH}/Data/${MOD}/Languages/${LANG_NAME}"
    OLD_DEST_DIR="${GAME_PATH}/Data/${MOD}/Languages/Persian"

    if [[ -d "$SRC_DIR" ]]; then
        if [[ -d "${GAME_PATH}/Data/${MOD}" ]]; then
            echo -e "Installing module: ${CLR_CYAN}${MOD}${CLR_RESET}..."

            rm -rf "$DEST_DIR"
            rm -rf "$OLD_DEST_DIR"
            mkdir -p "$DEST_DIR"

            if compgen -G "${SRC_DIR}/*" >/dev/null; then
                cp -r "${SRC_DIR}/"* "$DEST_DIR/"
            fi

            # Replace Strings/ with original English Strings/ when installing Essential or Mod from a repo checkout
            if [[ "$IS_PACKAGED_BUNDLE" != true && "$USED_LOCAL_SOURCE" == true && ( "$EDITION" == "essential" || "$EDITION" == "mod" ) ]]; then
                rm -rf "${DEST_DIR}/Strings"
                if [[ -d "${SRC_BASE}/src/english/${MOD}/Strings" ]]; then
                    cp -r "${SRC_BASE}/src/english/${MOD}/Strings" "${DEST_DIR}/Strings"
                fi
            fi

            # Purge cached .tar files so RimWorld loads loose XML assets
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

# Install Harmony RTL Mod into Mods/ folder if selected
if [[ "$INSTALL_MOD" == true && -n "$MOD_SRC" && -d "$MOD_SRC" ]]; then
    echo -e "\n${CLR_CYAN}Installing RTL Persian Support mod (Vazirmatn font & Harmony engine)...${CLR_RESET}"
    MOD_DEST="${GAME_PATH}/Mods/RTL_Persian_Support"
    rm -rf "$MOD_DEST"
    mkdir -p "$MOD_DEST"
    if compgen -G "${MOD_SRC}/*" >/dev/null; then
        cp -r "${MOD_SRC}/"* "$MOD_DEST/"
    fi
    # Bundled 0Harmony.dll means Workshop dependency tag is unnecessary in standalone installs
    if [[ -f "${MOD_DEST}/Assemblies/0Harmony.dll" && -f "${MOD_DEST}/About/About.xml" ]] && command -v python3 &>/dev/null; then
        python3 - "${MOD_DEST}/About/About.xml" << 'PYEOF'
import pathlib, re, sys
p = pathlib.Path(sys.argv[1])
txt = p.read_text(encoding="utf-8")
updated = re.sub(r"\s*<modDependencies>.*?</modDependencies>\s*", "\n    ", txt, flags=re.DOTALL)
if updated != txt:
    p.write_text(updated, encoding="utf-8")
PYEOF
    fi
    echo -e "  ${CLR_GREEN}[OK]${CLR_RESET} RTL Persian Support mod installed to: ${CLR_BLUE}${MOD_DEST}${CLR_RESET}"
fi

echo -e "\n${CLR_BOLD}${CLR_MAGENTA}======================================================================${CLR_RESET}"
echo -e "${CLR_BOLD}${CLR_GREEN}   Installation completed successfully! (${INSTALLED_COUNT} modules, option: ${EDITION})${CLR_RESET}"
echo -e "   1. Launch RimWorld."
echo -e "   2. Navigate to: Options -> Language -> Select 'Persian (فارسی)'."
if [[ "$INSTALL_MOD" == true ]]; then
    echo -e "   3. Under 'Mods', enable 'Persian RTL Support' for Vazirmatn font and RTL layout."
fi
echo -e "${CLR_BOLD}${CLR_MAGENTA}======================================================================${CLR_RESET}\n"
