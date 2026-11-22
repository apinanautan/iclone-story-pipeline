# Builds Ai-iclone.exe (project root) from launcher\AiIclone.cs with the C# compiler that ships with Windows.
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$csc = "$env:WINDIR\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
& $csc /nologo /target:exe /optimize+ /r:System.IO.Compression.dll /r:System.IO.Compression.FileSystem.dll /out:"$root\Ai-iclone.exe" "$PSScriptRoot\AiIclone.cs"
if ($LASTEXITCODE -ne 0) { throw "csc failed" }
Get-Item "$root\Ai-iclone.exe" | Select-Object Name, Length
