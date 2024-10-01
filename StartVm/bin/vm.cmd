@echo off
setlocal

rem Set the path to the PowerShell script
set BATCH_NAME=%~n0
set POWERSHELL_SCRIPT=%~dp0../src/%1.ps1

rem Check if a script name was provided
if "%~1"=="" (
    echo Error: Please provide a script name.
    exit /b 1
)

rem Check if the PowerShell script exists
if not exist "%POWERSHELL_SCRIPT%" (
    echo Error: PowerShell script not found at %POWERSHELL_SCRIPT%
    exit /b 1
)

rem Execute the PowerShell script
PowerShell.exe -ExecutionPolicy Bypass -File "%POWERSHELL_SCRIPT%"

rem Check the exit code
if %ERRORLEVEL% NEQ 0 (
    echo Error: PowerShell script execution failed with exit code %ERRORLEVEL%
    exit /b %ERRORLEVEL%
)

endlocal
