<#
.SYNOPSIS
    SeikoClaw Godot MCP Orchestration & Automation Helper

.DESCRIPTION
    Provides automated workflows to scaffold, install, configure, launch, and invoke
    Godot MCP tools across local Godot C# projects via godot-cli and Model Context Protocol.

.EXAMPLE
    .\scripts\godot-harness.ps1 status D:\DevWorkspace\MyGodotGame
    .\scripts\godot-harness.ps1 setup D:\DevWorkspace\MyGodotGame
    .\scripts\godot-harness.ps1 open D:\DevWorkspace\MyGodotGame
    .\scripts\godot-harness.ps1 run-tool node-create D:\DevWorkspace\MyGodotGame -InputJson '{"name":"Player","typeClassName":"CharacterBody3D"}'
    .\scripts\godot-harness.ps1 screenshot D:\DevWorkspace\MyGodotGame
#>

param(
    [Parameter(Position=0)]
    [ValidateSet("status", "setup", "open", "close", "wait", "build", "run-tool", "screenshot", "logs", "create-project")]
    [string]$Action = "status",

    [Parameter(Position=1)]
    [string]$ProjectPath = ".",

    [Parameter(Position=2)]
    [string]$ToolName = "",

    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$ExtraArgs
)

$ErrorActionPreference = "Stop"

function Resolve-GodotProjectPath([string]$path) {
    $resolved = [System.IO.Path]::GetFullPath($path)
    if (-not (Test-Path $resolved)) {
        if ($Action -ne "create-project") {
            throw "Project path does not exist: $resolved"
        }
    }
    return $resolved
}

function Show-Header {
    Write-Host "`n=== SeikoClaw Godot MCP Orchestrator ===" -ForegroundColor Cyan
}

$fullProjectPath = Resolve-GodotProjectPath $ProjectPath

switch ($Action) {
    "status" {
        Show-Header
        Write-Host "Checking Godot-MCP status for: $fullProjectPath" -ForegroundColor Yellow
        godot-cli status $fullProjectPath
    }

    "create-project" {
        Show-Header
        Write-Host "Scaffolding Godot C# (.NET) project at: $fullProjectPath..." -ForegroundColor Yellow
        godot-cli create-project --dotnet $fullProjectPath
        Write-Host "[SUCCESS] Godot project scaffolded at $fullProjectPath" -ForegroundColor Green
    }

    "setup" {
        Show-Header
        Write-Host "1. Installing godot_mcp addon with managed server binary..." -ForegroundColor Yellow
        godot-cli install-plugin $fullProjectPath --with-server

        Write-Host "`n2. Enabling all MCP tools, prompts, and resources..." -ForegroundColor Yellow
        godot-cli configure $fullProjectPath --enable-all-tools --enable-all-prompts --enable-all-resources

        Write-Host "`n3. Configuring Antigravity MCP settings..." -ForegroundColor Yellow
        godot-cli setup-mcp antigravity $fullProjectPath

        Write-Host "`n[SUCCESS] Project $fullProjectPath configured for Godot MCP!" -ForegroundColor Green
        Write-Host "Next step: Run '.\scripts\godot-harness.ps1 open `"$fullProjectPath`"' to launch the Editor." -ForegroundColor Cyan
    }

    "open" {
        Show-Header
        Write-Host "Building C# assembly and launching Godot Editor for: $fullProjectPath..." -ForegroundColor Yellow
        godot-cli open $fullProjectPath
        Write-Host "`nWaiting for Godot Editor and MCP server to be ready..." -ForegroundColor Yellow
        godot-cli wait-for-ready $fullProjectPath
        Write-Host "[SUCCESS] Godot Editor is ready and accepting tool calls!" -ForegroundColor Green
    }

    "close" {
        Show-Header
        Write-Host "Gracefully closing Godot Editor for: $fullProjectPath..." -ForegroundColor Yellow
        godot-cli close $fullProjectPath
    }

    "wait" {
        Show-Header
        Write-Host "Waiting for Godot Editor ready state: $fullProjectPath..." -ForegroundColor Yellow
        godot-cli wait-for-ready $fullProjectPath
    }

    "build" {
        Show-Header
        Write-Host "Compiling C# project assembly (dotnet build) for: $fullProjectPath..." -ForegroundColor Yellow
        godot-cli build $fullProjectPath
    }

    "run-tool" {
        if (-not $ToolName) {
            throw "ToolName parameter required for run-tool action."
        }
        $inputJson = if ($ExtraArgs) { $ExtraArgs -join " " } else { "{}" }
        godot-cli run-tool $ToolName $fullProjectPath --input $inputJson
    }

    "screenshot" {
        Show-Header
        Write-Host "Capturing Godot Editor Viewport screenshot for: $fullProjectPath..." -ForegroundColor Yellow
        godot-cli run-tool screenshot-viewport $fullProjectPath
    }

    "logs" {
        Show-Header
        Write-Host "Retrieving Godot Console logs for: $fullProjectPath..." -ForegroundColor Yellow
        $jsonInput = '{"maxCount":50}'
        godot-cli run-tool console-get-logs $fullProjectPath --input $jsonInput
    }
}
