# ─────────────────────────────────────────────────
# MODIFICĂ ACEASTĂ LINIE cu calea către folderul tău
$repoPath = "D:\TOPOGRAFIE - CADASTRU\%  SUPORT\VERIFICARI\VALCEA\Conducte-GAZE"
# ─────────────────────────────────────────────────

$gitExe   = "git"
$logFile  = Join-Path $repoPath "auto-push.log"
$watched  = "Conducte-GAZE.geojson"

function Write-Log($msg) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp  $msg" | Out-File -FilePath $logFile -Append -Encoding UTF8
}

Write-Log "=== Auto-push pornit. Monitorizez: $watched ==="

$watcher                     = New-Object System.IO.FileSystemWatcher
$watcher.Path                = $repoPath
$watcher.Filter              = $watched
$watcher.NotifyFilter        = [System.IO.NotifyFilters]::LastWrite
$watcher.EnableRaisingEvents = $true

$action = {
    # Asteapta 4 secunde sa termine QGIS scrierea
    Start-Sleep -Seconds 4

    $repo = $Event.MessageData
    $log  = Join-Path $repo "auto-push.log"
    $ts   = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

    try {
        Set-Location $repo

        & git add "Conducte-GAZE.geojson" 2>&1 | Out-Null

        $status = & git status --porcelain 2>&1
        if (-not $status) {
            "$ts  Nicio modificare de commit." | Out-File $log -Append -Encoding UTF8
            return
        }

        $commitMsg = "Auto-update $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
        & git commit -m $commitMsg 2>&1 | Out-Null
        & git push   2>&1 | Out-Null

        "$ts  Push reusit: $commitMsg" | Out-File $log -Append -Encoding UTF8
    } catch {
        "$ts  EROARE: $_" | Out-File $log -Append -Encoding UTF8
    }
}

Register-ObjectEvent $watcher Changed -Action $action -MessageData $repoPath | Out-Null

Write-Log "Astept modificari..."

# Tine scriptul activ
while ($true) { Start-Sleep -Seconds 30 }
