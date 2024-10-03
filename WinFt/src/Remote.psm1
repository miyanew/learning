class SshServer {
    [string]$IpAddress
    [string]$Account
    [System.Management.Automation.PSCredential]$Credential

    SshServer() {
        $this.IpAddress = $env:SSH_SERVER_IP
        $this.Account = $env:SSH_SERVER_ACCOUNT
        $securePw = ConvertTo-SecureString $env:SSH_SERVER_PASSWORD -AsPlainText -Force
        $this.Credential = New-Object System.Management.Automation.PSCredential ($this.Account, $securePw)
    }

    [void] Upload([string]$sourceFile = "*", [string]$destinationDir) {
        $cmdOpen = "open sftp://$($this.Account):$($this.Credential.GetNetworkCredential().Password)@$($this.IpAddress)"
        $cmdPut = "put $sourceFile $destinationDir/"
        $cmdExit = "exit"
        
        & $env:WINSCP_PATH /command $cmdOpen $cmdPut $cmdExit
    }
    
    [void] Download([string]$sourceFile = "*", [string]$destinationDir) {
        $cmdOpen = "open sftp://$($this.Account):$($this.Credential.GetNetworkCredential().Password)@$($this.IpAddress)"
        $cmdGet = "get $sourceFile `"`"$destinationDir\`"`""
        $cmdExit = "exit"

        & $env:WINSCP_PATH /command $cmdOpen $cmdGet $cmdExit
    }

    [void] Lst([string]$file = "*") {
        $cmdOpen = "open sftp://$($this.Account):$($this.Credential.GetNetworkCredential().Password)@$($this.IpAddress)"
        $cmdLs = "ls $file"
        $cmdExit = "exit"

        & $env:WINSCP_PATH /command $cmdOpen $cmdLs $cmdExit
    }
}

class S3 {
    [string]$Url
    [string]$Region
    [string]$Profile

    S3() {
        $this.Url = "s3://$($env:BUCKET_NAME)/$($env:OBJECT_PATH)/"
        $this.Region = $env:REGION
        $this.Profile = $env:PROFILE
    }

    [void] Upload([string]$filePattern = "*", [string]$sourceDir) {
        aws s3 mv $sourceDir $this.Url --include $filePattern --recursive --region $this.Region --profile $this.Profile
    }

    [void] Download([string]$filePattern = "*", [string]$destinationDir) {
        aws s3 mv $this.Url $destinationDir --include $filePattern --recursive --region $this.Region --profile $this.Profile
    }

    [string[]] Lst() {
        return aws s3 ls $this.Url --region $this.Region --profile $this.Profile
    }
}
