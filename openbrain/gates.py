import json
import sqlite3
import subprocess
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from openbrain.task_graph import TaskGraph

class GateEngine:
    """
    Gates Engine for SeikoClaw Hybrid Architecture.
    Evaluates and certifies execution gates (QA, Human, Test, Timer, Merge-Slot)
    to protect critical DAG frontiers.
    """
    def __init__(self, task_graph: TaskGraph):
        self.graph = task_graph

    def attach_gate(self, task_id: str, gate_type: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Attaches an async gate (qa, human, test, timer, merge-slot) to a task node.
        """
        task = self.graph.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} does not exist.")

        meta_str = json.dumps(metadata or {})
        with self.graph._get_conn() as conn:
            conn.execute(
                """
                UPDATE task_nodes
                SET gate_type = ?,
                    gate_status = 'pending',
                    gate_metadata = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (gate_type, meta_str, task_id)
            )
            conn.commit()
            return True

    def evaluate_gate(self, task_id: str) -> Tuple[bool, str]:
        """
        Evaluates whether a task's gate is satisfied.
        Returns (is_satisfied, status_message).
        """
        task = self.graph.get_task(task_id)
        if not task:
            return False, f"Task {task_id} not found."

        gate_type = task.get("gate_type")
        gate_status = task.get("gate_status")

        if not gate_type or gate_status in ("passed", "bypassed"):
            return True, f"Gate '{gate_type or 'none'}' is satisfied ({gate_status})."

        if gate_status == "failed":
            return False, f"Gate '{gate_type}' has FAILED. Prerequisite action required."

        # Pending gate evaluations
        if gate_type == "qa":
            return False, "Awaiting Seikojin QA Engineer validation (Clean Slate + Rabbit Path certification)."
        elif gate_type == "human":
            return False, "Awaiting explicit human operator approval."
        elif gate_type == "test":
            meta = task.get("gate_metadata", {})
            test_cmd = meta.get("command")
            if test_cmd:
                try:
                    result = subprocess.run(test_cmd, shell=True, capture_output=True, text=True, timeout=120)
                    if result.returncode == 0:
                        self._set_gate_status(task_id, "passed")
                        return True, "Automated test gate passed successfully."
                    else:
                        self._set_gate_status(task_id, "failed")
                        return False, f"Automated test gate failed: {result.stderr.strip()}"
                except Exception as e:
                    return False, f"Test execution error: {str(e)}"
            return False, "Awaiting test execution command."
        
        return False, f"Gate '{gate_type}' is pending."

    def certify_qa_gate(
        self,
        task_id: str,
        engineer_signature: str = "Seikojin-QA-Engineer",
        rabbit_path_verified: bool = True,
        pass_rate: float = 1.0,
        notes: str = ""
    ) -> Tuple[bool, str]:
        """
        Certifies a QA gate according to Seikojin QA Rules:
        - 100% Pass Rate Mandate
        - Rabbit Path verification
        - Clean Slate state
        """
        task = self.graph.get_task(task_id)
        if not task:
            return False, f"Task {task_id} not found."

        if not rabbit_path_verified:
            self._set_gate_status(task_id, "failed")
            return False, "Seikojin QA Certification REJECTED: Primary Rabbit Path was not verified."

        if pass_rate < 1.0:
            self._set_gate_status(task_id, "failed")
            return False, f"Seikojin QA Certification REJECTED: Pass rate is {pass_rate * 100:.1f}%. Seikojin Rule #4 mandates 100% stable pass rate."

        # Update gate status and metadata
        meta = task.get("gate_metadata", {})
        meta["qa_certified_by"] = engineer_signature
        meta["qa_certified_at"] = datetime.now().isoformat()
        meta["qa_notes"] = notes
        meta["rabbit_path_verified"] = True
        meta["pass_rate"] = pass_rate

        with self.graph._get_conn() as conn:
            conn.execute(
                """
                UPDATE task_nodes
                SET gate_status = 'passed',
                    gate_metadata = ?,
                    status = 'closed',
                    closed_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (json.dumps(meta), task_id)
            )
            conn.commit()

        return True, f"Task {task_id} certified by {engineer_signature}. Downstream frontier unblocked."

    def approve_human_gate(self, task_id: str, approver: str = "user", notes: str = "") -> bool:
        task = self.graph.get_task(task_id)
        if not task:
            return False

        meta = task.get("gate_metadata", {})
        meta["approved_by"] = approver
        meta["approved_at"] = datetime.now().isoformat()
        meta["notes"] = notes

        with self.graph._get_conn() as conn:
            conn.execute(
                """
                UPDATE task_nodes
                SET gate_status = 'passed',
                    gate_metadata = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (json.dumps(meta), task_id)
            )
            conn.commit()
            return True

    def _set_gate_status(self, task_id: str, status: str):
        with self.graph._get_conn() as conn:
            conn.execute(
                "UPDATE task_nodes SET gate_status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (status, task_id)
            )
            conn.commit()
