import unittest
import os
import tempfile
import shutil
from openbrain.task_graph import TaskGraph
from openbrain.gates import GateEngine

class TestGates(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_openbrain.db")
        self.graph = TaskGraph(self.db_path)
        self.gates = GateEngine(self.graph)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_attach_and_evaluate_gate(self):
        tid = self.graph.create_task("Implement Auth Tokens")
        self.gates.attach_gate(tid, "qa")

        sat, reason = self.gates.evaluate_gate(tid)
        self.assertFalse(sat)
        self.assertIn("Seikojin QA", reason)

    def test_seikojin_qa_certification_100_percent_mandate(self):
        t_core = self.graph.create_task("Core Payment Engine", gate_type="qa")
        t_downstream = self.graph.create_task("Payment Analytics Reporting")
        self.graph.add_dependency(t_core, t_downstream, edge_type="blocks")

        # Downstream must be blocked
        frontier = self.graph.get_ready_frontier()
        self.assertNotIn(t_downstream, [t["id"] for t in frontier])

        # Attempt certification with 95% pass rate (Must fail according to Seikojin Rules)
        ok, msg = self.gates.certify_qa_gate(t_core, pass_rate=0.95, notes="One flaky test")
        self.assertFalse(ok)
        self.assertIn("REJECTED", msg)

        # Attempt certification without Rabbit Path verification (Must fail)
        ok2, msg2 = self.gates.certify_qa_gate(t_core, rabbit_path_verified=False, pass_rate=1.0)
        self.assertFalse(ok2)
        self.assertIn("Rabbit Path", msg2)

        # Successful 100% certification
        ok3, msg3 = self.gates.certify_qa_gate(t_core, rabbit_path_verified=True, pass_rate=1.0, notes="100% stable pass")
        self.assertTrue(ok3)

        # Verify task is closed and downstream task is now on the ready frontier
        task = self.graph.get_task(t_core)
        self.assertEqual(task["status"], "closed")
        self.assertEqual(task["gate_status"], "passed")

        frontier_after = self.graph.get_ready_frontier()
        self.assertIn(t_downstream, [t["id"] for t in frontier_after])

    def test_human_approval_gate(self):
        tid = self.graph.create_task("Deploy to Production", gate_type="human")
        sat, _ = self.gates.evaluate_gate(tid)
        self.assertFalse(sat)

        ok = self.gates.approve_human_gate(tid, approver="lead-architect", notes="Approved for staging deployment")
        self.assertTrue(ok)

        task = self.graph.get_task(tid)
        self.assertEqual(task["gate_status"], "passed")
        self.assertEqual(task["gate_metadata"]["approved_by"], "lead-architect")

if __name__ == "__main__":
    unittest.main()
