using module .\Remote.psm1
using module .\Dotenv.psm1

function Main() {    
    $fileServer = [S3]::new()
    Write-Output $fileServer.Lst()
}

if ($MyInvocation.InvocationName -ne '.') {
    Set-DotEnv -envFile (Join-Path $PSScriptRoot '../.env')
    Main
}
