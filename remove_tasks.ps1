# Remove AI Employee Scheduled Tasks
# Run this in PowerShell

Write-Host "Removing AI Employee scheduled tasks..." -ForegroundColor Yellow

$tasks = @(
    "AI_Employee_Dashboard_Refresh",
    "AI_Employee_Inbox_Scan",
    "AI_Employee_Weekly_Briefing"
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
Write-Host "All AI Employee tasks removed." -ForegroundColor Cyan
