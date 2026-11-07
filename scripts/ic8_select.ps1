# Select one avatar in iClone (via the watcher) and go to frame 0.  Usage: ic8_select.ps1 p2_old
param([string]$name)
$D = "$env:LOCALAPPDATA\Tidmunz Studio\snapgen_data\ic8_jobs"
@"
import RLPy
RLPy.RScene.ClearSelectObjects()
RLPy.RScene.SelectObject([a for a in RLPy.RScene.GetAvatars() if a.GetName() == '$name'][0])
RLPy.RGlobal.SetTime(RLPy.RTime.FromValue(0))
"@ | Set-Content "$D\run\sel.py" -Encoding utf8
for ($i = 0; $i -lt 20 -and (Test-Path "$D\run\sel.py"); $i++) { Start-Sleep -Milliseconds 500 }
