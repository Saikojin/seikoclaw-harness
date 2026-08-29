# Task Checklist: [Feature / Task Goal]

> **Context**: [Brief context or implementation plan link]
> **Status**: In Progress <!-- In Progress | Blocked | Completed -->

## Prerequisites & Grounding
- [ ] Review Openbrain memories & known mistakes: `python seikoclaw.py memory --query "[topic]"`
- [ ] Review `.master_wiki/` guidelines and relevant `.agents/skills/`

---

## Execution Tasks

<!--
Every discrete execution block must take no more than 1-2 edits and 1 verification run.
Tasks must use checkbox format `- [ ]` so completion triggers the automated learning loop.
-->

- [ ] **Task 1: [Component / Unit Setup]**
  - Files: `path/to/file`
  - Action: Implement logic
  - Verify: `pytest path/to/test.py` or `npm test`

- [ ] **Task 2: [Implementation Core]**
  - Files: `path/to/file`
  - Action: Implement core logic
  - Verify: `pytest ...`

- [ ] **Task 3: [Integration & Verification]**
  - Files: `path/to/file`
  - Action: Verify end-to-end functionality
  - Verify: `python seikoclaw.py execute --task [TASK_ID] --verify "[command]"`

---

## Post-Completion Learning Trigger

<!--
When all checkboxes above are marked `- [x]`, run auto_capture to trigger the
automated skill evolution, regression gating, and Master Wiki sync.
-->
- [ ] **Auto-Capture & Reflection Hook**: `python auto_capture.py`
