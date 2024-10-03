Set-Location $PSScriptRoot

& .\LsSshServer.ps1 $args[0]
Write-Output "---"

& .\GetSshServer.ps1 $args[0] $args[1]
Write-Output "File retrieval complete, starting transfer."

& .\PutS3.ps1 $args[0]
Write-Output "File transfer complete!`n---"

& .\LsS3.ps1
