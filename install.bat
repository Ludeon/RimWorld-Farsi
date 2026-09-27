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

for %%M in (!MODULES!) do (
    if exist "%~dp0%%M" (
        if exist "!FLDR!\Data\%%M" (
            echo Installing %%M...
            rd /q /s "!FLDR!\Data\%%M\Languages\!LANG_NAME!" 2>nul
            xcopy /s /e /i /y "%~dp0%%M" "!FLDR!\Data\%%M\Languages\!LANG_NAME!" >nul
            del /q "!FLDR!\Data\%%M\Languages\!LANG_NAME!.tar" 2>nul
            del /q "!FLDR!\Data\%%M\Languages\Persian.tar" 2>nul
        ) else (
            echo [SKIPPED] %%M DLC not detected in game.
        )
    )
)

echo.
echo ======================================================================
echo  Installation completed successfully!
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
