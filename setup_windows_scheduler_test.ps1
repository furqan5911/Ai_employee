# Windows Task Scheduler Setup for AI Employee - TESTING MODE
# Run this in PowerShell as Administrator
#
# TESTING MODE: Tasks run every 1-2 minutes for verification
# PRODUCTION MODE: Use setup_windows_scheduler.ps1 for proper intervals

$ProjectPath = "C:\Users\uses\Downloads\ai employee"
$PythonExe = "python"
$VaultPath = "$ProjectPath\AI_Employee_Vault"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AI EMPLOYEE - Task Scheduler (TEST MODE)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[TESTING] Tasks will run every 1-2 minutes" -ForegroundColor Yellow
Write-Host "[PRODUCTION] Use setup_windows_scheduler.ps1 for hourly/daily intervals" -ForegroundColor Yellow
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "[ERROR] Please run PowerShell as Administrator" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Running as Administrator" -ForegroundColor Green
Write-Host ""

# Task 1: Dashboard Refresh (Every 2 minutes - TESTING)
Write-Host "Creating task: Dashboard Refresh (Every 2 min - TESTING)..." -ForegroundColor Yellow
$Action1 = New-ScheduledTaskAction -Execute $PythonExe -Argument "`"$ProjectPath\scripts\scheduler_tasks.py`" dashboard_refresh" -WorkingDirectory $ProjectPath
$Trigger1 = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 2) -RepetitionDuration (New-TimeSpan -Days 365)
Register-ScheduledTask -TaskName "AI_Employee_Dashboard_Refresh_TEST" -Action $Action1 -Trigger $Trigger1 -Description "TESTING: Refresh dashboard every 2 minutes. PRODUCTION: Daily at 8 AM" | Out-Null
Write-Host "[OK] Task created: AI_Employee_Dashboard_Refresh_TEST" -ForegroundColor Green

# Task 2: Inbox Scan (Every 1 minute - TESTING)
Write-Host "Creating task: Inbox Scan (Every 1 min - TESTING)..." -ForegroundColor Yellow
$Action2 = New-ScheduledTaskAction -Execute $PythonExe -Argument "`"$ProjectPath\scripts\scheduler_tasks.py`" inbox_scan" -WorkingDirectory $ProjectPath
$Trigger2 = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 1) -RepetitionDuration (New-TimeSpan -Days 365)
Register-ScheduledTask -TaskName "AI_Employee_Inbox_Scan_TEST" -Action $Action2 -Trigger $Trigger2 -Description "TESTING: Scan inbox every 1 minute. PRODUCTION: Every 2 hours" | Out-Null
Write-Host "[OK] Task created: AI_Employee_Inbox_Scan_TEST" -ForegroundColor Green

# Task 3: Gmail Watcher Test (Every 2 minutes - TESTING)
Write-Host "Creating task: Gmail Watcher (Every 2 min - TESTING)..." -ForegroundColor Yellow
$Action3 = New-ScheduledTaskAction -Execute $PythonExe -Argument "`"$ProjectPath\scripts\gmail_watcher.py`" --once" -WorkingDirectory $ProjectPath
$Trigger3 = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 2) -RepetitionDuration (New-TimeSpan -Days 365)
Register-ScheduledTask -TaskName "AI_Employee_Gmail_Watcher_TEST" -Action $Action3 -Trigger $Trigger3 -Description "TESTING: Check Gmail every 2 minutes. PRODUCTION: Every 2 hours" | Out-Null
Write-Host "[OK] Task created: AI_Employee_Gmail_Watcher_TEST" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TESTING SETUP COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Created TEST tasks:" -ForegroundColor White
Write-Host "  - AI_Employee_Dashboard_Refresh_TEST (Every 2 min)" -ForegroundColor Gray
Write-Host "  - AI_Employee_Inbox_Scan_TEST (Every 1 min)" -ForegroundColor Gray
Write-Host "  - AI_Employee_Gmail_Watcher_TEST (Every 2 min)" -ForegroundColor Gray
Write-Host ""
Write-Host "TO SWITCH TO PRODUCTION:" -ForegroundColor Yellow
Write-Host "  1. Run: .\remove_tasks_test.ps1" -ForegroundColor Gray
Write-Host "  2. Run: .\setup_windows_scheduler.ps1 (production intervals)" -ForegroundColor Gray
Write-Host ""
Write-Host "To view tasks: Open Task Scheduler and search for 'AI_Employee'" -ForegroundColor Yellow
Write-Host "To delete test tasks: .\remove_tasks_test.ps1" -ForegroundColor Yellow
Write-Host ""
