@echo off
chcp 65001 > nul
color 0a
title RimWorld Persian Translation Installer

powershell -Command "& {Write-Host '==============================================' -BackgroundColor Green -ForegroundColor Green; Write-Host '==============================================' -BackgroundColor White -ForegroundColor White; Write-Host '==============================================' -BackgroundColor Red -ForegroundColor Red;}"

echo === RimWorld Persian Translation Installer ===
echo.

:: Check if in correct RimWorld folder (Data folder must exist)
IF NOT EXIST "%~dp0Data" (
    echo [Error] Data folder not found. Please run this BAT in the RimWorld root folder.
    pause
    exit /b
)

:: Set paths
set DOWNLOAD_URL=https://github.com/Ludeon/RimWorld-Farsi/releases/latest/download/persian.language.zip
set ZIP_PATH=%TEMP%\persian.language.zip
set EXTRACT_PATH=%~dp0Temp
set LANG_PATH=%~dp0Data

:: Notify user
powershell -command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('Downloading the latest Persian translation...')"

:: Download translation ZIP from GitHub
powershell.exe -Command "Invoke-WebRequest -OutFile '%ZIP_PATH%' '%DOWNLOAD_URL%'" >nul

:: Extract ZIP to temporary folder
powershell.exe -Command "Add-Type -A 'System.IO.Compression.FileSystem'; [IO.Compression.ZipFile]::ExtractToDirectory('%ZIP_PATH%', '%EXTRACT_PATH%')" >nul

:: Copy contents to appropriate DLC folders
(for /d %%D in ("%EXTRACT_PATH%\Persian\*") do (
    if exist "%LANG_PATH%\%%~nxD" (
        xcopy /E /I /Y "%%D" "%LANG_PATH%\%%~nxD" >nul
        echo %%~nxD copied.
    ) else (
        echo %%~nxD skipped [DLC not found].
    )
)) > "%TEMP%\copy_log.txt"

:: Clean up
rmdir /S /Q "%EXTRACT_PATH%"
del "%ZIP_PATH%" >nul

:: Show summary
cls
type "%TEMP%\copy_log.txt"
del "%TEMP%\copy_log.txt"

:: Show credits
echo.
echo [✓] Persian translation installed!
echo If you like this project:
echo GitHub: https://github.com/Ludeon/RimWorld-Farsi
echo Donate: ETH 0x526968dF2AB74d7B4132F8D68Cf1BE6D126c6f82
echo        https://reymit.ir/danialpahlavan
pause
