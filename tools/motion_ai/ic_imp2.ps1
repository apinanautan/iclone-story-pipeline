# ic_imp2.ps1 <fbx> : Import External Motion onto selected avatar. Keyboard for menu (only if iClone has focus), dialog filled by window messages.
param([string]$Fbx)
Add-Type -Namespace IM -Name U -MemberDefinition @'
[DllImport("user32.dll",CharSet=CharSet.Unicode)] public static extern IntPtr FindWindow(string c,string t);
[DllImport("user32.dll",CharSet=CharSet.Unicode)] public static extern IntPtr FindWindowEx(IntPtr p,IntPtr a,string c,string t);
[DllImport("user32.dll",CharSet=CharSet.Unicode)] public static extern IntPtr SendMessage(IntPtr h,int m,IntPtr w,string l);
[DllImport("user32.dll")] public static extern IntPtr PostMessage(IntPtr h,int m,IntPtr w,IntPtr l);
[DllImport("user32.dll")] public static extern IntPtr GetDlgItem(IntPtr h,int id);
[DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
[DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
[DllImport("user32.dll")] public static extern int GetWindowThreadProcessId(IntPtr h, IntPtr p);
[DllImport("user32.dll",EntryPoint="GetWindowThreadProcessId")] public static extern int GetWindowThreadProcessId2(IntPtr h, out int p);
[DllImport("kernel32.dll")] public static extern int GetCurrentThreadId();
[DllImport("user32.dll")] public static extern bool AttachThreadInput(int a,int b,bool f);
[DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr h);
'@
Add-Type -AssemblyName System.Windows.Forms
$k = [System.Windows.Forms.SendKeys]
$ic = (Get-Process iClone).MainWindowHandle
$d = [IM.U]::FindWindow('#32770', 'เปิด')
if ($d -eq 0) {
$ft=[IM.U]::GetWindowThreadProcessId([IM.U]::GetForegroundWindow(),0); $me=[IM.U]::GetCurrentThreadId(); [IM.U]::AttachThreadInput($me,$ft,$true)|Out-Null; [IM.U]::BringWindowToTop($ic)|Out-Null; [IM.U]::SetForegroundWindow($ic) | Out-Null; [IM.U]::AttachThreadInput($me,$ft,$false)|Out-Null; Start-Sleep -Milliseconds 500
$pp=0; [IM.U]::GetWindowThreadProcessId2([IM.U]::GetForegroundWindow(),[ref]$pp)|Out-Null
if ($pp -ne (Get-Process iClone).Id) { "ABORT no focus (fg pid $pp)"; exit 1 }
$k::SendWait('{ESC}'); Start-Sleep -Milliseconds 200
$k::SendWait('%f'); Start-Sleep -Milliseconds 700
foreach ($x in @('{DOWN}')*5 + @('{RIGHT}') + @('{DOWN}')*3) { $pp=0; [IM.U]::GetWindowThreadProcessId2([IM.U]::GetForegroundWindow(),[ref]$pp)|Out-Null; if ($pp -ne 0 -and $pp -ne (Get-Process iClone).Id) { "ABORT lost focus pid $pp"; exit 1 }; $k::SendWait($x); Start-Sleep -Milliseconds 350 }
$k::SendWait('{ENTER}')
$d = 0; for ($i = 0; $i -lt 20 -and $d -eq 0; $i++) { Start-Sleep -Milliseconds 500; $d = [IM.U]::FindWindow('#32770', 'เปิด') }
if ($d -eq 0) { "ABORT no dialog"; exit 1 }; Start-Sleep 2
}
$c = [IM.U]::GetDlgItem($d, 0x47C); $ed = [IM.U]::FindWindowEx($c, 0, 'Edit', $null); if ($ed -eq 0) { $ed = [IM.U]::FindWindowEx([IM.U]::FindWindowEx($c, 0, 'ComboBox', $null), 0, 'Edit', $null) }
[IM.U]::SendMessage($ed, 0x0C, 0, $Fbx) | Out-Null; Start-Sleep -Milliseconds 300
[IM.U]::PostMessage([IM.U]::GetDlgItem($d, 1), 0xF5, 0, 0) | Out-Null; Start-Sleep 2
"OK " + $Fbx
