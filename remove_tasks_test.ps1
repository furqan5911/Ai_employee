# Remove AI Employee Test Tasks from Windows Task Scheduler
# Run this in PowerShell as Administrator

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AI EMPLOYEE - Remove Test Tasks" -ForegroundColor Cyan
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

$tasks = @(
    "AI_Employee_Dashboard_Refresh_TEST",
    "AI_Employee_Inbox_Scan_TEST",
    "AI_Employee_Gmail_Watcher_TEST"
)

foreach ($task in $tasks) {
    try {
        Unregister-ScheduledTask -TaskName $task -Confirm:$false -ErrorAction Stop
        Write-Host "[OK] Removed: $task" -ForegroundColor Green
    } catch {
        Write-Host "[SKIP] Task not found: $task" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "Test tasks removed. Ready for production setup." -ForegroundColor Green
Write-Host "Run: .\setup_windows_scheduler.ps1" -ForegroundColor Yellow
Write-Host ""
