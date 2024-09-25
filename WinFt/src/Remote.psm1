class Remote {
    [string]$IpAddress
    [string]$Account
    [System.Management.Automation.PSCredential]$Credential

    Remote() {
        $this.IpAddress = $env:REMOTE_IP
        $this.Account = $env:REMOTE_ACCOUNT
        $securePassword = ConvertTo-SecureString $env:REMOTE_PASSWORD -AsPlainText -Force
        $this.Credential = New-Object System.Management.Automation.PSCredential ($this.Account, $securePassword)
    }

    [void] Upload([string]$fileNamePattern = "*", [string]$remoteDir = "") {
        $cmdOpen = "open sftp://$($this.Account):$($this.Credential.GetNetworkCredential().Password)@$($this.IpAddress)"
        $cmdPut = "put $($fileNamePattern) $($remoteDir)/"
        $cmdExit = "exit"
        
        & $env:WINSCP_PATH /command $cmdOpen $cmdPut $cmdExit
    }
    
    [void] Download([string]$fileNamePattern = "*", [string]$localDir) {
        $cmdOpen = "open sftp://$($this.Account):$($this.Credential.GetNetworkCredential().Password)@$($this.IpAddress)"
        $cmdGet = "get $($fileNamePattern) $($localDir)\"
        $cmdExit = "exit"

        & $env:WINSCP_PATH /command $cmdOpen $cmdGet $cmdExit
    }
}

class S3 {
    [string]$Url
    [string]$Region
    [string]$Profile

    S3([string]$objectpath) {
        $bucket = "s3-bkt-name"
        $this.Url = "s3://$($bucket)/$($objectpath)/"
        $this.Region = "ap-northeast-1"
        $this.Profile = "mfa_profile"
    }

    [void] Upload([string]$localDir) {
        aws s3 mv $localDir $this.Url --include "*" --recursive --region $this.Region --profile $this.Profile
    }

    [void] Download([string]$localDir) {
        aws s3 mv $this.Url $localDir --include "*" --recursive --region $this.Region --profile $this.Profile
    }

    [string[]] Lst() {
        return aws s3 ls $this.Url --region $this.Region --profile $this.Profile
    }
}
