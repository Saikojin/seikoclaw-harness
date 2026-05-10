---
name: learnings
description: Captures session-specific technical insights, updates the knowledge base, and syncs to Openbrain.
---

# Learnings Skill

## Goal
To crystallize technical "gotchas," architectural patterns, and process improvements discovered during a session into permanent agent memory.

## Workflow
1. **Distill**: Analyze the session and identify pitfalls, dependency solutions, or structural rules.
2. **Report**: Create a summary table of findings.
3. **Update**: Create/Update Knowledge Items (KIs) in `.master_wiki/`.
4. **Sync**: Use `openbrain/engine.py` to record the learnings.

## Checklists
- [ ] Learnings are specific and actionable.
- [ ] `.master_wiki/` is updated with relevant standards.
- [ ] Openbrain memory is updated.
