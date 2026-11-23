# ic8_watch.ps1 : answers iClone popups by rule (scripts/ic8_dialogs.json), user 2026-11-21.
#   powershell -File scripts\ic8_watch.ps1            run until iClone closes (ic8_part.py starts it once)
#   powershell -File scripts\ic8_watch.ps1 -Once      one pass, then exit
#   powershell -File scripts\ic8_watch.ps1 -Textures   OCR the iClone window, print 'TEXLOAD <n>' (0 = no 'Texture Loading' label)
#   powershell -File scripts\ic8_watch.ps1 -Test x.png  OCR a saved screenshot, print text + matched rule (no clicks)
# Each pass: every small visible iClone window -> text by UIA; if UIA gives nothing, screenshot it and run
# Windows OCR. Text matches a rule -> press the button (UIA Invoke, else click the OCR'd word). No rule -> save
# png + txt to ic8_jobs/dialogs/ once and leave it (log: ic8_jobs/dialogs/watch.log).
param([switch]$Once, [string]$Test, [switch]$Textures)
$ErrorActionPreference = 'Continue'
Add-Type -AssemblyName UIAutomationClient, System.Drawing, System.Runtime.WindowsRuntime
Add-Type -Namespace W -Name U -MemberDefinition @'
public delegate bool EnumProc(IntPtr h,IntPtr l);
[DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc e,IntPtr l);
[DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr w,out uint p);
[DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
[DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h,out RECT r);
[DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
[DllImport("user32.dll")] public static extern bool SetCursorPos(int x,int y);
[DllImport("user32.dll")] public static extern void mouse_event(int f,int x,int y,int d,int e);
[DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
public struct RECT{public int L,T,R,B;}
'@
[W.U]::SetProcessDPIAware() | Out-Null
$ROOT = Split-Path $PSScriptRoot
$OUT = Join-Path $env:LOCALAPPDATA 'Tidmunz Studio\snapgen_data\ic8_jobs\dialogs'
New-Item -ItemType Directory -Force $OUT | Out-Null
$RULES = (Get-Content (Join-Path $PSScriptRoot 'ic8_dialogs.json') -Raw -Encoding UTF8 | ConvertFrom-Json).rules
function Log($s) { $l = "{0:HH:mm:ss} {1}" -f (Get-Date), $s; Add-Content (Join-Path $OUT 'watch.log') $l -Encoding UTF8; Write-Output $l }

# ---- Windows OCR (built in, English) ----
$null = [Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType = WindowsRuntime]
$null = [Windows.Graphics.Imaging.BitmapDecoder, Windows.Foundation, ContentType = WindowsRuntime]
$null = [Windows.Storage.StorageFile, Windows.Storage, ContentType = WindowsRuntime]
$asTask = ([System.WindowsRuntimeSystemExtensions].GetMethods() | ? { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0]
function Await($op, $t) { $k = $asTask.MakeGenericMethod($t).Invoke($null, @($op)); $k.Wait(-1) | Out-Null; $k.Result }
$null = [Windows.Globalization.Language, Windows.Globalization, ContentType = WindowsRuntime]
$ENG = $null; try { $ENG = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage([Windows.Globalization.Language]::new('en-US')) } catch {}
if (-not $ENG) { $ENG = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages() }
function Ocr([string]$png) {   # -> @{text=...; words=@(@{t;x;y}...)} in image pixels
  # 3x upscale first: short button words ("OK", "No") are missed at screen size
  $src = [Drawing.Image]::FromFile($png); $big = New-Object Drawing.Bitmap ($src.Width * 3), ($src.Height * 3); $g = [Drawing.Graphics]::FromImage($big)
  $g.InterpolationMode = 'HighQualityBicubic'; $g.DrawImage($src, 0, 0, $big.Width, $big.Height); $g.Dispose(); $src.Dispose()
  $up = $png -replace '\.png$', '_x3.png'; $big.Save($up); $big.Dispose()
  $f = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync($up)) ([Windows.Storage.StorageFile])
  $s = Await ($f.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
  $d = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($s)) ([Windows.Graphics.Imaging.BitmapDecoder])
  $b = Await ($d.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
  $r = Await ($ENG.RecognizeAsync($b)) ([Windows.Media.Ocr.OcrResult]); $s.Dispose()
  Remove-Item $up -ErrorAction SilentlyContinue
  $w = foreach ($ln in $r.Lines) { foreach ($x in $ln.Words) { @{ t = $x.Text; x = ($x.BoundingRect.X + $x.BoundingRect.Width / 2) / 3; y = ($x.BoundingRect.Y + $x.BoundingRect.Height / 2) / 3 } } }
  @{ text = (($r.Lines | % { $_.Text }) -join "`n"); words = @($w) }
}
function Same($a, $b) { ($a -replace "0", "O").Trim(".,:") -ieq ($b -replace "0", "O") }
function Rule([string]$text) { foreach ($r in $RULES) { if ($text -match "(?is)$($r.match)") { return $r } }; $null }

if ($Test) { $o = Ocr (Resolve-Path $Test).Path; "OCR:`n$($o.text)"; $r = Rule $o.text
  "RULE: " + $(if ($r) { "press '$($r.press)'" } else { 'none' })
  if ($r) { $w = $o.words | ? { (Same $_.t ($r.press -split ' ')[0]) } | select -Last 1; "BUTTON: " + $(if ($w) { "found at {0:N0},{1:N0}" -f $w.x, $w.y } else { 'not found by OCR' }) }
  exit 0 }

if ($Textures) {   # the viewport label "Texture Loading: 1631" is drawn by OpenGL (no UIA): read it with OCR
  $p = Get-Process iClone -ErrorAction SilentlyContinue | select -First 1; if (-not $p) { 'TEXLOAD 0'; exit 0 }
  $r = New-Object W.U+RECT; [void][W.U]::GetWindowRect($p.MainWindowHandle, [ref]$r)
  $png = Join-Path $OUT 'tex.png'; $bmp = New-Object Drawing.Bitmap ($r.R - $r.L), ($r.B - $r.T); $g = [Drawing.Graphics]::FromImage($bmp)
  $g.CopyFromScreen($r.L, $r.T, 0, 0, $bmp.Size); $bmp.Save($png); $g.Dispose(); $bmp.Dispose()
  $t = (Ocr $png).text
  if ($t -match '(?i)Texture\s*Load\w*\W*([0-9OoIl]+)') { 'TEXLOAD ' + (($Matches[1] -replace '[Oo]', '0') -replace '[Il]', '1') } elseif ($t -match '(?i)Texture\s*Load') { 'TEXLOAD 1' } else { 'TEXLOAD 0' }
  exit 0 }

function Windows {   # small visible top-level windows of iClone (popups), not the main window
  $p = Get-Process iClone -ErrorAction SilentlyContinue | select -First 1; if (-not $p) { return }
  $script:pid2 = [uint32]$p.Id; $script:hw = New-Object 'System.Collections.Generic.List[System.IntPtr]'
  $cb = [W.U+EnumProc]{ param($h, $l); [uint32]$q = 0; [void][W.U]::GetWindowThreadProcessId($h, [ref]$q); if ($q -eq $script:pid2 -and [W.U]::IsWindowVisible($h)) { $script:hw.Add($h) }; $true }
  [void][W.U]::EnumWindows($cb, [IntPtr]::Zero)
  foreach ($h in $script:hw) { $r = New-Object W.U+RECT; [void][W.U]::GetWindowRect($h, [ref]$r); $wd = $r.R - $r.L; $ht = $r.B - $r.T
    if ($h -ne $p.MainWindowHandle -and $wd -gt 150 -and $ht -gt 80 -and $wd -lt 1300 -and $ht -lt 1000) { @{ h = $h; r = $r } } }
}
function SaveRoot { try { (Get-Content (Join-Path $env:LOCALAPPDATA 'Tidmunz Studio\snapgen_data\ic8_jobs\paths.json') -Raw -Encoding UTF8 | ConvertFrom-Json).SAVE } catch { Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'iClone Story Save' } }   # this PC's {SAVE} (scripts/paths.py)
function Fresh([int]$sec) {   # the open project was written < sec seconds ago
  $t = (Get-Process iClone).MainWindowTitle; if ($t -notmatch 'iClone 8 - (.+?)( \*)?$') { return $false }
  $f = Get-ChildItem (SaveRoot) -Recurse -Filter $Matches[1] -ErrorAction SilentlyContinue | sort LastWriteTime -Desc | select -First 1
  $f -and ((Get-Date) - $f.LastWriteTime).TotalSeconds -lt $sec
}
$seen = @{}
function Pass {
  foreach ($d in (Windows)) {
    $A = [Windows.Automation.AutomationElement]; $el = $null; $txt = ''
    try { $el = $A::FromHandle($d.h); $txt = ($el.FindAll('Descendants', [Windows.Automation.Condition]::TrueCondition) | % { $_.Current.Name } | ? { $_ }) -join "`n" } catch {}
    $words = @()
    $png = Join-Path $OUT ("dlg_{0:yyyyMMdd_HHmmss}.png" -f (Get-Date))
    if ($txt.Trim().Length -lt 10) {   # UIA gave nothing useful: screenshot + OCR
      $r = $d.r; $bmp = New-Object Drawing.Bitmap ($r.R - $r.L), ($r.B - $r.T); $g = [Drawing.Graphics]::FromImage($bmp)
      $g.CopyFromScreen($r.L, $r.T, 0, 0, $bmp.Size); $bmp.Save($png); $g.Dispose(); $bmp.Dispose()
      $o = Ocr $png; $txt = $o.text; $words = $o.words
    }
    $rule = Rule $txt
    if (-not $rule) {
      $key = ($txt -replace '\s+', ' ').Trim(); if ($key -and -not $seen[$key]) { $seen[$key] = 1
        if (-not (Test-Path $png)) { $r = $d.r; $bmp = New-Object Drawing.Bitmap ($r.R - $r.L), ($r.B - $r.T); $g = [Drawing.Graphics]::FromImage($bmp); $g.CopyFromScreen($r.L, $r.T, 0, 0, $bmp.Size); $bmp.Save($png); $g.Dispose(); $bmp.Dispose() }
        Set-Content ($png -replace '\.png$', '.txt') $txt -Encoding UTF8; Log "UNKNOWN popup (left alone, add a rule): $key  -> $png" }
      continue }
    if (-not $rule.press) { continue }
    if ($rule.fresh_save_s -and -not (Fresh $rule.fresh_save_s)) { Log "rule '$($rule.match)' needs a save < $($rule.fresh_save_s) s: NOT pressing $($rule.press)"; continue }
    $done = $false
    if ($el) { $b = $el.FindAll('Descendants', (New-Object Windows.Automation.PropertyCondition($A::ControlTypeProperty, [Windows.Automation.ControlType]::Button))) | ? { $_.Current.Name.Trim() -eq $rule.press } | select -First 1
      if ($b) { try { $b.GetCurrentPattern([Windows.Automation.InvokePattern]::Pattern).Invoke(); $done = $true } catch {
          $q = $b.Current.BoundingRectangle; [W.U]::SetForegroundWindow($d.h) | Out-Null; [W.U]::SetCursorPos($q.X + $q.Width / 2, $q.Y + $q.Height / 2) | Out-Null; Start-Sleep -m 100; [W.U]::mouse_event(2, 0, 0, 0, 0); [W.U]::mouse_event(4, 0, 0, 0, 0); $done = $true } } }
    if (-not $done) {   # click the OCR'd button word
      if (-not $words) { $r = $d.r; $bmp = New-Object Drawing.Bitmap ($r.R - $r.L), ($r.B - $r.T); $g = [Drawing.Graphics]::FromImage($bmp); $g.CopyFromScreen($r.L, $r.T, 0, 0, $bmp.Size); $bmp.Save($png); $g.Dispose(); $bmp.Dispose(); $words = (Ocr $png).words }
      $first = ($rule.press -split ' ')[0]; $w = $words | ? { (Same $_.t $first) } | select -Last 1
      if ($w) { [W.U]::SetForegroundWindow($d.h) | Out-Null; [W.U]::SetCursorPos($d.r.L + $w.x, $d.r.T + $w.y) | Out-Null; Start-Sleep -m 100; [W.U]::mouse_event(2, 0, 0, 0, 0); [W.U]::mouse_event(4, 0, 0, 0, 0); $done = $true } }
    Log $(if ($done) { "pressed '$($rule.press)' for: $(($txt -replace '\s+',' ').Substring(0,[Math]::Min(90,($txt -replace '\s+',' ').Length)))" } else { "rule matched but no '$($rule.press)' button found" })
  }
}
if ($Once) { Pass; exit 0 }
while (Get-Process iClone -ErrorAction SilentlyContinue) { Pass; Start-Sleep -Milliseconds 1500 }
