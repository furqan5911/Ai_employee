@echo off
:: AI Employee - Fix and Install Scheduler (Auto-Elevate)
:: Double-click this file to run as Administrator

echo ========================================
echo AI Employee - Scheduler Fix & Install
echo ========================================
echo.

:: Check for Administrator privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Running as Administrator
    echo.
    goto :run_scripts
)

:: Request elevation
echo [INFO] Requesting Administrator privileges...
echo.
powershell -Command "Start-Process '%~f0' -Verb RunAs"
exit /b

:run_scripts
cd /d "%~dp0"

echo Step 1: Removing old broken tasks...
powershell -ExecutionPolicy Bypass -File "%~dp0remove_tasks_test.ps1"
echo.

echo Step 2: Installing fixed scheduler...
powershell -ExecutionPolicy Bypass -File "%~dp0setup_windows_scheduler_test.ps1"
echo.

echo ========================================
echo COMPLETE!
echo ========================================
echo.
echo Tasks created:
echo   - AI_Employee_Dashboard_Refresh_TEST (Every 2 min)
echo   - AI_Employee_Inbox_Scan_TEST (Every 1 min)
echo   - AI_Employee_Gmail_Watcher_TEST (Every 2 min)
echo.
echo To verify: Open Task Scheduler and search for "AI_Employee"
echo.
pause
