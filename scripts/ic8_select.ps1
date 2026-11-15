# Select one avatar in iClone (via the watcher) and go to frame 0.  Usage: ic8_select.ps1 p2_old
param([string]$name)
$D = "$env:LOCALAPPDATA\Tidmunz Studio\snapgen_data\ic8_jobs"
@"
import RLPy
RLPy.RScene.ClearSelectObjects()
RLPy.RScene.SelectObject([a for a in RLPy.RScene.GetAvatars() if a.GetName() == '$name'][0])
RLPy.RGlobal.SetTime(RLPy.RTime.FromValue(0))
"@ | ForEach-Object { [IO.File]::WriteAllText("$D\run\sel.py", $_, (New-Object Text.UTF8Encoding $false)) }  # no BOM (a BOM broke the watcher: SyntaxError)
for ($i = 0; $i -lt 20 -and (Test-Path "$D\run\sel.py"); $i++) { Start-Sleep -Milliseconds 500 }
