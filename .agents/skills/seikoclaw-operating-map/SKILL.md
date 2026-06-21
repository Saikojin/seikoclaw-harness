---
name: seikoclaw-operating-map
description: Maintains a project map of parallel agent sessions, ownership lanes, blockers, and archived outcomes. Use when delegating concurrent tasks to multiple executors.
---

# Seikoclaw Operating Map

## Goal
To track parallel executor sessions, manage their lanes, monitor blockers, and cleanly archive outcomes without collisions.

## Workflow
1. **Initialize State**: Check for an existing `operating_map.md` or `.map` state file in the workspace. If absent, create it.
2. **Lane Allocation**: When the Architect delegates a task, assign a unique lane name (e.g., `lane-auth`, `lane-db`).
3. **Status Updates**: Periodically check executor progress. Update the map with active blockers or waiting states.
4. **Archival**: When a lane finishes, move its final output/receipt to an archived section and free the lane.

## Required Inputs
- Task list from the Architect
- Target workspace path

## Output Format
A continuously updated `operating_map.md` at the root or within the `.gemini/` local context, structured with:
- Active Lanes (Assignee, Task, Status)
- Blockers (Blocked by, Resolution plan)
- Archived (Completed lanes, timestamp)

## Boundaries
- Do NOT perform the tasks yourself. You are only the map manager.
- If a blocker involves missing credentials, halt the lane and notify the user.
