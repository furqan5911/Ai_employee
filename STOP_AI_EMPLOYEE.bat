@echo off
:: STOP ALL AI EMPLOYEE PROCESSES
:: Run this to save CPU during development

echo ========================================
echo STOPPING AI EMPLOYEE PROCESSES
echo ========================================
echo.

echo Step 1: Disabling scheduled tasks...
schtasks /Change /TN "AI_Employee_Dashboard_Refresh_TEST" /DISABLE >nul 2>&1
schtasks /Change /TN "AI_Employee_Inbox_Scan_TEST" /DISABLE >nul 2>&1
schtasks /Change /TN "AI_Employee_Gmail_Watcher_TEST" /DISABLE >nul 2>&1
echo [OK] Scheduled tasks disabled
echo.

echo Step 2: Stopping Python watcher processes...
for /f "tokens=2" %%i in ('tasklist /FI "IMAGENAME eq python.exe" ^| find "python.exe"') do (
    taskkill /F /PID %%i >nul 2>&1
)
echo [OK] Python processes stopped
echo.

echo ========================================
echo ALL AI EMPLOYEE PROCESSES STOPPED
echo ========================================
echo.
echo CPU resources saved!
echo.
echo To re-enable later: RUN ENABLE_TEST_TASKS.bat
echo.
timeout /t 3 >nul
