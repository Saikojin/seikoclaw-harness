import os
import sys
import tiktoken

def estimate_tokens(text: str, model: str = "gpt-4") -> int:
    """
    Estimates token count using tiktoken. 
    GPT-4 encoding is a good proxy for Gemini/Claude density.
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except Exception:
        # Fallback to rough heuristic: chars / 4
        return len(text) // 4

def estimate_file(file_path: str) -> int:
    if not os.path.exists(file_path):
        return 0
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        return estimate_tokens(f.read())

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python token_estimator.py <file_path or string>")
        sys.exit(1)
    
    arg = sys.argv[1]
    if os.path.isfile(arg):
        count = estimate_file(arg)
        print(f"File: {arg}")
        print(f"Estimated Tokens: {count}")
    else:
        count = estimate_tokens(arg)
        print(f"String snippet estimated tokens: {count}")
