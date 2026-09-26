"""
Openbrain Persistence Engine (Compatibility Module).

This module provides backward-compatibility for scripts referencing `OpenbrainEngine`.
The canonical persistence engine is `openbrain.memory_engine.MemoryEngine`.
"""

import os
from .memory_engine import MemoryEngine

class OpenbrainEngine(MemoryEngine):
    """
    Backward-compatible alias for MemoryEngine.
    Maintains support for legacy method signatures while ensuring full feature parity.
    """
    def __init__(self, db_path="openbrain.db", chroma_path="./chroma_db"):
        super().__init__(db_path=db_path, chroma_path=chroma_path)

    def get_memories(self, limit=10):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT content, tier, tags FROM memories ORDER BY created_at DESC LIMIT ?", (limit,))
        rows = cur.fetchall()
        conn.close()
        return rows

    def update_project_state(self, project_name, next_step, checkpoint_data=None):
        import json
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO project_states (project_name, next_step, checkpoint_data, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(project_name) DO UPDATE SET
                next_step=excluded.next_step,
                checkpoint_data=COALESCE(excluded.checkpoint_data, project_states.checkpoint_data),
                updated_at=CURRENT_TIMESTAMP
        """, (project_name, next_step, json.dumps(checkpoint_data) if checkpoint_data else None))
        conn.commit()
        conn.close()

if __name__ == "__main__":
    engine = OpenbrainEngine()
    print("[OpenbrainEngine] Initialized successfully as MemoryEngine alias.")
