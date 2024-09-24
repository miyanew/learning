using module .\Remote.psm1

function GenerateLocalDir($rootDir) {
    $tmpDir = Join-Path $rootDir 'tmp'
    $dateDir = Join-Path $tmpDir (Get-Date).ToString('yyyyMMddHHmmss')

    if (-not (Test-Path $dateDir)) {
        New-Item -Path $dateDir -ItemType Directory -Force | Out-Null
    }
}

function Main($remoteDir, $include) {
    $rootDir = Join-Path $PSScriptRoot '..'
    $lolalDir = GenerateLocalDir $rootDir
    
    $fileServer = [Remote]::new("ip", "user", "pw")
    $fileServer.Download("/remote/path", "*.txt", $lolalDir)
}

# $fileServer.Upload($lolalDir, "*.txt", "/remote/path")

if ($MyInvocation.InvocationName -ne '.') {
    Main -remoteDir $args[0] -include $args[1]
}


<#
https://learn.microsoft.com/en-us/powershell/scripting/developer/module/understanding-a-windows-powershell-module?view=powershell-7.4
https://learn.microsoft.com/en-us/powershell/scripting/developer/module/how-to-write-a-powershell-script-module?view=powershell-7.4
https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/import-module?view=powershell-7.4
https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_using?view=powershell-7.4
#>