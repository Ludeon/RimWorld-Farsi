@if (@a==@b) @end /*
@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
title RimWorld Persian Translation Installer

echo ======================================================================
echo           RimWorld Persian (فارسی) Translation Installer
echo ======================================================================
echo.

set "DEFAULT_PATH=%ProgramFiles(x86)%\Steam\steamapps\common\RimWorld"
set "FLDR="

if exist "!DEFAULT_PATH!\Data\Core" (
    echo Auto-detected RimWorld at: !DEFAULT_PATH!
    set /p "USE_DEFAULT=Use this location? [Y/n]: "
    if /i "!USE_DEFAULT!"=="" set "FLDR=!DEFAULT_PATH!"
    if /i "!USE_DEFAULT!"=="y" set "FLDR=!DEFAULT_PATH!"
    if /i "!USE_DEFAULT!"=="yes" set "FLDR=!DEFAULT_PATH!"
)

if "!FLDR!"=="" (
    echo Please select your RimWorld folder in the dialog window...
    for /f "delims=" %%I in ('cscript /nologo /e:jscript "%~f0"') do (
        set "FLDR=%%I"
    )
)

if "!FLDR!"=="" (
    echo [ERROR] No directory selected. Installation aborted.
    pause
    exit /b 1
)

if not exist "!FLDR!\Data\Core" (
    echo [ERROR] Invalid RimWorld directory. 'Data\Core' was not found in:
    echo "!FLDR!"
    pause
    exit /b 1
)

echo.
echo Installing Persian translation to: !FLDR!
echo.

set "LANG_NAME=Persian (فارسی)"
set "MODULES=Core Royalty Ideology Biotech Anomaly Odyssey"
set "SRC_BASE=%~dp0"

echo [INFO] Checking for latest Persian translation release on GitHub...
set "TEMP_ZIP=%TEMP%\rw_farsi_%RANDOM%.zip"
set "TEMP_DIR=%TEMP%\rw_farsi_%RANDOM%"

powershell -NoProfile -Command ^
  "try {" ^
  "  [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12;" ^
  "  $rel = Invoke-RestMethod -Uri 'https://api.github.com/repos/Ludeon/RimWorld-Farsi/releases/latest' -Headers @{'User-Agent'='RimWorld-Farsi-Installer'};" ^
  "  $asset = $rel.assets | Where-Object { $_.name -like 'persian-language-*.zip' } | Select-Object -First 1;" ^
  "  if (-not $asset) { throw 'Asset not found' };" ^
  "  Invoke-WebRequest -Uri $asset.browser_download_url -OutFile '!TEMP_ZIP!' -UseBasicParsing;" ^
  "  Expand-Archive -Path '!TEMP_ZIP!' -DestinationPath '!TEMP_DIR!' -Force;" ^
  "  Remove-Item '!TEMP_ZIP!' -Force;" ^
  "  exit 0;" ^
  "} catch {" ^
  "  exit 1;" ^
  "}"

if exist "!TEMP_DIR!\Core" (
    set "SRC_BASE=!TEMP_DIR!"
    echo [INFO] Downloaded latest processed release translation package.
) else (
    if not exist "!SRC_BASE!\Core" (
        echo [ERROR] Failed to download latest release from GitHub and no local translation files found in !SRC_BASE!
        echo Please download the latest package manually from: https://github.com/Ludeon/RimWorld-Farsi/releases
        pause
        exit /b 1
    ) else (
        echo [INFO] Using local repository translation files.
    )
)

set /a INSTALLED_COUNT=0

for %%M in (!MODULES!) do (
    set "MOD_SRC="
    if exist "!SRC_BASE!\%%M\%%M\DefInjected" (
        set "MOD_SRC=!SRC_BASE!\%%M\%%M"
    ) else if exist "!SRC_BASE!\%%M\DefInjected" (
        set "MOD_SRC=!SRC_BASE!\%%M"
    ) else if exist "!SRC_BASE!\%%M\Languages" (
        set "MOD_SRC=!SRC_BASE!\%%M"
    )

    if defined MOD_SRC (
        if exist "!FLDR!\Data\%%M" (
            echo Installing %%M...
            rd /q /s "!FLDR!\Data\%%M\Languages\!LANG_NAME!" 2>nul
            rd /q /s "!FLDR!\Data\%%M\Languages\Persian" 2>nul
            xcopy /s /e /i /y "!MOD_SRC!" "!FLDR!\Data\%%M\Languages\!LANG_NAME!" >nul
            del /q "!FLDR!\Data\%%M\Languages\!LANG_NAME!.tar" 2>nul
            del /q "!FLDR!\Data\%%M\Languages\Persian.tar" 2>nul
            del /q "!FLDR!\Data\%%M\Languages\Persian (فارسی).tar" 2>nul
            set /a INSTALLED_COUNT+=1
        ) else (
            echo [SKIPPED] %%M DLC not detected in game.
        )
    )
)

if !INSTALLED_COUNT! EQU 0 (
    echo.
    echo [ERROR] No translation modules could be installed.
    echo Please verify your RimWorld folder contains 'Data\Core'.
    pause
    exit /b 1
)

echo.
echo ======================================================================
echo  Installation completed successfully! (!INSTALLED_COUNT! modules installed)
echo  Launch RimWorld, go to Options -^> Language, and select Persian (فارسی).
echo ======================================================================
echo.
pause
exit /b 0

*/
var sh = new ActiveXObject('Shell.Application');
var folder = sh.BrowseForFolder(0, 'Select your RimWorld installation folder (contains RimWorldWin64.exe and Data folder):', 0, 0);
if (folder != null) {
    WScript.Echo(folder.Self.Path);
}
