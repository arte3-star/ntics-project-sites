# Registra o auto-sync do 132-samarco como Windows Scheduled Task rodando a cada 2h.
# Rode UMA VEZ no PowerShell (admin ou usuário comum) para ativar.
# Para desativar: schtasks /Delete /TN "NTICS-projeto-sync-132" /F

param(
    [string]$Slug = "132-samarco",
    [int]$IntervaloMinutos = 120,
    [string]$ProjectsOsPath = "g:\O meu disco\projects-os"
)

$TaskName = "NTICS-projeto-sync-$Slug"
$PythonExe = (Get-Command python).Source
$ScriptPath = Join-Path $ProjectsOsPath "tools\sync\projeto_sync.py"
$LogPath = Join-Path $ProjectsOsPath "projects\$Slug\.cache\cron.log"

if (-not (Test-Path $ScriptPath)) {
    Write-Error "Script não encontrado: $ScriptPath"
    exit 1
}

# Comando: executa o sync e redireciona stderr pro log de cron (rotação manual por enquanto)
$Command = "`"$PythonExe`" `"$ScriptPath`" $Slug --quiet 2>&1 >> `"$LogPath`""

Write-Host "Registrando task:"
Write-Host "  Nome:    $TaskName"
Write-Host "  Comando: $Command"
Write-Host "  Cadência: a cada $IntervaloMinutos minutos"
Write-Host ""

$Action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c $Command"
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes $IntervaloMinutos) -RepetitionDuration (New-TimeSpan -Days 3650)
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -MultipleInstances IgnoreNew

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Force

Write-Host ""
Write-Host "[ok] Task registrada. Rodará a cada $IntervaloMinutos min a partir de agora."
Write-Host "     Log de cron: $LogPath"
Write-Host ""
Write-Host "Para verificar: schtasks /Query /TN `"$TaskName`""
Write-Host "Para remover:   schtasks /Delete /TN `"$TaskName`" /F"
