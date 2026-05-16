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
        print("Executing task...")
        # logic for task execution

if __name__ == "__main__":
    main()
