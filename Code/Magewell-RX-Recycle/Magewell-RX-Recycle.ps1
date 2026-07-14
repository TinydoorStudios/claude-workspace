<#
  Magewell Pro Convert Audio DX - RX stream recycler
  -----------------------------------------------------
  Turns both RX streams OFF, waits, then turns them back ON.
  Clears stale NDI receivers that go quiet after a few days.

  Runs on the PC on the same network as the unit. No dependencies
  (uses built-in PowerShell). Schedule it via Task Scheduler - see README.

  Captured from the unit's own web UI on 2026-06-27:
    POST http://192.168.66.1/api/rx/live-apply  toggles a channel via "enable".
    POST http://192.168.66.1/api/user/login     auth, SHA256 password, sid cookie.
#>

# ---- Settings -------------------------------------------------------------
$Device   = "192.168.66.1"      # Pro Convert management IP (as seen from this PC)
$Username = "Admin"
$Password = "PUT_PASSWORD_HERE"  # <-- web UI password for the unit
$OffOnGap = 5                    # seconds to stay OFF before turning back ON
$LogFile  = Join-Path $PSScriptRoot "rx-recycle.log"
# ---------------------------------------------------------------------------

# RX channels exactly as the unit's UI sends them. If you ever re-point a
# source in the web UI, re-capture the url here.
$Channels = @(
  @{ uid = 1; "stream-no" = "Stream1"; name = "FSQ Audio 1-4";
     url = "ntkndi://ndi?ndi-name=FSQ BIG BRIDGE (FSQ-AUDIO (FSQ 1-4))&ndi-url=192.168.0.55:5969&mw-buffer-duration=60&mw-headroom-db=-20&mw-audio-standard=SMPTE" },
  @{ uid = 2; "stream-no" = "Stream2"; name = "FSQ Audio 5-8";
     url = "ntkndi://ndi?ndi-name=FSQ BIG BRIDGE (FSQ-AUDIO (FSQ 5-8))&ndi-url=192.168.0.55:5968&mw-buffer-duration=60&mw-headroom-db=-20&mw-audio-standard=SMPTE" }
)

$ErrorActionPreference = "Stop"
function Log([string]$msg) {
  $line = "{0}  {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $msg
  Write-Host $line
  Add-Content -Path $LogFile -Value $line
}

function Sha256Hex([string]$s) {
  $sha   = [System.Security.Cryptography.SHA256]::Create()
  $bytes = $sha.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($s))
  ($bytes | ForEach-Object { $_.ToString("x2") }) -join ""
}

function Apply($ch, [bool]$enable) {
  $body = @{
    uid         = $ch.uid
    enable      = $enable
    "stream-no" = $ch."stream-no"
    name        = $ch.name
    url         = $ch.url
  } | ConvertTo-Json -Compress
  Invoke-RestMethod -Uri "$Base/rx/live-apply" -Method Post -Body $body `
    -ContentType "application/json" -WebSession $Session | Out-Null
}

try {
  $Base = "http://$Device/api"

  # --- Log in (cookie jar carries the sid automatically) ---
  $loginBody = @{ username = $Username; password = (Sha256Hex $Password) } | ConvertTo-Json -Compress
  $login = Invoke-RestMethod -Uri "$Base/user/login" -Method Post -Body $loginBody `
             -ContentType "application/json" -SessionVariable Session
  if ($login.status -ne 0) { throw "Login failed (status $($login.status)) - check username/password." }

  # --- OFF ---
  foreach ($ch in $Channels) { Apply $ch $false }
  Log ("OFF : " + (($Channels | ForEach-Object { $_.name }) -join ", "))

  Start-Sleep -Seconds $OffOnGap

  # --- ON ---
  foreach ($ch in $Channels) { Apply $ch $true }
  Log ("ON  : " + (($Channels | ForEach-Object { $_.name }) -join ", ") + "  -- recycle complete")
}
catch {
  Log ("ERROR: " + $_.Exception.Message)
  exit 1
}
