@echo off
:: Execute with administrator privileges
powershell -Command "if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] 'Administrator')) {Start-Process powershell -ArgumentList '-ExecutionPolicy Bypass -File \"%~dp0dont_run_this_code.ps1\"' -Verb RunAs; exit}"
:: Execute the script
powershell -ExecutionPolicy Bypass -File "%~dp0dont_run_this_code.ps1"
:: Exit upon user action
echo "The script has completed. Press Enter to exit."
pause
