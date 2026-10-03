<# AuraTrace-IR: Elite Windows Standalone Collector #>
[CmdletBinding()]
Param()

If (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Warning "[-] FATAL: Administrator privileges required to access Security Event logs and raw sockets."
    Exit 1
}

$TS = Get-Date -Format "yyyyMMdd_HHmmss"
$Dir = "$env:TEMP\auratrace_$($env:COMPUTERNAME)_$TS"
New-Item -ItemType Directory -Path $Dir -Force | Out-Null

Write-Host "[*] Harvesting Deep Windows State..." -ForegroundColor Cyan
Get-WmiObject Win32_Process | Select-Object ProcessId,ParentProcessId,Name,CommandLine | Export-Csv "$Dir\processes.csv" -NoTypeInfo
Get-NetTCPConnection | Select-Object LocalAddress,LocalPort,RemoteAddress,RemotePort,State,OwningProcess | Export-Csv "$Dir\network.csv" -NoTypeInfo
ipconfig /displaydns | Out-File "$Dir\dns_cache.txt"
Get-SmbSession | Export-Csv "$Dir\smb_sessions.csv" -NoTypeInfo -ErrorAction SilentlyContinue

Write-Host "[*] Extracting Autoruns & Script Payloads..." -ForegroundColor Cyan
Get-ItemProperty "HKLM:\Software\Microsoft\Windows\CurrentVersion\Run" -ErrorAction SilentlyContinue | Out-File "$Dir\hklm_run.txt"
Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4624,4625,7045,4688} -MaxEvents 500 -ErrorAction SilentlyContinue | Select-Object TimeCreated,Id,Message | Export-Csv "$Dir\security_events.csv" -NoTypeInfo
Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-PowerShell/Operational'; Id=4104} -MaxEvents 50 -ErrorAction SilentlyContinue | Select-Object TimeCreated,Message | Export-Csv "$Dir\powershell_scriptblocks.csv" -NoTypeInfo

Write-Host "[*] Cryptographically Sealing Artifacts..." -ForegroundColor Cyan
Get-ChildItem -Path $Dir -File | ForEach-Object { Get-FileHash -Path $_.FullName -Algorithm SHA256 } | Export-Csv "$Dir\Evidence_Hashes.csv" -NoTypeInfo
$Zip = "$env:TEMP\auratrace_$($env:COMPUTERNAME)_$TS.zip"
Compress-Archive -Path "$Dir\*" -DestinationPath $Zip -Force
Remove-Item -Recurse -Force $Dir

Write-Host "[+] Chain of Custody Sealed: $Zip" -ForegroundColor Green
