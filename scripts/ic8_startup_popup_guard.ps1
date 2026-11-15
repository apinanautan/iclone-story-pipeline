param([switch]$Once,[switch]$DryRun,[int]$IntervalMs=700)
# iClone popup guard: closes KNOWN popups automatically so no AI/human has to screenshot + click them.
# Runs forever in the background (installed as a logon task by install_ic8_startup_popup_guard.ps1).
# Reads popup text with UI Automation (iClone popups are Qt, not Win32), presses the whitelisted button
# with UIA Invoke, and falls back to a DPI-aware mouse click (needed for the FBX "Convert All" button).
# Log: %LOCALAPPDATA%\iCloneStartupGuard\guard.log
#
# To add a popup: add a row to $RULES (text that must appear, button name regex). Never add Save/Delete/Overwrite.
$ErrorActionPreference='Continue'
$logDir=Join-Path $env:LOCALAPPDATA 'iCloneStartupGuard'; New-Item -ItemType Directory -Force -Path $logDir|Out-Null
$log=Join-Path $logDir 'guard.log'
function Log([string]$s){Add-Content -Path $log -Encoding UTF8 -Value ((Get-Date -Format 'yyyy-MM-dd HH:mm:ss')+' '+$s)}

Add-Type -AssemblyName UIAutomationClient,UIAutomationTypes
Add-Type -Namespace G -Name U -MemberDefinition @'
[DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
[DllImport("user32.dll")] public static extern bool SetCursorPos(int x,int y);
[DllImport("user32.dll")] public static extern bool GetCursorPos(out POINT p);
[DllImport("user32.dll")] public static extern void mouse_event(int f,int x,int y,int d,int e);
[DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
public struct POINT{public int X,Y;}
public delegate bool EnumProc(IntPtr h,IntPtr l);
[DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc e,IntPtr l);
[DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr w,out uint p);
[DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr w);
'@
[G.U]::SetProcessDPIAware()|Out-Null
$A=[Windows.Automation.AutomationElement]; $TS=[Windows.Automation.TreeScope]

# name = log tag; text = regex that must match the popup's text; button = regex for the button to press;
# mouse = use a real click (UIA Invoke does not work on that dialog); anyProcess = popup is not owned by iClone.exe
$RULES=@(
 @{name='offline';      text='Failed to establish a connection|proper internet connection'; button='^OK$'},
 @{name='signup';       text='SIGN UP|Sign up|sign up|Sign me up|Why Register'; button='^(No, thank you\.?|No Thanks|Not Now)$'},
 @{name='plugin_compat';text='not compatible with this version of iClone'; button='^(OK|Yes)$'},
 @{name='fbx_import';   text='Import Settings|FBX Import Settings|Convert All'; button='^Convert All$'; mouse=$true},
 @{name='render_reminder'; text='^Reminder'; button='^Discard$'}
)

function TextOf($el){
 $parts=New-Object System.Collections.Generic.List[string]
 $parts.Add($el.Current.Name)
 try{ $el.FindAll($TS::Descendants,[Windows.Automation.Condition]::TrueCondition)|%{ if($_.Current.Name){$parts.Add($_.Current.Name)} } }catch{}
 ($parts -join "`n")
}
function Press($el,$btn,$mouse){
 if(-not $mouse){ try{ $btn.GetCurrentPattern([Windows.Automation.InvokePattern]::Pattern).Invoke(); return 'invoke' }catch{} }
 $r=$btn.Current.BoundingRectangle; if($r.Width -le 0){return 'no-rect'}
 $p=New-Object G.U+POINT; [G.U]::GetCursorPos([ref]$p)|Out-Null
 try{[G.U]::SetForegroundWindow([IntPtr]$el.Current.NativeWindowHandle)|Out-Null}catch{}
 Start-Sleep -Milliseconds 150
 [G.U]::SetCursorPos([int]($r.X+$r.Width/2),[int]($r.Y+$r.Height/2))|Out-Null; Start-Sleep -Milliseconds 80
 [G.U]::mouse_event(2,0,0,0,0); [G.U]::mouse_event(4,0,0,0,0)
 Start-Sleep -Milliseconds 80; [G.U]::SetCursorPos($p.X,$p.Y)|Out-Null   # put the user's mouse back
 'click'
}

$seen=@{}
Log "START once=$Once dryrun=$DryRun"
do{
 try{
  $ic=@(Get-Process -Name iClone -ErrorAction SilentlyContinue|%{$_.Id})
  if($ic.Count -gt 0){
   # Win32 EnumWindows sees every visible top-level window of iClone.exe, including owned dialogs that
   # UIA does not list under the desktop (FBX "Import Settings" = IC::CExternalImportDlg on the primary display)
   $script:hw=New-Object 'System.Collections.Generic.List[System.IntPtr]'
   $cb=[G.U+EnumProc]{ param([IntPtr]$h,[IntPtr]$l); [uint32]$p=0; [void][G.U]::GetWindowThreadProcessId($h,[ref]$p)
     if(($ic -contains [int]$p) -and [G.U]::IsWindowVisible($h)){ $script:hw.Add($h) }; return $true }
   [void][G.U]::EnumWindows($cb,[IntPtr]::Zero)
   $cands=@(); foreach($h in $script:hw){ try{ $cands+=$A::FromHandle($h) }catch{} }
   foreach($w in @(1)){
    foreach($d in $cands){
     $rc=$d.Current.BoundingRectangle
     if($rc.Width -le 0 -or $rc.Width -gt 1300 -or $rc.Height -gt 1000){continue}   # popups are small; big = panels
     $txt=TextOf $d
     foreach($rule in $RULES){
      if($txt -notmatch $rule.text){continue}
      $cond=New-Object Windows.Automation.PropertyCondition($A::ControlTypeProperty,[Windows.Automation.ControlType]::Button)
      $btn=$d.FindAll($TS::Descendants,$cond)|?{ $_.Current.Name.Trim() -match $rule.button }|select -First 1
      if(-not $btn){continue}
      $key="$($d.Current.NativeWindowHandle)-$($rule.name)-"+[int]((Get-Date).TimeOfDay.TotalSeconds/3)
      if($seen.ContainsKey($key)){continue}; $seen[$key]=1
      if($DryRun){Log "DRYRUN $($rule.name) -> '$($btn.Current.Name)'"; continue}
      $how=Press $d $btn $rule.mouse
      Log "CLOSED $($rule.name) -> '$($btn.Current.Name)' ($how)"
      break
     }
    }
   }
  }
 }catch{Log ('ERROR '+$_.Exception.Message)}
 if($seen.Count -gt 500){$seen=@{}}
 if(-not $Once){Start-Sleep -Milliseconds ([Math]::Max(300,$IntervalMs))}
}while(-not $Once)
Log 'END'
