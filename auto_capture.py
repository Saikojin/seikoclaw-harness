import os
import sys
import json
from datetime import datetime

# Add local path to sys.path to allow importing openbrain
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from openbrain.memory_engine import MemoryEngine
from openbrain.usage_monitor import UsageMonitor

class AutoCapture:
    def __init__(self):
        # Resolve DB path local-first with global fallback
        cwd_openbrain = os.path.join(os.getcwd(), "openbrain")
        if os.path.isdir(cwd_openbrain):
            db_path = os.path.join(cwd_openbrain, "openbrain.db")
            chroma_path = os.path.join(cwd_openbrain, "chroma_db")
        else:
            global_dir = os.path.join(os.path.expanduser("~"), ".gemini", "antigravity", "openbrain")
            os.makedirs(global_dir, exist_ok=True)
            db_path = os.path.join(global_dir, "openbrain.db")
            chroma_path = os.path.join(global_dir, "chroma_db")
            
        print(f"[AutoCapture] Using Database: {db_path}")
        self.memory = MemoryEngine(db_path, chroma_path)
        self.usage = UsageMonitor(db_path)

    def find_recent_task_md(self):
        # 1. Check local directory first
        for p in ["task.md", "artifact/task.md"]:
            if os.path.exists(p):
                return p
        # 2. Check global brain folders for the most recently modified task.md
        brain_dir = os.path.join(os.path.expanduser("~"), ".gemini", "antigravity", "brain")
        if os.path.exists(brain_dir):
            task_files = []
            for root, dirs, files in os.walk(brain_dir):
                if "task.md" in files:
                    p = os.path.join(root, "task.md")
                    try:
                        mtime = os.path.getmtime(p)
                        task_files.append((p, mtime))
                    except Exception:
                        pass
            if task_files:
                task_files.sort(key=lambda x: x[1], reverse=True)
                return task_files[0][0]
        return None

    def capture_session(self):
        print("[AutoCapture] Evaluating session state...")
        
        # 1. Read task.md for progress
        progress = "No recent task info found."
        task_md_path = self.find_recent_task_md()
        if task_md_path and os.path.exists(task_md_path):
            print(f"[AutoCapture] Reading tasks from: {task_md_path}")
            with open(task_md_path, "r", encoding="utf-8") as f:
                progress = f.read()
        
        # 2. Get Usage Metrics
        google_usage = self.usage.get_todays_usage("google")
        usage_str = f"Usage today: {google_usage['tokens']} tokens."
        
        # 3. Summarize
        project_name = os.path.basename(os.getcwd())
        summary = f"Session Capture ({project_name}): Successfully completed tasks. {usage_str} Progress:\n{progress[:2000]}"
        
        # 4. Save to memory
        mem_id = self.memory.save_memory(summary, tier="Shortterm", source="auto-capture")
        print(f"[AutoCapture] Saved session summary: {mem_id}")
        
        # 5. Extract skills (Mocking for now)
        skill_text = "Skill Learned: Implemented dynamic database path resolution for global agent operations."
        self.memory.save_memory(skill_text, tier="Midterm", source="auto-capture", tags="skill")
        print("[AutoCapture] Captured new skills.")

        # 6. Trigger Visual Recap
        try:
            from seikoclaw import SeikoClaw
            claw = SeikoClaw()
            recap_url = claw.generate_visual_recap(project_name)
            if recap_url:
                self.memory.save_memory(f"Visual Recap URL: {recap_url}", tier="Shortterm", source="auto-capture", tags="recap,visual")
                print(f"[AutoCapture] Saved Visual Recap URL to Openbrain: {recap_url}")
        except Exception as e:
            print(f"[AutoCapture Warning] Visual recap generation failed: {e}")

def main():
    ac = AutoCapture()
    ac.capture_session()

if __name__ == "__main__":
    main()
