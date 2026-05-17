# Registra o secondbrain_sync.py como Windows Scheduled Task diária às 21h.
# Rode UMA VEZ no PowerShell (pode ser necessário admin dependendo da configuração).
# Para desativar: schtasks /Delete /TN "NTICS-secondbrain-clickup-sync" /F

param(
    [string]$RepoPath = "G:\O meu disco\Claude-NTICS-Projetos",
    [string]$HoraBRT  = "21:00"   # 21h BRT = 00:00 UTC+3 próximo dia (ajuste se mudar horário)
)

$TaskName  = "NTICS-secondbrain-clickup-sync"
$PythonExe = (Get-Command python).Source
$ScriptPath = Join-Path $RepoPath "tools\sync\secondbrain_sync.py"
$LogPath    = Join-Path $RepoPath ".tmp\logs\secondbrain_sync.log"

if (-not (Test-Path $ScriptPath)) {
    Write-Error "Script nao encontrado: $ScriptPath"
    exit 1
}

New-Item -ItemType Directory -Force -Path (Split-Path $LogPath) | Out-Null

$Command = "`"$PythonExe`" `"$ScriptPath`" --quiet 2>&1 >> `"$LogPath`""

Write-Host "Registrando task:"
Write-Host "  Nome:     $TaskName"
Write-Host "  Horario:  $HoraBRT (horario local BRT)"
Write-Host "  Comando:  $Command"
Write-Host ""

$Action   = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c $Command" -WorkingDirectory $RepoPath
$Trigger  = New-ScheduledTaskTrigger -Daily -At $HoraBRT
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1) `
    -MultipleInstances IgnoreNew

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Force

Write-Host ""
Write-Host "[ok] Task registrada. Rodara todo dia as $HoraBRT."
Write-Host "     Log: $LogPath"
Write-Host ""
Write-Host "Para verificar: schtasks /Query /TN `"$TaskName`""
Write-Host "Para rodar agora: schtasks /Run /TN `"$TaskName`""
Write-Host "Para remover:   schtasks /Delete /TN `"$TaskName`" /F"
