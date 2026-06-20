import os
import sys
import argparse
import subprocess
import concurrent.futures
import json
from datetime import datetime

# Add local paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import token_estimator
from openbrain.vault import Vault
from openbrain.usage_monitor import UsageMonitor
from openbrain.memory_engine import MemoryEngine

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
    def __init__(self):
        cwd_openbrain = os.path.join(os.getcwd(), "openbrain")
        if os.path.isdir(cwd_openbrain):
            db_path = os.path.join(cwd_openbrain, "openbrain.db")
            chroma_path = os.path.join(cwd_openbrain, "chroma_db")
        else:
            global_dir = os.path.join(os.path.expanduser("~"), ".gemini", "antigravity", "openbrain")
            os.makedirs(global_dir, exist_ok=True)
            db_path = os.path.join(global_dir, "openbrain.db")
            chroma_path = os.path.join(global_dir, "chroma_db")
            
        self.sqlite_path = db_path
        self.chroma_path = chroma_path
        self.vault = Vault(db_path)
        self.usage = UsageMonitor(db_path)
        self.memory = MemoryEngine(db_path, chroma_path)
        
        # Default limits
        self.limits = {
            "anthropic": {"tokens": 100000, "requests": 500},
            "google": {"tokens": 200000, "requests": 1000}
        }

    def unlock_vault(self):
        print("[SeikoClaw] Initializing Vault...")
        password = os.getenv("SEIKOCLAW_MASTER_PASS")
        if not password:
            print("[WARNING] SEIKOCLAW_MASTER_PASS env var not set. Some features will be locked.")
            return False
        
        self.vault.unlock(password)
        return True

    def _git_run(self, cmd):
        result = subprocess.run(f"git {cmd}", shell=True, capture_output=True, text=True)
        return result.returncode, result.stdout.strip(), result.stderr.strip()

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
        """Executes a single command with usage oversight."""
        provider = "google" # Default for most tools here
        
        # 1. Check limits before starting
        limit_reached, msg = self.usage.check_limits(
            provider, 
            self.limits[provider]["tokens"], 
            self.limits[provider]["requests"]
        )
        
        if limit_reached:
            print(f"[PAUSED] {name}: {msg}")
            return f"SKIP: {msg}"

        print(f"[Executing] {name}: {command} (in {cwd or '.'})")
        
        # 2. Execute
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=cwd)
            
            # 3. Estimate actual token usage of the output
            output_text = result.stdout + result.stderr
            actual_tokens = token_estimator.estimate_tokens(output_text)
            
            # 4. Track usage
            self.usage.track_usage(provider, tokens=actual_tokens, requests=1) 
            
            # 5. Safety Warning: If output is very large, alert for manual summarization
            if actual_tokens > 10000:
                print(f"[CRITICAL] {name} output is {actual_tokens} tokens! Consider summarizing before next task.")

            if result.returncode == 0:
                return f"SUCCESS: {name}"
            else:
                return f"FAILURE: {name}\nError: {result.stderr}"
        except Exception as e:
            return f"ERROR: {name}\nException: {str(e)}"

    def execute_tablebuddy_tests(self):
        """Orchestrates Tablebuddy Phase 11 testing."""
        print("[SeikoClaw] Starting Tablebuddy Backend...")
        # Start server in background
        server = subprocess.Popen([sys.executable, "server.py"], cwd="d:/DevWorkspace/Tablebuddy")
        import time
        time.sleep(3) # Wait for startup
        
        try:
            tasks = [
                {"name": "Auth & Roles", "command": "java -cp \"../karate.jar;.\" com.intuit.karate.Main api/auth_and_roles.feature"},
                {"name": "Asset Management", "command": "java -cp \"../karate.jar;.\" com.intuit.karate.Main api/asset_management.feature"},
                {"name": "WebSocket Sync", "command": "java -cp \"../karate.jar;.\" com.intuit.karate.Main api/websocket_sync.feature"},
                {"name": "Network Validation", "command": "java -cp \"../karate.jar;.\" com.intuit.karate.Main api/network_validation.feature"}
            ]
            self.execute_parallel(tasks, cwd="d:/DevWorkspace/Tablebuddy/karate_e2e_tests")
        finally:
            print("[SeikoClaw] Shutting down Tablebuddy Backend...")
            server.terminate()

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
        """Analyzes a task file and synthesizes or evolves a skill."""
        if not os.path.exists(task_file):
            return "Error: Task file not found."

        with open(task_file, "r", encoding="utf-8") as f:
            content = f.read()

        if "[x]" not in content:
            return "No completed tasks found to reflect upon."

        print(f"[SeikoClaw] Reflecting on completed tasks in {os.path.basename(task_file)}...")
        
        # 1. Synthesis via LocalMind
        try:
            from localmind.engine import LocalMindEngine
            model_dir = "d:/DevWorkspace/BookIngestion/models"
            llm = LocalMindEngine(backend="auto", model_dir=model_dir)
            
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
            
            prompt = SKILL_SYNTHESIS_PROMPT.format(trajectory=content, previous_skill=previous_skill_text)
            skill_text = llm.generate(prompt, max_tokens=1024)
            
            if skill_text and "[Mock Response]" not in skill_text:
                # 2. Extract Skill Name and metadata
                name_match = re.search(r"name:\s*(.*)", skill_text)
                skill_name = name_match.group(1).strip() if name_match else "New Skill"
                
                desc_match = re.search(r"description:\s*(.*)", skill_text) # if we added it to YAML
                desc = desc_match.group(1).strip() if desc_match else "Auto-learned skill"
                
                # 3. Save to Openbrain (Both Memory and Dedicated Table)
                self.memory.save_memory(
                    text=skill_text,
                    tier="Longterm",
                    source="SeikoClaw-Reflection",
                    tags=f"skill,auto-learned,{skill_name}"
                )
                self.memory.save_skill(name=skill_name, description=desc, example=skill_text)
                
                print(f"[SUCCESS] { 'Evolved' if previous_skill_text != 'None' else 'Synthesized' } skill: {skill_name}")
                return skill_name
        except Exception as e:
            print(f"[ERROR] Skill reflection failed: {e}")
            return None

    def sync_wiki(self, message="Auto-sync from SeikoClaw"):
        """Syncs the current project state into the Master Wiki."""
        print("[SeikoClaw] Syncing state to Master Wiki...")
        wiki_dir = "d:/DevWorkspace/.master_wiki"
        if not os.path.exists(wiki_dir):
            print(f"[ERROR] Master Wiki not found at {wiki_dir}")
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
        
        # 3. Write to wiki using CLI
        print("[SeikoClaw] Writing to wiki via llmwiki-cli...")
        try:
            proc = subprocess.Popen(["wiki", "write", "wiki/synthesis/latest_sync.md"], 
                                   cwd=wiki_dir, stdin=subprocess.PIPE, 
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
            out, err = proc.communicate(input=json_input)
            if proc.returncode != 0:
                print(f"[WARNING] Wiki write failed: {err}")
                
            # 4. Auto-commit with descriptive message for rollback
            subprocess.run(["git", "add", "."], cwd=wiki_dir, shell=True)
            subprocess.run(["git", "commit", "-m", f"Auto-sync: {message}"], cwd=wiki_dir, shell=True)
            print("[SUCCESS] Master Wiki updated and committed.")
        except Exception as e:
            print(f"[ERROR] Failed to sync wiki: {e}")

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

    def loop_until_goal(self, goal, max_turns=5):
        """Autonomous loop that continues until a goal is met or budget is exhausted."""
        budget = IterationBudget(max_turns=max_turns)
        print(f"[SeikoClaw] Starting autonomous loop for goal: {goal}")
        
        while not budget.is_exhausted():
            print(f"\n--- Turn {budget.current_turns + 1} ---")
            
            # 1. Estimate current context
            # We estimate by summing up Shortterm memories + recent task info
            memories = self.memory.retrieve_similar(goal, n_results=20)
            context_text = "\n".join([m['content'] for m in memories])
            current_context_tokens = token_estimator.estimate_tokens(context_text)
            
            budget.consume(tokens=0, context_tokens=current_context_tokens)
            print(f"[STATUS] {budget}")
            
            # 2. Check for early break / handoff
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

            # 3. Check goal (mock check)
            if "complete" in goal.lower():
                print("[SUCCESS] Goal detected as complete.")
                break
                
            # 4. Memory Compression (Maintenance)
            if self.memory.context_engine.compress_shortterm(threshold=5):
                print("[MAINTENANCE] Compressed recent short-term memories into Midterm.")

            # 5. Simulate a task implementation step
            print("[ACTION] Implementing next step...")
            
        if budget.is_exhausted() and current_context_tokens < (budget.context_limit * 0.9):
            print("[PAUSED] Iteration budget exhausted.")

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
        mdx_content = f"""---
title: "SeikoClaw Visual Plan"
brief: "Visual plan generated for task planning"
localOnly: true
---

# SeikoClaw Task Plan

## Task Description
{content}

<Checklist id="seikoclaw-checklist" items={[
"""
        # Convert checklist lines
        item_id = 1
        for line in content.splitlines():
            # Match task checklist item
            m = re.match(r"^\s*-\s*\[\s*\]\s*(.*)", line)
            if m:
                label = m.group(1).replace('"', '\\"').strip()
                mdx_content += f'  {{ id: "task-{item_id}", label: "{label}" }},\n'
                item_id += 1
        
        mdx_content += """]} />
"""
        
        plan_mdx_path = os.path.join(plan_dir, "plan.mdx")
        with open(plan_mdx_path, "w", encoding="utf-8") as f:
            f.write(mdx_content)
        
        # 4. Serve the bridge
        npm_global_bin = "D:/DevWorkspace/.npm-global/agent-native.cmd"
        cmd_prefix = npm_global_bin if os.path.exists(npm_global_bin) else "npx @agent-native/core"

        print("[SeikoClaw] Checking visual plan syntax...")
        subprocess.run(f"{cmd_prefix} plan local check --dir .agents/plans/plan", shell=True)
        
        print("[SeikoClaw] Serving visual plan on local bridge...")
        # Start server in background so CLI execution doesn't block permanently
        subprocess.Popen(f"{cmd_prefix} plan local serve --dir .agents/plans/plan --kind plan --open", shell=True)
        
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
            
        npm_global_bin = "D:/DevWorkspace/.npm-global/agent-native.cmd"
        cmd_prefix = npm_global_bin if os.path.exists(npm_global_bin) else "npx @agent-native/core"

        print("[SeikoClaw] Checking visual recap syntax...")
        subprocess.run(f"{cmd_prefix} plan local check --dir .agents/plans/recap", shell=True)
        
        print("[SeikoClaw] Serving visual recap on local bridge...")
        subprocess.Popen(f"{cmd_prefix} plan local serve --dir .agents/plans/recap --kind recap --open", shell=True)
        
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
    parser.add_argument("action", choices=["plan", "execute", "usage", "doctor", "sync-global", "memory", "reflect", "wiki-sync", "kanban", "loop", "recap"])
    parser.add_argument("--task", type=str)
    parser.add_argument("--status", type=str)
    parser.add_argument("--goal", type=str)
    parser.add_argument("--turns", type=int, default=5)
    parser.add_argument("--command", type=str, help="Command to run when executing a task")
    parser.add_argument("--verify", type=str, help="Verification command to run after executing a task")
    parser.add_argument("--sandbox", action="store_true", help="Enable git-backed sandboxing for execution")
    parser.add_argument("--query", type=str, help="Search query for memory")
    
    args = parser.parse_args()
    claw = SeikoClaw()

    if args.action == "plan":
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
    elif args.action == "loop":
        if args.goal:
            claw.loop_until_goal(args.goal, max_turns=args.turns)
        else:
            print("Error: --goal is required.")
    elif args.action == "memory":
        if args.query:
            print(f"--- Searching memories for: '{args.query}' ---")
            results = claw.memory.retrieve_similar(args.query)
            if not results:
                print("No matches found.")
            for r in results:
                print(f"[{r['metadata']['tier']}] {r['metadata']['source']}:")
                print(f"{r['content'][:500]}...") # Show snippet
                print("-" * 20)
        else:
            print("Error: --query is required for memory search.")
    elif args.action == "reflect":
        if args.task:
            claw.reflect_on_task(args.task)
        else:
            print("Error: --task is required for reflection.")
    elif args.action == "usage":
        print("--- Today's Usage ---")
        for p in ["anthropic", "google"]:
            u = claw.usage.get_todays_usage(p)
            print(f"{p.upper()}: {u['tokens']} tokens, {u['requests']} requests")
    elif args.action == "doctor":
        print("[Doctor] Checking Openbrain...")
        db_path = claw.sqlite_path
        print(f"Database path: {db_path}")
        if os.path.exists(db_path):
            print("[OK] database found.")
        else:
            print("[FAIL] database missing.")
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

            # Check limits before executing
            provider = "google"
            limit_reached, msg = claw.usage.check_limits(
                provider, 
                claw.limits[provider]["tokens"], 
                claw.limits[provider]["requests"]
            )
            if limit_reached:
                print(f"[PAUSED] {args.task}: {msg}")
                if sandbox_active:
                    claw.discard_sandbox(args.task, original_branch, stashed)
                sys.exit(1)

            # Run command
            print(f"[EXECUTE] Running command: {args.command}")
            exec_res = subprocess.run(args.command, shell=True, capture_output=True, text=True)
            print(exec_res.stdout)
            
            # Track command token usage
            output_text = exec_res.stdout + exec_res.stderr
            actual_tokens = token_estimator.estimate_tokens(output_text)
            claw.usage.track_usage(provider, tokens=actual_tokens, requests=1)
            
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
                print(f"[VERIFY] Running verification: {args.verify}")
                verify_res = subprocess.run(args.verify, shell=True, capture_output=True, text=True)
                print(verify_res.stdout)
                
                # Track verify token usage
                verify_tokens = token_estimator.estimate_tokens(verify_res.stdout + verify_res.stderr)
                claw.usage.track_usage(provider, tokens=verify_tokens, requests=1)
                
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
                claw.commit_and_merge_sandbox(args.task, original_branch, stashed)
                
            print("[SUCCESS] Task execution completed successfully.")
        elif args.task == "tablebuddy":
            claw.execute_tablebuddy_tests()
        else:
            # Generic parallel test execution
            tasks = [
                {"name": "Test Suite A", "command": "pytest --version"},
                {"name": "Check Imports", "command": "python -c 'import openbrain'"}
            ]
            claw.execute_parallel(tasks)

if __name__ == "__main__":
    main()
