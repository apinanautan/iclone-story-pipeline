# install.ps1 - set up Toyxyz Motion AI (Kimodo) on this PC so tools/motion_ai/drive_gen.py can run. Safe to re-run.
# Needs: NVIDIA GPU, ~20 GB free on C:, Blender 5.2+, gh (GitHub CLI) logged in.
# Downloads from the official repo https://github.com/toyxyz/toyxyz-motion-ai-tool (add-on = latest release,
# companion = newest "windows-companion-*" release), checks SHA256, extracts to C:\MotionAI.
# The companion's install.cmd asks which models to install: choose Kimodo and the text encoder it requests.
$ErrorActionPreference = 'Stop'
$Root = 'C:\MotionAI'; $Dl = "$Root\_dl"; $Repo = 'toyxyz/toyxyz-motion-ai-tool'
New-Item -ItemType Directory -Force $Dl | Out-Null

$blender = Get-ChildItem 'C:\Program Files\Blender Foundation\Blender 5.*\blender.exe' -EA SilentlyContinue | Sort-Object FullName | Select-Object -Last 1
if (-not $blender) { throw 'Blender 5.2+ not found. Install it from blender.org first (winget install BlenderFoundation.Blender).' }
"Blender: $($blender.FullName)"

$addon = gh release download -R $Repo -p '*-blender-addon.zip' -p 'SHA256SUMS.txt' -D "$Dl\addon" --clobber 2>&1
$comp = (gh release list -R $Repo -L 20 --json tagName -q '.[].tagName' | Where-Object { $_ -like 'windows-companion-*' } | Select-Object -First 1)
gh release download $comp -R $Repo -p 'MotionAI_Windows_Companion-*.zip' -p 'SHA256SUMS.txt' -D "$Dl\companion" --clobber

foreach ($d in "$Dl\addon", "$Dl\companion") {           # verify every downloaded zip against its SHA256SUMS
    $sums = Get-Content "$d\SHA256SUMS.txt"
    foreach ($z in Get-ChildItem "$d\*.zip") {
        $want = ($sums | Where-Object { $_ -match [regex]::Escape($z.Name) }) -replace '\s.*'
        if ((Get-FileHash $z.FullName -Algorithm SHA256).Hash -ne $want.ToUpper()) { throw "SHA256 mismatch: $($z.Name)" }
    }
}
Copy-Item "$Dl\addon\*-blender-addon.zip" $Dl -Force    # drive_gen.py installs the newest add-on zip into Blender

$cz = Get-ChildItem "$Dl\companion\MotionAI_Windows_Companion-*.zip" | Select-Object -First 1
$cdir = Join-Path $Root $cz.BaseName
if (-not (Test-Path "$cdir\install.cmd")) { Expand-Archive $cz.FullName $Root -Force }
if (-not (Test-Path "$cdir\engines\*")) {
    "Running companion installer (choose Kimodo + the text encoder; several GB download)..."
    Start-Process -FilePath "$cdir\install.cmd" -WorkingDirectory $cdir -Wait
}
"READY companion=$cdir blender=$($blender.FullName)"
"Generate: set C:\MotionAI\gen.json then run: & '$($blender.FullName)' --factory-startup --python tools\motion_ai\drive_gen.py"
