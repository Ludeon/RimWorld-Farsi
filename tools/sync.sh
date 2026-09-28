#!/usr/bin/env bash
# ==============================================================================
# RimWorld Persian Translation Sync Tool
# Synchronizes Persian translation data between the repo and a game installation.
# ==============================================================================

set -euo pipefail

# ANSI color codes
CLR_RESET="\033[0m"
CLR_BOLD="\033[1m"
CLR_GREEN="\033[32m"
CLR_YELLOW="\033[33m"
CLR_BLUE="\033[34m"
CLR_RED="\033[31m"
CLR_CYAN="\033[36m"

# Script and Project directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPO_DATA_DIR="${REPO_ROOT}/Data"

# Defaults
GAME_PATH=""
DIRECTION="push" # "push" (repo -> game) or "pull" (game -> repo)
DRY_RUN=false
DELETE_EXTRANEOUS=false
VERBOSE=true

print_usage() {
    echo -e "${CLR_BOLD}Usage:${CLR_RESET}"
    echo -e "  $(basename "$0") --gamepath <PATH> [OPTIONS]\n"
    echo -e "${CLR_BOLD}Description:${CLR_RESET}"
    echo -e "  Synchronizes Persian translation data (Languages/Persian) between this repository"
    echo -e "  and a local RimWorld game installation using rsync.\n"
    echo -e "${CLR_BOLD}Options:${CLR_RESET}"
    echo -e "  -g, --gamepath <PATH>     Path to the RimWorld game directory (Required)"
    echo -e "  -d, --direction <DIR>     Sync direction: 'push' (repo -> game, default) or 'pull' (game -> repo)"
    echo -e "  -n, --dry-run             Perform a trial run with no files transferred or changed"
    echo -e "      --delete              Delete files in destination that no longer exist in source"
    echo -e "  -q, --quiet               Quiet mode (suppress individual file transfer logs)"
    echo -e "  -h, --help                Display this help message\n"
    echo -e "${CLR_BOLD}Examples:${CLR_RESET}"
    echo -e "  # Sync translations from repo into game:"
    echo -e "  $(basename "$0") --gamepath \"/home/dany/Documents/games/RimWorld\"\n"
    echo -e "  # Preview changes without modifying files (Dry-run):"
    echo -e "  $(basename "$0") --gamepath \"/home/dany/Documents/games/RimWorld\" --dry-run\n"
    echo -e "  # Pull modified translation files from game back into repo:"
    echo -e "  $(basename "$0") --gamepath \"/home/dany/Documents/games/RimWorld\" --direction pull\n"
}

# --- Parse Arguments ---
while [[ $# -gt 0 ]]; do
    case "$1" in
        -g|--gamepath)
            if [[ -n "${2:-}" && ! "$2" =~ ^- ]]; then
                GAME_PATH="$2"
                shift 2
            else
                echo -e "${CLR_RED}Error:${CLR_RESET} --gamepath requires a non-empty directory path." >&2
                exit 1
            fi
            ;;
        --gamepath=*)
            GAME_PATH="${1#*=}"
            shift
            ;;
        -d|--direction)
            if [[ -n "${2:-}" && ! "$2" =~ ^- ]]; then
                DIRECTION="$2"
                shift 2
            else
                echo -e "${CLR_RED}Error:${CLR_RESET} --direction requires an argument ('push' or 'pull')." >&2
                exit 1
            fi
            ;;
        --direction=*)
            DIRECTION="${1#*=}"
            shift
            ;;
        -n|--dry-run)
            DRY_RUN=true
            shift
            ;;
        --delete)
            DELETE_EXTRANEOUS=true
            shift
            ;;
        -q|--quiet)
            VERBOSE=false
            shift
            ;;
        -h|--help)
            print_usage
            exit 0
            ;;
        *)
            echo -e "${CLR_RED}Error:${CLR_RESET} Unknown option: $1" >&2
            echo "Run '$(basename "$0") --help' for usage instructions." >&2
            exit 1
            ;;
    esac
done

# --- Validate Environment & Dependencies ---
if ! command -v rsync &> /dev/null; then
    echo -e "${CLR_RED}Error:${CLR_RESET} 'rsync' command was not found on this system." >&2
    echo "Please install rsync (e.g. 'sudo apt-get install rsync') and try again." >&2
    exit 1
fi

if [[ -z "$GAME_PATH" ]]; then
    echo -e "${CLR_RED}Error:${CLR_RESET} Missing required option: --gamepath <PATH>" >&2
    echo "Run '$(basename "$0") --help' for usage instructions." >&2
    exit 1
fi

# Expand tilde if present
GAME_PATH="${GAME_PATH/#\~/$HOME}"
# Convert to absolute path if directory exists
if [[ -d "$GAME_PATH" ]]; then
    GAME_PATH="$(cd "$GAME_PATH" && pwd)"
fi

if [[ ! -d "$GAME_PATH" ]]; then
    echo -e "${CLR_RED}Error:${CLR_RESET} Game directory does not exist: $GAME_PATH" >&2
    exit 1
fi

GAME_DATA_DIR="${GAME_PATH}/Data"
if [[ ! -d "$GAME_DATA_DIR" ]]; then
    echo -e "${CLR_RED}Error:${CLR_RESET} 'Data' folder not found inside game directory: $GAME_PATH" >&2
    echo "Please ensure you pointed to the root RimWorld folder containing 'Data/'." >&2
    exit 1
fi

KNOWN_MODULES=("Core" "Royalty" "Ideology" "Biotech" "Anomaly" "Odyssey")
HAS_REPO_MODULES=false
for MOD in "${KNOWN_MODULES[@]}"; do
    if [[ -d "${REPO_ROOT}/${MOD}" || -d "${REPO_ROOT}/Data/${MOD}" ]]; then
        HAS_REPO_MODULES=true
        break
    fi
done

if [[ "$HAS_REPO_MODULES" == false ]]; then
    echo -e "${CLR_RED}Error:${CLR_RESET} No Persian translation modules found in repository: $REPO_ROOT" >&2
    exit 1
fi

if [[ "$DIRECTION" != "push" && "$DIRECTION" != "pull" ]]; then
    echo -e "${CLR_RED}Error:${CLR_RESET} Invalid direction '$DIRECTION'. Must be 'push' or 'pull'." >&2
    exit 1
fi

# --- Configure rsync options ---
RSYNC_OPTS=(-a --update)

if [[ "$VERBOSE" == true ]]; then
    RSYNC_OPTS+=(-v --stats)
fi

if [[ "$DRY_RUN" == true ]]; then
    RSYNC_OPTS+=(-n)
fi

if [[ "$DELETE_EXTRANEOUS" == true ]]; then
    RSYNC_OPTS+=(--delete)
fi

# --- Execution Banner ---
echo -e "${CLR_BOLD}======================================================================${CLR_RESET}"
echo -e "${CLR_BOLD}${CLR_CYAN}RIMWORLD PERSIAN TRANSLATION SYNC TOOL${CLR_RESET}"
echo -e "${CLR_BOLD}======================================================================${CLR_RESET}"
echo -e "Repository Root: ${CLR_BLUE}${REPO_ROOT}${CLR_RESET}"
echo -e "Game Data:       ${CLR_BLUE}${GAME_DATA_DIR}${CLR_RESET}"
echo -e "Direction:       ${CLR_BOLD}${DIRECTION}${CLR_RESET} ($( [[ "$DIRECTION" == "push" ]] && echo "Repo -> Game" || echo "Game -> Repo" ))"
if [[ "$DRY_RUN" == true ]]; then
    echo -e "Mode:            ${CLR_YELLOW}${CLR_BOLD}[DRY-RUN] No files will be modified${CLR_RESET}"
else
    echo -e "Mode:            ${CLR_GREEN}[LIVE RUN] Changes will be synced to disk${CLR_RESET}"
fi
if [[ "$DELETE_EXTRANEOUS" == true ]]; then
    echo -e "Delete Extras:   ${CLR_YELLOW}ENABLED (--delete)${CLR_RESET}"
fi
echo -e "======================================================================\n"

# --- Process Modules ---
SYNCED_COUNT=0
SKIPPED_COUNT=0

for MODULE_NAME in "${KNOWN_MODULES[@]}"; do
    if [[ -d "${REPO_ROOT}/${MODULE_NAME}" ]]; then
        REPO_PERSIAN_DIR="${REPO_ROOT}/${MODULE_NAME}"
    elif [[ -d "${REPO_ROOT}/Data/${MODULE_NAME}/Languages/Persian" ]]; then
        REPO_PERSIAN_DIR="${REPO_ROOT}/Data/${MODULE_NAME}/Languages/Persian"
    else
        continue
    fi

    GAME_MODULE_DIR="${GAME_DATA_DIR}/${MODULE_NAME}"
    GAME_PERSIAN_DIR="${GAME_MODULE_DIR}/Languages/Persian"

    echo -e "${CLR_BOLD}Module: ${CLR_CYAN}${MODULE_NAME}${CLR_RESET}"

    if [[ "$DIRECTION" == "push" ]]; then
        # Check if the game has this expansion / module installed
        if [[ ! -d "$GAME_MODULE_DIR" ]]; then
            echo -e "  ${CLR_YELLOW}[SKIPPED]${CLR_RESET} DLC/module '${MODULE_NAME}' is not installed in the game."
            SKIPPED_COUNT=$((SKIPPED_COUNT + 1))
            echo ""
            continue
        fi

        # Ensure destination directory exists (unless dry-run)
        if [[ "$DRY_RUN" == false && ! -d "$GAME_PERSIAN_DIR" ]]; then
            mkdir -p "$GAME_PERSIAN_DIR"
        fi

        echo -e "  Syncing: ${CLR_BLUE}${REPO_PERSIAN_DIR}/${CLR_RESET} -> ${CLR_BLUE}${GAME_PERSIAN_DIR}/${CLR_RESET}"
        rsync "${RSYNC_OPTS[@]}" "${REPO_PERSIAN_DIR}/" "${GAME_PERSIAN_DIR}/"
        SYNCED_COUNT=$((SYNCED_COUNT + 1))

    elif [[ "$DIRECTION" == "pull" ]]; then
        if [[ ! -d "$GAME_PERSIAN_DIR" ]]; then
            echo -e "  ${CLR_YELLOW}[SKIPPED]${CLR_RESET} No Persian language folder found in game for '${MODULE_NAME}'."
            SKIPPED_COUNT=$((SKIPPED_COUNT + 1))
            echo ""
            continue
        fi

        echo -e "  Syncing: ${CLR_BLUE}${GAME_PERSIAN_DIR}/${CLR_RESET} -> ${CLR_BLUE}${REPO_PERSIAN_DIR}/${CLR_RESET}"
        rsync "${RSYNC_OPTS[@]}" "${GAME_PERSIAN_DIR}/" "${REPO_PERSIAN_DIR}/"
        SYNCED_COUNT=$((SYNCED_COUNT + 1))
    fi

    echo ""
done

# --- Summary ---
echo -e "======================================================================"
echo -e "${CLR_BOLD}SYNC SUMMARY${CLR_RESET}"
echo -e "======================================================================"
echo -e "Modules Synced:  ${CLR_GREEN}${SYNCED_COUNT}${CLR_RESET}"
echo -e "Modules Skipped: ${CLR_YELLOW}${SKIPPED_COUNT}${CLR_RESET}"

if [[ "$DRY_RUN" == true ]]; then
    echo -e "\n${CLR_YELLOW}${CLR_BOLD}[DRY RUN COMPLETE]${CLR_RESET} Run without '--dry-run' to apply changes."
else
    echo -e "\n${CLR_GREEN}${CLR_BOLD}[SUCCESS]${CLR_RESET} Synchronization completed successfully!"
fi
echo -e "======================================================================"
