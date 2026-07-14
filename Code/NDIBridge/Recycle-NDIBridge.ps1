<#
  Recycle-NDIBridge.ps1
  Leaves the NDI Bridge, waits, then rejoins -- to keep the connection fresh.
  Uses UI Automation to find the Join/Leave toggle (autoId 'JoinBridgeButton')
  and clicks it by its live screen position. Verifies the rejoin actually lands
  (button label flips back to 'Leave' = connected).

  Usage:  powershell -ExecutionPolicy Bypass -File Recycle-NDIBridge.ps1 [-Gap 60]
#>
param([int]$Gap = 60)

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
$LogFile = Join-Path $PSScriptRoot 'ndibridge-recycle.log'

function Log($m) {
    $l = "{0}  {1}" -f ([DateTime]::Now.ToString('yyyy-MM-dd HH:mm:ss')), $m
    Write-Host $l
    Add-Content -Path $LogFile -Value $l
}

function Get-BridgeWindow {
    $p = Get-Process -Name 'Application.NDI.Bridge.UI' -ErrorAction SilentlyContinue
    if (-not $p) { return $null }
    $cond = New-Object System.Windows.Automation.PropertyCondition($AE::ProcessIdProperty, $p[0].Id)
    return $AE::RootElement.FindFirst($TS::Children, $cond)
}
function Get-JoinButton($win) {
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
    if (-not $b) { Log '  ERROR: Join/Leave button not found at click time.'; return $false }
    $r = $b.Current.BoundingRectangle
    $x = [int]($r.X + $r.Width / 2)
    $y = [int]($r.Y + $r.Height / 2)
    Log ("  clicking '" + $b.Current.Name + "' at $x,$y")
    [Win]::Click($x, $y)
    return $true
}

$win = Get-BridgeWindow
if (-not $win) { Log 'ERROR: NDI Bridge UI window not found (is the bridge running?).'; exit 1 }

$label = Get-Label $win
Log "Bridge button reads '$label'."

# --- Leave (if currently joined) ---
if ($label -eq 'Leave') {
    if (-not (Click-JoinButton $win)) { exit 1 }
    Start-Sleep -Seconds 3
    Log ("After Leave, button reads '" + (Get-Label (Get-BridgeWindow)) + "'.")
} else {
    Log "Bridge wasn't joined (button '$label') -- will just join."
}

Log "Waiting $Gap seconds with the bridge down..."
Start-Sleep -Seconds $Gap

# --- Rejoin ---
$win = Get-BridgeWindow
if (-not $win) { Log 'ERROR: bridge window vanished during the wait.'; exit 1 }
if ((Get-Label $win) -eq 'Join') {
    if (-not (Click-JoinButton $win)) { exit 1 }
} else {
    Log ("Button already reads '" + (Get-Label $win) + "' before rejoin click.")
}

# --- Verify it actually reconnected ---
$ok = $false
for ($i = 0; $i -lt 20; $i++) {
    Start-Sleep -Seconds 3
    $win = Get-BridgeWindow
    if ($win -and (Get-Label $win) -eq 'Leave') { $ok = $true; break }
}
if ($ok) {
    Log 'Rejoined -- button reads Leave (connected). Recycle complete.'
} else {
    Log 'ERROR: bridge did not return to connected state after rejoin.'
    exit 1
}
