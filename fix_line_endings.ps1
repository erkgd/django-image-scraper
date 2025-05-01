$content = Get-Content -Path "docker-entrypoint.sh" -Raw
$content = $content -replace "`r`n", "`n"
Set-Content -Path "docker-entrypoint.sh" -Value $content -NoNewline
