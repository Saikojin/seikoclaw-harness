#!/bin/bash
# Cross-platform Bash pre-exec guard hook
# Accepts JSON on stdin containing .command or .tool_input.command

HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PATTERNS_FILE="${HOOK_DIR}/dangerous-patterns.txt"

if [ ! -f "$PATTERNS_FILE" ]; then
    exit 0
fi

INPUT_JSON=$(cat)
if [ -z "$INPUT_JSON" ]; then
    exit 0
fi

COMMAND=""

if command -v jq >/dev/null 2>&1; then
    COMMAND=$(echo "$INPUT_JSON" | jq -r '.command // .tool_input.command // empty' 2>/dev/null)
elif command -v python3 >/dev/null 2>&1; then
    COMMAND=$(python3 -c "import sys, json; raw=sys.stdin.read(); data=json.loads(raw) if raw.strip().startswith('{') else {}; print(data.get('command') or (data.get('tool_input') or {}).get('command', ''))" <<< "$INPUT_JSON" 2>/dev/null)
elif command -v python >/dev/null 2>&1; then
    COMMAND=$(python -c "import sys, json; raw=sys.stdin.read(); data=json.loads(raw) if raw.strip().startswith('{') else {}; print(data.get('command') or (data.get('tool_input') or {}).get('command', ''))" <<< "$INPUT_JSON" 2>/dev/null)
else
    echo "BLOCKED: Guard requires jq or python to parse incoming tool execution payload." >&2
    exit 2
fi

# If JSON payload was parsed but command is empty, check if input itself was raw plain string (non-JSON)
if [ -z "$COMMAND" ]; then
    if [[ "$INPUT_JSON" =~ ^[[:space:]]*\{ ]]; then
        # It was valid JSON but had no command field
        exit 0
    else
        COMMAND="$INPUT_JSON"
    fi
fi

while IFS= read -r pattern || [ -n "$pattern" ]; do
    [[ "$pattern" =~ ^[[:space:]]*# ]] && continue
    [[ -z "${pattern// }" ]] && continue
    
    if echo "$COMMAND" | grep -E -q "$pattern"; then
        echo "BLOCKED: Command contains prohibited dangerous pattern: $pattern" >&2
        exit 2
    fi
done < "$PATTERNS_FILE"

exit 0
