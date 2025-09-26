#EnPowerShelladmin
# Buscar proyectos de PyCharm en C:
$startPath = "C:\"
$pattern = ".idea"

Write-Host "ðŸ”Ž Buscando proyectos de PyCharm en $startPath ... (puede tardar varios minutos)"

# Buscar todas las carpetas .idea
$results = Get-ChildItem -Path $startPath -Directory -Recurse -ErrorAction SilentlyContinue |
           Where-Object { $_.Name -eq $pattern }

# Preparar lista de proyectos (la carpeta padre de .idea)
$projects = $results | ForEach-Object { $_.Parent.FullName } | Sort-Object -Unique

# Mostrar resultados
if ($projects.Count -gt 0) {
    Write-Host "`nâœ… Se encontraron $($projects.Count) proyectos de PyCharm:`n" -ForegroundColor Green
    $projects | ForEach-Object { Write-Host $_ -ForegroundColor Cyan }

    # Guardar en archivo en el Escritorio
    $outFile = "$env:USERPROFILE\Desktop\PyCharm_Projects_Found.txt"
    $projects | Out-File -FilePath $outFile -Encoding UTF8
    Write-Host "`nðŸ“„ Lista guardada en: $outFile" -ForegroundColor Yellow
} else {
    Write-Host "`nâš ï¸ No se encontraron proyectos de PyCharm en $startPath" -ForegroundColor Red
}

#ðŸš€ CÃ³mo usarlo

#Abre PowerShell (Win + R â†’ escribe powershell â†’ Enter).
#Si puedes, ejecÃºtalo como administrador porque busca en todo C:.
#Copia y pega el script.
#Espera unos minutos (depende del tamaÃ±o de tu disco).
#Al final verÃ¡s en pantalla todas las carpetas encontradas y ademÃ¡s un archivo:
