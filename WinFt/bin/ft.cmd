@echo off
setlocal

rem Set the path to the PowerShell script
set POWERSHELL_SCRIPT=%~dp0../src/%1.ps1

rem Check if the PowerShell script exists
if not exist "%POWERSHELL_SCRIPT%" (
    echo Error: PowerShell script not found at %POWERSHELL_SCRIPT%
    exit /b 1
)

rem Execute the PowerShell script
PowerShell.exe -ExecutionPolicy Bypass -File "%POWERSHELL_SCRIPT%" %2 %3

rem Check the exit code
IF %ERRORLEVEL% NEQ 0 (
    echo Error: PowerShell script execution failed with exit code %ERRORLEVEL%
    exit /b %ERRORLEVEL%
)

endlocal
