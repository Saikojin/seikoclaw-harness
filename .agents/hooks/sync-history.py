#!/usr/bin/env python3
"""
Portable hook runner for OpenBrain Conversation History Sync.
Compatible with Antigravity hooks.json, shell startup scripts, and CLI agents.
"""

import os
import sys
import json

def find_harness_root():
    # 1. Check environment variable
    env_dir = os.getenv("SEIKOCLAW_DIR")
    if env_dir and os.path.exists(env_dir):
        return env_dir
    
    # 2. Walk up from current script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidate = os.path.abspath(os.path.join(script_dir, "..", ".."))
    if os.path.exists(os.path.join(candidate, "openbrain")):
        return candidate
    
    # 3. Check CWD
    if os.path.exists(os.path.join(os.getcwd(), "openbrain")):
        return os.getcwd()
        
    return None

def main():
    root = find_harness_root()
    if not root:
        # Fallback to repo root containing this hook script
        root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    if root not in sys.path:
        sys.path.insert(0, root)

    try:
        from openbrain.history_sync import ConversationHistorySyncer
        syncer = ConversationHistorySyncer()
        # Fast sync recent conversations (limit to 10 by default on invocation)
        stats = syncer.sync(limit=10)
        
        # Output JSON payload on stdout for Antigravity hook protocol compliance
        result = {
            "status": "success",
            "memories_created": stats.get("memories_created", 0),
            "conversations_updated": stats.get("conversations_updated", 0),
            "latest_timestamp": stats.get("latest_timestamp")
        }
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))

if __name__ == "__main__":
    main()
