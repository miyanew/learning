using module .\Remote.psm1
using module .\Dotenv.psm1

function Main($localFile, $remoteDir) {
    if ([string]::IsNullOrEmpty($remoteDir)) {
        $remoteDir = "./"
    }

    $localDir = GetLatestLocalDir
    $localPath = Join-Path $localDir $localFile

    $fileServer = [SshServer]::new()
    $fileServer.Upload($localPath, $remoteDir)
}

function GetLatestLocalDir() {        
    if ([System.IO.Path]::IsPathRooted($env:LOCAL_DIR)) {
        $tmpDir = $env:LOCAL_DIR
    } else {
        $rootDir = Join-Path $PSScriptRoot '..'
        $tmpDir = Join-Path $rootDir $env:LOCAL_DIR
    }

    $dirs = Get-ChildItem -Path $tmpDir -Directory
    return ($dirs | Sort-Object LastWriteTime)[-1].FullName
}

if ($MyInvocation.InvocationName -ne '.') {
    Set-DotEnv -envFile (Join-Path $PSScriptRoot '../.env')
    Main -localFile $args[0] -remoteDir $args[1]
}
