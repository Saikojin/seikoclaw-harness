# SeikoClaw SessionStart Hook (PowerShell)
# Injects high-rigor operating directive and playbook routing into agent context on startup, resume, or compaction.

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ContextFile = Join-Path $ScriptDir "session-start-context.md"

if (Test-Path $ContextFile) {
    Get-Content $ContextFile -Raw -Encoding utf8
}
