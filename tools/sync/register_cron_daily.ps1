# Registra sync_all_active.py como Windows Scheduled Task rodando todo dia as 7h.
# Rode UMA VEZ no PowerShell para ativar.
# Para desativar: schtasks /Delete /TN "NTICS-sync-all-active" /F

param(
    [string]$Hora = "07:00",
    [string]$ProjetosPath = "g:\O meu disco\Claude-NTICS-Projetos"
)

$TaskName = "NTICS-sync-all-active"
$PythonExe = (Get-Command python).Source
$ScriptPath = Join-Path $ProjetosPath "tools\sync\sync_all_active.py"
$LogDir = Join-Path $ProjetosPath "output\sync"
$LogPath = Join-Path $LogDir "cron.log"

if (-not (Test-Path $ScriptPath)) {
    Write-Error "Script nao encontrado: $ScriptPath"
    exit 1
}

if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

$Command = "`"$PythonExe`" `"$ScriptPath`" 2>&1 >> `"$LogPath`""

Write-Host "Registrando task:"
Write-Host "  Nome:    $TaskName"
Write-Host "  Comando: $Command"
Write-Host "  Cadencia: diaria as $Hora"
Write-Host ""

$Action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c $Command"
$Trigger = New-ScheduledTaskTrigger -Daily -At $Hora
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -MultipleInstances IgnoreNew

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Force

Write-Host ""
Write-Host "[ok] Task registrada. Rodara todo dia as $Hora."
Write-Host "     Log: $LogPath"
Write-Host "     Resumo do dia: output/sync/YYYY-MM-DD-resumo.md"
Write-Host ""
Write-Host "Verificar: schtasks /Query /TN `"$TaskName`""
Write-Host "Remover:   schtasks /Delete /TN `"$TaskName`" /F"
