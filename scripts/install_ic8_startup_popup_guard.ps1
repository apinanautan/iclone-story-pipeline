param([switch]$Remove)
$ErrorActionPreference='Stop'
$taskName='iClone Startup Popup Guard'
if($Remove){
 Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
 Write-Output "REMOVED $taskName"
 exit 0
}
$guard=Join-Path $PSScriptRoot 'ic8_startup_popup_guard.ps1'
if(-not (Test-Path $guard)){throw "Missing: $guard"}
$exe=Join-Path $env:WINDIR 'System32\WindowsPowerShell\v1.0\powershell.exe'
$arg='-NoProfile -NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File "'+$guard+'"'
$action=New-ScheduledTaskAction -Execute $exe -Argument $arg
$trigger=New-ScheduledTaskTrigger -AtLogOn -User "$env:USERDOMAIN\$env:USERNAME"
$principal=New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited
$settings=New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Days 90) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
$task=New-ScheduledTask -Action $action -Trigger $trigger -Principal $principal -Settings $settings
Register-ScheduledTask -TaskName $taskName -InputObject $task -Force|Out-Null
Start-ScheduledTask -TaskName $taskName
Get-ScheduledTask -TaskName $taskName|Select TaskName,State
Write-Output 'INSTALLED: Runs at Windows sign-in; -Remove unregisters the task.'
