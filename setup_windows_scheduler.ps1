# Windows Task Scheduler Setup for AI Employee
# Run this in PowerShell as Administrator

$ProjectPath = "C:\Users\uses\Downloads\ai employee"
$PythonExe = "python"
$VaultPath = "$ProjectPath\AI_Employee_Vault"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AI EMPLOYEE - Windows Task Scheduler Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "[ERROR] Please run PowerShell as Administrator" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Running as Administrator" -ForegroundColor Green
Write-Host ""

# Task 1: Daily Dashboard Refresh (8:00 AM)
Write-Host "Creating task: Daily Dashboard Refresh (8:00 AM)..." -ForegroundColor Yellow
$Action1 = New-ScheduledTaskAction -Execute $PythonExe -Argument "`"$ProjectPath\scripts\scheduler_tasks.py`" dashboard_refresh" -WorkingDirectory $ProjectPath
$Trigger1 = New-ScheduledTaskTrigger -Daily -At 8am
Register-ScheduledTask -TaskName "AI_Employee_Dashboard_Refresh" -Action $Action1 -Trigger $Trigger1 -Description "Refresh AI Employee Dashboard daily at 8 AM" | Out-Null
Write-Host "[OK] Task created: AI_Employee_Dashboard_Refresh" -ForegroundColor Green

# Task 2: Inbox Scan (Every 2 hours)
Write-Host "Creating task: Inbox Scan (Every 2 hours)..." -ForegroundColor Yellow
$Action2 = New-ScheduledTaskAction -Execute $PythonExe -Argument "`"$ProjectPath\scripts\scheduler_tasks.py`" inbox_scan" -WorkingDirectory $ProjectPath
$Trigger2 = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 2) -RepetitionDuration ([TimeSpan]::MaxValue)
Register-ScheduledTask -TaskName "AI_Employee_Inbox_Scan" -Action $Action2 -Trigger $Trigger2 -Description "Scan AI Employee Inbox every 2 hours" | Out-Null
Write-Host "[OK] Task created: AI_Employee_Inbox_Scan" -ForegroundColor Green

# Task 3: Weekly CEO Briefing (Monday 7:00 AM)
Write-Host "Creating task: Weekly CEO Briefing (Monday 7:00 AM)..." -ForegroundColor Yellow
$Action3 = New-ScheduledTaskAction -Execute $PythonExe -Argument "`"$ProjectPath\scripts\scheduler_tasks.py`" weekly_briefing" -WorkingDirectory $ProjectPath
$Trigger3 = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 7am
Register-ScheduledTask -TaskName "AI_Employee_Weekly_Briefing" -Action $Action3 -Trigger $Trigger3 -Description "Generate Monday Morning CEO Briefing" | Out-Null
Write-Host "[OK] Task created: AI_Employee_Weekly_Briefing" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SETUP COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Created tasks:" -ForegroundColor White
Write-Host "  - AI_Employee_Dashboard_Refresh (Daily 8:00 AM)" -ForegroundColor Gray
Write-Host "  - AI_Employee_Inbox_Scan (Every 2 hours)" -ForegroundColor Gray
Write-Host "  - AI_Employee_Weekly_Briefing (Monday 7:00 AM)" -ForegroundColor Gray
Write-Host ""
Write-Host "To view tasks: Open Task Scheduler and search for 'AI_Employee'" -ForegroundColor Yellow
Write-Host "To delete tasks: .\remove_tasks.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "To test manually:" -ForegroundColor Yellow
Write-Host "  python scripts\scheduler_tasks.py dashboard_refresh" -ForegroundColor Gray
Write-Host "  python scripts\scheduler_tasks.py inbox_scan" -ForegroundColor Gray
Write-Host "  python scripts\scheduler_tasks.py weekly_briefing" -ForegroundColor Gray
Write-Host ""
