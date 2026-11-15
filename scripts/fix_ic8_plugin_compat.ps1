# Stop iClone's "<plugin> Python plugin is not compatible with this version of iClone" popup.
# iClone shows it when an OpenPlugin main.py has no rl_plugin_info. Adds the line (with a .bak backup).
# Default plugin = iCloneStoryBridge (the watcher auto-loader: never delete it). Needs admin (UAC), re-launches itself elevated.
param([string]$Plugin = 'iCloneStoryBridge')
$main = "C:\Program Files\Reallusion\iClone 8\Bin64\OpenPlugin\$Plugin\main.py"
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Start-Process powershell -Verb RunAs -Wait -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`" -Plugin `"$Plugin`""
    if ((Get-Content $main -Raw -Encoding UTF8) -match 'rl_plugin_info') { "FIXED: $main" } else { "NOT FIXED (UAC declined?): $main" }
    exit
}
$s = Get-Content $main -Raw -Encoding UTF8
if ($s -match 'rl_plugin_info') { "already has rl_plugin_info"; exit }
Copy-Item $main "$main.bak" -Force
$s = $s -replace "import traceback\r?\n", "import traceback`r`n`r`nrl_plugin_info = { `"ap`": `"iClone`", `"ap_version`": `"8.0`" }`r`n"
[IO.File]::WriteAllText($main, $s, (New-Object Text.UTF8Encoding $false))
