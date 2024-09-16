class WslDistribution {
    [string]$Name
    [string]$RootPath
    [string]$SnapshotDir
    [string]$DistributionDir

    WslDistribution([string]$newDistName) {
        $this.Name = $newDistName
        $this.RootPath = Join-Path $PSScriptRoot '..' -Resolve
        $this.SnapshotDir = Join-Path $this.RootPath "snapshot"
        $this.DistributionDir = Join-Path $this.RootPath "distribution"
    }

    [string] Clone([string]$srcDistribution) {
        $snapshotPath = $this.Export($srcDistribution)
        $deployDir = $this.Import($snapshotPath)
        return $deployDir
    }

    hidden [string] Export([string]$srcDistribution) {
        $snapshotPath = Join-Path $this.SnapshotDir "$($this.Name).tar"
        wsl --export $srcDistribution $snapshotPath
        return $snapshotPath
    }

    hidden [string] Import([string]$snapshotPath) {
        $deployDir = Join-Path $this.DistributionDir $this.Name
        wsl --import $this.Name $deployDir $snapshotPath
        return $deployDir
    }
}

function Main {
    param (
        [string]$srcDistName,
        [string]$newDistName
    )

    $newDist = [WslDistribution]::new($newDistName)
    $deployDir = $newDist.Clone($srcDistName)
    Write-Output "Snapshot deployed as new distribution to $($deployDir)"
}

if ($MyInvocation.InvocationName -ne '.') {
    Main -srcDistName $args[0] -newDistName $args[1]
}
