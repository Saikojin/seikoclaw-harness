"""
Declarative Execution Playbooks for SeikoClaw OpenBrain Engine.
Adapted from Lauren Tan's pstack playbooks for high-rigor, verified engineering.
"""

from typing import Dict, List, Any, Optional

PLAYBOOKS: Dict[str, Dict[str, Any]] = {
    "bug-fix": {
        "name": "bug-fix",
        "description": "Reproduce a defect, root-cause it, fix with runtime evidence, verify blast radius, and deslop.",
        "steps": [
            {
                "title": "Repro Defect (Failing Evidence)",
                "description": "Write or run a minimal reproduction script/test that triggers the failure. Capture failing output.",
                "task_type": "wisp",
                "gate_type": "test"
            },
            {
                "title": "Root Cause Investigation (/how, /why)",
                "description": "Trace symptom to underlying root cause. Identify exact broken invariant. Do not add symptom patches.",
                "task_type": "wisp",
                "gate_type": None
            },
            {
                "title": "Implement Root Cause Fix",
                "description": "Implement minimal fix adhering to Laziness Protocol and Boundary Discipline.",
                "task_type": "wisp",
                "gate_type": None
            },
            {
                "title": "Verify Passing State (Passing Evidence)",
                "description": "Re-run the reproduction test to prove the defect is resolved with real runtime output.",
                "task_type": "wisp",
                "gate_type": "test"
            },
            {
                "title": "Blast Radius & Regression Audit (/blast-radius)",
                "description": "Audit callers crossing module boundaries and execute full test suite to guarantee zero regressions.",
                "task_type": "wisp",
                "gate_type": "qa"
            },
            {
                "title": "Anti-Slop Clean (/no-comments, /deslop)",
                "description": "Strip noisy comments, remove dead weight and single-caller wrappers, convert invariants to assertions.",
                "task_type": "wisp",
                "gate_type": None
            }
        ]
    },
    "feature": {
        "name": "feature",
        "description": "Build new or changed capability starting from foundational data domain models.",
        "steps": [
            {
                "title": "Model Domain Data Structures",
                "description": "Define core types, schemas, and invariants first. Make illegal states unrepresentable.",
                "task_type": "wisp",
                "gate_type": None
            },
            {
                "title": "Boundary Interfaces & Validation",
                "description": "Implement public interfaces and concentrate input validation at boundaries.",
                "task_type": "wisp",
                "gate_type": None
            },
            {
                "title": "Implement Pure Core Logic",
                "description": "Implement business logic as pure, predictable functions without scattered conditionals.",
                "task_type": "wisp",
                "gate_type": None
            },
            {
                "title": "Behavioral Test Coverage (/tdd)",
                "description": "Write behavioral unit and integration tests asserting observable user-facing outcomes.",
                "task_type": "wisp",
                "gate_type": "test"
            },
            {
                "title": "Anti-Slop Hardening & Documentation",
                "description": "Clean diff with /deslop and /no-comments. Document public interface in repo docs.",
                "task_type": "wisp",
                "gate_type": "qa"
            }
        ]
    },
    "hillclimb": {
        "name": "hillclimb",
        "description": "Sustained, scientific metric optimization looping hypotheses with 1-commit-per-win.",
        "steps": [
            {
                "title": "Establish Baseline Measurement",
                "description": "Profile current performance/metric with /benchmark-checklist and /explain-the-number.",
                "task_type": "wisp",
                "gate_type": "test"
            },
            {
                "title": "Formulate Focused Hypothesis",
                "description": "Identify single bottleneck limiter and specify precise optimization mechanism.",
                "task_type": "wisp",
                "gate_type": None
            },
            {
                "title": "Apply Optimization",
                "description": "Implement single change in isolated sandbox branch.",
                "task_type": "wisp",
                "gate_type": None
            },
            {
                "title": "Measure Delta & Verify Limitation",
                "description": "Run benchmark suite. Verify measured gain against baseline. Reject if no statistically valid gain.",
                "task_type": "wisp",
                "gate_type": "test"
            },
            {
                "title": "Log Decision Trail & Commit (/show-me-your-work)",
                "description": "Record hypothesis, baseline, delta, and verdict in decision trail. Commit single win.",
                "task_type": "wisp",
                "gate_type": None
            }
        ]
    },
    "refactoring": {
        "name": "refactoring",
        "description": "Behavior-preserving structural migration to converge directly on target architecture.",
        "steps": [
            {
                "title": "Characterization Testing",
                "description": "Ensure existing behavior is completely locked in by automated tests before touching code.",
                "task_type": "wisp",
                "gate_type": "test"
            },
            {
                "title": "Subtract Dead Weight (/deslop)",
                "description": "Delete unused helpers, stubs, and redundant layers before restructuring.",
                "task_type": "wisp",
                "gate_type": None
            },
            {
                "title": "Structural Migration",
                "description": "Migrate module to target architecture in one clean wave.",
                "task_type": "wisp",
                "gate_type": None
            },
            {
                "title": "Delete Legacy APIs & Callers",
                "description": "Update all callers and delete legacy API in the same wave. No temporary bridge shims.",
                "task_type": "wisp",
                "gate_type": None
            },
            {
                "title": "Verify Parity & Blast Radius",
                "description": "Prove 100% test pass rate and behavior preservation across all dependent modules.",
                "task_type": "wisp",
                "gate_type": "qa"
            }
        ]
    },
    "visual-parity": {
        "name": "visual-parity",
        "description": "Pixel-exact UI equivalence between implementation and design reference.",
        "steps": [
            {
                "title": "Capture Baseline State",
                "description": "Take automated screenshot / DOM layout snapshot of reference target.",
                "task_type": "wisp",
                "gate_type": None
            },
            {
                "title": "Inspect Visual Deltas",
                "description": "Compare margins, font metrics, color contrasts, padding, and alignment.",
                "task_type": "wisp",
                "gate_type": None
            },
            {
                "title": "Apply Visual Refinements",
                "description": "Apply targeted CSS/layout adjustments following Emil Kowalski motion and optical alignment.",
                "task_type": "wisp",
                "gate_type": None
            },
            {
                "title": "Certify Visual Parity",
                "description": "Capture new screenshot and verify pixel-level parity against reference.",
                "task_type": "wisp",
                "gate_type": "qa"
            }
        ]
    },
    "shipping": {
        "name": "shipping",
        "description": "Independently verify green stack, execute adversarial interrogation, and land stack bottom-up.",
        "steps": [
            {
                "title": "Independent Stack Verification",
                "description": "Re-run full clean test suite on each commit/PR in stack bottom-up.",
                "task_type": "wisp",
                "gate_type": "test"
            },
            {
                "title": "Adversarial Interrogation (/interrogate)",
                "description": "Perform multi-model red-team review on cumulative diff. Zero blocking issues required.",
                "task_type": "wisp",
                "gate_type": "adversarial"
            },
            {
                "title": "Land Verified Stack",
                "description": "Merge contiguous green verified run to main. Update project state in OpenBrain.",
                "task_type": "wisp",
                "gate_type": "human"
            }
        ]
    }
}


def get_playbook(name: str) -> Optional[Dict[str, Any]]:
    """Retrieves a playbook definition by name."""
    return PLAYBOOKS.get(name.lower().strip())


def list_playbooks() -> List[Dict[str, Any]]:
    """Returns a list of all available playbook summaries."""
    return [
        {"name": k, "description": v["description"], "step_count": len(v["steps"])}
        for k, v in PLAYBOOKS.items()
    ]
