@echo off
:: AI Employee - Stop All Running Watchers
:: Run this to stop all background processes

echo ========================================
echo AI Employee - STOP All Watchers
echo ========================================
echo.
echo Stopping all Python watcher processes...
echo.

:: Kill all gmail_watcher.py processes
taskkill /F /IM python.exe /FI "WINDOWTITLE eq gmail_watcher*" 2>nul

:: Also try to kill by process name pattern (more aggressive)
for /f "tokens=2" %%i in ('tasklist /FI "IMAGENAME eq python.exe" ^| find "python.exe"') do (
    wmic process where "ProcessId=%%i" get CommandLine 2>nul | findstr /C:"gmail_watcher" /C:"filesystem_watcher" >nul
    if not errorlevel 1 (
        taskkill /F /PID %%i >nul 2>&1
        echo [OK] Stopped process %%i (watcher)
    )
)

echo.
echo ========================================
echo ALL WATCHERS STOPPED
echo ========================================
echo.
echo To run watchers manually:
echo   python scripts\gmail_watcher.py --once
echo   python scripts\filesystem_watcher.py
echo.
echo To re-enable scheduled tasks:
echo   .\ENABLE_TEST_TASKS.bat
echo.
pause
