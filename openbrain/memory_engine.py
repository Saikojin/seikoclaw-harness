import os
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
        """Ensures all necessary SQLite tables exist from schema.sql."""
        conn = sqlite3.connect(self.sqlite_path)
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.sql")
        if os.path.exists(schema_path):
            with open(schema_path, "r", encoding="utf-8") as f:
                conn.executescript(f.read())

        cur = conn.cursor()
        # Self-heal columns if table was created in older version
        cur.execute("PRAGMA table_info(memories)")
        cols = [c[1] for c in cur.fetchall()]
        if "compressed_into" not in cols:
            try:
                cur.execute("ALTER TABLE memories ADD COLUMN compressed_into TEXT")
            except Exception:
                pass
        if "archived_at" not in cols:
            try:
                cur.execute("ALTER TABLE memories ADD COLUMN archived_at TIMESTAMP")
            except Exception:
                pass
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

    def retrieve_similar(self, query: str, n_results: int = 5, min_tier: str = "Shortterm", top_k: int = None):
        """Search Chroma for similar items, with SQLite fallback."""
        if top_k is not None:
            n_results = top_k
        if self.collection:
            try:
                where_filter = {"tier": {"$ne": "Archived"}} if min_tier != "All" else None
                results = self.collection.query(
                    query_texts=[query],
                    n_results=n_results,
                    where=where_filter
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

        # Fallback to SQLite LIKE query (excluding Archived memories by default)
        conn = sqlite3.connect(self.sqlite_path)
        cur = conn.cursor()
        tier_clause = "AND tier != 'Archived'" if min_tier != "All" else ""
        cur.execute(f"SELECT id, content, tier, source, tags FROM memories WHERE content LIKE ? {tier_clause} ORDER BY created_at DESC LIMIT ?", (f"%{query}%", n_results))
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
                if new_tier == "Archived":
                    self.collection.delete(ids=[mem_id])
                else:
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

    def record_decision_trail(
        self,
        decision_summary: str,
        rationale: str,
        alternatives: str = "",
        tradeoffs: str = "",
        task_id: str = None,
        tags: str = "decision,pstack"
    ) -> str:
        """
        Records a structured decision trail into SQLite and vector indexes into ChromaDB.
        """
        import uuid
        trail_id = str(uuid.uuid4())
        conn = sqlite3.connect(self.sqlite_path)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO decision_trails (id, task_id, decision_summary, alternatives_considered, rationale, tradeoffs, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (trail_id, task_id, decision_summary, alternatives, rationale, tradeoffs, tags))
        conn.commit()
        conn.close()

        # Vectorize into memories
        vector_text = f"DECISION: {decision_summary}\nRATIONALE: {rationale}\nALTERNATIVES: {alternatives}\nTRADEOFFS: {tradeoffs}"
        self.save_memory(
            text=vector_text,
            tier="Longterm",
            source=f"decision:{task_id or 'general'}",
            tags=tags
        )
        return trail_id

    def ingest_decision_tsv(self, tsv_path: str) -> int:
        """
        Parses a TSV decision log (from /show-me-your-work) and ingests unindexed rows.
        Expected columns: timestamp \t task_id \t decision \t alternatives \t rationale \t tradeoffs
        """
        if not os.path.exists(tsv_path):
            return 0
        
        count = 0
        with open(tsv_path, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split("\t")
                if len(parts) >= 3:
                    if parts[0].lower() in ("timestamp", "date", "#"):
                        continue
                    task_id = parts[1] if len(parts) > 1 else None
                    decision = parts[2] if len(parts) > 2 else parts[0]
                    alts = parts[3] if len(parts) > 3 else ""
                    rationale = parts[4] if len(parts) > 4 else ""
                    tradeoffs = parts[5] if len(parts) > 5 else ""
                    self.record_decision_trail(
                        decision_summary=decision,
                        rationale=rationale,
                        alternatives=alts,
                        tradeoffs=tradeoffs,
                        task_id=task_id
                    )
                    count += 1
        return count

