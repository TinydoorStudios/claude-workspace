# launch-order.ps1
# Auto-start audio chain in fixed order with 60s between each.
# Order matters: Dante Virtual Soundcard (audio driver) must be up
# before VB-Audio Matrix (routing), which must be up before Smaart (analyzer).

$delay = 60

$programs = @(
    "C:\Program Files\Audinate\Dante Virtual Soundcard\dvs_gui.exe",
    "C:\Program Files (x86)\VB\VBAudioMatrix\VBAudioMatrix_x64.exe",
    "C:\Program Files (x86)\Smaart 8\Smaart.exe"
)

for ($i = 0; $i -lt $programs.Count; $i++) {
    $exe = $programs[$i]
    if (Test-Path $exe) {
        Start-Process -FilePath $exe
    } else {
        # Path missing - log it but keep going so the rest still boot.
        $log = Join-Path $env:LOCALAPPDATA "launch-order.log"
        "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')  MISSING: $exe" | Out-File -FilePath $log -Append
    }
    # Wait after every launch except the last one.
    if ($i -lt $programs.Count - 1) {
        Start-Sleep -Seconds $delay
    }
}
