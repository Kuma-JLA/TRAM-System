# Check for administrator privileges
if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "Please run as Administrator."
    exit
}

# 1-1: Create "TRAMs" at the root of C and navigate to it
$tramsPath = "C:\TRAMs"
if (-not (Test-Path $tramsPath)) {
    New-Item -Path $tramsPath -ItemType Directory
}
Set-Location -Path $tramsPath

# 2-1: Download and install the RICOH THETA 360 driver
$thetaDriverUrl = "https://support.theta360.com/intl/download/liveapp4k/win3"
$thetaDriverInstallerPath = "$env:TEMP\RICOH_THETA_UVC_Driver_setup.exe"

Write-Host "Downloading RICOH THETA 360 4K driver installer..."
Invoke-WebRequest -Uri $thetaDriverUrl -OutFile $thetaDriverInstallerPath

Write-Host "Installing RICOH THETA 360 4K driver..."
Start-Process -FilePath $thetaDriverInstallerPath -ArgumentList "/quiet" -Wait
Write-Host "RICOH THETA 360 4K driver installation complete."

# 3-1: Python setup
$pythonInstallerUrl = "https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe"
$pythonInstallerPath = "$env:TEMP\python-installer.exe"

Write-Host "Downloading Python installer..."
Invoke-WebRequest -Uri $pythonInstallerUrl -OutFile $pythonInstallerPath

Write-Host "Installing Python..."
Start-Process -FilePath $pythonInstallerPath -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait
Write-Host "Python installation complete."

# 3-2: Install required Python modules
$modules = @("requests", "numpy", "pandas", "mss", "pillow", "pyvisa", "flask", "flask-cors", "pyautogui", "opencv-contrib-python", "pygrabber")  # Add required modules here
foreach ($module in $modules) {
    Write-Host "Installing Python module: $module..."
    Start-Process -FilePath "python" -ArgumentList "-m pip install $module --upgrade" -Wait
    Write-Host "Module $module installed."
}

# 4-1: Setup virtualDisplay
$zipUrl = "https://github.com/MolotovCherry/virtual-display-rs/releases/download/v0.3.1/virtual-desktop-driver-installer-x64.zip"
$zipPath = "$tramsPath\virtual-desktop-driver-installer-x64.zip"
$extractPath = "$tramsPath\virtual-desktop-driver"

Write-Host "Downloading and extracting virtual-display-driver..."
Invoke-WebRequest -Uri $zipUrl -OutFile $zipPath
Expand-Archive -Path $zipPath -DestinationPath $extractPath
Write-Host "Extraction complete."

# 4-2: Install DriverCertificate.cer
$certPath = "$extractPath\DriverCertificate.cer"
Write-Host "Installing driver certificate..."
Start-Process -FilePath "certutil" -ArgumentList "-addstore -f root `"$certPath`"" -Wait
Start-Process -FilePath "certutil" -ArgumentList "-addstore -f TrustedPublisher `"$certPath`"" -Wait
Write-Host "Driver certificate installed."

# 4-3: Run the installer
$msiPath = "$extractPath\virtual-display-driver-0.3.1-x86_64.msi"
Write-Host "Running virtual display driver installer..."
Start-Process -FilePath "msiexec.exe" -ArgumentList "/i `"$msiPath`"" -Wait
Write-Host "Installation complete."

# 4-4: Create config.json
$configDir = "$env:APPDATA\Virtual Display Driver\config"
if (-not (Test-Path $configDir)) {
    New-Item -Path $configDir -ItemType Directory -Force
}
$configPath = "$configDir\config.json"
$configContent = @'
{
    "enabled": false,
    "monitors": [
        {
            "name": "Click the ↗switch to turn it ON‼  And close this window...",
            "enabled": true,
            "monitor": {
                "id": 1,
                "modes": {
                    "2560x1440": {
                        "width": 2560,
                        "height": 1440,
                        "refresh_rates": [
                            {
                                "rate": 30
                            }
                        ]
                    }
                }
            }
        }
    ]
}
'@
$configContent | Set-Content -Path $configPath
Write-Host "config.json created."

# 4-5: Run VirtualDisplayDriverControl.exe and wait
$exePath = "C:\Program Files\VirtualDisplayDriver\bin\VirtualDisplayDriverControl.exe"
if (Test-Path $exePath) {
    Write-Host "Running VirtualDisplayDriverControl.exe... Close the window after the operation."
    Start-Process -FilePath $exePath -Wait
    Write-Host "VirtualDisplayDriverControl.exe has been closed by the user."
} else {
    Write-Host "VirtualDisplayDriverControl.exe not found at the specified path."
}
C:\Windows\System32/DisplaySwitch.exe /extend

#4-6
# ディスプレイのスケーリングを100%に設定 (LogPixelsを96に設定)
cd 'HKCU:\Control Panel\Desktop'
Set-ItemProperty -Path . -Name Win8DpiScaling -Value 1
Set-ItemProperty -Path . -Name LogPixels -Value 96
Write-Host "Display 2 scaling set to 100%."

# 5-1: Setup MultiMonitorTool
$zipUrl = "https://www.nirsoft.net/utils/multimonitortool-x64.zip"
$zipPath = "$tramsPath\multimonitortool-x64.zip"
$extractPath = "$tramsPath\multimonitortool"
if (!(Test-Path $zipPath)) {
    Write-Host "Downloading MultiMonitorTool..."
    Invoke-WebRequest -Uri $zipUrl -OutFile $zipPath
} else {
    Write-Host "MultiMonitorTool already exists."
}
Write-Host "Extracting MultiMonitorTool..."
Expand-Archive -Path $zipPath -DestinationPath $extractPath
Write-Host "Extraction complete."

# 6-1: Open the SignalVu download page in a browser
$downloadUrl = "https://www.tek.com/ja/support/software/application/signalvupc-vector-signal-analysis-software-v550143"
Start-Process "msedge.exe" -ArgumentList $downloadUrl
Write-Host "Opened SignalVu download page in browser."

# 7-1: Completion message
$completionMessage = "Please download SignalVu from the official TEKTRONIX page, follow the installer instructions, and reboot your computer after installation is complete. The setup script has finished."
Write-Host $completionMessage

# 7-2: Wait for Enter key input before exiting
Write-Host "The script has completed. Press Enter to exit."
Read-Host
