<#
ic8_gui.ps1 - helper for non-save iClone GUI chores.
Every command checks its own result and prints OK/FAIL lines. Run with:
  powershell -NoProfile -ExecutionPolicy Bypass -File scripts\ic8_gui.ps1 <command> [args]

  shot                         DPI-correct screenshot of the iClone screen -> ic8_jobs\gui_shot.png (+ timeline crop gui_tl.png)
  job <file.py>                run a Python file through the watcher, print its .log (refuses RFileIO.SaveProject)
  open <full .iProject path>   Ctrl+O, fill the dialog, wait until loaded
  reopen                       open the current project again = proof the saved file loads
  switch                       viewport camera dropdown -> Switch
  tozero                       stop, deselect, playhead to frame 0, play range 0..project end
  sound <wav> [-Replace]       (-Replace: delete the current Project Sound clip first) Ctrl+I the wav at frame 0
  lip <avatar> <wav> <s> <e>   AccuLips: select avatar, Animation > Create Script > Audio File <wav>, keep visemes s..e only
  render <out.mp4> <end> <wav> [-Publish <folder>] [-Shots "t1,t2,.."]
                               render 0..end 1080p60 (Switch), mux clean wav, check fps/len/volume, frame per shot, raw -> Recycle Bin
Project saving is intentionally disabled here. Use iClone's visible File > Save Project / Save Project As menu manually.
#>
param([Parameter(Position=0)][string]$Cmd='shot',[Parameter(Position=1)][string]$A1,[Parameter(Position=2)][string]$A2,
      [Parameter(Position=3)][string]$A3,[Parameter(Position=4)][string]$A4,[switch]$Replace,[switch]$Discard,[string]$Publish,[string]$Shots,[int]$Width=1920,[int]$Height=1080)
$ErrorActionPreference='Stop'
$J   = Join-Path $env:LOCALAPPDATA 'Tidmunz Studio\snapgen_data\ic8_jobs'
$RUN = Join-Path $J 'run'
$SCR = $PSScriptRoot
$FF  = if ($env:IC8_FF) { $env:IC8_FF } else { (& py -3 (Join-Path $PSScriptRoot 'paths.py') ffmpeg) }   # found on any PC (paths.py), no one-PC path
$FFP = if ($env:IC8_FFP) { $env:IC8_FFP } else { (& py -3 (Join-Path $PSScriptRoot 'paths.py') ffprobe) }

Add-Type -AssemblyName System.Windows.Forms,System.Drawing,UIAutomationClient,UIAutomationTypes,Microsoft.VisualBasic
Add-Type -Path (Join-Path $PSScriptRoot 'IG.Win32.dll')
[IG.U]::SetProcessDPIAware()|Out-Null

function Say($s){ Write-Output $s }
function Fail($s){ [Console]::Error.WriteLine("FAIL: $s"); exit 1 }
function Proc { $p=Get-Process iClone -ErrorAction SilentlyContinue|select -First 1; if(-not $p){Fail 'iClone is not running'}; $p }
function Title { (Get-Process iClone -ErrorAction SilentlyContinue|select -First 1).MainWindowTitle }
# the main window handle/rect are read ONCE: while a dropdown or popup is open, MainWindowHandle points at the popup
function MainH { if(-not $script:MH){ $script:MH=(Proc).MainWindowHandle }; $script:MH }
# bring iClone to the front and PROVE it: Windows may refuse SetForegroundWindow from a background script, and then
# keystrokes would go to another app. No mouse fallback; abort unless iClone is in front.
function FgIsIclone { [uint32]$p=0; [void][IG.U]::GetWindowThreadProcessId([IG.U]::GetForegroundWindow(),[ref]$p); $p -eq [uint32](Proc).Id }
# iClone warnings that only need OK (user 2026-11-21: "physics memory is insufficient ... proceed?" blocked
# everything for minutes). Answered here before every keyboard action.
# never scan the MAIN window: its UIA tree (timeline, scene list) takes minutes once a scene is loaded (2026-11-21)
function Nag { foreach($h in (IcloneWindows)){ if($h -eq (MainH)){continue}; try{ $w=[Windows.Automation.AutomationElement]::FromHandle($h); $t=($w.FindAll([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.Condition]::TrueCondition)|%{$_.Current.Name}) -join ' ' }catch{continue}
    if($t -match 'physics memory is insufficient|may not run smoothly'){ if(PressButton '^OK$'){ Say 'answered iClone warning: physics memory -> OK' } } } }
# 2026-11-22: the Preview window (progress_app.py, topmost) sits over iClone's top-left menu, so menu clicks hit
# Preview (AccuLips "file dialog did not appear"). Minimise it during menu clicks, restore after.
function PreviewWin([int]$cmd){ Get-Process | ?{ $_.MainWindowTitle -like 'Preview*' } | %{ [IG.U]::ShowWindow($_.MainWindowHandle,$cmd)|Out-Null } }
function Front { Nag; $h=MainH
  # Windows foreground lock: a tapped Alt lets a background process take the foreground (rules: Win32 Alt trick)
  for($i=0;$i -lt 5;$i++){ if($i -gt 0){ [IG.U]::keybd_event(0x12,0,0,0); [IG.U]::keybd_event(0x12,0,2,0); [IG.U]::ShowWindow($h,5)|Out-Null }
    if($i -gt 1){ # attach to the foreground thread (works even when the foreground is "Idle"/nothing; proven in ic_imp2.ps1)
      $ft=[IG.U]::ThreadOf([IG.U]::GetForegroundWindow(),[IntPtr]::Zero); $me=[IG.U]::GetCurrentThreadId(); $it=[IG.U]::ThreadOf($h,[IntPtr]::Zero)
      [IG.U]::AttachThreadInput($me,$it,$true)|Out-Null; if($ft){[IG.U]::AttachThreadInput($me,$ft,$true)|Out-Null}
      [IG.U]::BringWindowToTop($h)|Out-Null; [IG.U]::SetForegroundWindow($h)|Out-Null
      if($ft){[IG.U]::AttachThreadInput($me,$ft,$false)|Out-Null}; [IG.U]::AttachThreadInput($me,$it,$false)|Out-Null }
    [IG.U]::SetForegroundWindow($h)|Out-Null; Start-Sleep -Milliseconds 400; if(FgIsIclone){ return $h }
    }
  Fail 'could not bring iClone to the front; no keys were sent' }
function WinRect { if(-not $script:WR){ $r=New-Object IG.U+RECT; [IG.U]::GetWindowRect((MainH),[ref]$r)|Out-Null; $script:WR=$r }; $script:WR }
function Click([int]$x,[int]$y){ [IG.U]::SetCursorPos($x,$y)|Out-Null; Start-Sleep -Milliseconds 120; [IG.U]::mouse_event(2,0,0,0,0); [IG.U]::mouse_event(4,0,0,0,0); Start-Sleep -Milliseconds 300 }
# click at a point measured on the maximized iClone window (layout of this PC), relative to the window's top-left
function ClickRel([int]$rx,[int]$ry){ $r=WinRect; $x=$r.L+$rx; $y=$r.T+$ry; if($env:IC8_GUI_DEBUG){Say "click $x,$y"}; Click $x $y }
# Keyboard events in this helper are only for non-save chores. Project saving uses the manually clicked File menu.
function English { $h=MainH; $en=[IG.U]::LoadKeyboardLayout('00000409',1); [IG.U]::PostMessage($h,0x50,[IntPtr]::Zero,$en)|Out-Null; Start-Sleep -Milliseconds 300 }
function Keys([byte[]]$mods,[byte]$vk){ English; Front|Out-Null; if(-not (FgIsIclone)){Fail "iClone lost focus; key not sent"}; foreach($m in $mods){[IG.U]::keybd_event($m,0,0,0)}; [IG.U]::keybd_event($vk,0,0,0); [IG.U]::keybd_event($vk,0,2,0); [array]::Reverse($mods); foreach($m in $mods){[IG.U]::keybd_event($m,0,2,0)}; Start-Sleep -Milliseconds 300 }
$CTRL=0x11; $SHIFT=0x10

# Mutating GUI commands must be single-flight and pass live screen checks.
function WaitReady([switch]$NeedsWatcher){
  $pending=@(Get-ChildItem -LiteralPath $RUN -Filter '*.py' -File -ErrorAction SilentlyContinue)
  if($pending.Count){Fail ("pending iClone job; do not retry: "+($pending.Name -join ', '))}
  if($NeedsWatcher){
    $marker=Join-Path $RUN 'watcher.alive'
    if(-not (Test-Path $marker) -or (Get-Content $marker -Raw).Trim() -ne ("guard-v2:"+ (Proc).Id)){
      Fail 'reload updated scripts/ic8_watch.py via Script > Load Python before sending jobs'
    }
  }
  $check=Join-Path $SCR 'ic8_watch.ps1'
  $stdout=Join-Path $J 'guard_check.out'; $stderr=Join-Path $J 'guard_check.err'
  for($i=0;$i -lt 2;$i++){
    $probeArgs=@('-NoProfile','-ExecutionPolicy','Bypass','-File',('"' + $check + '"'),'-ReadyCheck')
    if($NeedsWatcher){$probeArgs+= '-BackgroundJob'}
    $probe=Start-Process -FilePath 'powershell.exe' -ArgumentList $probeArgs -NoNewWindow -PassThru -RedirectStandardOutput $stdout -RedirectStandardError $stderr
    if(-not $probe.WaitForExit(18000)){try{$probe.Kill()}catch{}; Fail 'screen readiness check timed out; no new command sent'}
    $msg=Get-Content $stdout -Raw -ErrorAction SilentlyContinue
    if(($null -ne $probe.ExitCode -and $probe.ExitCode -ne 0) -or $msg -notmatch '(?m)^GUARD_READY\s*$'){Fail ("screen not ready; no new command sent: "+$msg)}
    Start-Sleep -Milliseconds 400
  }
  if(@(Get-ChildItem -LiteralPath $RUN -Filter '*.py' -File -ErrorAction SilentlyContinue).Count -or -not (Proc).Responding){Fail 'iClone changed state after screen check'}
}
function PublishJob([string]$f,[string]$code){
  if(Test-Path -LiteralPath $f){Fail "job already pending: $f"}
  $tmp=$f+'.'+$PID+'.tmp'
  [IO.File]::WriteAllText($tmp,$code,(New-Object Text.UTF8Encoding $false))
  [IO.File]::Move($tmp,$f)
}
function Job([string]$code,[string]$name='zz_gui',[int]$wait=300){
  if($code -match 'SaveProject\s*\('){ Fail 'refusing: RFileIO.SaveProject (script saves corrupt projects; save via GUI)' }
  WaitReady -NeedsWatcher
  $f=Join-Path $RUN "$name.py"; foreach($x in 'done','log','err'){Remove-Item "$f.$x","$RUN\$name.$x" -ErrorAction SilentlyContinue}
  PublishJob $f $code
  for($i=0;$i -lt $wait*2 -and (Test-Path $f);$i++){Start-Sleep -Milliseconds 500}
  if(Test-Path $f){ Fail "watcher did not run $name.py in 5 min (watcher stopped? look at the screen: gui shot)" }
  if(Test-Path (Join-Path $RUN "$name.err")){ Fail ("watcher job failed: "+(Get-Content (Join-Path $RUN "$name.log") -Raw -ErrorAction SilentlyContinue)) }
  if(-not (Test-Path (Join-Path $RUN "$name.done"))){Fail "watcher job has no completion marker: $name"}
  $log=Join-Path $RUN "$name.log"; if(Test-Path $log){ Get-Content $log -Raw -Encoding UTF8 } else { '' }
}
function Py([string]$body){ "import RLPy,os`nJ=os.path.join(os.environ['LOCALAPPDATA'],'Tidmunz Studio','snapgen_data','ic8_jobs')`nT=lambda s:RLPy.RTime.FromValue(int(round(s*6000)))`n$body`n" }

# fill the Win32 file dialog (Open / Save As / Import): WM_SETTEXT into the name box, then click Open/Save
function FillDialog([string]$path){
  for($i=0;$i -lt 120;$i++){ $dlg=Dialogs|?{ $_.FindFirst([Windows.Automation.TreeScope]::Descendants,(New-Object Windows.Automation.PropertyCondition([Windows.Automation.AutomationElement]::ClassNameProperty,"Edit"))) }|select -First 1; if($dlg){break}; Start-Sleep -Milliseconds 500 }
  if(-not $dlg){ Fail 'file dialog did not appear' }
  $all=$dlg.FindAll([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.Condition]::TrueCondition)
  $e=$all|?{$_.Current.ClassName -eq 'Edit'}|select -First 1
  [IG.U]::SendMessage([IntPtr]$e.Current.NativeWindowHandle,0x000C,[IntPtr]::Zero,$path)|Out-Null
  $b=$all|?{$_.Current.ClassName -eq 'Button' -and $_.Current.Name -match '^(&?Open|&?Save|เปิด|บันทึก)'}|select -First 1
  [IG.U]::PostMessage([IntPtr]$b.Current.NativeWindowHandle,0x00F5,[IntPtr]::Zero,[IntPtr]::Zero)|Out-Null
  Start-Sleep -Milliseconds 1000
  # "already exists, replace?" confirmation (a second, small #32770)
  foreach($d in @(Dialogs)){ $y=$d.FindAll([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.Condition]::TrueCondition)|?{$_.Current.ClassName -eq 'Button' -and $_.Current.Name -match '^(&?Yes|ใช่)'}|select -First 1
    if($y){ [IG.U]::PostMessage([IntPtr]$y.Current.NativeWindowHandle,0x00F5,[IntPtr]::Zero,[IntPtr]::Zero)|Out-Null; Say 'confirmed overwrite' } }
}
# visible Win32 dialogs (#32770) of iClone.exe, found with EnumWindows (a desktop-wide UIA search takes minutes)
function Dialogs { $A=[Windows.Automation.AutomationElement]
  foreach($h in (IcloneWindows)){ try{$w=$A::FromHandle($h)}catch{continue}; if($w.Current.ClassName -eq '#32770'){ $w } } }
function IcloneWindows { $script:pid2=[uint32](Proc).Id; $script:hw=New-Object 'System.Collections.Generic.List[System.IntPtr]'
  $cb=[IG.E+EnumProc]{ param($h,$l); [uint32]$p=0; [void][IG.E]::GetWindowThreadProcessId($h,[ref]$p); if($p -eq $script:pid2 -and [IG.E]::IsWindowVisible($h)){$script:hw.Add($h)}; $true }
  [void][IG.E]::EnumWindows($cb,[IntPtr]::Zero); $script:hw }
# press a button in a small iClone popup (Qt dialogs are only reachable via EnumWindows + UIA FromHandle)
# IG.Win32.dll already loaded above
function PressButton([string]$rx){
  $A=[Windows.Automation.AutomationElement]
  foreach($h in (IcloneWindows)){ try{$w=$A::FromHandle($h)}catch{continue}; $r=$w.Current.BoundingRectangle; if($r.Width -gt 1300 -or $r.Height -gt 1000){continue}
    $b=$w.FindAll([Windows.Automation.TreeScope]::Descendants,(New-Object Windows.Automation.PropertyCondition($A::ControlTypeProperty,[Windows.Automation.ControlType]::Button)))|?{$_.Current.Name.Trim() -match $rx}|select -First 1
    if($b){ try{$b.GetCurrentPattern([Windows.Automation.InvokePattern]::Pattern).Invoke()}catch{ $q=$b.Current.BoundingRectangle; Click ($q.X+$q.Width/2) ($q.Y+$q.Height/2) }; return $true } }
  $false
}
function SaveRoot { try { (Get-Content (Join-Path $env:LOCALAPPDATA 'Tidmunz Studio\snapgen_data\ic8_jobs\paths.json') -Raw -Encoding UTF8 | ConvertFrom-Json).SAVE } catch { Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'iClone Story Save' } }   # this PC's {SAVE} (scripts/paths.py)
function CurrentFile { $t=Title; if($t -match 'iClone 8 - (.+?)( \*)?$'){ $n=$Matches[1]; Get-ChildItem (SaveRoot) -Recurse -Filter $n -ErrorAction SilentlyContinue|sort LastWriteTime -Desc|select -First 1 } }
# user 2026-11-22: hidden timestamped backups in ic8_jobs\backup filled the disk (90+ GB). Now ONE visible copy
# NEXT TO the project in the save folder: <name>.backup.iProject = the project before the last save, overwritten
# each save. Old timestamped copies of this project in ic8_jobs\backup are deleted.
# a load/save shows iClone's progress window (CRLProgressDlg). Wait for it to come AND go, so "loaded" is real
# (the title alone already matches before a reopen of the same file starts).
function Busy { $A=[Windows.Automation.AutomationElement]; foreach($h in (IcloneWindows)){ try{ if($A::FromHandle($h).Current.ClassName -eq 'CRLProgressDlg'){ return $true } }catch{} }; $false }
function WaitLoaded([string]$name){
  $seen=$false; for($i=0;$i -lt 60;$i++){ if(Busy){$seen=$true;break}; Start-Sleep -Milliseconds 500 }
  if(-not $seen){ Say 'note: no progress window seen (small project?)' }
  for($i=0;$i -lt 600;$i++){ if(-not (Busy)){break}; Start-Sleep 1 }
  for($i=0;$i -lt 300;$i++){ $t=Title; if($t -match [regex]::Escape($name) -and $t -notmatch '\*$'){ break }; Start-Sleep 1 }
  Start-Sleep 3
  if((Busy) -or -not (Proc).Responding){Fail "project load still busy: $(Title)"}
  if((Title) -notmatch [regex]::Escape($name)){ Fail "project did not load: $(Title)" }
  Say "OK loaded: $(Title)"
}
function Shot { $s=[Windows.Forms.Screen]::AllScreens|?{$_.Bounds.X -le (WinRect).L+50 -and $_.Bounds.Right -gt (WinRect).L+50}|select -First 1
  if(-not $s){$s=[Windows.Forms.Screen]::PrimaryScreen}; $r=$s.Bounds; $bmp=New-Object Drawing.Bitmap $r.Width,$r.Height
  [Drawing.Graphics]::FromImage($bmp).CopyFromScreen($r.Location,[Drawing.Point]::Empty,$r.Size); $out=Join-Path $J 'gui_shot.png'; $bmp.Save($out)
  $w=WinRect; $tl=$bmp.Clone((New-Object Drawing.Rectangle 0,([Math]::Max(0,$w.T+840-$r.Y)),$r.Width,130),$bmp.PixelFormat); $tl.Save((Join-Path $J 'gui_tl.png'))
  Say "shot: $out (timeline crop gui_tl.png)" }

# Preview dispatch is required for mutating pipeline GUI commands.
# Read-only screenshots and manual File-menu saves remain separate.
if($Cmd -notin @('shot','save','saveas')){
  $lease=Join-Path (Split-Path $PSScriptRoot) 'progress\preview_lease.json'
  try {
    $grant=Get-Content -LiteralPath $lease -Raw -Encoding UTF8 | ConvertFrom-Json
    if(-not $env:AIICLONE_PREVIEW_TOKEN -or $grant.token -cne $env:AIICLONE_PREVIEW_TOKEN){throw 'no Preview permit'}
    if(-not (Get-Process -Id $grant.pid -ErrorAction SilentlyContinue)){throw 'Preview controller exited'}
    $allowed=@{open=@('open');cast=@('job');pose=@('job');sound=@('sound');lip=@('lip','job');cams=@('job');motion_check=@('job');face_check=@('job');switch=@('switch');ready=@('switch','tozero');render=@('render')}
    if($Cmd -notin $allowed[[string]$grant.step]){throw "command $Cmd not allowed in step $($grant.step)"}
  } catch { Fail ("Preview gate: "+$_.Exception.Message+"; use Ai-iclone do") }
}
$guardMutex=$null; $guardHeld=$false
try {
  if($Cmd -notin @('shot','press','save','saveas')){
    $guardMutex=New-Object Threading.Mutex($false,'Local\AiIcloneGuiSingleFlight')
    try{$guardHeld=$guardMutex.WaitOne(0)}catch [Threading.AbandonedMutexException]{$guardHeld=$true}
    if(-not $guardHeld){Fail 'another iClone command is running; no overlapping command sent'}
    if($Cmd -eq 'job'){WaitReady -NeedsWatcher}else{Front|Out-Null; WaitReady}
  }
switch($Cmd){
 'shot'   { Shot }
 'showsound' { $code=Py "from PySide2 import QtWidgets`napp=QtWidgets.QApplication.instance()`nmain=next(w for w in app.allWidgets() if w.objectName()=='iClone6 MainWindow')`nact=next(a for a in main.actions() if a.objectName()=='qtShowAllAudioTrackAction')`nact.trigger()"; Job $code 'zz_gui_showsound'|Out-Null; Shot|Out-Null; Say 'Shown all audio tracks: inspect gui_tl.png' }
 'press'  { if(PressButton $A1){ Say "OK pressed $A1" } else { $n=@(IcloneWindows).Count; Fail "no visible iClone popup has a button matching $A1 ($n iClone windows)" } }
 'job'    { Job (Get-Content $A1 -Raw -Encoding UTF8) ([IO.Path]::GetFileNameWithoutExtension($A1)) }
 # prop <file.fbx> <name> "x,y,z" "rx,ry,rz": load an FBX prop (clicks Convert All in Import Settings), rename, place in world space
 'prop'   { $p=$A3 -split ','; $r=$(if($A4){$A4 -split ','}else{0,0,0}); $n='zz_gui_prop'; $f=Join-Path $RUN "$n.py"
            foreach($x in 'done','log','err'){Remove-Item "$f.$x","$RUN\$n.$x" -ErrorAction SilentlyContinue}
            $code=Py ("import math`nold=set(o.GetName() for o in RLPy.RScene.FindObjects(RLPy.EObjectType_Prop))`nprint('load',RLPy.RFileIO.LoadFile(r'''$A1'''))`nnew=[o for o in RLPy.RScene.FindObjects(RLPy.EObjectType_Prop) if o.GetName() not in old]`n" +
              "for i,o in enumerate(new):`n  o.SetName('$A2' if i==0 else '$A2_%d'%i)`n  c=o.GetControl('Transform');t=RLPy.RTransform();c.GetValue(T(0),t)`n  t.T().x,t.T().y,t.T().z=$($p[0]),$($p[1]),$($p[2])`n" +
              "  m=RLPy.RMatrix3();m.FromEulerAngle(RLPy.EEulerOrder_XYZ,math.radians($($r[0])),math.radians($($r[1])),math.radians($($r[2])));q=RLPy.RQuaternion();q.FromRotationMatrix(m)`n  t.R().x,t.R().y,t.R().z,t.R().w=q.x,q.y,q.z,q.w`n  c.ClearKeys();c.SetValue(T(0),t)`nprint('props',[o.GetName() for o in new])")
            WaitReady -NeedsWatcher; PublishJob $f $code
            $log=Join-Path $RUN "$n.log"; $pressed=$false
            for($i=0;$i -lt 240 -and -not (Test-Path $log);$i++){ Start-Sleep -Milliseconds 500; if(-not $pressed -and (PressButton '^Convert All$')){ $pressed=$true; Say 'pressed Convert All' } }
            if(-not (Test-Path $log)){ Fail "prop load did not finish in 2 min (dialog on the other screen? gui shot)" }
            $t=Get-Content $log -Raw -Encoding UTF8; $t; if($t -notmatch "props \['"){ Fail 'no new prop appeared' }; Say "OK prop $A2" }
 'tozero' { Job (Py "RLPy.RGlobal.Stop();RLPy.RScene.ClearSelectObjects()`nL=RLPy.RGlobal.GetProjectLength()`nRLPy.RGlobal.SetStartTime(T(0));RLPy.RGlobal.SetEndTime(L);RLPy.RGlobal.SetPreviewStartTime(T(0));RLPy.RGlobal.SetPreviewEndTime(L)`nRLPy.RGlobal.SetTime(T(0))`nprint('len',L.ToFloat()/6000)") 'zz_gui_tozero' | Out-Null; Say 'OK playhead 0, play range = whole project' }
 'save'   { Fail 'project saving is disabled in scripts: use the visible iClone File > Save Project menu manually' }
 'saveas' { Fail 'project saving is disabled in scripts: use the visible iClone File > Save Project As menu manually' }
 'open'   { $dirty=(Title) -match '\*$'
            # iClone keeps '*' after a good save: if the open file was written < 120 s ago, nothing is lost -> answer No
            $cf=CurrentFile; if($dirty -and $cf -and ((Get-Date)-$cf.LastWriteTime).TotalSeconds -lt 120){ $Discard=$true; Say 'file just saved: the * is stale' }
            if($dirty -and -not $Discard){ Fail "unsaved changes in $(Title): save first, or add -Discard to throw them away" }
            Keys @($CTRL) 0x4F
            # the title does not always show '*' (render/range jobs change the project): ALWAYS watch for the save prompt
            for($i=0;$i -lt ($(if($dirty){40}else{6}));$i++){ Start-Sleep 1
              if($Discard){ if(PressButton '^No$'){ Say 'discarded unsaved changes'; break } }
              elseif(PressButton '^Cancel$'){ Fail "iClone asks to save $(Title): save first, or add -Discard to throw the changes away" } }
            FillDialog $A1; WaitLoaded (Split-Path $A1 -Leaf) }
 'reopen' { $f=CurrentFile; if(-not $f){Fail 'no saved file for the current title'}
            # iClone can keep '*' right after a good save: trust the FILE (written < 120 s ago) and answer No to its prompt
            $fresh=((Get-Date)-$f.LastWriteTime).TotalSeconds -lt 120
            if((Title) -match '\*$' -and -not $fresh){Fail 'unsaved changes: save first'}
            Keys @($CTRL) 0x4F
            for($i=0;$i -lt 6;$i++){ Start-Sleep 1; if(PressButton '^No$'){ Say 'file just saved; ignored the stale * prompt'; break } }
            FillDialog $f.FullName; WaitLoaded $f.Name; Say 'OK reopen test passed' }
 'switch' { Front|Out-Null; ClickRel 1218 84; Start-Sleep -Milliseconds 1000; ClickRel 1203 118; Start-Sleep 1; Shot|Out-Null
            Say 'clicked Switch (look at gui_shot.png toolbar if unsure: dropdown must read Switch)' }
 'sound'  { if(-not (Test-Path $A1)){Fail "no wav: $A1"}
            Job (Py "RLPy.RGlobal.Stop();RLPy.RScene.ClearSelectObjects();RLPy.RGlobal.SetTime(T(0))") 'zz_gui_t0'|Out-Null
            if($Replace){ Front|Out-Null; ClickRel 1700 950; Keys @() 0x2E; Say 'deleted the old sound clip (row Sound)'; Job (Py "RLPy.RGlobal.SetTime(T(0))") 'zz_gui_t0b'|Out-Null }
            Keys @($CTRL) 0x49; FillDialog $A1; Start-Sleep 4; Front|Out-Null; Keys @($SHIFT) 0x72; Keys @() 0x24; Shot|Out-Null
            Say "imported $(Split-Path $A1 -Leaf) at frame 0 - check gui_tl.png: Sound row must start with the clip name at frame 0, then: save" }
 'lip'    { $av=$A1; $wav=$A2; [double]$s=$A3; [double]$e=$A4
            Job (Py "RLPy.RGlobal.Stop();RLPy.RScene.ClearSelectObjects()`na=[x for x in RLPy.RScene.GetAvatars() if x.GetName()=='$av'][0]`nRLPy.RScene.SelectObject(a);RLPy.RGlobal.SetTime(T(0))") 'zz_gui_sel'|Out-Null
            PreviewWin 6; Front|Out-Null; ClickRel 220 49; ClickRel 290 79; ClickRel 538 129; try { FillDialog $wav } finally { PreviewWin 9 }; Start-Sleep 8
            $chk=Py "a=[x for x in RLPy.RScene.GetAvatars() if x.GetName()=='$av'][0]`nopen(os.path.join(J,'gui_vis.txt'),'w').write(str(len(a.GetVisemeComponent().GetVisemeKeys())))"
            $n=0; for($i=0;$i -lt 30;$i++){ Job $chk 'zz_gui_vis'|Out-Null; $n=[int](Get-Content (Join-Path $J 'gui_vis.txt')); if($n -gt 0){break}; Start-Sleep 2 }
            if($n -eq 0){ Fail "no viseme keys on $av (look at the screen)" }
            $trim=Py "import json`nos.environ['LIPWIN']=json.dumps({'$av':[$s,$e]})`nexec(open(r'$SCR\ic8_lip_trim.py',encoding='utf-8').read())"
            Job $trim 'zz_gui_trim'|Out-Null; Get-Content (Join-Path $J 'lip_trim.txt') -Encoding UTF8|?{$_ -match "^$av "}
            Job (Py "RLPy.RScene.ClearSelectObjects()") 'zz_gui_desel'|Out-Null }
 'render' { $out=$A1; [double]$end=$A2; $wav=$A3; if(-not (Test-Path $wav)){Fail "no wav: $wav"}
            $raw=$out -replace '\.mp4$','_raw.mp4'
            # IC8_RENDER_POST=1: iClone is ALREADY rendering $raw (e.g. the caller was stopped): only wait for the
            # file to be complete, then add sound + checks. Never starts a second render.
            if(-not $env:IC8_RENDER_POST){ Remove-Item $raw -ErrorAction SilentlyContinue
            [IO.File]::WriteAllText((Join-Path $J 'render.json'),(@{out=($raw -replace '\\','/');start=0;end=$end;width=$Width;height=$Height;fps=60}|ConvertTo-Json -Compress),(New-Object Text.UTF8Encoding $false))
            Remove-Item (Join-Path $J 'render_log.txt') -ErrorAction SilentlyContinue
            # 2026-11-21: a 76 s part took > 40 min, the old 2400 s limit failed while iClone was still writing.
            # Wait up to 2 h, and then until the raw file is a COMPLETE mp4 (ffprobe reads its duration).
            Job (Get-Content (Join-Path $SCR 'ic8_render2.py') -Raw -Encoding UTF8) 'zz_gui_render' 7200|Out-Null }
            else { for($w=0;$w -lt 480 -and -not (Test-Path $raw);$w++){ Start-Sleep 15 } }
            if(-not (Test-Path $raw)){ Fail "render produced no file ($raw). Render panel on Image? click Video, run again" }
            $ErrorActionPreference='Continue'   # ffprobe on a half-written mp4 prints "moov atom not found" to stderr: not fatal, try again
            for($w=0;$w -lt 240;$w++){ $d=& $FFP -v error -show_entries format=duration -of csv=p=0 $raw 2>$null; if($d){break}; Start-Sleep 15 }
            if(-not $d){ Fail "raw video never finished ($raw)" }
            $ErrorActionPreference='Continue'   # ffmpeg writes progress to stderr
            # -t: the first render after opening a project ignores the frame range (rules) -> always trim to 0..end
            & $FF -v error -y -i $raw -i $wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -t $end $out 2>$null
            $p=& $FFP -v error -show_entries stream=width,height,r_frame_rate:format=duration -of compact $out; Say $p
            $vol=(cmd /c "`"$FF`" -hide_banner -i `"$out`" -af volumedetect -vn -f null - 2>&1" | Select-String 'mean_volume'); Say "$vol"
            if("$vol" -match 'mean_volume: -([0-9.]+)' -and [double]$Matches[1] -gt 60){ Say 'WARN: audio is (almost) silent' }
            if(($p -join ' ') -notmatch ('width='+$Width+'\|height='+$Height+'\|r_frame_rate=60/1')){ Say ('WARN: not '+$Width+'x'+$Height+' 60fps') }
            if($Shots){ $i=0; foreach($t in $Shots.Split(',')){ $i++; & $FF -v error -y -ss $t -i $out -frames:v 1 -vf scale=480:-1 (Join-Path $J ("gui_r{0:D2}.jpg" -f $i)) }
                        & $FF -v error -y -i (Join-Path $J 'gui_r%02d.jpg') -vf "tile=${i}x1" (Join-Path $J 'gui_render_check.jpg'); Say "frames per shot: $J\gui_render_check.jpg" }
            Remove-Item -LiteralPath $raw -Force; Say "OK $out (raw deleted: the checked mp4 is the result; Recycle Bin filled the disk)"
            if($Publish){ New-Item -ItemType Directory -Force $Publish|Out-Null; Copy-Item $out $Publish -Force; Say "published to $Publish" }
            Job (Py "L=RLPy.RGlobal.GetProjectLength()`nRLPy.RGlobal.SetStartTime(T(0));RLPy.RGlobal.SetEndTime(L);RLPy.RGlobal.SetPreviewStartTime(T(0));RLPy.RGlobal.SetPreviewEndTime(L);RLPy.RGlobal.SetTime(T(0))") 'zz_gui_range'|Out-Null }
 default  { Get-Content $PSCommandPath -TotalCount 22 }
}

} finally {
  if($guardHeld){$guardMutex.ReleaseMutex()}
  if($guardMutex){$guardMutex.Dispose()}
}
