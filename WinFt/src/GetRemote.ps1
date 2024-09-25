using module .\Remote.psm1
using module .\Dotenv.psm1

function GenerateLocalDir($parentDir) {
    $dateDir = Join-Path $parentDir (Get-Date).ToString('yyyyMMddHHmmss')
    if (-not (Test-Path $dateDir)) {
        New-Item -Path $dateDir -ItemType Directory -Force | Out-Null
    }
    return $dateDir
}

function Main($remoteFile) {
    Set-DotEnv
    $rootDir = Join-Path $PSScriptRoot '..'
    $tmpDir = Join-Path $rootDir 'tmp'
    $env:WINSCP_PATH

    $fileServer = [Remote]::new()
    $localDir = GenerateLocalDir $tmpDir

    $fileServer.Download($remoteFile, $localDir)
}

if ($MyInvocation.InvocationName -ne '.') {
    Main -remoteFile $args[0]
}
