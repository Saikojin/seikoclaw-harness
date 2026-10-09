<#
.SYNOPSIS
    SeikoClaw Unity MCP Orchestration & Automation Helper

.DESCRIPTION
    Provides automated workflows to scaffold, install, configure, launch, and invoke
    Unity MCP tools across local Unity projects.

.EXAMPLE
    .\scripts\unity-harness.ps1 status D:\DevWorkspace\MyGame
    .\scripts\unity-harness.ps1 setup D:\DevWorkspace\MyGame
    .\scripts\unity-harness.ps1 open D:\DevWorkspace\MyGame
    .\scripts\unity-harness.ps1 run-tool gameobject-create D:\DevWorkspace\MyGame -InputJson '{"name":"Hero","primitiveType":"Cube"}'
#>

param(
    [Parameter(Position=0)]
    [ValidateSet("status", "setup", "open", "close", "wait", "run-tool", "test", "screenshot", "exec-cs")]
    [string]$Action = "status",

    [Parameter(Position=1)]
    [string]$ProjectPath = ".",

    [Parameter(Position=2)]
    [string]$ToolName = "",

    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$ExtraArgs
)

$ErrorActionPreference = "Stop"

function Resolve-UnityProjectPath([string]$path) {
    $resolved = [System.IO.Path]::GetFullPath($path)
    if (-not (Test-Path $resolved)) {
        throw "Project path does not exist: $resolved"
    }
    return $resolved
}

function Show-Header {
    Write-Host "`n=== SeikoClaw Unity MCP Orchestrator ===" -ForegroundColor Cyan
}

$fullProjectPath = Resolve-UnityProjectPath $ProjectPath

switch ($Action) {
    "status" {
        Show-Header
        Write-Host "Checking Unity-MCP status for: $fullProjectPath" -ForegroundColor Yellow
        unity-mcp-cli status $fullProjectPath
    }

    "setup" {
        Show-Header
        Write-Host "1. Installing Unity-MCP plugin with server binary..." -ForegroundColor Yellow
        unity-mcp-cli install-plugin $fullProjectPath --with-server

        Write-Host "`n2. Enabling all MCP tools and prompts..." -ForegroundColor Yellow
        unity-mcp-cli configure $fullProjectPath --enable-all-tools --enable-all-prompts --enable-all-resources

        Write-Host "`n3. Configuring Antigravity MCP settings..." -ForegroundColor Yellow
        unity-mcp-cli setup-mcp antigravity $fullProjectPath --transport stdio

        Write-Host "`n[SUCCESS] Project $fullProjectPath configured for Unity MCP!" -ForegroundColor Green
        Write-Host "Next step: Run '.\scripts\unity-harness.ps1 open `"$fullProjectPath`"' to launch the Editor." -ForegroundColor Cyan
    }

    "open" {
        Show-Header
        Write-Host "Launching Unity Editor for: $fullProjectPath..." -ForegroundColor Yellow
        unity-mcp-cli open $fullProjectPath
        Write-Host "`nWaiting for Unity Editor and MCP server to be ready..." -ForegroundColor Yellow
        unity-mcp-cli wait-for-ready $fullProjectPath
        Write-Host "[SUCCESS] Unity Editor is ready and accepting tool calls!" -ForegroundColor Green
    }

    "close" {
        Show-Header
        Write-Host "Gracefully closing Unity Editor for: $fullProjectPath..." -ForegroundColor Yellow
        unity-mcp-cli close $fullProjectPath
    }

    "wait" {
        Show-Header
        Write-Host "Waiting for Unity Editor ready state: $fullProjectPath..." -ForegroundColor Yellow
        unity-mcp-cli wait-for-ready $fullProjectPath
    }

    "run-tool" {
        if (-not $ToolName) {
            throw "ToolName parameter required for run-tool action."
        }
        $inputJson = if ($ExtraArgs) { $ExtraArgs -join " " } else { "{}" }
        unity-mcp-cli run-tool $ToolName $fullProjectPath --input $inputJson
    }

    "test" {
        Show-Header
        $mode = if ($ExtraArgs -contains "-PlayMode") { "PlayMode" } else { "EditMode" }
        Write-Host "Executing Unity $mode Tests for: $fullProjectPath..." -ForegroundColor Yellow
        $jsonInput = '{"testMode":"' + $mode + '","includeMessages":true,"includePassingTests":false}'
        unity-mcp-cli run-tool tests-run $fullProjectPath --input $jsonInput
    }

    "screenshot" {
        Show-Header
        Write-Host "Capturing Game View screenshot for: $fullProjectPath..." -ForegroundColor Yellow
        unity-mcp-cli run-tool screenshot-game-view $fullProjectPath
    }

    "exec-cs" {
        Show-Header
        $csCode = $ExtraArgs -join " "
        if (-not $csCode) {
            throw "C# code snippet required for exec-cs action."
        }
        Write-Host "Compiling and executing C# via Roslyn: $fullProjectPath..." -ForegroundColor Yellow
        $payload = @{
            csharpCode = $csCode
            isMethodBody = $true
        } | ConvertTo-Json -Compress
        unity-mcp-cli run-tool script-execute $fullProjectPath --input $payload
    }
}
