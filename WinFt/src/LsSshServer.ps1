using module .\Remote.psm1
using module .\Dotenv.psm1

function Main($remoteFile) {    
    $fileServer = [SshServer]::new()
    Write-Output $fileServer.Lst($remoteFile)
}

if ($MyInvocation.InvocationName -ne '.') {
    $OutputEncoding = [System.Text.Encoding]::UTF8
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8

    Set-DotEnv -envFile (Join-Path $PSScriptRoot '../.env')
    Main -remoteFile $args[0]
    Start-Sleep 3
}
