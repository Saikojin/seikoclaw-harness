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

from .llm_provider import get_llm_provider

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
        self.llm = get_llm_provider()
        logger.info(f"ContextEngine initialized with LLM provider: {self.llm.name}")

    def compress_shortterm(self, tag: str = None, threshold: int = 10) -> bool:
        """
        Scans short-term memories and consolidates them if the threshold is met.
        Guarantees zero data loss:
        - Refuses compression if only heuristic fallback is active.
        - Preserves source memories by marking tier='Archived' instead of deleting them.
        """
        if not self.llm or getattr(self.llm, "is_heuristic", False) or not getattr(self.llm, "is_neural", False):
            logger.info("Memory compression skipped: requires active neural LLM backend.")
            return False

        # 1. Fetch short-term memories
        conn = self._get_conn()
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
        source_ids = [r[0] for r in rows]

        # 3. Summarize via Pluggable Neural LLM Provider
        prompt = CAVEMAN_PROMPT.format(memories=combined_text)
        summary = self.llm.generate(prompt, max_tokens=1024, temperature=0.3)

        if summary and "[Mock Response]" not in summary and summary.strip():
            # 4. Save new Midterm memory
            midterm_id = self.memory.save_memory(
                text=summary.strip(), 
                tier="Midterm", 
                source="ContextEngine", 
                tags=f"compressed,{tag if tag else ''}"
            )

            # 5. Soft-archive old memories with linkage to midterm memory
            cur.executemany("""
                UPDATE memories 
                SET tier = 'Archived', 
                    compressed_into = ?, 
                    archived_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, [(midterm_id, mid) for mid in source_ids])
            conn.commit()
            
            # Remove from Chroma vector index to keep vector search dense & focused on midterm summary
            if getattr(self.memory, "collection", None):
                try:
                    self.memory.collection.delete(ids=source_ids)
                except Exception:
                    pass
            
            logger.info(f"Successfully compressed {len(rows)} memories into 1 midterm entry ({midterm_id}); source memories archived.")
            conn.close()
            return True
        
        conn.close()
        return False

    def _get_conn(self):
        import sqlite3
        return sqlite3.connect(self.memory.sqlite_path)
