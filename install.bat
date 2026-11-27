@if (@a==@b) @end /*
@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
title RimWorld Persian (فارسی) Translation & RTL Engine Installer

echo ======================================================================
echo           RimWorld Persian (فارسی) Translation Installer
echo               With Vazirmatn Font & RTL Support Engine
echo ======================================================================
echo.

set "EDITION="
for %%A in (%*) do (
    if /i "%%~A"=="/essential" set "EDITION=essential"
    if /i "%%~A"=="--essential" set "EDITION=essential"
    if /i "%%~A"=="/full" set "EDITION=full"
    if /i "%%~A"=="--full" set "EDITION=full"
)

if "!EDITION!"=="" (
    echo Select translation edition:
    echo   [1] Essential ^(Recommended - Persian UI ^& gameplay, original English Strings/^)
    echo   [2] Full      ^(Complete Persian translation including Strings/^)
    set /p "ED_CHOICE=Enter choice [1/2] (default 1): "
    if "!ED_CHOICE!"=="" set "ED_CHOICE=1"
    if "!ED_CHOICE!"=="1" (
        set "EDITION=essential"
    ) else if /i "!ED_CHOICE!"=="essential" (
        set "EDITION=essential"
    ) else if "!ED_CHOICE!"=="2" (
        set "EDITION=full"
    ) else if /i "!ED_CHOICE!"=="full" (
        set "EDITION=full"
    ) else (
        echo [ERROR] Invalid choice '!ED_CHOICE!'. Please enter 1 or 2.
        pause
        exit /b 1
    )
    echo.
)

echo Selected edition: !EDITION!
echo.

set "FLDR="

:: Check common RimWorld installation paths
for %%P in (
    "%ProgramFiles(x86)%\Steam\steamapps\common\RimWorld"
    "%ProgramFiles%\Steam\steamapps\common\RimWorld"
    "D:\SteamLibrary\steamapps\common\RimWorld"
    "E:\SteamLibrary\steamapps\common\RimWorld"
    "F:\SteamLibrary\steamapps\common\RimWorld"
    "C:\GOG Games\RimWorld"
    "D:\GOG Games\RimWorld"
    "C:\Games\RimWorld"
    "D:\Games\RimWorld"
) do (
    if "!FLDR!"=="" (
        if exist "%%~P\Data\Core" (
            set "FLDR=%%~P"
        )
    )
)

if not "!FLDR!"=="" (
    echo Auto-detected RimWorld at: !FLDR!
    set /p "USE_DEFAULT=Use this location? [Y/n]: "
    if /i "!USE_DEFAULT!"=="n" set "FLDR="
    if /i "!USE_DEFAULT!"=="no" set "FLDR="
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
set "USED_REMOTE=0"

echo [INFO] Checking for latest Persian translation release (!EDITION!) on GitHub...
set "TEMP_ZIP=%TEMP%\rw_farsi_%RANDOM%.zip"
set "TEMP_DIR=%TEMP%\rw_farsi_%RANDOM%"

powershell -NoProfile -Command ^
  "try {" ^
  "  [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12;" ^
  "  $rel = Invoke-RestMethod -Uri 'https://api.github.com/repos/Ludeon/RimWorld-Farsi/releases/latest' -Headers @{'User-Agent'='RimWorld-Farsi-Installer'};" ^
  "  if ('!EDITION!' -eq 'essential') {" ^
  "    $asset = $rel.assets | Where-Object { $_.name -like 'persian-language-essential-*.zip' } | Select-Object -First 1;" ^
  "  } else {" ^
  "    $asset = $rel.assets | Where-Object { $_.name -like 'persian-language-full-*.zip' } | Select-Object -First 1;" ^
  "    if (-not $asset) { $asset = $rel.assets | Where-Object { $_.name -like 'persian-language-*.zip' -and $_.name -notlike '*essential*' } | Select-Object -First 1 };" ^
  "  }" ^
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
    set "USED_REMOTE=1"
    echo [INFO] Downloaded latest processed release translation package (!EDITION!).
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
            if /i "!EDITION!"=="essential" if "!USED_REMOTE!"=="0" (
                rd /q /s "!FLDR!\Data\%%M\Languages\!LANG_NAME!\Strings" 2>nul
                if exist "%~dp0src\english\%%M\Strings" (
                    xcopy /s /e /i /y "%~dp0src\english\%%M\Strings" "!FLDR!\Data\%%M\Languages\!LANG_NAME!\Strings\" >nul
                )
            )
            del /q "!FLDR!\Data\%%M\Languages\!LANG_NAME!.tar" 2>nul
            del /q "!FLDR!\Data\%%M\Languages\Persian.tar" 2>nul
            del /q "!FLDR!\Data\%%M\Languages\Persian (فارسی).tar" 2>nul
            del /q "!FLDR!\Data\%%M\Languages\Farsi.tar" 2>nul
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

:: Install Harmony RTL mod if available in local files
if exist "%~dp0mods\RTL_Persian_Support" (
    echo.
    echo [INFO] Installing RTL Persian Support mod (Vazirmatn font ^& RTL engine)...
    rd /q /s "!FLDR!\Mods\RTL_Persian_Support" 2>nul
    xcopy /s /e /i /y "%~dp0mods\RTL_Persian_Support" "!FLDR!\Mods\RTL_Persian_Support" >nul
    echo   [OK] RTL Persian Support mod installed to !FLDR!\Mods\RTL_Persian_Support
)

echo.
echo ======================================================================
echo  Installation completed successfully! (!INSTALLED_COUNT! modules, edition: !EDITION!)
echo  1. Launch RimWorld.
echo  2. Go to Options -^> Language, and select Persian (فارسی).
echo  3. (Recommended) Under 'Mods', enable 'Persian RTL Support' for Vazirmatn font!
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
