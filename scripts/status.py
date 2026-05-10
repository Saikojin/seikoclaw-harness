import os
import sys

def estimate_tokens(text):
    # Simple heuristic: 4 chars per token
    return len(text) // 4

def get_session_context():
    files_to_check = ["task.md", "project_vision.md", "implementation_plan.md"]
    total_tokens = 0
    for f in files_to_check:
        if os.path.exists(f):
            with open(f, 'r', encoding='utf-8') as file:
                total_tokens += estimate_tokens(file.read())
    return total_tokens

def print_progress_bar(label, current, total, width=40):
    percent = float(current) / total if total > 0 else 0
    filled = int(width * percent)
    bar = "#" * filled + "-" * (width - filled)
    print(f"{label:15} [{bar}] {percent:4.1%} ({current}/{total})")

def main():
    print("\n" + "="*60)
    print(" [TOOL] SEIKOCLAW CONTEXT DASHBOARD")
    print("="*60 + "\n")
    
    session_weight = get_session_context()
    session_limit = 100000 
    
    print_progress_bar("Session Weight", session_weight, session_limit)
    
    print("\n" + "-"*60)
    if session_weight > (session_limit * 0.8):
        print("WARNING: Session is getting heavy. Consider summarizing soon.")
    else:
        print("Status: Context is healthy and responsive.")
    print("-"*60 + "\n")

if __name__ == "__main__":
    main()
