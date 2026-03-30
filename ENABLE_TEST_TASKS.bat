@echo off
:: AI Employee - Enable All Test Tasks
:: Run this to resume automated tasks

echo ========================================
echo AI Employee - START All Test Tasks
echo ========================================
echo.
echo Enabling all test scheduled tasks...
echo.

:: Enable test tasks
schtasks /Change /TN "AI_Employee_Dashboard_Refresh_TEST" /ENABLE 2>nul
if %errorLevel% == 0 (
    echo [OK] Enabled: AI_Employee_Dashboard_Refresh_TEST (Every 2 min)
) else (
    echo [SKIP] Not found: AI_Employee_Dashboard_Refresh_TEST
)

schtasks /Change /TN "AI_Employee_Inbox_Scan_TEST" /ENABLE 2>nul
if %errorLevel% == 0 (
    echo [OK] Enabled: AI_Employee_Inbox_Scan_TEST (Every 1 min)
) else (
    echo [SKIP] Not found: AI_Employee_Inbox_Scan_TEST
)

schtasks /Change /TN "AI_Employee_Gmail_Watcher_TEST" /ENABLE 2>nul
if %errorLevel% == 0 (
    echo [OK] Enabled: AI_Employee_Gmail_Watcher_TEST (Every 2 min)
) else (
    echo [SKIP] Not found: AI_Employee_Gmail_Watcher_TEST
)

echo.
echo ========================================
echo ALL TEST TASKS ENABLED
echo ========================================
echo.
echo Tasks are now RUNNING.
echo.
echo To DISABLE again (development mode):
echo   .\DISABLE_TEST_TASKS.bat
echo.
pause
