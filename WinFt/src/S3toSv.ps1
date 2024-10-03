Set-Location $PSScriptRoot

& .\LsS3.ps1
Write-Output "---"

& .\GetS3.ps1 $args[0]
Write-Output "File retrieval complete, starting transfer."

& .\PutSshServer.ps1 $args[0] $args[1]
Write-Output "File transfer complete!`n---"

& .\LsSshServer.ps1 $args[0]
