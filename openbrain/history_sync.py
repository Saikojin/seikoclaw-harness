import os
import sys
import json
import glob
import re
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from .memory_engine import MemoryEngine
from .watchdog import HealthPatrol
from .llm_provider import get_llm_provider, LLMProvider

def parse_iso_datetime(dt_str: str) -> Optional[datetime]:
    """Parses various ISO-8601 or SQLite datetime string formats to a UTC-aware datetime object."""
    if not dt_str:
        return None
    dt_str = dt_str.strip()
    try:
        # SQLite CURRENT_TIMESTAMP format: "YYYY-MM-DD HH:MM:SS"
        if " " in dt_str and "T" not in dt_str:
            dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
            return dt.replace(tzinfo=timezone.utc)
        
        # Standard ISO 8601 with Z or offset
        if dt_str.endswith("Z"):
            dt_str = dt_str[:-1] + "+00:00"
        return datetime.fromisoformat(dt_str).astimezone(timezone.utc)
    except Exception:
        return None

def clean_user_content(content: str) -> str:
    """Strips system prompts, metadata, and user settings changes from user input content."""
    if not content:
        return ""
    # Extract inside <USER_REQUEST> if present
    req_match = re.search(r"<USER_REQUEST>\s*(.*?)\s*</USER_REQUEST>", content, re.DOTALL)
    if req_match:
        return req_match.group(1).strip()
    
    # Remove <ADDITIONAL_METADATA>...</ADDITIONAL_METADATA>
    content = re.sub(r"<ADDITIONAL_METADATA>.*?</ADDITIONAL_METADATA>", "", content, flags=re.DOTALL)
    # Remove <USER_SETTINGS_CHANGE>...</USER_SETTINGS_CHANGE>
    content = re.sub(r"<USER_SETTINGS_CHANGE>.*?</USER_SETTINGS_CHANGE>", "", content, flags=re.DOTALL)
    # Remove <user_information>...</user_information>
    content = re.sub(r"<user_information>.*?</user_information>", "", content, flags=re.DOTALL)
    return content.strip()

class ConversationHistorySyncer:
    """
    Scans conversation history transcripts across projects, identifies conversation events
    newer than the latest memory timestamp, and ingests them as structured OpenBrain memories.
    """
    def __init__(
        self,
        memory_engine: Optional[MemoryEngine] = None,
        watchdog: Optional[HealthPatrol] = None,
        llm_provider: Optional[LLMProvider] = None,
        brain_dir: Optional[str] = None
    ):
        self.memory = memory_engine or MemoryEngine()
        self.watchdog = watchdog or HealthPatrol()
        self.llm = llm_provider or get_llm_provider()
        
        # Resolve brain directory
        env_brain = os.getenv("SEIKOCLAW_BRAIN_DIR")
        default_brain = os.path.join(os.path.expanduser("~"), ".gemini", "antigravity", "brain")
        self.brain_dir = brain_dir or env_brain or default_brain

    def get_latest_memory_timestamp(self) -> Optional[datetime]:
        """Returns the newest memory or sync watermark timestamp as UTC datetime."""
        ts_str = self.memory.get_latest_memory_timestamp()
        if ts_str:
            return parse_iso_datetime(ts_str)
        return None

    def find_all_transcripts(self) -> List[Dict[str, str]]:
        """
        Discovers all conversation transcript files across brain folders.
        Returns list of dicts with conversation_id, transcript_path, and dir_mtime.
        """
        if not os.path.exists(self.brain_dir):
            return []

        results = []
        for entry in os.scandir(self.brain_dir):
            if not entry.is_dir():
                continue
            conv_id = entry.name
            logs_dir = os.path.join(entry.path, ".system_generated", "logs")
            transcript_path = os.path.join(logs_dir, "transcript.jsonl")
            if not os.path.exists(transcript_path):
                # Fallback to transcript_full.jsonl
                transcript_path = os.path.join(logs_dir, "transcript_full.jsonl")
            
            if os.path.exists(transcript_path):
                mtime = os.path.getmtime(transcript_path)
                results.append({
                    "conversation_id": conv_id,
                    "conv_dir": entry.path,
                    "transcript_path": transcript_path,
                    "mtime": mtime
                })
        
        # Sort by mtime descending (most recently active conversations first)
        results.sort(key=lambda x: x["mtime"], reverse=True)
        return results

    def extract_project_name(self, steps: List[Dict[str, Any]], conv_dir: str) -> str:
        """Determines the project name from transcript steps or conversation directory."""
        from collections import Counter
        project_counter = Counter()

        # 1. Primary check: <user_information> active workspace mapping
        for step in steps:
            content = step.get("content", "")
            if isinstance(content, str) and "<user_information>" in content:
                # e.g. d:\DevWorkspace\SeikoClaw-Harness -> Saikojin/seikoclaw-harness
                m = re.search(r"d:[/\\](?:DevWorkspace|Projects|Workspace|dev)[/\\]([A-Za-z0-9_\-]+)\s*->", content, re.IGNORECASE)
                if m:
                    return m.group(1)

        # 2. Score candidate mentions across steps and tool calls
        for step in steps:
            content = step.get("content", "")
            if isinstance(content, str):
                for m in re.finditer(r"(?:[A-Za-z]:[/\\](?:DevWorkspace|Projects|Workspace|dev)[/\\]|/home/[^/]+/[^/]+[/\\])([A-Za-z0-9_\-]+)", content, re.IGNORECASE):
                    project_counter[m.group(1)] += 1

            for call in step.get("tool_calls", []):
                args = call.get("args", {})
                for k, v in args.items():
                    if isinstance(v, str):
                        for m_tool in re.finditer(r"(?:[A-Za-z]:[/\\](?:DevWorkspace|Projects|Workspace|dev)[/\\]|/home/[^/]+/[^/]+[/\\])([A-Za-z0-9_\-]+)", v, re.IGNORECASE):
                            # Give extra weight to tool target paths and working directories
                            weight = 3 if k in ("Cwd", "TargetFile", "AbsolutePath", "DirectoryPath") else 1
                            project_counter[m_tool.group(1)] += weight

        if project_counter:
            return project_counter.most_common(1)[0][0]

        # 3. Check for local markdown artifacts in conv_dir
        for root, dirs, files in os.walk(conv_dir):
            for f in files:
                if f.endswith(".md"):
                    try:
                        with open(os.path.join(root, f), "r", encoding="utf-8", errors="ignore") as fp:
                            c = fp.read()
                            m = re.search(r"d:[/\\](?:DevWorkspace|Projects|Workspace|dev)[/\\]([A-Za-z0-9_\-]+)", c, re.IGNORECASE)
                            if m:
                                return m.group(1)
                    except Exception:
                        pass

        # Fallback to current working directory name or default
        return os.path.basename(os.getcwd()) or "default-project"

    def parse_turns(
        self,
        transcript_path: str,
        since_time: Optional[datetime] = None,
        since_step: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Parses a transcript file into segmented conversation turns,
        filtering for turns newer than since_time or since_step.
        """
        if not os.path.exists(transcript_path):
            return []

        all_steps = []
        try:
            with open(transcript_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        step_data = json.loads(line)
                        all_steps.append(step_data)
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            print(f"[HistorySync] Failed to read {transcript_path}: {e}")
            return []

        if not all_steps:
            return []

        # Group into turns by USER_INPUT
        turns = []
        current_turn = None

        for step in all_steps:
            step_idx = step.get("step_index", 0)
            step_type = step.get("type", "")
            step_source = step.get("source", "")
            step_time_raw = step.get("created_at", "")
            step_time = parse_iso_datetime(step_time_raw)

            if step_type == "USER_INPUT" or step_source == "USER_EXPLICIT":
                if current_turn:
                    turns.append(current_turn)
                
                clean_req = clean_user_content(step.get("content", ""))
                current_turn = {
                    "start_step": step_idx,
                    "end_step": step_idx,
                    "created_at_raw": step_time_raw,
                    "created_at": step_time,
                    "user_request": clean_req,
                    "tool_actions": [],
                    "model_responses": [],
                    "errors": [],
                    "steps_count": 1
                }
            else:
                if current_turn is None:
                    # Turn started before logged user input
                    current_turn = {
                        "start_step": step_idx,
                        "end_step": step_idx,
                        "created_at_raw": step_time_raw,
                        "created_at": step_time,
                        "user_request": "System / Initial Turn",
                        "tool_actions": [],
                        "model_responses": [],
                        "errors": [],
                        "steps_count": 0
                    }
                
                current_turn["end_step"] = step_idx
                current_turn["steps_count"] += 1
                if step_time:
                    current_turn["created_at"] = step_time
                    current_turn["created_at_raw"] = step_time_raw

                # Record tool actions
                for call in step.get("tool_calls", []):
                    t_name = call.get("name", "tool")
                    args = call.get("args", {})
                    summary = args.get("toolSummary") or args.get("toolAction") or t_name
                    current_turn["tool_actions"].append(f"{t_name}: {summary}")

                # Record errors
                if step.get("status") == "ERROR":
                    err_msg = str(step.get("content", ""))[:300]
                    current_turn["errors"].append(err_msg)

                # Record model response snippet
                content = step.get("content")
                if content and isinstance(content, str) and step_type in ("PLANNER_RESPONSE", "MODEL_RESPONSE"):
                    current_turn["model_responses"].append(content[:400])

        if current_turn:
            turns.append(current_turn)

        # Filter turns based on timestamp and step watermark
        filtered_turns = []
        for turn in turns:
            turn_time = turn.get("created_at")
            turn_step = turn.get("end_step", 0)

            is_newer_time = True
            if since_time and turn_time:
                is_newer_time = turn_time > since_time
            
            is_newer_step = turn_step > since_step

            # Ingest if newer than the timestamp watermark or step watermark
            if is_newer_time and is_newer_step:
                if turn.get("user_request") or turn.get("tool_actions"):
                    filtered_turns.append(turn)

        return filtered_turns

    def synthesize_turn_memory(
        self,
        project_name: str,
        conv_id: str,
        turn: Dict[str, Any],
        use_llm: bool = False
    ) -> str:
        """Formats a conversation turn into a structured memory markdown document."""
        user_req = turn.get("user_request", "").strip() or "General inquiry/task execution"
        time_str = turn.get("created_at_raw") or datetime.now(timezone.utc).isoformat()
        
        # Deduplicate actions
        actions = turn.get("tool_actions", [])
        unique_actions = []
        for a in actions:
            if a not in unique_actions:
                unique_actions.append(a)
        actions_str = "\n".join([f"  - {a}" for a in unique_actions[:8]]) if unique_actions else "  - Direct analysis & response"

        errors = turn.get("errors", [])
        error_str = f"\n• Errors/Blockers Encountered:\n" + "\n".join([f"  - {e}" for e in errors[:3]]) if errors else ""

        if use_llm and hasattr(self.llm, "generate") and self.llm.name != "HeuristicFallbackProvider":
            prompt = (
                f"Synthesize this developer session turn into a concise 3-line memory record.\n"
                f"Project: {project_name}\n"
                f"User Request: {user_req}\n"
                f"Actions: {', '.join(unique_actions[:5])}\n"
                f"Summary:"
            )
            try:
                llm_summary = self.llm.generate(prompt, max_tokens=150)
                if llm_summary and "[Mock Response]" not in llm_summary:
                    return (
                        f"[CONVERSATION SYNC] Project: {project_name} | Conv: {conv_id[:8]} | Time: {time_str}\n"
                        f"{llm_summary.strip()}\n"
                        f"• Context: User asked: '{user_req[:120]}'"
                    )
            except Exception:
                pass

        # Deterministic structured summary
        memory_text = (
            f"[CONVERSATION SYNC] Project: {project_name} | Conv: {conv_id[:8]} | Time: {time_str}\n"
            f"• Request / Intent: {user_req[:250]}\n"
            f"• Executed Actions:\n{actions_str}{error_str}"
        )
        return memory_text

    def sync(
        self,
        project_filter: Optional[str] = None,
        since_time: Optional[str] = None,
        limit: Optional[int] = None,
        dry_run: bool = False,
        force: bool = False,
        use_llm: bool = False
    ) -> Dict[str, Any]:
        """
        Executes cross-project conversation history memory synchronization.
        """
        baseline_time = None
        if since_time:
            baseline_time = parse_iso_datetime(since_time)
        elif not force:
            baseline_time = self.get_latest_memory_timestamp()

        print(f"[HistorySync] Initializing Conversation History Sync...")
        print(f"[HistorySync] Brain Directory: {self.brain_dir}")
        print(f"[HistorySync] Latest Memory Watermark: {baseline_time.isoformat() if baseline_time else 'None (Full History Scan)'}")
        if project_filter:
            print(f"[HistorySync] Project Filter: {project_filter}")

        transcripts = self.find_all_transcripts()
        print(f"[HistorySync] Found {len(transcripts)} conversation transcripts.")

        if limit and limit > 0:
            transcripts = transcripts[:limit]
            print(f"[HistorySync] Limiting scan to {limit} conversations.")

        stats = {
            "conversations_scanned": 0,
            "conversations_updated": 0,
            "memories_created": 0,
            "mistakes_recorded": 0,
            "latest_timestamp": baseline_time.isoformat() if baseline_time else None,
            "synced_projects": set(),
            "dry_run": dry_run
        }

        newest_seen_time = baseline_time

        for item in transcripts:
            conv_id = item["conversation_id"]
            conv_dir = item["conv_dir"]
            transcript_path = item["transcript_path"]
            stats["conversations_scanned"] += 1

            watermark = self.memory.get_history_sync_watermark(conv_id) if not force else None
            since_step = watermark["last_synced_step"] if watermark else 0
            conv_since_time = parse_iso_datetime(watermark["last_synced_time"]) if watermark and watermark.get("last_synced_time") else baseline_time
            
            # Read first few steps to determine project
            initial_steps = []
            try:
                with open(transcript_path, "r", encoding="utf-8", errors="ignore") as f:
                    for _ in range(15):
                        line = f.readline()
                        if not line:
                            break
                        try:
                            initial_steps.append(json.loads(line))
                        except Exception:
                            pass
            except Exception:
                continue

            project_name = self.extract_project_name(initial_steps, conv_dir)

            # Apply project filter
            if project_filter and project_filter.lower() not in project_name.lower():
                continue

            # Parse turns newer than watermark
            turns = self.parse_turns(
                transcript_path,
                since_time=conv_since_time if not force else None,
                since_step=since_step
            )

            if not turns:
                continue

            stats["conversations_updated"] += 1
            stats["synced_projects"].add(project_name)
            last_turn_step = turns[-1]["end_step"]
            last_turn_time_raw = turns[-1]["created_at_raw"]
            last_turn_time = turns[-1]["created_at"]

            if last_turn_time:
                if newest_seen_time is None or last_turn_time > newest_seen_time:
                    newest_seen_time = last_turn_time

            print(f"  -> [{project_name}] Conv {conv_id[:8]}: Ingesting {len(turns)} new turn(s)...")

            conv_memories_created = 0
            for turn in turns:
                memory_text = self.synthesize_turn_memory(project_name, conv_id, turn, use_llm=use_llm)
                tier = "Midterm" if len(turn.get("tool_actions", [])) > 1 else "Shortterm"
                tags = f"conversation,history-sync,{project_name},conv:{conv_id}"

                if dry_run:
                    print(f"\n[DRY RUN MEMORY ({tier}) - {project_name}]")
                    print(memory_text)
                else:
                    self.memory.save_memory(
                        text=memory_text,
                        tier=tier,
                        source="conversation-history",
                        tags=tags,
                        created_at=turn.get("created_at_raw")
                    )
                    stats["memories_created"] += 1
                    conv_memories_created += 1

                # If blockers or severe errors present, save mistake record
                if turn.get("errors") and not dry_run:
                    err_joined = "\n".join(turn["errors"])
                    self.memory.save_mistake(
                        task_id=f"{project_name}-conv-{conv_id[:8]}",
                        error_trace=err_joined,
                        context=f"Conversation turn in {project_name}: {turn.get('user_request', '')[:100]}",
                        hypothesis="Investigate failed tool call or step error from conversation history."
                    )
                    stats["mistakes_recorded"] += 1

            if not dry_run:
                self.memory.update_history_sync_state(
                    conversation_id=conv_id,
                    project_name=project_name,
                    last_step=last_turn_step,
                    last_time=last_turn_time_raw or datetime.now(timezone.utc).isoformat(),
                    new_memories_count=conv_memories_created
                )

        if newest_seen_time:
            stats["latest_timestamp"] = newest_seen_time.isoformat()

        stats["synced_projects"] = list(stats["synced_projects"])

        if not dry_run:
            self.watchdog.record_action(
                action_type="history_sync",
                target=f"{len(stats['synced_projects'])} projects",
                result_snippet=f"Ingested {stats['memories_created']} memories across {stats['conversations_updated']} conversations.",
                success=True
            )

        print("\n=== [OpenBrain] Conversation History Sync Complete ===")
        print(f"Scanned Conversations: {stats['conversations_scanned']}")
        print(f"Updated Conversations: {stats['conversations_updated']}")
        print(f"Memories Ingested: {stats['memories_created']}")
        print(f"Mistakes Recorded: {stats['mistakes_recorded']}")
        print(f"Projects Synced: {', '.join(stats['synced_projects']) if stats['synced_projects'] else 'None'}")
        print(f"New Watermark Timestamp: {stats['latest_timestamp']}")
        if dry_run:
            print("[NOTE: Ran in dry-run mode. No database records were modified.]")

        return stats
