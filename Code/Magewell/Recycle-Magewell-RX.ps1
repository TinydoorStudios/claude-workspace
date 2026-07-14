<#
  Recycle-Magewell-RX.ps1   (v2 — verifies the stream actually CONNECTS)
  ------------------------------------------------------------------
  Nightly "off then on" recycle of the two RX streams on the
  Magewell Pro Convert Audio DX (ESP Audio, serial A426250206029).

  v2 change: after re-enabling, it polls the unit's status until each
  stream reports actually connected (report.is-connected = true), not just
  that the API accepted the command. If a stream is still "Connecting"
  after the timeout, it cycles that stream off/on again, up to N tries.
  Only logs "all streams connected" when they truly are; otherwise ERROR
  + (optional) Slack alert + non-zero exit.

  USAGE
    1. Edit the $Password line below (web-UI Admin password).
    2. Test:     right-click this file > Run with PowerShell
    3. Schedule: from an elevated prompt -
                   powershell -ExecutionPolicy Bypass -File .\Recycle-Magewell-RX.ps1 -Install
                 registers a 2 AM daily task. -Uninstall removes it.

  Logs to recycle-magewell-rx.log beside this script.
#>

param(
    [switch]$Install,
    [switch]$Uninstall
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
$SlackWebhook = ''                         # optional: paste an n8n/Slack webhook URL to get a failure alert

# The two RX channels, exactly as the unit's web UI sends them.
$Channels = @(
    @{ uid = 1; 'stream-no' = 'Stream1'; name = 'FSQ Audio 1-4';
       url = 'ntkndi://ndi?ndi-name=FSQ BIG BRIDGE (FSQ-AUDIO (FSQ 1-4))&ndi-url=192.168.0.55:5969&mw-buffer-duration=60&mw-headroom-db=-20&mw-audio-standard=SMPTE' },
    @{ uid = 2; 'stream-no' = 'Stream2'; name = 'FSQ Audio 5-8';
       url = 'ntkndi://ndi?ndi-name=FSQ BIG BRIDGE (FSQ-AUDIO (FSQ 5-8))&ndi-url=192.168.0.55:5968&mw-buffer-duration=60&mw-headroom-db=-20&mw-audio-standard=SMPTE' }
)
# ------------------------------------------------------------------

$ErrorActionPreference = 'Stop'
$LogFile = Join-Path $PSScriptRoot 'recycle-magewell-rx.log'

function Log($m) {
    $line = "{0}  {1}" -f ([DateTime]::Now.ToString('yyyy-MM-dd HH:mm:ss')), $m
    Write-Host $line
    Add-Content -Path $LogFile -Value $line
}

# ---- Scheduled-task install / uninstall ----
$TaskName = 'Magewell RX Nightly Recycle'

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
    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger `
                 -Settings $set -RunLevel Highest -Force `
                 -Description 'Toggles the Magewell Pro Convert RX streams off then on, then verifies they reconnect, to clear stale NDI receivers.' | Out-Null
    Write-Host "Installed scheduled task '$TaskName' for $RunAt daily."
    return
}

# ----------------------------- RUN --------------------------------
function Get-Sha256Hex([string]$s) {
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($s)
    $sha   = [System.Security.Cryptography.SHA256]::Create()
    -join ($sha.ComputeHash($bytes) | ForEach-Object { $_.ToString('x2') })
}

$base = "http://$Device"

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
    foreach ($k in 'channels','rx-channels','rx','data','list') {
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

        Log ("  {0,-14} attempt {1}: still connecting after {2}s — retrying" -f $ch.name, $attempt, $ConnectTimeout)
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

try {
    # 1. Log in -> session cookie
    $loginBody = @{ username = $Username; password = (Get-Sha256Hex $Password) } | ConvertTo-Json -Compress
    $login = Invoke-RestMethod -Uri "$base/api/user/login" -Method Post `
                -Body $loginBody -ContentType 'application/json' -SessionVariable sess
    if ($login.status -ne 0) { throw "Login failed (status $($login.status)) - check the password." }
    if ($login.sid) {
        $sess.Cookies.Add((New-Object System.Net.Cookie("sid-$Serial", $login.sid, '/', $Device)))
    }
    Log "Logged in to $Device."

    # 2. Recycle each stream and confirm it actually reconnects.
    Log 'Recycling RX streams (off -> on -> verify connected)...'
    $failed = @()
    foreach ($c in $Channels) {
        if (-not (Recycle-One $c)) { $failed += $c.name }
    }

    if ($failed.Count -gt 0) {
        $msg = "Magewell RX recycle INCOMPLETE on $Device — still not connected: $($failed -join ', ')"
        Log "ERROR: $msg"
        Send-Alert ":rotating_light: $msg"
        exit 1
    }

    Log 'Recycle complete — all streams verified connected.'
}
catch {
    Log "ERROR: $($_.Exception.Message)"
    Send-Alert ":rotating_light: Magewell RX recycle errored on $Device — $($_.Exception.Message)"
    exit 1
}
