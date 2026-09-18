import sqlite3
import hashlib
import time
import os
import json
import re
import contextlib
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple

class TaskGraph:
    """
    DAG-based Task Graph and Ready Frontier Engine for SeikoClaw.
    Provides dependency-aware task tracking, hash-based collision-free IDs,
    async gates, and claimable frontier computation.
    """
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_tables()

    @contextlib.contextmanager
    def _get_conn(self):
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        try:
            yield conn
        finally:
            conn.close()

    def _init_tables(self):
        with self._get_conn() as conn:
            conn.executescript("""
            CREATE TABLE IF NOT EXISTS task_nodes (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                status TEXT CHECK(status IN ('open', 'in_progress', 'in_qa', 'blocked', 'closed', 'deferred')) DEFAULT 'open',
                priority INTEGER DEFAULT 2, -- 0=critical, 1=high, 2=normal, 3=low, 4=backlog
                task_type TEXT DEFAULT 'task', -- task, bug, epic, wisp, spike
                assignee TEXT DEFAULT NULL,
                is_ephemeral INTEGER DEFAULT 0,
                gate_type TEXT DEFAULT NULL, -- qa, human, test, timer, merge-slot
                gate_status TEXT DEFAULT 'pending', -- pending, passed, failed, bypassed
                gate_metadata TEXT DEFAULT '{}',
                claimed_by TEXT DEFAULT NULL,
                claimed_at TIMESTAMP DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                closed_at TIMESTAMP DEFAULT NULL
            );

            CREATE TABLE IF NOT EXISTS task_edges (
                from_id TEXT NOT NULL,
                to_id TEXT NOT NULL,
                edge_type TEXT CHECK(edge_type IN ('blocks', 'parent-child', 'waits-for', 'relates-to', 'discovered-from')) DEFAULT 'blocks',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (from_id, to_id, edge_type),
                FOREIGN KEY (from_id) REFERENCES task_nodes(id) ON DELETE CASCADE,
                FOREIGN KEY (to_id) REFERENCES task_nodes(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_task_nodes_status ON task_nodes(status);
            CREATE INDEX IF NOT EXISTS idx_task_edges_to ON task_edges(to_id);
            CREATE INDEX IF NOT EXISTS idx_task_edges_from ON task_edges(from_id);
            """)
            conn.commit()

    def generate_id(self, title: str, parent_id: Optional[str] = None) -> str:
        """
        Generates a content-derived collision-free hash ID (e.g. sc-a1b2 or sc-a1b2.1).
        Adaptive length ensures zero collision.
        """
        with self._get_conn() as conn:
            if parent_id:
                # Generate hierarchical sub-id: parent_id.1, parent_id.2, etc.
                cursor = conn.execute(
                    "SELECT id FROM task_nodes WHERE id LIKE ? ORDER BY LENGTH(id) DESC, id DESC",
                    (f"{parent_id}.%",)
                )
                rows = cursor.fetchall()
                child_nums = []
                for row in rows:
                    match = re.match(rf"^{re.escape(parent_id)}\.(\d+)$", row["id"])
                    if match:
                        child_nums.append(int(match.group(1)))
                next_num = max(child_nums, default=0) + 1
                return f"{parent_id}.{next_num}"

            # Top-level hash ID: sc-xxxx
            nonce = 0
            while True:
                raw_str = f"{title}_{time.time_ns()}_{nonce}"
                digest = hashlib.sha256(raw_str.encode('utf-8')).hexdigest()
                short_hash = digest[:4]
                candidate_id = f"sc-{short_hash}"
                
                cursor = conn.execute("SELECT id FROM task_nodes WHERE id = ?", (candidate_id,))
                if not cursor.fetchone():
                    return candidate_id
                
                # Expand hash if colliding
                if nonce > 5:
                    candidate_id = f"sc-{digest[:6]}"
                    cursor = conn.execute("SELECT id FROM task_nodes WHERE id = ?", (candidate_id,))
                    if not cursor.fetchone():
                        return candidate_id
                nonce += 1

    def create_task(
        self,
        title: str,
        description: str = "",
        priority: int = 2,
        task_type: str = "task",
        parent_id: Optional[str] = None,
        gate_type: Optional[str] = None,
        is_ephemeral: bool = False,
        task_id: Optional[str] = None,
        gate_metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Creates a new task node in the DAG.
        """
        if not task_id:
            task_id = self.generate_id(title, parent_id=parent_id)

        meta_str = json.dumps(gate_metadata or {})
        with self._get_conn() as conn:
            conn.execute(
                """
                INSERT INTO task_nodes (
                    id, title, description, priority, task_type,
                    gate_type, is_ephemeral, gate_metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (task_id, title, description, priority, task_type, gate_type, int(is_ephemeral), meta_str)
            )

            if parent_id:
                # Add parent-child edge
                conn.execute(
                    "INSERT OR IGNORE INTO task_edges (from_id, to_id, edge_type) VALUES (?, ?, 'parent-child')",
                    (parent_id, task_id)
                )
            conn.commit()

        return task_id

    def create_wisp(self, title: str, description: str = "", parent_id: Optional[str] = None) -> str:
        """
        Creates an ephemeral wisp task.
        """
        return self.create_task(
            title=title,
            description=description,
            priority=2,
            task_type="wisp",
            parent_id=parent_id,
            is_ephemeral=True
        )

    def add_dependency(self, from_id: str, to_id: str, edge_type: str = "blocks") -> bool:
        """
        Adds a directed dependency edge: `from_id` blocks/precedes `to_id`.
        Performs cycle detection to ensure DAG validity.
        """
        if from_id == to_id:
            raise ValueError(f"Cannot create self-referencing dependency on {from_id}")

        with self._get_conn() as conn:
            # Check existence
            c1 = conn.execute("SELECT id FROM task_nodes WHERE id = ?", (from_id,)).fetchone()
            c2 = conn.execute("SELECT id FROM task_nodes WHERE id = ?", (to_id,)).fetchone()
            if not c1 or not c2:
                raise ValueError(f"Both task IDs must exist: {from_id} -> {to_id}")

            # Check for cycles if adding a blocking edge
            if edge_type in ("blocks", "waits-for", "parent-child"):
                if self._has_path(conn, start_id=to_id, target_id=from_id):
                    raise ValueError(f"Circular dependency detected: adding {from_id} -> {to_id} creates a cycle.")

            conn.execute(
                "INSERT OR IGNORE INTO task_edges (from_id, to_id, edge_type) VALUES (?, ?, ?)",
                (from_id, to_id, edge_type)
            )
            conn.commit()
            return True

    def remove_dependency(self, from_id: str, to_id: str, edge_type: Optional[str] = None) -> bool:
        with self._get_conn() as conn:
            if edge_type:
                conn.execute("DELETE FROM task_edges WHERE from_id = ? AND to_id = ? AND edge_type = ?", (from_id, to_id, edge_type))
            else:
                conn.execute("DELETE FROM task_edges WHERE from_id = ? AND to_id = ?", (from_id, to_id))
            conn.commit()
            return True

    def _has_path(self, conn: sqlite3.Connection, start_id: str, target_id: str) -> bool:
        """
        Checks if a directed path exists from start_id to target_id along blocking/waits-for edges.
        """
        visited = set()
        queue = [start_id]
        while queue:
            curr = queue.pop(0)
            if curr == target_id:
                return True
            if curr in visited:
                continue
            visited.add(curr)

            cursor = conn.execute(
                "SELECT to_id FROM task_edges WHERE from_id = ? AND edge_type IN ('blocks', 'waits-for', 'parent-child')",
                (curr,)
            )
            for row in cursor.fetchall():
                queue.append(row["to_id"])
        return False

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        with self._get_conn() as conn:
            cursor = conn.execute("SELECT * FROM task_nodes WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            if not row:
                return None
            
            task = dict(row)
            # Fetch dependencies
            in_deps = conn.execute(
                "SELECT from_id, edge_type FROM task_edges WHERE to_id = ?", (task_id,)
            ).fetchall()
            out_deps = conn.execute(
                "SELECT to_id, edge_type FROM task_edges WHERE from_id = ?", (task_id,)
            ).fetchall()

            task["blocked_by"] = [dict(d) for d in in_deps]
            task["blocks"] = [dict(d) for d in out_deps]
            try:
                task["gate_metadata"] = json.loads(task.get("gate_metadata") or "{}")
            except Exception:
                task["gate_metadata"] = {}
            return task

    def list_tasks(self, status: Optional[str] = None, include_ephemeral: bool = True) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            query = "SELECT * FROM task_nodes WHERE 1=1"
            params = []
            if status:
                query += " AND status = ?"
                params.append(status)
            if not include_ephemeral:
                query += " AND is_ephemeral = 0"
            query += " ORDER BY priority ASC, created_at ASC"

            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    def get_ready_frontier(self, include_ephemeral: bool = True) -> List[Dict[str, Any]]:
        """
        Computes the claimable frontier:
        Tasks with status = 'open' whose prerequisite blockers (edges with 'blocks' or 'waits-for')
        are all closed, and whose parent epics are not blocked.
        """
        with self._get_conn() as conn:
            ephemeral_filter = "" if include_ephemeral else "AND t.is_ephemeral = 0"
            query = f"""
            SELECT t.*
            FROM task_nodes t
            WHERE t.status = 'open'
            {ephemeral_filter}
            AND NOT EXISTS (
                -- Has an unclosed blocker
                SELECT 1 FROM task_edges e
                JOIN task_nodes blocker ON e.from_id = blocker.id
                WHERE e.to_id = t.id
                AND e.edge_type IN ('blocks', 'waits-for')
                AND blocker.status != 'closed'
            )
            ORDER BY t.priority ASC, t.created_at ASC
            """
            rows = conn.execute(query).fetchall()
            results = []
            for row in rows:
                t_dict = dict(row)
                try:
                    t_dict["gate_metadata"] = json.loads(t_dict.get("gate_metadata") or "{}")
                except Exception:
                    t_dict["gate_metadata"] = {}
                results.append(t_dict)
            return results

    def claim_task(self, task_id: str, worker_id: str) -> bool:
        """
        Atomically claims a task for a worker.
        """
        with self._get_conn() as conn:
            cursor = conn.execute(
                """
                UPDATE task_nodes
                SET status = 'in_progress',
                    claimed_by = ?,
                    claimed_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND status = 'open'
                """,
                (worker_id, task_id)
            )
            conn.commit()
            return cursor.rowcount > 0

    def claim_next_ready(self, worker_id: str, include_ephemeral: bool = True) -> Optional[Dict[str, Any]]:
        """
        Atomically claims the highest-priority ready task from the frontier.
        """
        frontier = self.get_ready_frontier(include_ephemeral=include_ephemeral)
        for candidate in frontier:
            if self.claim_task(candidate["id"], worker_id):
                return self.get_task(candidate["id"])
        return None

    def update_status(self, task_id: str, status: str, assignee: Optional[str] = None) -> bool:
        """
        Updates task status (open, in_progress, in_qa, blocked, closed, deferred).
        """
        with self._get_conn() as conn:
            closed_clause = ", closed_at = CURRENT_TIMESTAMP" if status == "closed" else ""
            if assignee:
                cursor = conn.execute(
                    f"""
                    UPDATE task_nodes
                    SET status = ?, assignee = ?, updated_at = CURRENT_TIMESTAMP {closed_clause}
                    WHERE id = ?
                    """,
                    (status, assignee, task_id)
                )
            else:
                cursor = conn.execute(
                    f"""
                    UPDATE task_nodes
                    SET status = ?, updated_at = CURRENT_TIMESTAMP {closed_clause}
                    WHERE id = ?
                    """,
                    (status, task_id)
                )
            conn.commit()
            return cursor.rowcount > 0

    def close_task(self, task_id: str) -> bool:
        return self.update_status(task_id, "closed")

    def purge_wisps(self) -> int:
        """
        Deletes all closed ephemeral wisps from database.
        """
        with self._get_conn() as conn:
            cursor = conn.execute(
                "DELETE FROM task_nodes WHERE is_ephemeral = 1 AND status = 'closed'"
            )
            deleted_count = cursor.rowcount
            conn.commit()
            return deleted_count

    def to_markdown(self) -> str:
        """
        Renders the task graph as a clean, hierarchical markdown checklist.
        """
        tasks = self.list_tasks(include_ephemeral=True)
        if not tasks:
            return "# Project Tasks\n\nNo tasks currently recorded.\n"

        # Organize by top-level vs children
        top_level = [t for t in tasks if "." not in t["id"]]
        children_map: Dict[str, List[Dict[str, Any]]] = {}
        for t in tasks:
            if "." in t["id"]:
                parent_prefix = t["id"].rsplit(".", 1)[0]
                children_map.setdefault(parent_prefix, []).append(t)

        lines = ["# SeikoClaw Task Board & DAG Frontier\n"]
        
        # Add ready frontier callout
        frontier = self.get_ready_frontier()
        if frontier:
            lines.append("## 🚀 Ready Frontier (Claimable Work)")
            for r in frontier:
                gate_tag = f" `[{r['gate_type'].upper()}_GATE]`" if r.get("gate_type") else ""
                lines.append(f"- **`{r['id']}`**: {r['title']} (P{r['priority']}){gate_tag}")
            lines.append("\n---\n")

        lines.append("## 📋 All Tasks\n")

        def render_item(t: Dict[str, Any], indent_level: int = 0) -> str:
            indent = "  " * indent_level
            check = "x" if t["status"] == "closed" else (" " if t["status"] == "open" else "~")
            gate_badge = f" `[GATE: {t['gate_type'].upper()}]`" if t.get("gate_type") else ""
            wisp_badge = " `[WISP]`" if t.get("is_ephemeral") else ""
            status_badge = f" `({t['status'].upper()})`" if t["status"] not in ("open", "closed") else ""
            
            res = f"{indent}- [{check}] **`{t['id']}`**: {t['title']} (P{t['priority']}){status_badge}{gate_badge}{wisp_badge}"
            if t.get("description"):
                res += f"\n{indent}  - {t['description']}"
            return res

        for item in top_level:
            lines.append(render_item(item, 0))
            if item["id"] in children_map:
                for child in children_map[item["id"]]:
                    lines.append(render_item(child, 1))

        return "\n".join(lines) + "\n"

    def sync_to_file(self, file_path: str):
        content = self.to_markdown()
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
