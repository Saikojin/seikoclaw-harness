import hashlib
import time
from typing import List, Dict, Any, Optional, Tuple

class HealthPatrol:
    """
    Autonomous Watchdog & Health Patrol for SeikoClaw loops.
    Detects loop spin, repetitive failures, command stalls, and context ceiling limits.
    """
    def __init__(self, spin_threshold: int = 3, context_limit: int = 1000000, ceiling_ratio: float = 0.85):
        self.spin_threshold = spin_threshold
        self.context_limit = context_limit
        self.ceiling_ratio = ceiling_ratio
        self.action_history: List[Dict[str, Any]] = []
        self.stall_events: List[Dict[str, Any]] = []

    def record_action(self, action_type: str, target: str, result_snippet: str = "", success: bool = True):
        """
        Records an action signature into health patrol buffer.
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
            "total_actions": len(self.action_history),
            "recommendations": recommendations
        }
