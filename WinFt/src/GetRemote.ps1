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
    $rootDir = Join-Path $PSScriptRoot '..'
    $tmpDir = Join-Path $rootDir 'tmp'

    $fileServer = [Remote]::new()
    $localDir = GenerateLocalDir $tmpDir

    $fileServer.Download($remoteFile, $localDir)
}

if ($MyInvocation.InvocationName -ne '.') {
    Set-DotEnv -envFile (Join-Path $PSScriptRoot '.env')
    Main -remoteFile $args[0]
}
