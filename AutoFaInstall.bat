@echo off
chcp 65001 > nul

IF "%TEMP%"=="" (
    set TEMP=Temp
)

REM بررسی وجود پوشه Data
IF NOT EXIST "%~dp0Data" (
    echo پوشه Data وجود ندارد. لطفاً اسکریپت را در مسیر صحیح اجرا کنید.
    pause
    exit /b
)

REM دریافت آخرین نسخه از صفحه انتشار GitHub
set DOWNLOAD_URL=https://github.com/Ludeon/RimWorld-Farsi/releases/latest/download/persian.language.zip
set ZIP_PATH=%TEMP%\persian.language.zip
set EXTRACT_PATH=%~dp0Temp
set LANG_PATH=%~dp0Data

powershell -command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('در حال دانلود آخرین بومی سازی...')"

powershell.exe -Command "Invoke-WebRequest -OutFile %ZIP_PATH% %DOWNLOAD_URL%" >> nul
powershell.exe "Add-Type -A 'System.IO.Compression.FileSystem';[IO.Compression.ZipFile]::ExtractToDirectory('%ZIP_PATH%', '%EXTRACT_PATH%');" > nul

REM کپی کردن محتوای استخراج شده به پوشه data
(for /d %%D in ("%EXTRACT_PATH%\Persian\*") do (
    if exist "%LANG_PATH%\%%~nxD" (
        xcopy /E /I /Y "%%D" "%LANG_PATH%\%%~nxD" > nul
        echo %%~nxD copied.
    ) else (
        echo %%~nxD skipped[dlc not found].
    )
)) > "%TEMP%\copy_log.txt"

REM حذف پوشه Temp
rmdir /S /Q "%EXTRACT_PATH%"

REM نمایش نتیجه کپی

cls

for /f "tokens=*" %%i in (%TEMP%\copy_log.txt) do (
    echo %%i
)


echo if you like this project , star project , donate me .
echo project link : https://github.com/Ludeon/RimWorld-Farsi
echo donation : Ethereum (ETH) 0x526968dF2AB74d7B4132F8D68Cf1BE6D126c6f82
echo  reymit : https://reymit.ir/danialpahlavan
del "%TEMP%\copy_log.txt"

pause
