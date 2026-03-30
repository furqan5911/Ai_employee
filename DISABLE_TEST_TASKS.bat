@echo off
:: AI Employee - Disable All Test Tasks (Development Mode)
:: Run this to stop all automated tasks while developing

echo ========================================
echo AI Employee - STOP All Test Tasks
echo ========================================
echo.
echo Disabling all test scheduled tasks...
echo.

:: Disable test tasks
schtasks /Change /TN "AI_Employee_Dashboard_Refresh_TEST" /DISABLE 2>nul
if %errorLevel% == 0 (
    echo [OK] Disabled: AI_Employee_Dashboard_Refresh_TEST
) else (
    echo [SKIP] Not found: AI_Employee_Dashboard_Refresh_TEST
)

schtasks /Change /TN "AI_Employee_Inbox_Scan_TEST" /DISABLE 2>nul
if %errorLevel% == 0 (
    echo [OK] Disabled: AI_Employee_Inbox_Scan_TEST
) else (
    echo [SKIP] Not found: AI_Employee_Inbox_Scan_TEST
)

schtasks /Change /TN "AI_Employee_Gmail_Watcher_TEST" /DISABLE 2>nul
if %errorLevel% == 0 (
    echo [OK] Disabled: AI_Employee_Gmail_Watcher_TEST
) else (
    echo [SKIP] Not found: AI_Employee_Gmail_Watcher_TEST
)

echo.
echo ========================================
echo ALL TEST TASKS DISABLED
echo ========================================
echo.
echo Tasks are now STOPPED. They will not run automatically.
echo.
echo To RE-ENABLE later:
echo   .\ENABLE_TEST_TASKS.bat
echo.
echo To DELETE permanently:
echo   .\remove_tasks_test.ps1
echo.
pause
