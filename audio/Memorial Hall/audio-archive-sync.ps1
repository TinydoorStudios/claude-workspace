# audio-archive-sync.ps1
# Reaper PC nightly archive sync
# Schedule: Windows Task Scheduler, nightly at 2:00 AM

$source        = "A:\2026"
$dest          = "Z:\"
$logDir        = "Z:\sync-logs"
$today         = Get-Date -Format "yyyy-MM-dd"
$logFile       = "$logDir\sync-$today.txt"
$copyAgeDays   = 3
$deleteAgeDays = 5

if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir | Out-Null
}

$copiedFolders    = [System.Collections.Generic.List[string]]::new()
$deletedFolders   = [System.Collections.Generic.List[string]]::new()
$errors           = [System.Collections.Generic.List[string]]::new()
$totalBytesCopied = 0
$now              = Get-Date
$folders          = Get-ChildItem -Path $source -Directory -ErrorAction Stop

foreach ($folder in $folders) {
    $ageDays    = ($now - $folder.CreationTime).TotalDays
    $destFolder = Join-Path $dest $folder.Name

    if ($ageDays -lt $copyAgeDays -and -not (Test-Path $destFolder)) {
        try {
            $bytes = (Get-ChildItem $folder.FullName -Recurse -File | Measure-Object -Property Length -Sum).Sum
            Copy-Item -Path $folder.FullName -Destination $destFolder -Recurse -Force
            $mb = [math]::Round($bytes / 1MB, 2)
            $copiedFolders.Add("  $($folder.Name)  ($mb MB)")
            $totalBytesCopied += $bytes
        } catch {
            $errors.Add("  COPY ERROR: $($folder.Name) - $($_.Exception.Message)")
        }
    }

    if ($ageDays -gt $deleteAgeDays) {
        try {
            Remove-Item -Path $folder.FullName -Recurse -Force
            $deletedFolders.Add("  $($folder.Name)")
        } catch {
            $errors.Add("  DELETE ERROR: $($folder.Name) - $($_.Exception.Message)")
        }
    }
}

$totalMB = [math]::Round($totalBytesCopied / 1MB, 2)
$totalGB = [math]::Round($totalBytesCopied / 1GB, 3)

$lines = [System.Collections.Generic.List[string]]::new()
$lines.Add("Audio Archive Sync Report - $today")
$lines.Add("==================================================")
$lines.Add("")
$lines.Add("COPIED TO NAS  ($($copiedFolders.Count) folder(s), $totalMB MB / $totalGB GB)")
$lines.Add("--------------------------------------------------")
if ($copiedFolders.Count -eq 0) { $lines.Add("  (none)") } else { foreach ($f in $copiedFolders) { $lines.Add($f) } }
$lines.Add("")
$lines.Add("DELETED FROM PC  ($($deletedFolders.Count) folder(s))")
$lines.Add("--------------------------------------------------")
if ($deletedFolders.Count -eq 0) { $lines.Add("  (none)") } else { foreach ($f in $deletedFolders) { $lines.Add($f) } }
if ($errors.Count -gt 0) {
    $lines.Add("")
    $lines.Add("ERRORS")
    $lines.Add("--------------------------------------------------")
    foreach ($e in $errors) { $lines.Add($e) }
}
$lines.Add("")
$lines.Add("Run completed: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')")

$lines | Out-File -FilePath $logFile -Encoding UTF8

Write-Host "Sync complete. Log written to $logFile"
