@echo off

:: 1. SignalVu-PC.exe を起動
echo Start SignalVu-PC.exe...
start "SignalVu-PC" "C:\Program Files\Tektronix\SignalVu-PC\SignalVu-PC.exe"
timeout /t 25

:: 2. Tek SignalVu-PCウィンドウを第二ディスプレイに移動
C:\TRAMs\multimonitortool\MultiMonitorTool.exe /MoveWindow Primary title "Tek SignalVu"
C:\TRAMs\multimonitortool\MultiMonitorTool.exe /MoveWindow Next title "Tek SignalVu"

:: 3. SVHandler.python を起動 (非表示)
echo Start SVHandler.python...
start /min cmd /c "python C:\TRAMs\TRAM-System\SVHandler\SVHandler.py"

:: 4. TVHandler.python を起動 (非表示)
echo Start TVHandler.python...
start /min cmd /c "python C:\TRAMs\TRAM-System\TVHandler\TVHandler.py"

:: 5. VDHandler.python を起動 (非表示)
echo Start VDHandler.python...
start /min cmd /c "python C:\TRAMs\TRAM-System\VDHandler\VDHandler.py"

:: 6. デフォルトブラウザで index.html をフルスクリーンモードで開く
start "" "%ProgramFiles%\Internet Explorer\iexplore.exe" "C:\TRAMs\TRAM-System\Controller\index.html"
timeout /t 3
C:\TRAMs\multimonitortool\MultiMonitorTool.exe /MoveWindow Primary title "TRAMs Control"


:loop
timeout /t 60
goto loop
