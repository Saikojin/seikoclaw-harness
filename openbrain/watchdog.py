import hashlib
import time
import sqlite3
import os
from typing import List, Dict, Any, Optional, Tuple

class HealthPatrol:
    """
    Autonomous Watchdog & Health Patrol for SeikoClaw loops.
    Detects loop spin, repetitive failures, command stalls, and context ceiling limits.
    Supports in-memory and SQLite-backed telemetry persistence.
    """
    def __init__(self, spin_threshold: int = 3, context_limit: int = 1000000, ceiling_ratio: float = 0.85, db_path: Optional[str] = None):
        self.spin_threshold = spin_threshold
        self.context_limit = context_limit
        self.ceiling_ratio = ceiling_ratio
        self.db_path = db_path
        self.action_history: List[Dict[str, Any]] = []
        self.stall_events: List[Dict[str, Any]] = []
        if self.db_path:
            self._init_db()

    def _init_db(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS health_patrol_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action_type TEXT NOT NULL,
                    target TEXT NOT NULL,
                    signature TEXT NOT NULL,
                    success INTEGER NOT NULL,
                    result_snippet TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            conn.close()
        except Exception:
            pass

    def record_action(self, action_type: str, target: str, result_snippet: str = "", success: bool = True):
        """
        Records an action signature into health patrol buffer and database.
        """
        raw = f"{action_type}:{target}:{result_snippet[:200]}"
        sig = hashlib.sha256(raw.encode('utf-8')).hexdigest()[:12]
        
        entry = {
            "action_type": action_type,
            "target": target,
            "signature": sig,
            "success": success,
            "timestamp": time.time()
        }
        self.action_history.append(entry)

        if self.db_path:
            try:
                conn = sqlite3.connect(self.db_path)
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO health_patrol_actions (action_type, target, signature, success, result_snippet)
                    VALUES (?, ?, ?, ?, ?)
                """, (action_type, target, sig, int(success), result_snippet[:200]))
                conn.commit()
                conn.close()
            except Exception:
                pass

    def check_spin(self) -> Tuple[bool, Optional[str]]:
        """
        Checks if the last N actions have identical signatures or failure loops.
        """
        if len(self.action_history) < self.spin_threshold:
            return False, None

        recent = self.action_history[-self.spin_threshold:]
        first_sig = recent[0]["signature"]
        all_same = all(a["signature"] == first_sig for a in recent)
        
        if all_same:
            action_desc = f"{recent[0]['action_type']} on {recent[0]['target']}"
            return True, f"Agent spin detected: Repeated identical action {self.spin_threshold} times ({action_desc})."

        # Check consecutive failures
        all_failed = all(not a["success"] for a in recent)
        if all_failed:
            return True, f"Consecutive failure stall: {self.spin_threshold} actions failed in succession."

        return False, None

    def check_context_ceiling(self, current_tokens: int) -> Tuple[bool, float]:
        """
        Checks if context tokens exceed the ceiling ratio (default 85%).
        """
        ratio = current_tokens / max(self.context_limit, 1)
        is_breached = ratio >= self.ceiling_ratio
        return is_breached, ratio

    def get_health_status(self, current_tokens: int = 0) -> Dict[str, Any]:
        total_actions = len(self.action_history)
        if self.db_path and os.path.exists(self.db_path):
            try:
                conn = sqlite3.connect(self.db_path)
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM health_patrol_actions")
                row = cur.fetchone()
                if row:
                    total_actions = row[0]
                # Load recent actions if in-memory buffer is empty
                if not self.action_history:
                    cur.execute("""
                        SELECT action_type, target, signature, success, created_at 
                        FROM health_patrol_actions ORDER BY id DESC LIMIT 10
                    """)
                    rows = cur.fetchall()
                    for r in reversed(rows):
                        self.action_history.append({
                            "action_type": r[0],
                            "target": r[1],
                            "signature": r[2],
                            "success": bool(r[3]),
                            "timestamp": time.time()
                        })
                conn.close()
            except Exception:
                pass

        is_spinning, spin_msg = self.check_spin()
        ceiling_breached, ratio = self.check_context_ceiling(current_tokens)
        
        status = "HEALTHY"
        recommendations = []

        if is_spinning:
            status = "STALLED"
            recommendations.append("Trigger circuit-breaker: interrupt current execution, query OpenBrain for past mistakes, or summon Seikojin QA Strategist.")

        if ceiling_breached:
            status = "CONTEXT_CEILING" if status == "HEALTHY" else "CRITICAL"
            recommendations.append(f"Context utilization at {ratio*100:.1f}%. Trigger automatic memory checkpoint and re-prime next frontier task.")

        return {
            "status": status,
            "is_spinning": is_spinning,
            "spin_reason": spin_msg,
            "context_utilization": ratio,
            "ceiling_breached": ceiling_breached,
            "total_actions": total_actions,
            "recommendations": recommendations
        }
