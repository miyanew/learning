@echo off
setlocal

rem Set the path to the PowerShell script
set SCRIPT_DIR=%~dp0../src
set POWERSHELL_SCRIPT=%SCRIPT_DIR%\%1.ps1
set SHORTCUT_FILE=%SCRIPT_DIR%\%1.lnk

rem Check if the PowerShell script exists
if exist "%POWERSHELL_SCRIPT%" (
    set SCRIPT_TO_RUN=%POWERSHELL_SCRIPT%
) else if exist "%SHORTCUT_FILE%" (
    for /f "delims=" %%I in ('powershell -command "(New-Object -ComObject WScript.Shell).CreateShortcut('%SHORTCUT_FILE%').TargetPath"') do set SCRIPT_TO_RUN=%%I
) else (
    echo Error: Neither PowerShell script nor shortcut found for %1
    exit /b 1
)

rem Execute the PowerShell script
PowerShell.exe -ExecutionPolicy Bypass -File "%SCRIPT_TO_RUN%" %2 %3

rem Check the exit code
IF %ERRORLEVEL% NEQ 0 (
    echo Error: PowerShell script execution failed with exit code %ERRORLEVEL%
    exit /b %ERRORLEVEL%
)

timeout /t 5

endlocal
