# Cross-platform PowerShell pre-exec guard hook
# Accepts JSON on stdin or -Command parameter

param(
    [string]$CommandString
)

$hookDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$patternsFile = Join-Path $hookDir "dangerous-patterns.txt"

if (-not (Test-Path $patternsFile)) {
    exit 0
}

if ([string]::IsNullOrWhiteSpace($CommandString)) {
    $inputJson = [Console]::In.ReadToEnd()
    if ($inputJson) {
        try {
            $parsed = $inputJson | ConvertFrom-Json
            if ($parsed.command) { $CommandString = $parsed.command }
            elseif ($parsed.tool_input -and $parsed.tool_input.command) { $CommandString = $parsed.tool_input.command }
            else { $CommandString = $inputJson }
        } catch {
            $CommandString = $inputJson
        }
    }
}

if ([string]::IsNullOrWhiteSpace($CommandString)) {
    exit 0
}

$patterns = Get-Content $patternsFile | Where-Object { $_ -and -not $_.StartsWith("#") }

foreach ($pattern in $patterns) {
    if ($CommandString -match $pattern) {
        [Console]::Error.WriteLine("BLOCKED: Command contains prohibited dangerous pattern: $pattern")
        exit 2
    }
}

exit 0
