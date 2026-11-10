# Security Audit & Coverage Ledger Standard

This standard defines the requirements for conducting defensive, source-grounded security audits and maintaining deterministic coverage ledgers across SeikoClaw codebases, adopting Cloudflare's verified security audit methodology.

---

## 1. Core Principles

1. **Defensive & Source-First**:
   A candidate finding without a concrete affected principal, resource, or demonstrable security outcome is **never** confirmed. Speculative vulnerabilities with missing runtime assumptions must carry verdict `needs_validation` with zero severity.

2. **Adversarial Disproof Verification**:
   No hunter agent may verify its own candidate finding. Every candidate finding must be submitted to a fresh, isolated verifier agent whose explicit objective is to **disprove** the vulnerability (find sanitizers, trace framework invariants, or break the exploit path).

3. **Deterministic Coverage Accounting**:
   All audit passes track reviewed attack surfaces, trust boundaries, and subsystems within a mechanical `coverage-ledger.json` document. Unexamined surfaces are treated as unverified.

---

## 2. Coverage Ledger Specification (`coverage-ledger.json`)

The coverage ledger is a top-level JSON array of coverage units, sorted lexicographically by `coverage_id`.

### Required Unit Structure

```json
{
  "coverage_id": "<canonical-id>",
  "canonical_refs": {
    "surface": "<entrypoint-or-route>",
    "boundary": "<trust-boundary-name>",
    "subsystem": "<subsystem-name>",
    "attack_class": "ATTACK-CLASSES.md#<Class-Name>"
  },
  "surface": "Human readable surface description",
  "boundary": "Human readable trust boundary",
  "subsystem": "Subsystem label",
  "attack_class": "Classification",
  "starting_paths": ["path/to/source.ts"],
  "ordinary_attack_class_block": "ATTACK-CLASSES.md#<Class-Name>",
  "selected_companion_blocks": [],
  "excluded_blocks": [],
  "prior_status": "new",
  "attempts": [],
  "wave": 1,
  "status": "planned | covered | candidate | blocked | not_applicable",
  "agent_id": null,
  "reviewed_paths": [],
  "local_checks": [],
  "result_fingerprints": [],
  "unresolved": []
}
```

### Mechanical Validation
Every ledger must pass automated validation:
```bash
node .agents/skills/cloudflare-security-audit/validate-coverage-ledger.cjs path/to/coverage-ledger.json
```

---

## 3. Finding Verdicts & Schema (`findings.json`)

Findings must strictly conform to `report-schema.json`:

1. **`confirmed`**:
   - Complete, verified source trace from entry point to sink.
   - Demonstrated or safely reproduced impact.
   - Survived adversarial disproof attempts.
   - Smallest effective remediation patch included.

2. **`needs_validation`**:
   - Specific unresolved factual question or missing deployment check.
   - **Zero severity assigned** to prevent alarm fatigue.
   - Actionable local or deployment validation plan provided.

3. **`rejected`**:
   - Explicitly preserves disproved candidate hypotheses and the reason they were rejected.
   - Prevents future audit waves from wasting cycles on disproved paths.

### Mechanical Validation
```bash
node .agents/skills/cloudflare-security-audit/validate-findings.cjs path/to/findings.json
```

---

## 4. Integration with SeikoClaw OpenBrain

* **Declarative Playbook**: Run via `python seikoclaw.py task --title "<Audit Goal>" --playbook security-audit`.
* **Execution Gate**: Critical candidate findings are evaluated through `gate:disproof` ([`GateEngine`](file:///d:/DevWorkspace/SeikoClaw-Harness/openbrain/gates.py)).
