import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any

# Ensure we can import localmind
import sys
harness_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
workspace_dir = os.path.dirname(harness_dir)
if os.path.join(workspace_dir, "LocalMind", "src") not in sys.path:
    sys.path.append(os.path.join(workspace_dir, "LocalMind", "src"))

try:
    from localmind.engine import LocalMindEngine
except ImportError:
    LocalMindEngine = None

logger = logging.getLogger(__name__)

CAVEMAN_PROMPT = """
Summarize following technical log/memories into single "Midterm" memory.
Use Smart Caveman logic:
1. Drop all articles (a, an, the).
2. Drop filler words and pleasantries.
3. Keep technical terms, PIDs, Ports, and Code exact.
4. Format as DAG-like facts: [subject] [action] [result].
5. Max density, min tokens.

INPUT MEMORIES:
{memories}
"""

class ContextEngine:
    def __init__(self, memory_engine):
        self.memory = memory_engine
        self.llm = None
        if LocalMindEngine:
            # Context engine uses a dedicated low-resource worker if possible
            model_dir = "d:/DevWorkspace/BookIngestion/models"
            self.llm = LocalMindEngine(backend="auto", model_dir=model_dir)
        else:
            logger.warning("LocalMind not found. ContextEngine will operate in pass-through mode.")

    def compress_shortterm(self, tag: str = None, threshold: int = 10) -> bool:
        """
        Scans short-term memories and consolidates them if the threshold is met.
        """
        if not self.llm:
            return False

        # 1. Fetch short-term memories
        conn = self.memory._get_conn() # Assuming we add this helper or use internal sqlite_path
        cur = conn.cursor()
        
        query = "SELECT id, content FROM memories WHERE tier = 'Shortterm'"
        params = []
        if tag:
            query += " AND tags LIKE ?"
            params.append(f"%{tag}%")
        
        cur.execute(query, params)
        rows = cur.fetchall()
        
        if len(rows) < threshold:
            conn.close()
            return False

        logger.info(f"Consolidating {len(rows)} short-term memories for tag: {tag or 'global'}")
        
        # 2. Prepare for summarization
        combined_text = "\n---\n".join([r[1] for r in rows])
        ids_to_delete = [r[0] for r in rows]

        # 3. Summarize via LLM
        prompt = CAVEMAN_PROMPT.format(memories=combined_text)
        summary = self.llm.generate(prompt, max_tokens=1024, temperature=0.3)

        if summary and "[Mock Response]" not in summary:
            # 4. Save new Midterm memory
            self.memory.save_memory(
                text=summary, 
                tier="Midterm", 
                source="ContextEngine", 
                tags=f"compressed,{tag if tag else ''}"
            )

            # 5. Cleanup old memories
            cur.executemany("DELETE FROM memories WHERE id = ?", [(mid,) for mid in ids_to_delete])
            conn.commit()
            
            # Also cleanup from Chroma
            self.memory.collection.delete(ids=ids_to_delete)
            
            logger.info(f"Successfully compressed {len(rows)} memories into 1 midterm entry.")
            conn.close()
            return True
        
        conn.close()
        return False

    def _get_conn(self):
        import sqlite3
        return sqlite3.connect(self.memory.sqlite_path)
