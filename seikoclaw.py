import os
import sys
import argparse
import subprocess
import concurrent.futures
import json
import shutil
from datetime import datetime

import re
try:
    import yaml
except ImportError:
    yaml = None

# Add local paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import token_estimator
from openbrain.vault import Vault
from openbrain.usage_monitor import UsageMonitor
from openbrain.memory_engine import MemoryEngine
from openbrain.skill_gating import SkillGater
from openbrain.task_graph import TaskGraph
from openbrain.gates import GateEngine
from openbrain.watchdog import HealthPatrol
from openbrain.llm_provider import get_llm_provider
from openbrain.history_sync import ConversationHistorySyncer

def validate_command_safety(command: str) -> tuple:
    """Validates a command against dangerous regex patterns in .agents/hooks/dangerous-patterns.txt."""
    if not command:
        return True, ""
        
    patterns_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".agents", "hooks", "dangerous-patterns.txt")
    if not os.path.exists(patterns_file):
        patterns_file = os.path.join(".agents", "hooks", "dangerous-patterns.txt")
        
    patterns = []
    if os.path.exists(patterns_file):
        with open(patterns_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    patterns.append(line)
    
    for pattern in patterns:
        try:
            if re.search(pattern, command):
                return False, f"Prohibited dangerous pattern: {pattern}"
        except re.error:
            continue
            
    return True, ""

SKILL_SYNTHESIS_PROMPT = """
Analyze task trajectory (actions taken, successes, failures).
Synthesize or Evolve a "Skill" in Caveman SKILL.md format.

If PREVIOUS_SKILL is provided, perform an EVOLUTION:
1. Version bump or refine rules based on new trajectory.
2. Maintain existing technical exactness while adding new insights.

If no PREVIOUS_SKILL, perform a SYNTHESIS.

FORMAT:
---
name: [Skill Name]
evolution: Lite | Full | Ultra
version: [X.Y.Z]
---
# RULES
[thing] [action] [result].
# BOUNDARIES
What NOT to do.
# AUTO-CLARITY
Technical PIDs/Ports/Patterns.

PREVIOUS_SKILL:
{previous_skill}

TRAJECTORY:
{trajectory}
"""

# Fix for Windows terminal UTF-8 encoding issues
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        # Fallback for older python
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

class IterationBudget:
    def __init__(self, max_turns=5, max_tokens=100000, context_limit=1000000):
        self.max_turns = max_turns
        self.max_tokens = max_tokens
        self.context_limit = context_limit
        self.current_turns = 0
        self.current_tokens = 0
        self.estimated_context = 0

    def consume(self, tokens=0, context_tokens=0):
        self.current_turns += 1
        self.current_tokens += tokens
        self.estimated_context = context_tokens

    def is_exhausted(self):
        return (self.current_turns >= self.max_turns or 
                self.current_tokens >= self.max_tokens or 
                self.estimated_context >= (self.context_limit * 0.9))

    def __str__(self):
        return (f"Budget: {self.current_turns}/{self.max_turns} turns, "
                f"Session: {self.current_tokens} tokens, "
                f"Context: {self.estimated_context}/{self.context_limit}")

class SeikoClaw:
    def __init__(self, config_path=None, brain_dir=None, wiki_dir=None, db_path=None):
        # 1. Configuration Resolution Hierarchy (CLI -> ENV -> YAML -> Local Discovery)
        self.config = {}
        target_config = config_path or os.getenv("SEIKOCLAW_CONFIG") or os.path.join(os.getcwd(), ".seikoclaw.yaml")
        if not os.path.exists(target_config):
            parent_config = os.path.join(os.path.dirname(os.getcwd()), ".seikoclaw.yaml")
            if os.path.exists(parent_config):
                target_config = parent_config
        
        if os.path.exists(target_config) and yaml is not None:
            try:
                with open(target_config, "r", encoding="utf-8") as f:
                    self.config = yaml.safe_load(f) or {}
            except Exception:
                self.config = {}

        # 2. Database & Chroma Path Resolution
        resolved_db = db_path or os.getenv("OPENBRAIN_DB_PATH") or self.config.get("db_path")
        if not resolved_db:
            cwd_openbrain = os.path.join(os.getcwd(), "openbrain")
            if os.path.isdir(cwd_openbrain):
                resolved_db = os.path.join(cwd_openbrain, "openbrain.db")
                chroma_path = os.path.join(cwd_openbrain, "chroma_db")
            else:
                global_dir = os.path.join(os.path.expanduser("~"), ".gemini", "antigravity", "openbrain")
                os.makedirs(global_dir, exist_ok=True)
                resolved_db = os.path.join(global_dir, "openbrain.db")
                chroma_path = os.path.join(global_dir, "chroma_db")
        else:
            chroma_path = os.path.join(os.path.dirname(resolved_db), "chroma_db")

        # 3. Brain Directory Resolution
        resolved_brain = brain_dir or os.getenv("SEIKOCLAW_BRAIN_DIR") or self.config.get("brain_dir")
        
        # 4. Wiki Directory Resolution
        resolved_wiki = wiki_dir or os.getenv("SEIKOCLAW_WIKI_DIR") or self.config.get("wiki_dir")
        if not resolved_wiki:
            for candidate in ["../.master_wiki", "./.master_wiki", os.path.join(os.path.expanduser("~"), ".master_wiki")]:
                if os.path.isdir(candidate):
                    resolved_wiki = candidate
                    break
        self.wiki_dir = resolved_wiki

        self.sqlite_path = resolved_db
        self.chroma_path = chroma_path
        self.vault = Vault(resolved_db)
        self.usage = UsageMonitor(resolved_db)
        self.memory = MemoryEngine(resolved_db, chroma_path)
        self.gater = SkillGater()
        self.graph = TaskGraph(resolved_db)
        self.gates = GateEngine(self.graph)
        self.watchdog = HealthPatrol(db_path=resolved_db)
        self.history_syncer = ConversationHistorySyncer(
            memory_engine=self.memory, 
            watchdog=self.watchdog,
            brain_dir=resolved_brain
        )
        
        # Default limits
        self.limits = {
            "anthropic": {"tokens": 100000, "requests": 500},
            "google": {"tokens": 200000, "requests": 1000},
            "local": {"tokens": 10000000, "requests": 100000}
        }

    def sync_conversation_history(self, project=None, since=None, limit=None, dry_run=False, force=False, use_llm=False, brain_dir=None):
        """Scans conversation history transcripts across projects and syncs new events into Openbrain memory."""
        if brain_dir:
            self.history_syncer.brain_dir = brain_dir
        return self.history_syncer.sync(
            project_filter=project,
            since_time=since,
            limit=limit,
            dry_run=dry_run,
            force=force,
            use_llm=use_llm
        )

    def unlock_vault(self):
        print("[SeikoClaw] Initializing Vault...")
        password = os.getenv("SEIKOCLAW_MASTER_PASS")
        if not password:
            print("[WARNING] SEIKOCLAW_MASTER_PASS env var not set. Some features will be locked.")
            return False
        
        self.vault.unlock(password)
        return True

    def _git_run(self, cmd):
        result = subprocess.run(f"git {cmd}", shell=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
        stdout = (result.stdout or "").strip()
        stderr = (result.stderr or "").strip()
        return result.returncode, stdout, stderr

    def _is_git_repo(self):
        rc, _, _ = self._git_run("rev-parse --is-inside-work-tree")
        return rc == 0

    def _get_current_branch(self):
        rc, out, _ = self._git_run("rev-parse --abbrev-ref HEAD")
        if rc == 0:
            return out
        return None

    def _is_git_dirty(self):
        rc, out, _ = self._git_run("status --porcelain")
        return rc == 0 and bool(out)

    def start_sandbox(self, task_id):
        if not self._is_git_repo():
            print("[SANDBOX WARNING] Not a Git repository. Running without sandbox.")
            return False, None, False

        original_branch = self._get_current_branch()
        if not original_branch:
            print("[SANDBOX ERROR] Could not determine current Git branch.")
            return False, None, False

        dirty = self._is_git_dirty()
        stashed = False
        if dirty:
            print(f"[SANDBOX] Working tree is dirty. Stashing changes...")
            rc, _, err = self._git_run("stash push -m \"seikoclaw-pre-sandbox-stash\"")
            if rc != 0:
                print(f"[SANDBOX ERROR] Failed to stash changes: {err}")
                return False, None, False
            stashed = True

        sandbox_branch = f"seikoclaw-sandbox-{task_id}"
        print(f"[SANDBOX] Creating and checking out sandbox branch: {sandbox_branch}")
        
        rc, _, err = self._git_run(f"checkout -b {sandbox_branch}")
        if rc != 0:
            print(f"[SANDBOX ERROR] Failed to create sandbox branch: {err}")
            if stashed:
                print("[SANDBOX] Restoring stashed changes...")
                self._git_run("stash pop")
            return False, None, False

        return True, original_branch, stashed

    def commit_sandbox(self, task_id):
        sandbox_branch = f"seikoclaw-sandbox-{task_id}"
        print(f"[SANDBOX] Committing changes on sandbox branch: {sandbox_branch}...")
        self._git_run("add -A")
        rc, _, err = self._git_run(f"commit -m \"seikoclaw: completed task {task_id}\"")
        if rc != 0:
            print(f"[SANDBOX WARNING] Failed to commit changes (possibly no changes made): {err}")

        print(f"[SANDBOX] Sandbox branch '{sandbox_branch}' left checked out for review.")
        print(f"[SANDBOX] Review changes, or merge to main via: git checkout <main-branch> && git merge {sandbox_branch}")
        return True

    def commit_and_merge_sandbox(self, task_id, original_branch, stashed):
        sandbox_branch = f"seikoclaw-sandbox-{task_id}"
        print(f"[SANDBOX] Committing changes on {sandbox_branch}...")
        self._git_run("add -A")
        rc, _, err = self._git_run(f"commit -m \"seikoclaw: completed task {task_id}\"")
        if rc != 0:
            print(f"[SANDBOX WARNING] Failed to commit changes (possibly no changes made): {err}")

        print(f"[SANDBOX] Returning to original branch: {original_branch}")
        rc, _, err = self._git_run(f"checkout {original_branch}")
        if rc != 0:
            print(f"[SANDBOX ERROR] Failed to return to original branch: {err}")
            return False

        print(f"[SANDBOX] Merging sandbox branch {sandbox_branch}...")
        rc, _, err = self._git_run(f"merge --no-ff -m \"Merge branch '{sandbox_branch}'\" {sandbox_branch}")
        if rc != 0:
            print(f"[SANDBOX ERROR] Merge failed: {err}")
            return False

        print(f"[SANDBOX] Deleting sandbox branch {sandbox_branch}...")
        self._git_run(f"branch -d {sandbox_branch}")

        if stashed:
            print("[SANDBOX] Restoring stashed changes...")
            self._git_run("stash pop")

        return True

    def discard_sandbox(self, task_id, original_branch, stashed):
        sandbox_branch = f"seikoclaw-sandbox-{task_id}"
        print(f"[SANDBOX] Discarding sandbox changes on {sandbox_branch}...")
        
        self._git_run("reset --hard")
        self._git_run("clean -fd")

        print(f"[SANDBOX] Returning to original branch: {original_branch}")
        rc, _, err = self._git_run(f"checkout {original_branch}")
        if rc != 0:
            print(f"[SANDBOX ERROR] Failed to return to original branch: {err}")
            return False

        print(f"[SANDBOX] Deleting sandbox branch {sandbox_branch}...")
        self._git_run(f"branch -D {sandbox_branch}")

        if stashed:
            print("[SANDBOX] Restoring stashed changes...")
            self._git_run("stash pop")

        return True

    def run_task(self, name, command, cwd=None):
        """Executes a single command with safety guard, usage oversight, and watchdog telemetry."""
        # 1. Check safety guard before execution
        is_safe, block_reason = validate_command_safety(command)
        if not is_safe:
            err_msg = f"BLOCKED by safety guard: {block_reason}"
            print(f"[BLOCKED] {name}: {err_msg}")
            self.watchdog.record_action(
                action_type="command_blocked",
                target=f"{name}: {command}",
                result_snippet=err_msg,
                success=False
            )
            return f"FAILURE: {name}\nError: {err_msg}"

        provider = "local" # Local shell command execution
        
        # 2. Check limits before starting
        limit_reached, msg = self.usage.check_limits(
            provider, 
            self.limits[provider]["tokens"], 
            self.limits[provider]["requests"]
        )
        
        if limit_reached:
            print(f"[PAUSED] {name}: {msg}")
            self.watchdog.record_action(action_type="task_paused", target=name, result_snippet=msg, success=False)
            return f"SKIP: {msg}"

        print(f"[Executing] {name}: {command} (in {cwd or '.'})")
        
        # 3. Execute
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=cwd)
            
            # 4. Estimate actual token usage of the output
            output_text = result.stdout + result.stderr
            actual_tokens = token_estimator.estimate_tokens(output_text)
            
            # 5. Track usage and watchdog telemetry
            self.usage.track_usage(provider, tokens=actual_tokens, requests=1)
            self.watchdog.record_action(
                action_type="command",
                target=f"{name}: {command}",
                result_snippet=output_text[:200],
                success=(result.returncode == 0)
            )
            
            if actual_tokens > 10000:
                print(f"[CRITICAL] {name} output is {actual_tokens} tokens! Consider summarizing before next task.")

            if result.returncode == 0:
                return f"SUCCESS: {name}"
            else:
                return f"FAILURE: {name}\nError: {result.stderr}"
        except Exception as e:
            self.watchdog.record_action(action_type="command_error", target=f"{name}: {command}", result_snippet=str(e)[:200], success=False)
            return f"ERROR: {name}\nException: {str(e)}"

    def execute_parallel(self, tasks, cwd=None):
        """Runs multiple tasks in parallel using a thread pool."""
        print(f"[SeikoClaw] Launching {len(tasks)} tasks in parallel...")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            fut_to_task = {executor.submit(self.run_task, t['name'], t['command'], cwd): t for t in tasks}
            for future in concurrent.futures.as_completed(fut_to_task):
                res = future.result()
                print(f"[Completed] {res}")

    def sync_global(self):
        """Syncs local .agents and third-party skills to global locations."""
        import shutil
        user_home = os.path.expanduser("~")
        global_root = os.path.join(user_home, ".gemini", "antigravity")
        
        mapping = {
            ".agents/workflows": os.path.join(global_root, "global_workflows"),
            ".agents/skills": os.path.join(global_root, "global_skills"),
            ".agents/modular_skills": os.path.join(global_root, "skills")
        }
        
        print("[SeikoClaw] Starting Global Sync...")
        # 1. Sync custom assets
        for local_dir, global_dir in mapping.items():
            if not os.path.exists(local_dir):
                continue
            os.makedirs(global_dir, exist_ok=True)
            for item in os.listdir(local_dir):
                s = os.path.join(local_dir, item)
                d = os.path.join(global_dir, item)
                if os.path.isdir(s):
                    if os.path.exists(d):
                        shutil.rmtree(d)
                    shutil.copytree(s, d)
                    print(f"[COPIED-DIR] {item} -> {global_dir}")
                elif os.path.isfile(s):
                    shutil.copy2(s, d)
                    print(f"[COPIED-FILE] {item} -> {global_dir}")
        
        # 2. Sync Third-Party Agent Skills (Preserving directory structure)
        tp_skills_root = "third-party/agent-skills/skills"
        global_skills_dest = os.path.join(global_root, "skills", "third-party")
        if os.path.exists(tp_skills_root):
            print("[SeikoClaw] Syncing Third-Party Skills (Modular)...")
            os.makedirs(global_skills_dest, exist_ok=True)
            for skill_name in os.listdir(tp_skills_root):
                skill_dir = os.path.join(tp_skills_root, skill_name)
                if os.path.isdir(skill_dir):
                    dest_dir = os.path.join(global_skills_dest, skill_name)
                    if os.path.exists(dest_dir):
                        shutil.rmtree(dest_dir)
                    shutil.copytree(skill_dir, dest_dir)
                    print(f"[SYNCED-DIR] {skill_name} -> {global_skills_dest}")

    def reflect_on_task(self, task_file: str):
        """Analyzes a task file and synthesizes or evolves a skill using pluggable LLM provider."""
        if not os.path.exists(task_file):
            return "Error: Task file not found."

        with open(task_file, "r", encoding="utf-8") as f:
            content = f.read()

        if "[x]" not in content:
            return "No completed tasks found to reflect upon."

        print(f"[SeikoClaw] Reflecting on completed tasks in {os.path.basename(task_file)}...")
        
        # 1. Check if a neural LLM is configured
        llm = get_llm_provider()
        if getattr(llm, "is_heuristic", False) or not getattr(llm, "is_neural", False):
            print(f"[INFO] Skipping automated skill reflection: No neural LLM configured (using '{llm.name}').")
            return None

        # 2. Synthesis via Pluggable Neural LLM Provider
        try:
            print(f"[SeikoClaw] Using Neural LLM Provider for reflection: {llm.name}")
            
            import re
            skill_name_candidate = None
            match = re.search(r"Skill:\s*(.*)", content)
            if match:
                skill_name_candidate = match.group(1).strip()
            
            previous_skill_text = "None"
            if skill_name_candidate:
                prev = self.memory.get_skill(skill_name_candidate)
                if prev:
                    previous_skill_text = str(prev)
                else:
                    # Check disk to protect existing hand-written skills
                    disk_skill_path = os.path.join(".agents", "skills", skill_name_candidate, "SKILL.md")
                    if os.path.exists(disk_skill_path):
                        try:
                            with open(disk_skill_path, "r", encoding="utf-8") as f:
                                previous_skill_text = f.read()
                        except Exception:
                            pass
            
            prompt = SKILL_SYNTHESIS_PROMPT.format(trajectory=content, previous_skill=previous_skill_text)
            skill_text = llm.generate(prompt, max_tokens=1024)
            
            if skill_text and "[Mock Response]" not in skill_text:
                # 3. Extract and Sanitize Skill Name
                name_match = re.search(r"name:\s*(.*)", skill_text)
                raw_name = name_match.group(1).strip() if name_match else "new-skill"
                skill_name = re.sub(r"[^\w\-]", "-", raw_name.lower()).strip("-") or "new-skill"
                
                # Ensure skill_text has the sanitized name
                skill_text = re.sub(r"name:\s*.*", f"name: {skill_name}", skill_text, count=1)
                
                # 4. Gating check before saving to candidate staging directory
                passed, gate_msg = self.gater.gate_and_save(
                    skill_text=skill_text,
                    skill_name=skill_name,
                    memory_engine=self.memory,
                    target_dir=".agents/skills",
                    previous_skill_text=previous_skill_text if previous_skill_text != "None" else None,
                    staging=True
                )
                
                if passed:
                    print(f"[STAGED CANDIDATE] { 'Evolved' if previous_skill_text != 'None' else 'Synthesized' } candidate skill: {skill_name}")
                    print(f"[INFO] Candidate saved to .agents/skills/.candidates/{skill_name}/SKILL.md. Use 'seikoclaw skill --promote {skill_name}' to apply.")
                    return skill_name
                else:
                    print(f"[GATING FAILED] {gate_msg}")
                    return None
        except Exception as e:
            print(f"[ERROR] Skill reflection failed: {e}")
            return None

    def gate_skill(self, skill_target: str):
        """Runs validation and regression tests against a skill file or registered skill."""
        print(f"[SeikoClaw] Gating skill: {skill_target}...")
        skill_text = ""
        if os.path.exists(skill_target):
            with open(skill_target, "r", encoding="utf-8") as f:
                skill_text = f.read()
        else:
            # Check Openbrain
            skill_record = self.memory.get_skill(skill_target)
            if skill_record and skill_record.get("example"):
                skill_text = skill_record["example"]
            else:
                # Check .agents/skills/<skill_target>/SKILL.md
                candidate_path = os.path.join(".agents", "skills", skill_target, "SKILL.md")
                if os.path.exists(candidate_path):
                    with open(candidate_path, "r", encoding="utf-8") as f:
                        skill_text = f.read()

        if not skill_text:
            print(f"[ERROR] Could not resolve skill content for: {skill_target}")
            return False

        passed, reason = self.gater.evaluate_regression(skill_text)
        if passed:
            print(f"[GATE PASS] Skill '{skill_target}' passed all validation and regression checks.")
            return True
        else:
            print(f"[GATE FAIL] Skill '{skill_target}' failed gating:\n  Reason: {reason}")
            return False

    def sync_wiki(self, message="Auto-sync from SeikoClaw"):
        """Syncs the current project state into the Master Wiki."""
        print("[SeikoClaw] Syncing state to Master Wiki...")
        wiki_dir = os.getenv("SEIKOCLAW_WIKI_DIR")
        if not wiki_dir or not os.path.exists(wiki_dir):
            for candidate in ["../.master_wiki", "./.master_wiki", os.path.join(os.path.expanduser("~"), ".master_wiki")]:
                if os.path.exists(candidate):
                    wiki_dir = candidate
                    break

        if not wiki_dir or not os.path.exists(wiki_dir):
            print("[INFO] Master Wiki not configured. Skipping wiki sync.")
            return
            
        # 1. Read task.md for progress
        progress = "No recent task info found."
        task_paths = ["task.md", "artifact/task.md"]
        for p in task_paths:
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8") as f:
                    progress = f.read()
                break
                
        # 2. Prepare payload for llmwiki-cli
        page_data = {
            "title": "Latest Task Sync",
            "tags": ["auto-sync", "seikoclaw"],
            "content": f"## Recent Progress\n\n```markdown\n{progress[:2000]}\n```"
        }
        json_input = json.dumps(page_data)
        
        # 3. Write directly to wiki directory
        print("[SeikoClaw] Writing progress to master wiki...")
        try:
            target_page = os.path.join(wiki_dir, "wiki", "synthesis", "latest_sync.md")
            os.makedirs(os.path.dirname(target_page), exist_ok=True)
            with open(target_page, "w", encoding="utf-8") as f:
                f.write(f"# Latest Task Sync\n\nTags: auto-sync, seikoclaw\n\n## Recent Progress\n\n```markdown\n{progress[:2000]}\n```\n")

            # 4. Auto-commit if wiki_dir is a git repo
            subprocess.run(["git", "add", "."], cwd=wiki_dir, shell=True, capture_output=True, timeout=10)
            subprocess.run(["git", "commit", "-m", f"Auto-sync: {message}"], cwd=wiki_dir, shell=True, capture_output=True, timeout=10)
            print("[SUCCESS] Master Wiki updated.")
        except Exception as e:
            print(f"[WARNING] Master Wiki sync encountered an issue: {e}")

    def manage_kanban(self, action, task_id=None, status=None, project="default"):
        """CLI helper for Kanban operations."""
        if action == "list":
            board = self.memory.get_kanban(project)
            print(f"--- Kanban Board: {project} ---")
            if not board:
                print("No tasks found.")
            for tid, info in board.items():
                print(f"[{info['status']}] {tid} (Updated: {info['updated_at']})")
        elif action == "update" and task_id and status:
            self.memory.update_kanban(project, task_id, status)
            print(f"[SUCCESS] Updated {task_id} to {status}")

    def loop_until_goal(self, goal, max_turns=5, mode="simulate", worker_id="loop-worker"):
        """
        Autonomous loop for SeikoClaw.
        - 'simulate': Context estimation & handoff benchmark loop.
        - 'dag': Live DAG task pump that claims and executes ready frontier tasks.
        """
        budget = IterationBudget(max_turns=max_turns)
        print(f"[SeikoClaw] Starting autonomous loop (mode={mode}) for goal: {goal}")
        
        while not budget.is_exhausted():
            print(f"\n--- Turn {budget.current_turns + 1} ---")
            
            # 1. Estimate current context
            memories = self.memory.retrieve_similar(goal, n_results=20)
            context_text = "\n".join([m['content'] for m in memories])
            current_context_tokens = token_estimator.estimate_tokens(context_text)
            
            budget.consume(tokens=0, context_tokens=current_context_tokens)
            print(f"[STATUS] {budget}")
            
            # 2. Watchdog Health & Circuit-Breaker Check
            health = self.watchdog.get_health_status(current_tokens=current_context_tokens)
            if health.get("is_spinning"):
                spin_msg = health.get("spin_reason")
                print(f"[CIRCUIT BREAKER] {spin_msg}")
                self.memory.save_mistake(
                    task_id=f"loop-stall-turn-{budget.current_turns}",
                    error_trace=spin_msg,
                    context=f"Autonomous loop for goal: {goal}",
                    hypothesis="Execution halted by watchdog circuit breaker. Resolve repetitive failures."
                )
                break

            # 3. Check for context ceiling / auto-handoff
            if current_context_tokens >= (budget.context_limit * 0.9):
                print(f"[CRITICAL] Context limit reached ({current_context_tokens} tokens).")
                print("[ACTION] Performing auto-handoff...")
                handoff_path = "handoff.md"
                with open(handoff_path, "w", encoding="utf-8") as f:
                    f.write(f"# Handoff: {goal}\n\nLoop paused due to context pressure.\n")
                    f.write(f"Tokens: {current_context_tokens}\n")
                    f.write(f"Last Action: Loop Turn {budget.current_turns}\n")
                print(f"[ALERT] Handoff created at {handoff_path}. Please start a new session.")
                break

            # 4. Mode Execution
            if mode == "dag":
                # Active DAG task pump
                claimed = self.graph.claim_next_ready(worker_id=worker_id, filter_gates=True)
                if not claimed:
                    # Check if tasks are blocked
                    remaining = self.graph.list_tasks(status="open")
                    if remaining:
                        print(f"[INFO] DAG pump complete: {len(remaining)} open tasks remain, but all are blocked by dependencies or pending gates.")
                    else:
                        print("[SUCCESS] All open DAG tasks completed!")
                    break

                task_id = claimed["id"]
                task_title = claimed["title"]
                meta = claimed.get("gate_metadata", {})
                cmd = meta.get("command") or f"echo 'Executing DAG task {task_id}: {task_title}'"
                
                print(f"[DAG ACTION] Claimed: {task_id} - {task_title}")
                res = self.run_task(task_title, cmd)
                if "SUCCESS" in res:
                    # Update status to closed
                    self.graph.close_task(task_id)
                    print(f"[DAG SUCCESS] Task {task_id} marked as closed.")
                else:
                    self.graph.update_status(task_id, "open")
                    print(f"[DAG RETRY] Task {task_id} command failed; returned to open pool.")
            else:
                # Simulation Mode
                if "complete" in goal.lower():
                    print("[SUCCESS] Goal detected as complete.")
                    break
                
                # Memory Compression (Maintenance)
                if self.memory.context_engine.compress_shortterm(threshold=5):
                    print("[MAINTENANCE] Compressed recent short-term memories into Midterm.")

                print("[ACTION] Implementing simulated next step...")
                self.watchdog.record_action("simulated_step", goal, f"Turn {budget.current_turns}", success=True)
            
        if budget.is_exhausted() and current_context_tokens < (budget.context_limit * 0.9):
            print("[PAUSED] Iteration budget exhausted.")

        # Post-Task Reflection Hook: Trigger auto-reflection if task.md exists
        for p in ["task.md", "artifact/task.md"]:
            if os.path.exists(p):
                print("[AUTO-HOOK] Triggering Post-Task Reflection Hook...")
                self.reflect_on_task(p)
                self.sync_wiki(f"Auto-sync after loop for goal: {goal}")
                break

    def show_ready_frontier(self, claim=False, worker_id="executor-1", as_json=False):
        """Displays or atomically claims the ready frontier from the Task DAG."""
        if claim:
            claimed = self.graph.claim_next_ready(worker_id=worker_id, filter_gates=True)
            if claimed:
                if as_json:
                    print(json.dumps(claimed, indent=2))
                else:
                    gate_info = f" [GATE: {claimed['gate_type'].upper()}]" if claimed.get('gate_type') else ""
                    print(f"[CLAIMED] Worker '{worker_id}' successfully claimed: {claimed['id']} - {claimed['title']}{gate_info}")
            else:
                if as_json:
                    print(json.dumps({"status": "empty", "message": "No ready tasks available on frontier."}))
                else:
                    print("[INFO] No ready tasks available on the frontier.")
            return claimed

        # Inspection view shows both claimable and pending-gated tasks
        all_frontier = self.graph.get_ready_frontier(filter_gates=False)
        claimable = [t for t in all_frontier if not t.get("gate_type") or t.get("gate_status") in ("passed", "bypassed")]
        gated = [t for t in all_frontier if t.get("gate_type") and t.get("gate_status") == "pending"]

        if as_json:
            print(json.dumps({"claimable": claimable, "pending_gates": gated}, indent=2))
        else:
            print("=== 🚀 SeikoClaw Ready Frontier (Claimable Work) ===")
            if not claimable:
                print("No unblocked claimable tasks. All tasks are closed or waiting on blockers/gates.")
            for t in claimable:
                wisp = " [WISP]" if t.get('is_ephemeral') else ""
                print(f"- {t['id']}: {t['title']} (P{t['priority']}){wisp}")

            if gated:
                print("\n=== 🚧 Tasks Awaiting Gate Certification ===")
                for t in gated:
                    print(f"- {t['id']}: {t['title']} (P{t['priority']}) [GATE: {t['gate_type'].upper()} - PENDING]")
        return all_frontier

    def show_health_status(self):
        """Displays health patrol diagnostics and watchdog recommendations."""
        status = self.watchdog.get_health_status()
        print("=== 🛡️ SeikoClaw Health Patrol Status ===")
        print(f"Status: {status['status']}")
        print(f"Is Spinning: {status['is_spinning']}")
        if status.get('spin_reason'):
            print(f"Alert: {status['spin_reason']}")
        print(f"Context Utilization: {status['context_utilization']*100:.1f}%")
        print(f"Total Tracked Actions: {status['total_actions']}")
        if status['recommendations']:
            print("Recommendations:")
            for rec in status['recommendations']:
                print(f"  * {rec}")
        return status

    def generate_visual_plan(self, task_file="task.md"):
        """Generates a visual plan from a task file or master vision and serves the local bridge."""
        import re
        import json
        print(f"[SeikoClaw] Generating Visual Plan from {task_file}...")
        
        # 1. Resolve content
        content = ""
        if os.path.exists(task_file):
            with open(task_file, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            # Fallback to project_vision.md
            vision_path = "project_vision.md"
            if os.path.exists(vision_path):
                with open(vision_path, "r", encoding="utf-8") as f:
                    content = f.read()
            else:
                content = "No task file found."

        # 2. Setup directory
        plan_dir = os.path.join(".agents", "plans", "plan")
        os.makedirs(plan_dir, exist_ok=True)
        
        # 3. Write plan.mdx
        header_text = (
            "---\n"
            'title: "SeikoClaw Visual Plan"\n'
            'brief: "Visual plan generated for task planning"\n'
            "localOnly: true\n"
            "---\n\n"
            "# SeikoClaw Task Plan\n\n"
            "## Task Description\n"
            f"{content}\n\n"
            "<Checklist id=\"seikoclaw-checklist\" items={[\n"
        )
        mdx_content = header_text
        # Convert checklist lines
        item_id = 1
        for line in content.splitlines():
            # Match task checklist item
            m = re.match(r"^\s*-\s*\[\s*\]\s*(.*)", line)
            if m:
                label = m.group(1).replace('"', '\\"').strip()
                mdx_content += f'  {{ id: "task-{item_id}", label: "{label}" }},\n'
                item_id += 1
        
        mdx_content += "]}\n/>\n"
        
        plan_mdx_path = os.path.join(plan_dir, "plan.mdx")
        with open(plan_mdx_path, "w", encoding="utf-8") as f:
            f.write(mdx_content)
        
        # 4. Serve the bridge
        agent_native_env = os.getenv("AGENT_NATIVE_CMD")
        if agent_native_env and os.path.exists(agent_native_env):
            cmd_prefix = agent_native_env
        else:
            cmd_prefix = shutil.which("agent-native") or "npx -y @agent-native/core"

        print("[SeikoClaw] Checking visual plan syntax...")
        try:
            subprocess.run(f"{cmd_prefix} plan local check --dir .agents/plans/plan", shell=True, timeout=15)
            print("[SeikoClaw] Serving visual plan on local bridge...")
            subprocess.Popen(f"{cmd_prefix} plan local serve --dir .agents/plans/plan --kind plan --open", shell=True)
        except Exception as e:
            print(f"[INFO] Visual plan bridge invocation skipped: {e}")
        
        # Read the URL
        url_file = os.path.join(plan_dir, ".plan-url")
        import time
        time.sleep(2)
        if os.path.exists(url_file):
            with open(url_file, "r", encoding="utf-8") as f:
                url = f.read().strip()
            print(f"[SUCCESS] Visual Plan served successfully!\nLocal Bridge URL: {url}")
        else:
            print("[INFO] Bridge starting. Open the local bridge URL from console logs.")

    def generate_visual_recap(self, task_id="current-task"):
        """Generates a visual recap from git diff and serves the local bridge."""
        import json
        print(f"[SeikoClaw] Generating Visual Recap for task: {task_id}...")
        
        # 1. Gather diff files
        rc, diff_stat, _ = self._git_run("diff --name-status HEAD")
        if rc != 0 or not diff_stat:
            # Try last commit if working tree is clean
            rc, diff_stat, _ = self._git_run("diff-tree --no-commit-id --name-status -r HEAD")
            is_last_commit = True
        else:
            is_last_commit = False

        if not diff_stat:
            print("[SeikoClaw] No git changes detected. Skipping recap.")
            return None

        recap_dir = os.path.join(".agents", "plans", "recap")
        os.makedirs(recap_dir, exist_ok=True)
        
        file_items = []
        diff_blocks = ""
        diff_id = 1
        
        for line in diff_stat.splitlines():
            parts = line.split()
            if len(parts) >= 2:
                status, filepath = parts[0], parts[1]
                change_type = "modified"
                if "A" in status:
                    change_type = "added"
                elif "D" in status:
                    change_type = "removed"
                
                # Normalize filepath for forward slashes
                filepath_normalized = filepath.replace("\\", "/")
                file_items.append({"path": filepath_normalized, "change": change_type})
                
                # Fetch before/after content for Diff blocks
                before_content = ""
                after_content = ""
                
                # If file exists, read it
                if os.path.exists(filepath):
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        after_content = f.read()
                        
                # Git show previous content
                git_ref = "HEAD" if not is_last_commit else "HEAD~1"
                rc_show, show_out, _ = self._git_run(f"show {git_ref}:{filepath}")
                if rc_show == 0:
                    before_content = show_out
                
                # Format code/diff blocks (escaping for MDX syntax)
                before_escaped = before_content.replace("`", "\\`").replace("$", "\\$")
                after_escaped = after_content.replace("`", "\\`").replace("$", "\\$")
                
                diff_blocks += f"""
<Diff 
  id="diff-{diff_id}" 
  filename="{filepath_normalized}" 
  language="{filepath_normalized.split('.')[-1] if '.' in filepath_normalized else 'text'}" 
  before={{{json.dumps(before_escaped)}}}
  after={{{json.dumps(after_escaped)}}}
  summary="Code changes in {filepath_normalized}" 
/>
"""
                diff_id += 1

        file_tree_json = json.dumps(file_items)
        
        mdx_content = f"""---
title: "SeikoClaw Task Recap"
brief: "Visual recap generated on completion of {task_id}"
localOnly: true
kind: recap
---

# SeikoClaw Task Recap

## Changed Files
<FileTree items={file_tree_json} />

## Code Walkthrough
{diff_blocks}
"""
        
        recap_mdx_path = os.path.join(recap_dir, "plan.mdx")
        with open(recap_mdx_path, "w", encoding="utf-8") as f:
            f.write(mdx_content)
            
        agent_native_env = os.getenv("AGENT_NATIVE_CMD")
        if agent_native_env and os.path.exists(agent_native_env):
            cmd_prefix = agent_native_env
        else:
            cmd_prefix = shutil.which("agent-native") or "npx -y @agent-native/core"

        print("[SeikoClaw] Checking visual recap syntax...")
        try:
            subprocess.run(f"{cmd_prefix} plan local check --dir .agents/plans/recap", shell=True, timeout=15)
            print("[SeikoClaw] Serving visual recap on local bridge...")
            subprocess.Popen(f"{cmd_prefix} plan local serve --dir .agents/plans/recap --kind recap --open", shell=True)
        except Exception as e:
            print(f"[INFO] Visual recap bridge invocation skipped: {e}")
        
        url_file = os.path.join(recap_dir, ".plan-url")
        import time
        time.sleep(2)
        if os.path.exists(url_file):
            with open(url_file, "r", encoding="utf-8") as f:
                url = f.read().strip()
            print(f"[SUCCESS] Visual Recap served successfully!\nLocal Bridge URL: {url}")
            return url
        else:
            print("[INFO] Bridge starting. Open the local bridge URL from console logs.")
            return None

def main():
    parser = argparse.ArgumentParser(description="SeikoClaw Harness CLI")
    parser.add_argument("action", choices=[
        "plan", "execute", "usage", "doctor", "sync-global", "memory", 
        "reflect", "wiki-sync", "kanban", "loop", "recap", "gate-skill", "skill",
        "ready", "claim", "task", "dep", "wisp", "gate", "health", "sync-tasks", "vault",
        "sync-history", "history-sync", "export-skills"
    ])
    parser.add_argument("--task", type=str, help="Task ID or target")
    parser.add_argument("--skill", type=str, help="Skill name or file to test/gate")
    parser.add_argument("--harness", type=str, default="agents", help="Target harness for export-skills (claude, codex, pi, antigravity, agents, all, custom)")
    parser.add_argument("--target", type=str, help="Target directory for export-skills (when harness is custom or path is explicit)")
    parser.add_argument("--symlink", action="store_true", help="Use symlinks instead of copying when exporting skills")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing destination skills during export")
    parser.add_argument("--list-candidates", action="store_true", help="List staged candidate skills")
    parser.add_argument("--diff", action="store_true", help="Show diff for candidate skill vs production")
    parser.add_argument("--promote", action="store_true", help="Promote candidate skill to production")
    parser.add_argument("--status", type=str, help="Task status (open, in_progress, in_qa, closed, deferred)")
    parser.add_argument("--goal", type=str, help="Goal description for autonomous loop")
    parser.add_argument("--turns", type=int, default=5, help="Max loop turns")
    parser.add_argument("--dag", action="store_true", help="Run autonomous loop in DAG task pump mode")
    parser.add_argument("--simulate", action="store_true", help="Run autonomous loop in token simulation mode")
    parser.add_argument("--command", type=str, help="Command to run when executing a task")
    parser.add_argument("--verify", type=str, help="Verification command to run after executing a task")
    parser.add_argument("--sandbox", action="store_true", help="Enable git-backed sandboxing for execution")
    parser.add_argument("--query", type=str, help="Search query for memory or secret key")
    parser.add_argument("--set-secret", type=str, help="Set secret in vault (KEY=VALUE)")
    parser.add_argument("--get-secret", type=str, help="Get secret from vault by KEY")
    
    parser.add_argument("--auto-merge", action="store_true", help="Auto-merge sandbox branch to original branch on success (default is to leave sandbox branch checked out for review)")
    parser.add_argument("--config", type=str, help="Path to custom .seikoclaw.yaml configuration file")
    
    # Conversation History Sync flags
    parser.add_argument("--since", type=str, help="Sync history events newer than ISO timestamp or SQLite datetime")
    parser.add_argument("--brain-dir", type=str, help="Custom brain conversation transcripts directory")
    parser.add_argument("--project", type=str, help="Filter history sync by project name")
    parser.add_argument("--limit", type=int, help="Limit number of conversations to sync")
    parser.add_argument("--dry-run", action="store_true", help="Preview history sync memories without writing")
    parser.add_argument("--force", action="store_true", help="Force sync ignoring previous watermarks")
    parser.add_argument("--use-llm", action="store_true", help="Use active LLM provider for memory synthesis")
    parser.add_argument("--sync-history", action="store_true", help="Trigger conversation history sync (when using memory action)")
    parser.add_argument("--stats", action="store_true", help="Show history sync statistics and watermark states")
    
    # Hybrid DAG & Fleet CLI flags
    parser.add_argument("--claim", action="store_true", help="Claim ready task atomically from frontier")
    parser.add_argument("--worker", type=str, default="executor-1", help="Worker ID for task claims and QA signatures")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    parser.add_argument("--title", type=str, help="Task or wisp title")
    parser.add_argument("--desc", type=str, default="", help="Task or wisp description")
    parser.add_argument("--priority", type=int, default=2, help="Priority (0=critical, 1=high, 2=normal, 3=low)")
    parser.add_argument("--parent", type=str, help="Parent task ID")
    parser.add_argument("--gate-type", type=str, help="Gate type (qa, human, test, timer, merge-slot)")
    parser.add_argument("--from-id", type=str, help="Source/blocker task ID")
    parser.add_argument("--to-id", type=str, help="Target/blocked task ID")
    parser.add_argument("--edge-type", type=str, default="blocks", help="Dependency edge type (blocks, parent-child, waits-for, relates-to)")
    parser.add_argument("--certify-qa", action="store_true", help="Certify task QA gate as passed (Seikojin-QA)")
    parser.add_argument("--certify-adversarial", action="store_true", help="Certify task adversarial interrogation gate as passed (/interrogate)")
    parser.add_argument("--pass-rate", type=float, default=1.0, help="Test pass rate for Seikojin QA certification (1.0 = 100%%)")
    parser.add_argument("--playbook", type=str, help="Declarative playbook name (bug-fix, feature, hillclimb, refactoring, visual-parity, shipping)")
    parser.add_argument("--approve", action="store_true", help="Approve human or verification gate")
    parser.add_argument("--purge", action="store_true", help="Purge completed ephemeral wisps")
    parser.add_argument("--notes", type=str, default="", help="Gate certification notes")
    
    args = parser.parse_args()
    claw = SeikoClaw(config_path=args.config, brain_dir=args.brain_dir)

    if args.action == "ready":
        claw.show_ready_frontier(claim=args.claim, worker_id=args.worker, as_json=args.json)
    elif args.action == "claim":
        if not args.task:
            print("Error: --task <task_id> is required for claim.")
            sys.exit(1)
        ok = claw.graph.claim_task(args.task, args.worker)
        if ok:
            print(f"[SUCCESS] Worker '{args.worker}' claimed task {args.task}.")
        else:
            print(f"[FAILED] Could not claim task {args.task}. Ensure task exists and is open.")
    elif args.action == "task":
        if args.title:
            tid = claw.graph.create_task(
                title=args.title,
                description=args.desc,
                priority=args.priority,
                parent_id=args.parent,
                gate_type=args.gate_type,
                task_id=args.task,
                playbook=args.playbook
            )
            print(f"[SUCCESS] Created task: {tid} - {args.title}" + (f" [Playbook: {args.playbook}]" if args.playbook else ""))
            claw.graph.sync_to_file("task.md")
        elif args.task and args.status:
            claw.graph.update_status(args.task, args.status)
            print(f"[SUCCESS] Updated {args.task} status to '{args.status}'")
            claw.graph.sync_to_file("task.md")
        elif args.task:
            t = claw.graph.get_task(args.task)
            print(json.dumps(t, indent=2) if t else f"Task {args.task} not found.")
        else:
            tasks = claw.graph.list_tasks()
            for t in tasks:
                print(f"[{t['status']}] {t['id']}: {t['title']} (P{t['priority']})")
    elif args.action == "dep":
        if not args.from_id or not args.to_id:
            print("Error: --from-id and --to-id are required.")
            sys.exit(1)
        try:
            claw.graph.add_dependency(args.from_id, args.to_id, edge_type=args.edge_type)
            print(f"[SUCCESS] Added dependency: {args.from_id} --({args.edge_type})--> {args.to_id}")
            claw.graph.sync_to_file("task.md")
        except ValueError as e:
            print(f"[ERROR] {e}")
            sys.exit(1)
    elif args.action == "wisp":
        if args.purge:
            n = claw.graph.purge_wisps()
            print(f"[SUCCESS] Purged {n} closed wisps.")
        elif args.title:
            wid = claw.graph.create_wisp(args.title, description=args.desc, parent_id=args.parent)
            print(f"[SUCCESS] Created wisp: {wid} - {args.title}")
            claw.graph.sync_to_file("task.md")
        else:
            wisps = [t for t in claw.graph.list_tasks() if t.get("is_ephemeral")]
            print("=== 👻 Ephemeral Wisps ===")
            for w in wisps:
                print(f"[{w['status']}] {w['id']}: {w['title']}")
    elif args.action == "gate":
        if not args.task:
            print("Error: --task <task_id> is required for gate commands.")
            sys.exit(1)
        if args.certify_qa:
            ok, msg = claw.gates.certify_qa_gate(
                args.task,
                engineer_signature=args.worker,
                pass_rate=args.pass_rate,
                notes=args.notes
            )
            print(f"[{'PASS' if ok else 'REJECT'}] {msg}")
            if ok:
                claw.graph.sync_to_file("task.md")
        elif args.certify_adversarial:
            ok, msg = claw.gates.certify_adversarial_gate(
                args.task,
                reviewer_model=args.worker,
                notes=args.notes
            )
            print(f"[{'PASS' if ok else 'REJECT'}] {msg}")
            if ok:
                claw.graph.sync_to_file("task.md")
        elif args.approve:
            ok = claw.gates.approve_human_gate(args.task, approver=args.worker, notes=args.notes)
            if ok:
                print(f"[SUCCESS] Gate approved for task {args.task}.")
                claw.graph.sync_to_file("task.md")
        elif args.gate_type:
            claw.gates.attach_gate(args.task, args.gate_type)
            print(f"[SUCCESS] Attached gate '{args.gate_type}' to task {args.task}.")
            claw.graph.sync_to_file("task.md")
        else:
            sat, reason = claw.gates.evaluate_gate(args.task)
            print(f"[GATE EVALUATION] {args.task}: {'SATISFIED' if sat else 'BLOCKED'} - {reason}")
    elif args.action == "health":
        claw.show_health_status()
    elif args.action == "sync-tasks":
        claw.graph.sync_to_file("task.md")
        print("[SUCCESS] Synchronized task graph to task.md.")
    elif args.action == "plan":
        task_file = args.task or "task.md"
        claw.generate_visual_plan(task_file)
    elif args.action == "recap":
        task_id = args.task or "current-task"
        claw.generate_visual_recap(task_id)
    elif args.action == "sync-global":
        claw.sync_global()
    elif args.action == "wiki-sync":
        claw.sync_wiki()
    elif args.action == "kanban":
        if args.task and args.status:
            claw.manage_kanban("update", task_id=args.task, status=args.status)
        else:
            claw.manage_kanban("list")
    elif args.action == "vault":
        key = args.get_secret or args.query or args.task
        secret_entry = args.set_secret
        if secret_entry:
            pw = os.getenv("SEIKOCLAW_MASTER_PASS")
            if not pw:
                print("[ERROR] SEIKOCLAW_MASTER_PASS environment variable is required to write to Vault.")
                sys.exit(1)
            claw.vault.unlock(pw)
            if "=" in secret_entry:
                k, v = secret_entry.split("=", 1)
            elif args.desc:
                k, v = secret_entry, args.desc
            else:
                print("[ERROR] Provide secret as KEY=VALUE or use --desc VALUE.")
                sys.exit(1)
            claw.vault.set_secret(k.strip(), v.strip())
            print(f"[VAULT SUCCESS] Stored encrypted secret '{k.strip()}' in Vault.")
        elif key:
            pw = os.getenv("SEIKOCLAW_MASTER_PASS")
            if not pw:
                print("[ERROR] SEIKOCLAW_MASTER_PASS environment variable is required to unlock Vault.")
                sys.exit(1)
            claw.vault.unlock(pw)
            val = claw.vault.get_secret(key)
            if val is not None:
                print(f"[VAULT] {key} = {val}")
            else:
                print(f"[VAULT] Secret '{key}' not found in vault.")
        else:
            print("Usage: seikoclaw vault --set-secret KEY=VALUE or seikoclaw vault --get-secret KEY")
    elif args.action == "loop":
        goal = args.goal or "Run pending ready DAG tasks"
        mode = "dag" if args.dag else ("simulate" if args.simulate else "simulate")
        claw.loop_until_goal(goal, max_turns=args.turns, mode=mode, worker_id=args.worker)
    elif args.action in ("sync-history", "history-sync"):
        if args.stats:
            states = claw.memory.list_history_sync_states()
            print("=== 📜 SeikoClaw Conversation History Sync States ===")
            if not states:
                print("No conversations have been synced yet.")
            for s in states:
                print(f"[{s['project_name']}] Conv {s['conversation_id'][:8]} | Last Step: {s['last_synced_step']} | Last Time: {s['last_synced_time']} | Memories: {s['memories_count']}")
        else:
            claw.sync_conversation_history(
                project=args.project,
                since=args.since,
                limit=args.limit,
                dry_run=args.dry_run,
                force=args.force,
                use_llm=args.use_llm,
                brain_dir=args.brain_dir
            )
    elif args.action == "memory":
        if args.sync_history:
            claw.sync_conversation_history(
                project=args.project,
                since=args.since,
                limit=args.limit,
                dry_run=args.dry_run,
                force=args.force,
                use_llm=args.use_llm,
                brain_dir=args.brain_dir
            )
        elif args.stats:
            states = claw.memory.list_history_sync_states()
            print("=== 📜 SeikoClaw Conversation History Sync States ===")
            if not states:
                print("No conversations have been synced yet.")
            for s in states:
                print(f"[{s['project_name']}] Conv {s['conversation_id'][:8]} | Last Step: {s['last_synced_step']} | Last Time: {s['last_synced_time']} | Memories: {s['memories_count']}")
        elif args.query:
            print(f"--- Searching memories for: '{args.query}' ---")
            results = claw.memory.retrieve_similar(args.query)
            if not results:
                print("No matches found.")
            for r in results:
                print(f"[{r['metadata']['tier']}] {r['metadata']['source']}:")
                print(f"{r['content'][:500]}...") # Show snippet
                print("-" * 20)
        else:
            print("Usage: seikoclaw memory --query <search> or seikoclaw memory --sync-history")
    elif args.action == "reflect":
        if args.task:
            claw.reflect_on_task(args.task)
        else:
            print("Error: --task is required for reflection.")
    elif args.action == "gate-skill":
        skill_target = args.skill or args.task
        if skill_target:
            claw.gate_skill(skill_target)
        else:
            print("Error: --skill (or --task) is required for gate-skill.")
    elif args.action == "skill":
        skill_target = args.skill or args.task
        if args.list_candidates:
            cands = claw.gater.list_candidates()
            print("=== 🧪 Staged Candidate Skills ===")
            if not cands:
                print("No candidate skills currently staged in .agents/skills/.candidates/.")
            for c in cands:
                print(f"• {c['name']} -> {c['path']}")
        elif args.diff:
            if not skill_target:
                print("Error: --skill <name> is required to diff a candidate.")
                sys.exit(1)
            diff_text = claw.gater.diff_candidate(skill_target)
            print(f"=== 🔍 Candidate Diff: {skill_target} ===")
            print(diff_text)
        elif args.promote:
            if not skill_target:
                print("Error: --skill <name> is required to promote a candidate.")
                sys.exit(1)
            ok, msg = claw.gater.promote_candidate(skill_target, memory_engine=claw.memory)
            print(f"[{'SUCCESS' if ok else 'FAILED'}] {msg}")
        else:
            print("Usage: seikoclaw skill [--list-candidates | --diff <name> | --promote <name>]")
    elif args.action == "export-skills":
        from scripts.export_skills import export_skills, HARNESS_MAP
        source_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".agents", "skills")
        if args.harness == "all":
            targets = list(HARNESS_MAP.values())
        elif args.harness == "custom":
            if not args.target:
                print("[ERROR] --target <path> is required when --harness custom is selected.")
                sys.exit(1)
            targets = [args.target]
        else:
            targets = [HARNESS_MAP.get(args.harness, args.target or HARNESS_MAP["agents"])]

        for t in targets:
            count = export_skills(source_dir, t, use_symlinks=args.symlink, overwrite=args.overwrite)
            print(f"[EXPORT SUCCESS] Exported {count} canonical skills to {t}")
    elif args.action == "usage":
        print("--- Today's Usage ---")
        for p in ["anthropic", "google", "local"]:
            u = claw.usage.get_todays_usage(p)
            print(f"{p.upper()}: {u['tokens']} tokens, {u['requests']} requests")
    elif args.action == "doctor":
        print("=== 🩺 SeikoClaw System Diagnostics ===")
        config_status = 'OK' if claw.config else 'DEFAULT (Local Discovery)'
        print(f"Configuration: {config_status}")
        db_path = claw.sqlite_path
        print(f"SQLite Database: {db_path} [{'OK' if os.path.exists(db_path) else 'FAIL'}]")
        chroma_ok = claw.memory.collection is not None
        print(f"ChromaDB Vector Store: {claw.chroma_path} [{'OK' if chroma_ok else 'FALLBACK (SQLite)'}]")
        
        llm = get_llm_provider()
        neural_status = "NEURAL" if getattr(llm, "is_neural", False) else "HEURISTIC FALLBACK"
        print(f"Background LLM Provider: {llm.name} [{neural_status}]")
        
        wiki_dir = claw.wiki_dir
        has_wiki = bool(wiki_dir and os.path.isdir(wiki_dir))
        print(f"Master Wiki: {wiki_dir or 'Unconfigured'} [{'OK' if has_wiki else 'OPTIONAL (Unconfigured)'}]")
        
        total_tasks = len(claw.graph.list_tasks())
        ready_frontier = len(claw.graph.get_ready_frontier())
        print(f"Task Graph Nodes: {total_tasks} total ({ready_frontier} on ready frontier)")
        
        # Test guard status
        guard_test, _ = validate_command_safety("git status")
        guard_block, _ = validate_command_safety("rm -rf /")
        guard_ok = guard_test and not guard_block
        print(f"Deny-Dangerous Guard: [{'OK' if guard_ok else 'FAIL'}]")

        health = claw.watchdog.get_health_status()
        print(f"Health Patrol: {health['status']} ({health['total_actions']} tracked actions)")
        print("[SUCCESS] Diagnostics complete.")
    elif args.action == "execute":
        if args.command:
            if not args.task:
                print("Error: --task is required when --command is provided.")
                sys.exit(1)
            print(f"Executing task: {args.task}")
            
            original_branch = None
            stashed = False
            sandbox_active = False

            if args.sandbox:
                sandbox_active, original_branch, stashed = claw.start_sandbox(args.task)
                if not sandbox_active:
                    print("[ERROR] Failed to initialize sandbox. Aborting task execution.")
                    sys.exit(1)

            # Check safety guard for command
            is_safe, block_reason = validate_command_safety(args.command)
            if not is_safe:
                print(f"[BLOCKED] Command prohibited by safety guard: {block_reason}")
                claw.watchdog.record_action("cli_execute_blocked", args.task, block_reason, success=False)
                if sandbox_active:
                    claw.discard_sandbox(args.task, original_branch, stashed)
                sys.exit(2)

            # Check limits before executing
            provider = "local"
            limit_reached, msg = claw.usage.check_limits(
                provider, 
                claw.limits[provider]["tokens"], 
                claw.limits[provider]["requests"]
            )
            if limit_reached:
                print(f"[PAUSED] {args.task}: {msg}")
                claw.watchdog.record_action("cli_execute", args.task, msg, success=False)
                if sandbox_active:
                    claw.discard_sandbox(args.task, original_branch, stashed)
                sys.exit(1)

            # Run command
            print(f"[EXECUTE] Running command: {args.command}")
            exec_res = subprocess.run(args.command, shell=True, capture_output=True, text=True)
            print(exec_res.stdout)
            
            # Track command token usage & watchdog
            output_text = exec_res.stdout + exec_res.stderr
            actual_tokens = token_estimator.estimate_tokens(output_text)
            claw.usage.track_usage(provider, tokens=actual_tokens, requests=1)
            claw.watchdog.record_action(
                action_type="cli_execute",
                target=f"{args.task}: {args.command}",
                result_snippet=output_text[:200],
                success=(exec_res.returncode == 0)
            )
            
            if actual_tokens > 10000:
                print(f"[CRITICAL] Command output is {actual_tokens} tokens! Consider summarizing before next task.")

            if exec_res.returncode != 0:
                print(f"[EXECUTE ERROR] Command failed with return code {exec_res.returncode}")
                print(exec_res.stderr)
                if sandbox_active:
                    claw.discard_sandbox(args.task, original_branch, stashed)
                sys.exit(1)

            # Run verification if provided
            if args.verify:
                is_safe_verify, block_reason_verify = validate_command_safety(args.verify)
                if not is_safe_verify:
                    print(f"[BLOCKED] Verification command prohibited by safety guard: {block_reason_verify}")
                    claw.watchdog.record_action("cli_verify_blocked", args.task, block_reason_verify, success=False)
                    if sandbox_active:
                        claw.discard_sandbox(args.task, original_branch, stashed)
                    sys.exit(2)

                print(f"[VERIFY] Running verification: {args.verify}")
                verify_res = subprocess.run(args.verify, shell=True, capture_output=True, text=True)
                print(verify_res.stdout)
                
                # Track verify token usage
                verify_tokens = token_estimator.estimate_tokens(verify_res.stdout + verify_res.stderr)
                claw.usage.track_usage(provider, tokens=verify_tokens, requests=1)
                claw.watchdog.record_action(
                    action_type="cli_verify",
                    target=f"{args.task}: {args.verify}",
                    result_snippet=(verify_res.stdout + verify_res.stderr)[:200],
                    success=(verify_res.returncode == 0)
                )
                
                if verify_res.returncode != 0:
                     print(f"[VERIFY FAILURE] Verification failed with return code {verify_res.returncode}")
                     print(verify_res.stderr)
                     if sandbox_active:
                         claw.discard_sandbox(args.task, original_branch, stashed)
                     sys.exit(1)
                else:
                    print("[VERIFY SUCCESS] Verification passed.")

            # If we got here, everything succeeded
            if sandbox_active:
                if args.auto_merge:
                    claw.commit_and_merge_sandbox(args.task, original_branch, stashed)
                else:
                    claw.commit_sandbox(args.task)
                
            print("[SUCCESS] Task execution completed successfully.")

            # Check if task.md has been fully completed
            for p in ["task.md", "artifact/task.md"]:
                if os.path.exists(p):
                    with open(p, "r", encoding="utf-8") as f:
                        task_content = f.read()
                    if "- [ ]" not in task_content and "- [x]" in task_content:
                        print("[AUTO-HOOK] All tasks completed! Triggering auto-capture and reflection...")
                        subprocess.run(f'"{sys.executable}" auto_capture.py', shell=True)
                    break
        else:
            # Generic parallel test execution
            tasks = [
                {"name": "Test Suite A", "command": "pytest --version"},
                {"name": "Check Imports", "command": "python -c 'import openbrain'"}
            ]
            claw.execute_parallel(tasks)

if __name__ == "__main__":
    main()
