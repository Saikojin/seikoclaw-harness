import os
import sys

# Add parent directory of scripts/ (i.e. SeikoClaw-Harness root) to allow imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

import token_estimator
from openbrain.usage_monitor import UsageMonitor

def get_session_context():
    """Reads all active task/vision files to estimate current 'context weight'."""
    files_to_check = [
        "task.md",
        "project_vision.md",
        "implementation_plan.md"
    ]
    total_tokens = 0
    for f in files_to_check:
        if os.path.exists(f):
            total_tokens += token_estimator.estimate_file(f)
    return total_tokens

def print_progress_bar(label, current, total, width=40):
    percent = float(current) / total if total > 0 else 0
    filled = int(width * percent)
    bar = "#" * filled + "-" * (width - filled)
    print(f"{label:15} [{bar}] {percent:4.1%} ({current}/{total})")

def main():
    db_path = os.path.join(parent_dir, "openbrain", "openbrain.db")
    usage = UsageMonitor(db_path)
    google_usage = usage.get_todays_usage("google")
    
    # 1. Get Daily Budget Health
    daily_limit = 200000 # Configured in seikoclaw.py
    current_daily = google_usage['tokens']
    
    # 2. Get Current Session Weight (files in context)
    session_weight = get_session_context()
    session_limit = 100000 # Suggested soft limit for high-density sessions
    
    print("\n" + "="*60)
    print(" [TOOL] SEIKOCLAW CONTEXT DASHBOARD")
    print("="*60 + "\n")
    
    print_progress_bar("Daily Budget", current_daily, daily_limit)
    print_progress_bar("Session Weight", session_weight, session_limit)
    
    print("\n" + "-"*60)
    if session_weight > (session_limit * 0.8):
        print("WARNING: Session is getting heavy. Consider summarizing soon.")
    else:
        print("Status: Context is healthy and responsive.")
    print("-"*60 + "\n")

if __name__ == "__main__":
    main()
