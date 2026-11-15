# Run by user once to enable automatic iClone watcher startup (UAC required).
$ErrorActionPreference = 'Stop'
$src = Join-Path $PSScriptRoot 'openplugin\main.py'
$destDir = 'C:\Program Files\Reallusion\iClone 8\Bin64\OpenPlugin\iCloneStoryBridge'
$dest = Join-Path $destDir 'main.py'
$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host 'Requesting Windows administrator approval to install the iClone startup bridge...'
    Start-Process -FilePath 'powershell.exe' -Verb RunAs -Wait -ArgumentList @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', ('"' + $PSCommandPath + '"'))
    exit $LASTEXITCODE
}
if (-not (Test-Path -LiteralPath $src)) { throw 'Missing source: openplugin\main.py' }
if (Test-Path -LiteralPath $dest) {
    $a = (Get-FileHash -LiteralPath $src -Algorithm SHA256).Hash
    $b = (Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash
    if ($a -eq $b) { Write-Host 'Already installed; no change needed.'; exit 0 }
    throw "Another version already exists at $dest; refusing to overwrite."
}
New-Item -ItemType Directory -Path $destDir -Force | Out-Null
Copy-Item -LiteralPath $src -Destination $dest -ErrorAction Stop
if ((Get-FileHash $src).Hash -ne (Get-FileHash $dest).Hash) { throw 'Copy verification failed' }
Write-Host "Installed: $dest"
Write-Host 'It will load on the next normal iClone launch, if the queue is empty.'
