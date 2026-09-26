import sqlite3
import uuid
from datetime import datetime
import chromadb
from .context_engine import ContextEngine

class MemoryEngine:
    def __init__(self, db_path="openbrain.db", chroma_path="./chroma_db"):
        self.sqlite_path = db_path
        self._init_sqlite()
        self._init_chroma(chroma_path)
        self.context_engine = ContextEngine(self)

    def _get_conn(self):
        return sqlite3.connect(self.sqlite_path)

    def _init_sqlite(self):
        """Ensures all necessary SQLite tables exist."""
        conn = sqlite3.connect(self.sqlite_path)
        cur = conn.cursor()
        
        # 1. Tiered Memories
        cur.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                tier TEXT CHECK(tier IN ('Core', 'Longterm', 'Midterm', 'Shortterm')) DEFAULT 'Shortterm',
                source TEXT,
                tags TEXT,
                weight REAL DEFAULT 1.0,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 2. Learned Skills
        cur.execute("""
            CREATE TABLE IF NOT EXISTS skills (
                id TEXT PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                example_usage TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 3. Project States
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
        
        # 4. Usage Statistics
        cur.execute("""
            CREATE TABLE IF NOT EXISTS usage_stats (
                stat_date DATE DEFAULT (DATE('now')),
                provider TEXT NOT NULL,
                tokens_used INTEGER DEFAULT 0,
                requests_count INTEGER DEFAULT 0,
                PRIMARY KEY (stat_date, provider)
            )
        """)

        # 5. Generated Assets (for ArtistAgent)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS generated_assets (
                id TEXT PRIMARY KEY,
                prompt TEXT,
                style_markers TEXT,
                bias_weight REAL,
                seed INTEGER,
                output_path TEXT,
                rating INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 6. Encrypted Secrets Vault
        cur.execute("""
            CREATE TABLE IF NOT EXISTS secrets_vault (
                secret_key TEXT PRIMARY KEY,
                encrypted_value TEXT NOT NULL,
                salt TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 7. Conversation History Sync Watermarks
        cur.execute("""
            CREATE TABLE IF NOT EXISTS history_sync_state (
                conversation_id TEXT PRIMARY KEY,
                project_name TEXT,
                last_synced_step INTEGER DEFAULT 0,
                last_synced_time TIMESTAMP,
                memories_count INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def _init_chroma(self, path):
        try:
            self.chroma_client = chromadb.PersistentClient(path=path)
            self.collection = self.chroma_client.get_or_create_collection(name="openbrain_memories")
        except Exception:
            self.chroma_client = None
            self.collection = None

    def save_memory(self, text: str, tier: str = "Shortterm", source: str = "user", tags: str = "", created_at: str = None):
        """Saves a memory to both SQLite (meta) and ChromaDB (vector)."""
        mem_id = str(uuid.uuid4())
        
        # 1. Save to SQLite
        conn = sqlite3.connect(self.sqlite_path)
        cur = conn.cursor()
        if created_at:
            cur.execute("""
                INSERT INTO memories (id, content, tier, source, tags, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (mem_id, text, tier, source, tags, created_at))
        else:
            cur.execute("""
                INSERT INTO memories (id, content, tier, source, tags)
                VALUES (?, ?, ?, ?, ?)
            """, (mem_id, text, tier, source, tags))
        conn.commit()
        conn.close()
        
        # 2. Save to Chroma if available
        if self.collection:
            try:
                self.collection.add(
                    documents=[text],
                    metadatas=[{"id": mem_id, "tier": tier, "source": source, "tags": tags}],
                    ids=[mem_id]
                )
            except Exception:
                pass

        # 3. Check for consolidation
        if tier == "Shortterm" and hasattr(self, "context_engine") and self.context_engine:
            # Auto-trigger compression every 10 memories (can be tuned)
            self.context_engine.compress_shortterm(tag=tags.split(',')[0] if tags else None)

        return mem_id

    def retrieve_similar(self, query: str, n_results: int = 5, min_tier: str = "Shortterm"):
        """Search Chroma for similar items, with SQLite fallback."""
        if self.collection:
            try:
                results = self.collection.query(
                    query_texts=[query],
                    n_results=n_results
                )
                if results['documents'] and results['documents'][0]:
                    memories = []
                    for i in range(len(results['documents'][0])):
                        memories.append({
                            "id": results['ids'][0][i],
                            "content": results['documents'][0][i],
                            "metadata": results['metadatas'][0][i],
                            "distance": results['distances'][0][i]
                        })
                    return memories
            except Exception:
                pass

        # Fallback to SQLite LIKE query
        conn = sqlite3.connect(self.sqlite_path)
        cur = conn.cursor()
        cur.execute("SELECT id, content, tier, source, tags FROM memories WHERE content LIKE ? ORDER BY created_at DESC LIMIT ?", (f"%{query}%", n_results))
        rows = cur.fetchall()
        conn.close()
        return [{"id": r[0], "content": r[1], "metadata": {"id": r[0], "tier": r[2], "source": r[3], "tags": r[4]}, "distance": 0.0} for r in rows]

    def save_mistake(self, task_id: str, error_trace: str, context: str = "", hypothesis: str = "", tier: str = "Midterm"):
        """Persists a structured record of a failure, mistake, or gotcha into Openbrain."""
        formatted_text = (
            f"[MISTAKE RECORD] Task: {task_id}\n"
            f"Context: {context or 'Task execution'}\n"
            f"Error Trace:\n{error_trace.strip()}\n"
        )
        if hypothesis:
            formatted_text += f"Hypothesis / Resolution:\n{hypothesis.strip()}\n"

        return self.save_memory(
            text=formatted_text,
            tier=tier,
            source="ExecutionMistakeTracker",
            tags=f"mistake,failure,gotcha,{task_id}"
        )

    def get_mistakes(self, query: str = "mistake failure gotcha", n_results: int = 5):
        """Retrieves past mistake records matching a query."""
        results = self.retrieve_similar(query, n_results=n_results)
        return [r for r in results if "mistake" in r.get("metadata", {}).get("tags", "")]

    def save_asset(self, prompt, style_markers, bias_weight, seed, output_path):
        """Records a generated asset and its parameters."""
        asset_id = str(uuid.uuid4())
        conn = sqlite3.connect(self.sqlite_path)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO generated_assets (id, prompt, style_markers, bias_weight, seed, output_path)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (asset_id, prompt, style_markers, bias_weight, seed, output_path))
        conn.commit()
        conn.close()
        return asset_id

    def score_asset(self, asset_id, rating):
        """Updates asset rating and adjusts underlying memory weights/tiers."""
        conn = sqlite3.connect(self.sqlite_path)
        cur = conn.cursor()
        
        # 1. Update the asset rating
        cur.execute("UPDATE generated_assets SET rating = ? WHERE id = ?", (rating, asset_id))
        
        # 2. Get style markers associated with this asset
        cur.execute("SELECT style_markers FROM generated_assets WHERE id = ?", (asset_id,))
        row = cur.fetchone()
        if not row:
            conn.close()
            return
            
        markers = [m.strip() for m in row[0].split(",") if m.strip()]
        
        # 3. Adjust memory weights based on rating (the 'Learning Loop')
        # Rating 4 (Masterpiece) -> Longterm, Weight +0.2
        # Rating 3 (Great) -> Midterm, Weight +0.1
        # Rating 1 (Poor) -> Weight -0.2
        for marker in markers:
            if rating >= 4:
                cur.execute("UPDATE memories SET tier = 'Longterm', weight = weight + 0.2 WHERE content LIKE ?", (f"%{marker}%",))
            elif rating == 3:
                cur.execute("UPDATE memories SET tier = 'Midterm', weight = weight + 0.1 WHERE content LIKE ?", (f"%{marker}%",))
            elif rating <= 1:
                cur.execute("UPDATE memories SET weight = MAX(0.1, weight - 0.2) WHERE content LIKE ?", (f"%{marker}%",))
                
        conn.commit()
        conn.close()
 
    def promote_memory(self, mem_id: str, new_tier: str):
        """Updates the tier of a memory in both stores."""
        conn = sqlite3.connect(self.sqlite_path)
        cur = conn.cursor()
        cur.execute("UPDATE memories SET tier = ?, last_accessed = CURRENT_TIMESTAMP WHERE id = ?", (new_tier, mem_id))
        conn.commit()
        conn.close()
        
        if self.collection:
            try:
                self.collection.update(
                    ids=[mem_id],
                    metadatas=[{"tier": new_tier}]
                )
            except Exception:
                pass

    def update_kanban(self, project_name: str, task_id: str, status: str, metadata: dict = None):
        """Updates a specific task's status on the Kanban board stored in checkpoint_data."""
        import json
        conn = sqlite3.connect(self.sqlite_path)
        cur = conn.cursor()
        
        # 1. Fetch existing checkpoint_data
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
        
        # 2. Upsert
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
        """Retrieves the Kanban board for a project."""
        import json
        conn = sqlite3.connect(self.sqlite_path)
        cur = conn.cursor()
        cur.execute("SELECT checkpoint_data FROM project_states WHERE project_name = ?", (project_name,))
        row = cur.fetchone()
        conn.close()
        
        if row and row[0]:
            data = json.loads(row[0])
            return data.get("kanban", {})
        return {}

    def save_skill(self, name: str, description: str, example: str):
        """Saves or updates a skill in the dedicated skills table."""
        conn = sqlite3.connect(self.sqlite_path)
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
        """Retrieves a skill by name."""
        conn = sqlite3.connect(self.sqlite_path)
        cur = conn.cursor()
        cur.execute("SELECT name, description, example_usage FROM skills WHERE name = ?", (name,))
        row = cur.fetchone()
        conn.close()
        if row:
            return {"name": row[0], "description": row[1], "example": row[2]}
        return None

    def get_latest_memory_timestamp(self) -> str | None:
        """Returns the most recent created_at timestamp across memories or history sync."""
        conn = sqlite3.connect(self.sqlite_path)
        cur = conn.cursor()
        cur.execute("SELECT MAX(created_at) FROM memories")
        row = cur.fetchone()
        mem_ts = row[0] if row and row[0] else None

        cur.execute("SELECT MAX(last_synced_time) FROM history_sync_state")
        row_sync = cur.fetchone()
        sync_ts = row_sync[0] if row_sync and row_sync[0] else None
        conn.close()

        if mem_ts and sync_ts:
            return max(str(mem_ts), str(sync_ts))
        return mem_ts or sync_ts

    def get_history_sync_watermark(self, conversation_id: str):
        """Retrieves sync watermark for a given conversation."""
        conn = sqlite3.connect(self.sqlite_path)
        cur = conn.cursor()
        cur.execute("SELECT last_synced_step, last_synced_time, memories_count FROM history_sync_state WHERE conversation_id = ?", (conversation_id,))
        row = cur.fetchone()
        conn.close()
        if row:
            return {"last_synced_step": row[0], "last_synced_time": row[1], "memories_count": row[2]}
        return None

    def update_history_sync_state(self, conversation_id: str, project_name: str, last_step: int, last_time: str, new_memories_count: int = 0):
        """Records or updates sync watermark for a conversation."""
        conn = sqlite3.connect(self.sqlite_path)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO history_sync_state (conversation_id, project_name, last_synced_step, last_synced_time, memories_count, updated_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(conversation_id) DO UPDATE SET
                project_name = excluded.project_name,
                last_synced_step = excluded.last_synced_step,
                last_synced_time = excluded.last_synced_time,
                memories_count = memories_count + excluded.memories_count,
                updated_at = CURRENT_TIMESTAMP
        """, (conversation_id, project_name, last_step, last_time, new_memories_count))
        conn.commit()
        conn.close()

    def list_history_sync_states(self):
        """Lists all conversation history sync records."""
        conn = sqlite3.connect(self.sqlite_path)
        cur = conn.cursor()
        cur.execute("SELECT conversation_id, project_name, last_synced_step, last_synced_time, memories_count, updated_at FROM history_sync_state ORDER BY updated_at DESC")
        rows = cur.fetchall()
        conn.close()
        return [{
            "conversation_id": r[0],
            "project_name": r[1],
            "last_synced_step": r[2],
            "last_synced_time": r[3],
            "memories_count": r[4],
            "updated_at": r[5]
        } for r in rows]

