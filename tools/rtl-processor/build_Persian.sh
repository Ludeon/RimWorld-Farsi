#!/bin/sh
if [ $# -eq 0 ] || [ $# -gt 2 ]; then
  printf "Usage: build_Persian.sh <translation_directory_path> [<destination_path>]\n"
  exit 1
fi

trans_dir=$1
dest_dir=$2

if ! [ -d "$trans_dir" ]; then
  printf "Invalid translation directory path.\n"
  exit 1
fi
if [ $# -eq 1 ]; then
  printf "No destination path provided; creating corrected translation directory in current directory.\n"
  dest_dir="./Persian"
fi

if [ -d "$dest_dir" ]; then
  printf "Destination directory $dest_dir already exists. Overwrite it?(Y/N) "
  read in
  if [ "$in" != "Y" ] && [ "$in" != "y" ] && [ "$in" != "YES" ] && [ "$in" != "yes" ]; then
    exit 1
  fi
fi

printf "Copying over Persian translation..."
if [ -d "$dest_dir" ]; then rm -rf "$dest_dir"; fi
cp -r "$trans_dir" "$dest_dir"
printf "done!\n"

printf "\nRunning PersianFixer.py...\n"
python3 PersianFixer.py "$dest_dir" || { printf "\n"; exit 1; }
printf "done!\n"

printf "Correction complete. Press any key to continue..."
read -n1
