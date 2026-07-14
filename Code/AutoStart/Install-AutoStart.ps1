# Install-AutoStart.ps1
# Registers launch-order.ps1 as a hidden "At log on" Scheduled Task.
# Run this ONCE, from an elevated (Run as Administrator) PowerShell,
# in the same folder as launch-order.ps1.

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$target    = Join-Path $scriptDir "launch-order.ps1"

if (-not (Test-Path $target)) {
    throw "Can't find launch-order.ps1 next to this installer ($target)."
}

$taskName = "Audio Chain AutoStart"

$action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$target`""

# Fire at logon for the current user only.
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME

# Run in the interactive session (S4U) so the GUIs appear on the desktop,
# highest privileges, no time limit, run on battery too.
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME `
    -LogonType Interactive -RunLevel Highest

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit ([TimeSpan]::Zero) `
    -StartWhenAvailable

Register-ScheduledTask -TaskName $taskName `
    -Action $action -Trigger $trigger -Principal $principal -Settings $settings `
    -Description "Launches Dante Virtual Soundcard, VB-Audio Matrix, then Smaart 8 in order with 60s gaps." `
    -Force

Write-Host "Installed scheduled task: '$taskName'." -ForegroundColor Green
Write-Host "Test now without rebooting:  Start-ScheduledTask -TaskName '$taskName'"
Write-Host "Remove it later:             Unregister-ScheduledTask -TaskName '$taskName' -Confirm:`$false"
