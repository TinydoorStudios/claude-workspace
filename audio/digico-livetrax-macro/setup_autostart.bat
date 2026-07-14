@echo off
echo Installing DiGiCo REAPER Relay auto-start...

:: Copy run_relay.bat to the Windows Startup folder so it launches at login
set STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
copy /y "%~dp0run_relay.bat" "%STARTUP%\run_relay.bat"

if %errorlevel% == 0 (
    echo.
    echo Done. The relay will start automatically every time you log in.
    echo.
    echo Starting it now...
    start "DiGiCo REAPER Relay" "%STARTUP%\run_relay.bat"
) else (
    echo.
    echo FAILED - try right-clicking setup_autostart.bat and choosing Run as administrator.
)
pause
