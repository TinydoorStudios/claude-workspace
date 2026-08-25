<#
  Recycle-Magewell-RX.ps1   (v3 - adds a per-minute connection WATCHDOG)
  ------------------------------------------------------------------
  Keeps the two RX streams on the Magewell Pro Convert Audio DX
  (ESP Audio, serial A426250206029) connected to "FSQ BIG BRIDGE".

  Two jobs live in this one file:

    NIGHTLY RECYCLE (-Install)   2:00 AM daily, unconditional off->on->verify
                                 of both streams. Belt-and-suspenders.

    WATCHDOG (-InstallWatchdog)  every 1 minute. Polls rx/live-info and
                                 toggles ONLY a stream that reports
                                 disconnected. A healthy stream is never
                                 touched (no audio glitch). This is the
                                 real fix: the Magewell firmware has NO
                                 auto-reconnect, so a mid-day drop used to
                                 sit dead until the 2 AM recycle - up to
                                 ~24 h of silence. The watchdog cuts that
                                 to ~1 minute.

  Alerting is TRANSITION-based (via a small state file) so a per-minute
  task does not spam Slack: one message when a stream drops, one when it
  comes back. Repeated failures while a stream stays down do NOT re-alert.

  USAGE
    Test recycle:    right-click > Run with PowerShell
    Test watchdog:   powershell -ExecutionPolicy Bypass -File .\Recycle-Magewell-RX.ps1 -Watchdog
    Install both (elevated):
        powershell -ExecutionPolicy Bypass -File .\Recycle-Magewell-RX.ps1 -Install
        powershell -ExecutionPolicy Bypass -File .\Recycle-Magewell-RX.ps1 -InstallWatchdog
    Remove:  -Uninstall  /  -UninstallWatchdog

  Nightly logs to recycle-magewell-rx.log; watchdog logs (action-only) to
  magewell-rx-watchdog.log; both beside this script.
#>

param(
    [switch]$Install,
    [switch]$Uninstall,
    [switch]$Watchdog,
    [switch]$InstallWatchdog,
    [switch]$UninstallWatchdog
)

# ----------------------------- CONFIG -----------------------------
$Device   = '192.168.66.1'                 # Pro Convert address as seen from this PC
$Serial   = 'A426250206029'                # unit serial (part of its session-cookie name)
$Username = 'Admin'
$Password = '3cdc3cdc'                     # web-UI Admin password
$OffOnGap = 5                              # seconds to leave a stream off before re-enabling
$ConnectTimeout = 30                       # seconds to wait for a stream to report connected
$PollEvery      = 3                        # seconds between status polls
$MaxAttempts    = 3                        # off/on cycles to try before giving up on a stream
$RunAt    = '2:00AM'                        # schedule time used by -Install
$SlackWebhook = 'https://n8n.tinydoorstudios.com/webhook/magewell-rx-alert'   # n8n webhook -> Slack #gear-repair

# The two RX channels, exactly as the unit's web UI sends them.
$Channels = @(
    @{ uid = 1; 'stream-no' = 'Stream1'; name = 'FSQ Audio 1-4';
       url = 'ntkndi://ndi?ndi-name=FSQ BIG BRIDGE (FSQ-AUDIO (FSQ 1-4))&ndi-url=192.168.0.55:5969&mw-buffer-duration=60&mw-headroom-db=-20&mw-audio-standard=SMPTE' },
    @{ uid = 2; 'stream-no' = 'Stream2'; name = 'FSQ Audio 5-8';
       url = 'ntkndi://ndi?ndi-name=FSQ BIG BRIDGE (FSQ-AUDIO (FSQ 5-8))&ndi-url=192.168.0.55:5968&mw-buffer-duration=60&mw-headroom-db=-20&mw-audio-standard=SMPTE' }
)
# ------------------------------------------------------------------

$ErrorActionPreference = 'Stop'
$LogFile   = Join-Path $PSScriptRoot 'recycle-magewell-rx.log'
$WatchLog  = Join-Path $PSScriptRoot 'magewell-rx-watchdog.log'
$StateFile = Join-Path $PSScriptRoot 'magewell-rx-watchdog.state'

# $script:CurrentLog is switched to the watchdog log when running as the watchdog.
$script:CurrentLog = $LogFile
function Log($m) {
    $line = "{0}  {1}" -f ([DateTime]::Now.ToString('yyyy-MM-dd HH:mm:ss')), $m
    Write-Host $line
    Add-Content -Path $script:CurrentLog -Value $line
}

$TaskName      = 'Magewell RX Nightly Recycle'
$WatchTaskName = 'Magewell RX Watchdog'

# ---- Nightly recycle: install / uninstall ----
if ($Uninstall) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "Removed scheduled task '$TaskName'."
    return
}
if ($Install) {
    $action  = New-ScheduledTaskAction -Execute 'powershell.exe' `
                 -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`""
    $trigger = New-ScheduledTaskTrigger -Daily -At $RunAt
    $set     = New-ScheduledTaskSettingsSet -StartWhenAvailable -WakeToRun `
                 -DontStopOnIdleEnd -ExecutionTimeLimit (New-TimeSpan -Minutes 10)
    $principal = New-ScheduledTaskPrincipal -UserId 'SYSTEM' -LogonType ServiceAccount -RunLevel Highest
    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger `
                 -Settings $set -Principal $principal -Force `
                 -Description 'Nightly off/on recycle of the Magewell Pro Convert RX streams (belt-and-suspenders behind the watchdog).' | Out-Null
    Write-Host "Installed scheduled task '$TaskName' for $RunAt daily (runs as SYSTEM, background)."
    return
}

# ---- Watchdog: install / uninstall ----
if ($UninstallWatchdog) {
    Unregister-ScheduledTask -TaskName $WatchTaskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "Removed scheduled task '$WatchTaskName'."
    return
}
if ($InstallWatchdog) {
    $action  = New-ScheduledTaskAction -Execute 'powershell.exe' `
                 -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`" -Watchdog"
    # An every-minute cadence must be its OWN -Once trigger with a repetition
    # interval; a repetition hung off -AtLogOn only starts repeating after the
    # next logon and leaves LastRunTime at the 1999 placeholder.
    $trigger = New-ScheduledTaskTrigger -Once -At ((Get-Date).AddMinutes(1)) `
                 -RepetitionInterval (New-TimeSpan -Minutes 1) `
                 -RepetitionDuration (New-TimeSpan -Days 3650)
    $set     = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd `
                 -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 4)
    $principal = New-ScheduledTaskPrincipal -UserId 'SYSTEM' -LogonType ServiceAccount -RunLevel Highest
    Register-ScheduledTask -TaskName $WatchTaskName -Action $action -Trigger $trigger `
                 -Settings $set -Principal $principal -Force `
                 -Description 'Every minute: toggle any Magewell RX stream that has dropped its NDI connection (Magewell firmware has no auto-reconnect).' | Out-Null
    Write-Host "Installed scheduled task '$WatchTaskName' (every 1 min, runs as SYSTEM, background)."
    return
}

# ----------------------------- SHARED ------------------------------
function Get-Sha256Hex([string]$s) {
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($s)
    $sha   = [System.Security.Cryptography.SHA256]::Create()
    -join ($sha.ComputeHash($bytes) | ForEach-Object { $_.ToString('x2') })
}

$base = "http://$Device"

function Connect-Device {
    $loginBody = @{ username = $Username; password = (Get-Sha256Hex $Password) } | ConvertTo-Json -Compress
    $login = Invoke-RestMethod -Uri "$base/api/user/login" -Method Post `
                -Body $loginBody -ContentType 'application/json' -SessionVariable sess
    if ($login.status -ne 0) { throw "Login failed (status $($login.status)) - check the password." }
    if ($login.sid) {
        $sess.Cookies.Add((New-Object System.Net.Cookie("sid-$Serial", $login.sid, '/', $Device)))
    }
    $script:sess = $sess
}

function Apply($ch, [bool]$enable) {
    $body = @{
        uid         = $ch.uid
        enable      = $enable
        'stream-no' = $ch.'stream-no'
        name        = $ch.name
        url         = $ch.url
    } | ConvertTo-Json -Compress
    $r = Invoke-RestMethod -Uri "$base/api/rx/live-apply" -Method Post `
            -Body $body -ContentType 'application/json' -WebSession $script:sess
    return $r.status
}

# Pull live status and normalise to a flat array of channel objects.
function Get-RxChannels {
    $info = Invoke-RestMethod -Uri "$base/api/rx/live-info" -Method Post `
                -Body '{}' -ContentType 'application/json' -WebSession $script:sess
    if ($info -is [System.Array]) { return $info }
    foreach ($k in 'gst','channels','rx-channels','rx','data','list') {
        if ($info.PSObject.Properties.Name -contains $k -and $info.$k) { return $info.$k }
    }
    return @($info)
}

# True only when the named uid reports a live NDI connection.
function Test-Connected($uid) {
    try {
        $ch = Get-RxChannels | Where-Object { $_.uid -eq $uid } | Select-Object -First 1
        return ($ch -and $ch.report.'is-connected' -eq $true -and $ch.report.'conn-state' -eq 2)
    } catch { return $false }
}

function Recycle-One($ch) {
    for ($attempt = 1; $attempt -le $MaxAttempts; $attempt++) {
        $s1 = Apply $ch $false
        Start-Sleep -Seconds $OffOnGap
        $s2 = Apply $ch $true

        $deadline = (Get-Date).AddSeconds($ConnectTimeout)
        do {
            Start-Sleep -Seconds $PollEvery
            if (Test-Connected $ch.uid) {
                Log ("  {0,-14} attempt {1}: CONNECTED (off={2}/on={3})" -f $ch.name, $attempt, $s1, $s2)
                return $true
            }
        } while ((Get-Date) -lt $deadline)

        Log ("  {0,-14} attempt {1}: still connecting after {2}s - retrying" -f $ch.name, $attempt, $ConnectTimeout)
    }
    Log ("  {0,-14} FAILED to connect after {1} attempts" -f $ch.name, $MaxAttempts)
    return $false
}

function Send-Alert($text) {
    if (-not $SlackWebhook) { return }
    try {
        Invoke-RestMethod -Uri $SlackWebhook -Method Post `
            -Body (@{ text = $text } | ConvertTo-Json -Compress) -ContentType 'application/json' | Out-Null
    } catch { Log "  (alert webhook failed: $($_.Exception.Message))" }
}

# ----------------------------- WATCHDOG ----------------------------
# Transition-based: only alerts when a stream changes up<->down, so the
# per-minute cadence never spams. State persists in $StateFile as
# uid -> 'up'|'down'.
function Get-State {
    if (Test-Path $StateFile) {
        try { return (Get-Content $StateFile -Raw | ConvertFrom-Json) } catch { }
    }
    return $null
}
function Prev-State($state, $uid) {
    if ($state) {
        $p = $state.PSObject.Properties | Where-Object { $_.Name -eq "$uid" } | Select-Object -First 1
        if ($p) { return $p.Value }
    }
    return 'up'   # assume healthy on first run so we don't alert on a cold start
}

if ($Watchdog) {
    $script:CurrentLog = $WatchLog
    try {
        Connect-Device
    } catch {
        # Can't even reach the unit. Record it, but don't Slack every minute:
        # only alert on the transition into an unreachable state.
        $state = Get-State
        if ((Prev-State $state 'device') -ne 'down') {
            Log "ERROR: cannot reach $Device - $($_.Exception.Message)"
            Send-Alert ":rotating_light: Magewell $Device unreachable from the ESP PC - $($_.Exception.Message)"
        }
        @{ device = 'down' } | ConvertTo-Json | Set-Content $StateFile
        exit 1
    }

    $state   = Get-State
    $newState = @{ device = 'up' }
    foreach ($c in $Channels) {
        $prev = Prev-State $state $c.uid
        $connected = Test-Connected $c.uid
        if ($connected) {
            if ($prev -eq 'down') {
                Log ("{0,-14} RECOVERED (now connected)" -f $c.name)
                Send-Alert (":white_check_mark: Magewell RX '$($c.name)' is back up.")
            }
            $newState["$($c.uid)"] = 'up'
        }
        else {
            if ($prev -ne 'down') {
                # Fresh drop - try to recover it right now.
                Log ("{0,-14} DOWN - toggling to recover" -f $c.name)
                if (Recycle-One $c) {
                    Send-Alert (":arrows_counterclockwise: Magewell RX '$($c.name)' dropped and was auto-recovered within a minute.")
                    $newState["$($c.uid)"] = 'up'
                } else {
                    Send-Alert (":rotating_light: Magewell RX '$($c.name)' dropped and did NOT reconnect - source may be offline. Watchdog will keep retrying.")
                    $newState["$($c.uid)"] = 'down'
                }
            }
            else {
                # Still down from a previous minute - keep retrying quietly, no repeat alert.
                if (Recycle-One $c) {
                    Log ("{0,-14} RECOVERED after sustained outage" -f $c.name)
                    Send-Alert (":white_check_mark: Magewell RX '$($c.name)' is back up.")
                    $newState["$($c.uid)"] = 'up'
                } else {
                    $newState["$($c.uid)"] = 'down'
                }
            }
        }
    }
    $newState | ConvertTo-Json | Set-Content $StateFile
    return
}

# ----------------------------- NIGHTLY RUN -------------------------
try {
    Connect-Device
    Log "Logged in to $Device."

    Log 'Recycling RX streams (off -> on -> verify connected)...'
    $failed = @()
    foreach ($c in $Channels) {
        if (-not (Recycle-One $c)) { $failed += $c.name }
    }

    if ($failed.Count -gt 0) {
        $msg = "Magewell RX recycle INCOMPLETE on $Device - still not connected: $($failed -join ', ')"
        Log "ERROR: $msg"
        Send-Alert ":rotating_light: $msg"
        exit 1
    }

    Log 'Recycle complete - all streams verified connected.'
}
catch {
    Log "ERROR: $($_.Exception.Message)"
    Send-Alert ":rotating_light: Magewell RX recycle errored on $Device - $($_.Exception.Message)"
    exit 1
}
