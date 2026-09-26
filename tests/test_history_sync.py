import os
import json
import tempfile
import pytest
from datetime import datetime, timezone

from openbrain.memory_engine import MemoryEngine
from openbrain.watchdog import HealthPatrol
from openbrain.history_sync import (
    ConversationHistorySyncer,
    parse_iso_datetime,
    clean_user_content
)

def test_parse_iso_datetime():
    # SQLite CURRENT_TIMESTAMP format
    dt_sqlite = parse_iso_datetime("2026-09-26 05:01:18")
    assert dt_sqlite is not None
    assert dt_sqlite.year == 2026
    assert dt_sqlite.month == 9
    assert dt_sqlite.day == 26
    assert dt_sqlite.hour == 5
    assert dt_sqlite.tzinfo == timezone.utc

    # ISO format with Z
    dt_z = parse_iso_datetime("2026-09-25T22:02:35Z")
    assert dt_z is not None
    assert dt_z.year == 2026
    assert dt_z.hour == 22

    # ISO format with offset
    dt_offset = parse_iso_datetime("2026-09-25T15:02:35-07:00")
    assert dt_offset is not None
    assert dt_offset.astimezone(timezone.utc).hour == 22

    # Invalid / empty
    assert parse_iso_datetime("") is None
    assert parse_iso_datetime("not-a-date") is None

def test_clean_user_content():
    raw = (
        "<USER_REQUEST>\n"
        "Build a new feature for SeikoClaw.\n"
        "</USER_REQUEST>\n"
        "<ADDITIONAL_METADATA>\n"
        "Current local time: 2026-09-25\n"
        "</ADDITIONAL_METADATA>\n"
        "<USER_SETTINGS_CHANGE>\n"
        "Model switched\n"
        "</USER_SETTINGS_CHANGE>"
    )
    cleaned = clean_user_content(raw)
    assert cleaned == "Build a new feature for SeikoClaw."

def test_extract_project_name():
    syncer = ConversationHistorySyncer()
    
    steps = [
        {
            "step_index": 0,
            "type": "USER_INPUT",
            "content": "<user_information> d:\\DevWorkspace\\Tactical-Adberrain -> Saikojin/Tactical-Adberrain </user_information>"
        },
        {
            "step_index": 1,
            "type": "PLANNER_RESPONSE",
            "tool_calls": [
                {
                    "name": "view_file",
                    "args": {"AbsolutePath": "d:\\DevWorkspace\\Tactical-Adberrain\\src\\main.py"}
                }
            ]
        }
    ]
    
    proj = syncer.extract_project_name(steps, "/tmp/dummy_conv")
    assert proj == "Tactical-Adberrain"

def test_conversation_sync_lifecycle():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp_dir:
        db_path = os.path.join(temp_dir, "test_openbrain.db")
        chroma_path = os.path.join(temp_dir, "test_chroma")
        brain_dir = os.path.join(temp_dir, "brain")
        os.makedirs(brain_dir, exist_ok=True)

        memory = MemoryEngine(db_path=db_path, chroma_path=chroma_path)
        watchdog = HealthPatrol(db_path=db_path)
        syncer = ConversationHistorySyncer(memory_engine=memory, watchdog=watchdog, brain_dir=brain_dir)

        # Baseline watermark on empty DB should be None
        assert syncer.get_latest_memory_timestamp() is None

        # Create mock conversation 1
        conv1_id = "conv-1111-aaaa"
        conv1_logs = os.path.join(brain_dir, conv1_id, ".system_generated", "logs")
        os.makedirs(conv1_logs, exist_ok=True)
        conv1_transcript = os.path.join(conv1_logs, "transcript.jsonl")

        conv1_steps = [
            {
                "step_index": 0,
                "source": "USER_EXPLICIT",
                "type": "USER_INPUT",
                "created_at": "2026-09-20T10:00:00Z",
                "content": "<USER_REQUEST>Implement user authentication</USER_REQUEST><user_information>d:\\DevWorkspace\\AuthProject</user_information>"
            },
            {
                "step_index": 1,
                "source": "MODEL",
                "type": "PLANNER_RESPONSE",
                "created_at": "2026-09-20T10:01:00Z",
                "tool_calls": [{"name": "write_to_file", "args": {"TargetFile": "d:\\DevWorkspace\\AuthProject\\auth.py", "toolSummary": "Write auth.py"}}]
            },
            {
                "step_index": 2,
                "source": "USER_EXPLICIT",
                "type": "USER_INPUT",
                "created_at": "2026-09-20T12:00:00Z",
                "content": "<USER_REQUEST>Add password hashing</USER_REQUEST>"
            },
            {
                "step_index": 3,
                "source": "MODEL",
                "type": "PLANNER_RESPONSE",
                "created_at": "2026-09-20T12:02:00Z",
                "status": "ERROR",
                "content": "Fatal: bcrypt module missing",
                "tool_calls": [{"name": "run_command", "args": {"CommandLine": "pytest", "toolSummary": "Run pytest"}}]
            }
        ]

        with open(conv1_transcript, "w", encoding="utf-8") as f:
            for s in conv1_steps:
                f.write(json.dumps(s) + "\n")

        # 1. Dry Run Test
        dry_stats = syncer.sync(dry_run=True)
        assert dry_stats["conversations_scanned"] == 1
        assert dry_stats["conversations_updated"] == 1
        assert dry_stats["memories_created"] == 0 # Dry run does not write

        # 2. Live Sync Test
        stats = syncer.sync()
        assert stats["conversations_scanned"] == 1
        assert stats["conversations_updated"] == 1
        assert stats["memories_created"] == 2
        assert stats["mistakes_recorded"] == 1
        assert "AuthProject" in stats["synced_projects"]

        # Check DB records
        memories = memory.retrieve_similar("authentication")
        assert len(memories) > 0
        assert "AuthProject" in memories[0]["content"]

        # Check Mistake records
        mistakes = memory.get_mistakes("bcrypt")
        assert len(mistakes) > 0

        # Check watermark state in SQLite
        watermark = memory.get_history_sync_watermark(conv1_id)
        assert watermark is not None
        assert watermark["last_synced_step"] == 3
        assert watermark["memories_count"] == 2

        # 3. Idempotency Test (Running again without new steps should not duplicate)
        stats2 = syncer.sync()
        assert stats2["conversations_updated"] == 0
        assert stats2["memories_created"] == 0

        # 4. Incremental Step Ingestion Test
        # Append a new step to conv1
        with open(conv1_transcript, "a", encoding="utf-8") as f:
            new_step_u = {
                "step_index": 4,
                "source": "USER_EXPLICIT",
                "type": "USER_INPUT",
                "created_at": "2026-09-21T08:00:00Z",
                "content": "<USER_REQUEST>Add JWT token support</USER_REQUEST>"
            }
            new_step_m = {
                "step_index": 5,
                "source": "MODEL",
                "type": "PLANNER_RESPONSE",
                "created_at": "2026-09-21T08:05:00Z",
                "status": "DONE",
                "tool_calls": [{"name": "write_to_file", "args": {"TargetFile": "d:\\DevWorkspace\\AuthProject\\jwt.py", "toolSummary": "Write jwt.py"}}]
            }
            f.write(json.dumps(new_step_u) + "\n")
            f.write(json.dumps(new_step_m) + "\n")

        stats3 = syncer.sync()
        assert stats3["conversations_updated"] == 1
        assert stats3["memories_created"] == 1

        updated_wm = memory.get_history_sync_watermark(conv1_id)
        assert updated_wm["last_synced_step"] == 5
        assert updated_wm["memories_count"] == 3
