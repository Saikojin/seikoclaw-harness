#!/usr/bin/env bash
# SeikoClaw SessionStart Hook
# Injects high-rigor operating directive and playbook routing into agent context on startup, resume, or compaction.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTEXT_FILE="$SCRIPT_DIR/session-start-context.md"

if [ -f "$CONTEXT_FILE" ]; then
    cat "$CONTEXT_FILE"
fi
