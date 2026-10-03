import os
import tempfile
import pytest
from openbrain.task_graph import TaskGraph
from openbrain.playbooks import get_playbook, list_playbooks
from openbrain.gates import GateEngine


def test_playbooks_registry():
    pbs = list_playbooks()
    assert len(pbs) >= 6
    names = [p["name"] for p in pbs]
    assert "bug-fix" in names
    assert "feature" in names
    assert "hillclimb" in names
    assert "refactoring" in names
    assert "visual-parity" in names
    assert "shipping" in names


def test_playbook_expansion_creates_sequential_dag():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    try:
        tg = TaskGraph(db_path)
        task_id = tg.create_task("Investigate and Fix Scroll Drift", playbook="bug-fix")
        
        # Verify parent status
        parent = tg.get_task(task_id)
        assert parent["status"] == "in_progress"
        assert parent["playbook"] == "bug-fix"

        # Verify child steps
        tasks = tg.list_tasks()
        child_wisps = [t for t in tasks if t.get("is_ephemeral")]
        assert len(child_wisps) == 6
        assert child_wisps[0]["title"] == "[bug-fix] Repro Defect (Failing Evidence)"

        # Check ready frontier has only the first step
        frontier = tg.get_ready_frontier()
        assert len(frontier) == 1
        assert frontier[0]["id"] == child_wisps[0]["id"]

        # Close first step, verify second step unlocks
        tg.close_task(frontier[0]["id"])
        frontier2 = tg.get_ready_frontier()
        assert len(frontier2) == 1
        assert frontier2[0]["id"] == child_wisps[1]["id"]
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_adversarial_gate_lifecycle():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    try:
        tg = TaskGraph(db_path)
        ge = GateEngine(tg)

        task_id = tg.create_task("Ship Security Refactor", gate_type="adversarial")
        
        # Initial evaluation should be blocked
        is_sat, msg = ge.evaluate_gate(task_id)
        assert not is_sat
        assert "Awaiting multi-model adversarial interrogation" in msg

        # Reject certification with blocking issue
        rej_ok, rej_msg = ge.certify_adversarial_gate(
            task_id,
            reviewer_model="opus-4.5",
            findings=[{"severity": "high", "message": "Potential timing attack on HMAC"}],
            has_blocking_issues=True
        )
        assert not rej_ok
        assert "REJECTED" in rej_msg

        # Post-rejection eval should be failed
        is_sat_fail, _ = ge.evaluate_gate(task_id)
        assert not is_sat_fail

        # Certify clean pass
        pass_ok, pass_msg = ge.certify_adversarial_gate(
            task_id,
            reviewer_model="claude-3-7-sonnet",
            findings=[],
            has_blocking_issues=False,
            notes="Zero security vulnerabilities found."
        )
        assert pass_ok
        assert "cleared adversarial interrogation" in pass_msg

        # Post-pass eval
        is_sat_pass, _ = ge.evaluate_gate(task_id)
        assert is_sat_pass
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)
