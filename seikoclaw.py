import os
import sys
import argparse
import subprocess
import concurrent.futures
import json
from datetime import datetime

# Add local paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from openbrain.engine import OpenbrainEngine

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
        db_path = "openbrain/openbrain.db"
        self.engine = OpenbrainEngine(db_path)

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
        """Executes a single command."""
        print(f"[Executing] {name}: {command} (in {cwd or '.'})")
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=cwd)
            if result.returncode == 0:
                return f"SUCCESS: {name}"
            else:
                return f"FAILURE: {name}\nError: {result.stderr}"
        except Exception as e:
            return f"ERROR: {name}\nException: {str(e)}"

    def manage_kanban(self, action, task_id=None, status=None, project="default"):
        if action == "list":
            board = self.engine.get_kanban(project)
            print(f"--- Kanban Board: {project} ---")
            if not board:
                print("No tasks found.")
            for tid, info in board.items():
                print(f"[{info['status']}] {tid} (Updated: {info['updated_at']})")
        elif action == "update" and task_id and status:
            self.engine.update_kanban(project, task_id, status)
            print(f"[SUCCESS] Updated {task_id} to {status}")

    def loop_until_goal(self, goal, max_turns=5):
        budget = IterationBudget(max_turns=max_turns)
        print(f"[SeikoClaw] Starting autonomous loop for goal: {goal}")
        
        while not budget.is_exhausted():
            print(f"\n--- Turn {budget.current_turns + 1} ---")
            
            # Simple context estimation (proxy)
            current_context_tokens = 0 # In harness, we might need a separate estimator tool
            
            budget.consume(tokens=0, context_tokens=current_context_tokens)
            print(f"[STATUS] {budget}")
            
            if "complete" in goal.lower():
                print("[SUCCESS] Goal detected as complete.")
                break
                
            print("[ACTION] Implementing next step...")
            
        if budget.is_exhausted():
            print("[PAUSED] Iteration budget exhausted.")

    def reflect_on_task(self, task_file: str):
        if not os.path.exists(task_file):
            return "Error: Task file not found."

        with open(task_file, "r", encoding="utf-8") as f:
            content = f.read()

        if "[x]" not in content:
            return "No completed tasks found to reflect upon."

        print(f"[SeikoClaw] Reflecting on completed tasks...")
        # Note: This requires an LLM backend which is typically provided by the assistant
        print("[INFO] Skill synthesis requires LLM intervention. See workflows.")

def main():
    parser = argparse.ArgumentParser(description="SeikoClaw Harness CLI")
    parser.add_argument("action", choices=["execute", "kanban", "loop", "reflect"])
    parser.add_argument("--task", type=str)
    parser.add_argument("--status", type=str)
    parser.add_argument("--goal", type=str)
    parser.add_argument("--turns", type=int, default=5)
    parser.add_argument("--command", type=str, help="Command to run when executing a task")
    parser.add_argument("--verify", type=str, help="Verification command to run after executing a task")
    parser.add_argument("--sandbox", action="store_true", help="Enable git-backed sandboxing for execution")
    
    args = parser.parse_args()
    claw = SeikoClaw()

    if args.action == "kanban":
        if args.task and args.status:
            claw.manage_kanban("update", task_id=args.task, status=args.status)
        else:
            claw.manage_kanban("list")
    elif args.action == "loop":
        if args.goal:
            claw.loop_until_goal(args.goal, max_turns=args.turns)
        else:
            print("Error: --goal is required.")
    elif args.action == "execute":
        if not args.task:
            print("Error: --task is required.")
            sys.exit(1)
        if not args.command:
            print("Error: --command is required.")
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

        # Run command
        print(f"[EXECUTE] Running command: {args.command}")
        exec_res = subprocess.run(args.command, shell=True, capture_output=True, text=True)
        print(exec_res.stdout)
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

if __name__ == "__main__":
    main()
