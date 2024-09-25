<#
.SYNOPSIS
Set-DotEnv loads from local .ENV files
#>
Function Set-DotEnv {
    param (
        [string]$envFile = ".env"
    )
    if (Test-Path $envFile) {
        Get-Content $envFile | ForEach-Object {
            if ($_ -match '^([^=]+)=(.*)$') {
                [Environment]::SetEnvironmentVariable($Matches[1], $Matches[2], "Process")
            }
        }
    }
}

Export-ModuleMember @('Set-DotEnv')