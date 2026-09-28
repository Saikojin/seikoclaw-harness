#!/bin/bash
# Cross-platform Bash pre-exec guard hook
# Accepts JSON on stdin containing .command or .tool_input.command

HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PATTERNS_FILE="${HOOK_DIR}/dangerous-patterns.txt"

if [ ! -f "$PATTERNS_FILE" ]; then
    exit 0
fi

INPUT_JSON=$(cat)
COMMAND=""

if command -v jq >/dev/null 2>&1; then
    COMMAND=$(echo "$INPUT_JSON" | jq -r '.command // .tool_input.command // empty')
else
    COMMAND="$INPUT_JSON"
fi

if [ -z "$COMMAND" ]; then
    exit 0
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
