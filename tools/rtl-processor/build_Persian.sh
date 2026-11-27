#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ $# -eq 0 || $# -gt 2 ]]; then
  printf "Usage: build_Persian.sh <translation_directory_path> [<destination_path>]\n"
  exit 1
fi

trans_dir="$1"
dest_dir="${2:-./Persian}"

if [[ ! -d "$trans_dir" ]]; then
  printf "Invalid translation directory path.\n" >&2
  exit 1
fi

if [[ $# -eq 1 ]]; then
  printf "No destination path provided; creating corrected translation directory in %s.\n" "$dest_dir"
fi

if [[ -d "$dest_dir" ]]; then
  printf "Destination directory %s already exists. Overwrite it?(Y/N) " "$dest_dir"
  read -r answer
  if [[ ! "$answer" =~ ^([Yy]|[Yy][Ee][Ss])$ ]]; then
    exit 1
  fi
fi

printf "Copying over Persian translation..."
rm -rf "$dest_dir"
cp -r "$trans_dir" "$dest_dir"
printf "done!\n"

printf "\nRunning PersianFixer.py...\n"
python3 "${SCRIPT_DIR}/PersianFixer.py" "$dest_dir"
printf "done!\n"
