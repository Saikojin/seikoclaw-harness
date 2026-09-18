import unittest
from openbrain.watchdog import HealthPatrol

class TestWatchdog(unittest.TestCase):
    def test_spin_detection_identical_actions(self):
        patrol = HealthPatrol(spin_threshold=3)
        
        # Record 2 actions - not yet spinning
        patrol.record_action("file_edit", "src/auth.py", result_snippet="SyntaxError: unexpected EOF", success=False)
        patrol.record_action("file_edit", "src/auth.py", result_snippet="SyntaxError: unexpected EOF", success=False)
        is_spin, _ = patrol.check_spin()
        self.assertFalse(is_spin)

        # 3rd identical action triggers spin detection
        patrol.record_action("file_edit", "src/auth.py", result_snippet="SyntaxError: unexpected EOF", success=False)
        is_spin, msg = patrol.check_spin()
        self.assertTrue(is_spin)
        self.assertIn("spin detected", msg)

    def test_consecutive_failure_detection(self):
        patrol = HealthPatrol(spin_threshold=3)
        
        # 3 different failed actions
        patrol.record_action("run_command", "npm test", result_snippet="Error: 1 failed", success=False)
        patrol.record_action("run_command", "pytest", result_snippet="FAILED", success=False)
        patrol.record_action("run_command", "python run.py", result_snippet="ModuleNotFoundError", success=False)

        is_spin, msg = patrol.check_spin()
        self.assertTrue(is_spin)
        self.assertIn("Consecutive failure", msg)

    def test_context_ceiling_detection(self):
        patrol = HealthPatrol(context_limit=100000, ceiling_ratio=0.85)
        
        # 80k tokens -> 80% (under ceiling)
        breached, ratio = patrol.check_context_ceiling(80000)
        self.assertFalse(breached)
        self.assertAlmostEqual(ratio, 0.80, places=2)

        # 86k tokens -> 86% (breaches ceiling)
        breached, ratio = patrol.check_context_ceiling(86000)
        self.assertTrue(breached)
        self.assertAlmostEqual(ratio, 0.86, places=2)

    def test_health_diagnostics_report(self):
        patrol = HealthPatrol(spin_threshold=2, context_limit=100000, ceiling_ratio=0.85)
        patrol.record_action("run", "build", "Failed", success=False)
        patrol.record_action("run", "build", "Failed", success=False)

        status = patrol.get_health_status(current_tokens=90000)
        self.assertEqual(status["status"], "CRITICAL")
        self.assertTrue(status["is_spinning"])
        self.assertTrue(status["ceiling_breached"])
        self.assertGreater(len(status["recommendations"]), 0)

if __name__ == "__main__":
    unittest.main()
