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
        """Fallback inline schema matching schema.sql."""
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                tier TEXT DEFAULT 'Shortterm',
                source TEXT,
                tags TEXT,
                weight REAL DEFAULT 1.0,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS project_states (
                project_name TEXT PRIMARY KEY,
                current_branch TEXT,
                last_blocker TEXT,
                next_step TEXT,
                checkpoint_data JSON,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS skills (
                id TEXT PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                example_usage TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

    def update_kanban(self, project_name: str, task_id: str, status: str, metadata: dict = None):
        """Updates a specific task's status on the Kanban board."""
        import json
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT checkpoint_data FROM project_states WHERE project_name = ?", (project_name,))
        row = cur.fetchone()
        
        data = {}
        if row and row[0]:
            data = json.loads(row[0])
            
        if "kanban" not in data:
            data["kanban"] = {}
            
        data["kanban"][task_id] = {
            "status": status,
            "updated_at": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        cur.execute("""
            INSERT INTO project_states (project_name, checkpoint_data, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(project_name) DO UPDATE SET 
                checkpoint_data = excluded.checkpoint_data,
                updated_at = CURRENT_TIMESTAMP
        """, (project_name, json.dumps(data)))
        conn.commit()
        conn.close()

    def get_kanban(self, project_name: str):
        import json
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT checkpoint_data FROM project_states WHERE project_name = ?", (project_name,))
        row = cur.fetchone()
        conn.close()
        if row and row[0]:
            data = json.loads(row[0])
            return data.get("kanban", {})
        return {}

    def save_skill(self, name: str, description: str, example: str):
        conn = self._get_conn()
        cur = conn.cursor()
        skill_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO skills (id, name, description, example_usage)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET 
                description = excluded.description,
                example_usage = excluded.example_usage
        """, (skill_id, name, description, example))
        conn.commit()
        conn.close()

    def get_skill(self, name: str):
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT name, description, example_usage FROM skills WHERE name = ?", (name,))
        row = cur.fetchone()
        conn.close()
        if row:
            return {"name": row[0], "description": row[1], "example": row[2]}
        return None

if __name__ == "__main__":
    engine = OpenbrainEngine()
    print("Openbrain Engine initialized.")
