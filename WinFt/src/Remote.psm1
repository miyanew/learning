class Remote {
    [string]$IpAddress
    [string]$Account
    [string]$Password
    [string]$LocalDir

    Remote([string]$ipAddress, [string]$account, [string]$password) {
        $this.IpAddress = $ipAddress
        $this.Account = $account
        $this.Password = $password
        # $this.HomeDir = ""
    }

    [void] Upload([string]$clientDir, [string]$fileNamePattern, [string]$relativeDir = "") {
        # sftp put コマンド  localDir -> remote
    }

    [void] Download([string]$relativeDir = "", [string]$fileNamePattern = "*", [string]$destDir) {
        # sftp get コマンド  remote -> localDir
    }

    [string] Lst([string]$relativeDir = "./") {
        # sftp lst コマンド
        return '$remoteDirResult'
    }
}

class S3 {
    [string]$IpAddress
    [string]$Account
    [string]$Password
    [string]$LocalDir

    S3([string]$ipAddress, [string]$account, [string]$password) {
        $this.IpAddress = $ipAddress
        $this.Account = $account
        $this.Password = $password
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
