# PowerShell hook runner for OpenBrain history sync
$ErrorActionPreference = "SilentlyContinue"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PyScript = Join-Path $ScriptDir "sync-history.py"

if (Test-Path $PyScript) {
    python $PyScript
} else {
    python -m openbrain.history_sync
}
