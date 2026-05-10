import sqlite3
import uuid
import os
from datetime import datetime

class OpenbrainEngine:
    """
    The core persistence engine for SeikoClaw.
    Manages structured project state and unstructured agent memories.
    """
    def __init__(self, db_path="openbrain.db"):
        self.sqlite_path = db_path
        self._init_sqlite()

    def _get_conn(self):
        return sqlite3.connect(self.sqlite_path)

    def _init_sqlite(self):
        """Ensures all necessary SQLite tables exist based on the schema."""
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        if not os.path.exists(schema_path):
            # Fallback inline schema if file is missing
            self._create_tables_inline()
            return

        with open(schema_path, 'r') as f:
            schema = f.read()
        
        conn = self._get_conn()
        conn.executescript(schema)
        conn.commit()
        conn.close()

    def _create_tables_inline(self):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                tier TEXT DEFAULT 'Shortterm',
                source TEXT,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS project_states (
                project_name TEXT PRIMARY KEY,
                next_step TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def save_memory(self, content, tier="Shortterm", source="agent", tags=""):
        mem_id = str(uuid.uuid4())
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO memories (id, content, tier, source, tags)
            VALUES (?, ?, ?, ?, ?)
        """, (mem_id, content, tier, source, tags))
        conn.commit()
        conn.close()
        return mem_id

    def get_memories(self, limit=10):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT content, tier, tags FROM memories ORDER BY created_at DESC LIMIT ?", (limit,))
        rows = cur.fetchall()
        conn.close()
        return rows

    def update_project_state(self, project_name, next_step):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO project_states (project_name, next_step, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(project_name) DO UPDATE SET
                next_step=excluded.next_step,
                updated_at=CURRENT_TIMESTAMP
        """, (project_name, next_step))
        conn.commit()
        conn.close()

if __name__ == "__main__":
    engine = OpenbrainEngine()
    print("Openbrain Engine initialized.")
