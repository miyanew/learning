class Remote {
    [string]$IpAddress
    [string]$Account
    [string]$Password
    [string]$LocalDir

    Remote([string]$newDistName) {
        $this.IpAddress = $IpAddress
        $this.Account = $Account
        $this.Password = $Password
        $this.RootDir = Join-Path $PSScriptRoot '..' -Resolve
        $this.LocalDir = Join-Path --Resolve $this.RootDir "tmp" Get-Date.ToString("yyyyMMdd_HHmmss")
    }

    [string] Download([string]$fileNamePattern = "*", [string]$remoteDir = "./") {
        # sftp get コマンド  remote -> localDir
        return '$localDir'
    }

    [string] Upload([string]$fileNamePattern = "*", [string]$remoteDir = "./") {
        # sftp put コマンド  localDir -> remote
        return '$remoteDir'
    }

    [string] Lst([string]$remoteDir = "./") {
        # sftp lst コマンド
        return '$remoteDirResult'
    }
}
