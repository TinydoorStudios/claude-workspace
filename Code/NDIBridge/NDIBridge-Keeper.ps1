<#
  NDIBridge-Keeper.ps1
  Keeps the NDI 6 Tools Bridge (GUI build) joined 24/7 on the ESP PC, and
  recycles it nightly to keep the connection fresh. Everything is driven by
  UI Automation: it finds the Join/Leave toggle (autoId 'JoinBridgeButton')
  and clicks it by its live screen position -- no process killing, no AutoHotkey.

  Modes:
    -Watchdog   Make sure the bridge is up and JOINED. If the window is closed,
                relaunch it; if it's sitting on 'Join' (left/disconnected),
                click Join. Runs every minute + at logon. Skips during a recycle.
    -Recycle    Leave the bridge, wait $Gap seconds, rejoin, verify it reconnects.
                Runs nightly (default 1:45 AM, before the Magewell 2:00 recycle).
    -Install    Register both scheduled tasks (run from an ELEVATED prompt).
    -Uninstall  Remove both tasks.
    (no args)   One-shot watchdog check -- handy for testing.

  The tasks run in the logged-in user's INTERACTIVE session at normal integrity,
  because a GUI app can't be driven from a session-0 service. The PC must stay
  logged in; the logon trigger re-arms everything after a reboot (pair with
  auto-login for hands-off reboot recovery).

  Log: ndi-bridge-keeper.log beside this script.
#>
param(
    [switch]$Watchdog,
    [switch]$Recycle,
    [switch]$Install,
    [switch]$Uninstall
)

# ------------------------------- CONFIG -------------------------------
$BridgeExe   = 'C:\Program Files\NDI\NDI 6 Tools\Bridge\Application.NDI.Bridge.UI.exe'
$EngineName  = 'Application.NDI.Bridge.x64'   # process that actually holds the bridge
$UIName      = 'Application.NDI.Bridge.UI'    # the window process
$Gap         = 60                              # seconds to stay "left" before rejoining
$RecycleAt   = '1:45AM'                        # nightly recycle time (before Magewell 2:00)
$WatchTask   = 'NDI Bridge Watchdog'
$RecycleTask = 'NDI Bridge Nightly Recycle'
# ----------------------------------------------------------------------

$ErrorActionPreference = 'Stop'
$ScriptDir = $PSScriptRoot
if (-not $ScriptDir) { $ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path }
$LogFile  = Join-Path $ScriptDir 'ndi-bridge-keeper.log'
$FlagFile = Join-Path $ScriptDir 'ndi-bridge-recycling.flag'

function Log($m) {
    $l = "{0}  {1}" -f ([DateTime]::Now.ToString('yyyy-MM-dd HH:mm:ss')), $m
    Write-Host $l
    try { Add-Content -Path $LogFile -Value $l } catch {}
}

# ----- scheduled task install / uninstall -----
if ($Uninstall) {
    Unregister-ScheduledTask -TaskName $WatchTask   -Confirm:$false -ErrorAction SilentlyContinue
    Unregister-ScheduledTask -TaskName $RecycleTask -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "Removed '$WatchTask' and '$RecycleTask'."
    return
}

if ($Install) {
    $me   = "$env:USERDOMAIN\$env:USERNAME"
    $self = $PSCommandPath
    # Normal integrity (Limited) so the task launches/drives the bridge the same
    # way you do by hand -- non-elevated, in your interactive desktop.
    $principal = New-ScheduledTaskPrincipal -UserId $me -LogonType Interactive -RunLevel Limited
    $settings  = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries `
                    -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew `
                    -ExecutionTimeLimit (New-TimeSpan -Minutes 5)

    # Watchdog: TWO triggers -- one repeating every minute starting now (fires
    # continuously regardless of logon), plus an at-logon trigger so it re-arms
    # after a reboot. (Attaching the repetition only to the logon trigger was the
    # bug that left it never running until the next logon.)
    $rep   = New-ScheduledTaskTrigger -Once -At (Get-Date).AddSeconds(30) `
                -RepetitionInterval (New-TimeSpan -Minutes 1) `
                -RepetitionDuration (New-TimeSpan -Days 3650)
    $logon = New-ScheduledTaskTrigger -AtLogOn -User $me
    $aWatch = New-ScheduledTaskAction -Execute 'powershell.exe' `
                -Argument "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$self`" -Watchdog"
    Register-ScheduledTask -TaskName $WatchTask -Trigger $rep, $logon -Action $aWatch `
                -Principal $principal -Settings $settings -Force `
                -Description 'Keeps the NDI Bridge joined; relaunches/rejoins if it is closed or left.' | Out-Null

    # Recycle: nightly
    $daily = New-ScheduledTaskTrigger -Daily -At $RecycleAt
    $aRec  = New-ScheduledTaskAction -Execute 'powershell.exe' `
                -Argument "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$self`" -Recycle"
    Register-ScheduledTask -TaskName $RecycleTask -Trigger $daily -Action $aRec `
                -Principal $principal -Settings $settings -Force `
                -Description 'Nightly leave/wait/rejoin of the NDI Bridge to keep the connection fresh.' | Out-Null

    Write-Host "Installed '$WatchTask' (logon + every 1 min) and '$RecycleTask' (daily $RecycleAt)."
    return
}

# ============================ UI AUTOMATION ============================
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class Win {
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint f, uint x, uint y, uint d, IntPtr e);
  const uint LD = 0x02, LU = 0x04;
  public static void Click(int x, int y) {
    SetCursorPos(x, y);
    System.Threading.Thread.Sleep(120);
    mouse_event(LD, 0, 0, 0, IntPtr.Zero);
    System.Threading.Thread.Sleep(60);
    mouse_event(LU, 0, 0, 0, IntPtr.Zero);
  }
}
"@

$AE = [System.Windows.Automation.AutomationElement]
$TS = [System.Windows.Automation.TreeScope]

function Get-BridgeWindow {
    # Return the MAIN bridge window (the one that holds JoinBridgeButton),
    # skipping any error/popup dialogs that share the same process.
    $p = Get-Process -Name $UIName -ErrorAction SilentlyContinue
    if (-not $p) { return $null }
    foreach ($proc in $p) {
        $cond = New-Object System.Windows.Automation.PropertyCondition($AE::ProcessIdProperty, $proc.Id)
        foreach ($w in $AE::RootElement.FindAll($TS::Children, $cond)) {
            $jb = New-Object System.Windows.Automation.PropertyCondition($AE::AutomationIdProperty, 'JoinBridgeButton')
            if ($w.FindFirst($TS::Descendants, $jb)) { return $w }
        }
    }
    return $null
}
# Click OK on any NDI Bridge error popup (e.g. "bridge name 'ESP' is already in use").
function Dismiss-ErrorDialog {
    $p = Get-Process -Name $UIName -ErrorAction SilentlyContinue
    if (-not $p) { return }
    foreach ($proc in $p) {
        $cond = New-Object System.Windows.Automation.PropertyCondition($AE::ProcessIdProperty, $proc.Id)
        foreach ($w in $AE::RootElement.FindAll($TS::Children, $cond)) {
            $okc = New-Object System.Windows.Automation.PropertyCondition($AE::NameProperty, 'OK')
            $ok  = $w.FindFirst($TS::Descendants, $okc)
            if ($ok) {
                [Win]::SetForegroundWindow([IntPtr]$w.Current.NativeWindowHandle) | Out-Null
                Start-Sleep -Milliseconds 300
                $r = $ok.Current.BoundingRectangle
                [Win]::Click([int]($r.X + $r.Width / 2), [int]($r.Y + $r.Height / 2))
                Log '  dismissed an error popup'
            }
        }
    }
}
function Get-JoinButton($win) {
    if (-not $win) { return $null }
    $cond = New-Object System.Windows.Automation.PropertyCondition($AE::AutomationIdProperty, 'JoinBridgeButton')
    return $win.FindFirst($TS::Descendants, $cond)
}
function Get-Label($win) {
    $b = Get-JoinButton $win
    if ($b) { return $b.Current.Name } else { return $null }
}
function Click-JoinButton($win) {
    $hwnd = [IntPtr]$win.Current.NativeWindowHandle
    [Win]::SetForegroundWindow($hwnd) | Out-Null
    Start-Sleep -Milliseconds 500
    $b = Get-JoinButton $win
    if (-not $b) { Log '  ERROR: Join/Leave button not found.'; return $false }
    $r = $b.Current.BoundingRectangle
    $x = [int]($r.X + $r.Width / 2); $y = [int]($r.Y + $r.Height / 2)
    Log ("  click '" + $b.Current.Name + "' at $x,$y")
    [Win]::Click($x, $y)
    return $true
}
# Launch the bridge if its window is gone; wait for the window to appear.
function Ensure-BridgeRunning {
    if (Get-BridgeWindow) { return $true }
    if (-not (Test-Path $BridgeExe)) { Log "  ERROR: bridge exe not found at $BridgeExe"; return $false }
    Log "  bridge window not found -- launching it"
    Start-Process -FilePath $BridgeExe | Out-Null
    for ($i = 0; $i -lt 20; $i++) { Start-Sleep -Seconds 2; if (Get-BridgeWindow) { return $true } }
    Log '  ERROR: bridge window did not appear after launch.'
    return $false
}
# Make sure the bridge is joined; returns $true when label reads 'Leave' (connected).
# A freshly relaunched window isn't ready for a few seconds, so keep re-clicking
# 'Join' until the button flips to 'Leave' (never click when it already reads 'Leave').
function Ensure-Joined {
    # Up to ~3 min: clear any error popup, click Join if needed, wait. This
    # outlasts the host releasing a name held by an abruptly-closed instance.
    for ($i = 0; $i -lt 36; $i++) {
        Dismiss-ErrorDialog
        $win = Get-BridgeWindow
        if ($win) {
            $lbl = Get-Label $win
            if ($lbl -eq 'Leave') { return $true }           # connected
            if ($lbl -eq 'Join')  { Click-JoinButton $win | Out-Null }
        }
        Start-Sleep -Seconds 5
    }
    $win = Get-BridgeWindow
    return ($win -and (Get-Label $win) -eq 'Leave')
}

# ============================== RECYCLE ===============================
if ($Recycle) {
    New-Item -Path $FlagFile -ItemType File -Force | Out-Null
    try {
        if (-not (Ensure-BridgeRunning)) { Log 'ERROR: recycle aborted - no bridge.'; exit 1 }
        $win = Get-BridgeWindow
        $label = Get-Label $win
        Log "Recycle: button reads '$label'."
        if ($label -eq 'Leave') {
            Click-JoinButton $win | Out-Null
            Start-Sleep -Seconds 3
            Log ("  after Leave, button reads '" + (Get-Label (Get-BridgeWindow)) + "'.")
        }
        Log "  waiting $Gap s with the bridge down..."
        Start-Sleep -Seconds $Gap
        if (Ensure-Joined) { Log 'Recycle complete -- rejoined (connected).' }
        else { Log 'ERROR: bridge did not reconnect after rejoin.'; exit 1 }
    }
    finally { Remove-Item $FlagFile -Force -ErrorAction SilentlyContinue }
    return
}

# ============================== WATCHDOG ==============================
# default (no args) also runs the watchdog check
if (Test-Path $FlagFile) { Log 'Watchdog: recycle in progress, skipping.'; return }

$engine = Get-Process -Name $EngineName -ErrorAction SilentlyContinue
$win    = Get-BridgeWindow
$label  = Get-Label $win

if ($engine -and $label -eq 'Leave') {
    # healthy and joined -- stay quiet (no log spam every minute)
    return
}

Log "Watchdog: not healthy (engine=$([bool]$engine), button='$label') -- recovering."
if (-not (Ensure-BridgeRunning)) { Log 'Watchdog ERROR: could not start bridge.'; exit 1 }
if (Ensure-Joined) { Log 'Watchdog: bridge is joined again.' }
else { Log 'Watchdog ERROR: bridge did not reach joined state.'; exit 1 }
