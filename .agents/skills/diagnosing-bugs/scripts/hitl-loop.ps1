# Hitl Loop Script
# Ported from bash version hitl-loop.template.sh from Matt Pocock's skills repo

param(
    [string]$Command = "pytest",
    [int]$MaxRetries = 3
)

$retryCount = 0
$success = $false

Write-Host "Starting HITL Loop for Command: $Command"

while ($retryCount -lt $MaxRetries -and -not $success) {
    Write-Host "Running attempt $($retryCount + 1)..."
    Invoke-Expression $Command
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Success on attempt $($retryCount + 1)!"
        $success = $true
    } else {
        Write-Host "Failed. Please apply a fix and press Enter to retry..."
        Read-Host
        $retryCount++
    }
}

if (-not $success) {
    Write-Host "Failed after $MaxRetries attempts."
    exit 1
}
