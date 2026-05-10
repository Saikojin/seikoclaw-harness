---
description: "Workflow to synchronize local DevWorkspace context state with the SpacetimeDB Openbrain database."
---

# Sync to Openbrain Workflow

## Overview
This workflow connects the DevWorkspace local agent to the user's SpacetimeDB Openbrain backend to synchronize knowledge.

## Prerequisites
- The SpacetimeDB CLI (`spacetime`) must be installed.
- The `openbrain` module must be accessible on SpacetimeDB.

## Steps

1. **Format the Payload**
   Format the session state or memory item as JSON containing:
   - `content`: the summarization text
   - `tier`: Core, Longterm, Midterm, or Shortterm
   - `metadata`: origin, project name, etc.

2. **Execute Spacetime Call**
   Use the `run_command` tool to invoke SpacetimeDB:
   `spacetime call openbrain insert_memory '{"content": "...", "tier": "Shortterm"}'`

3. **Verify Insertion**
   Run an inspection command:
   `spacetime sql openbrain "SELECT * FROM memories ORDER BY created_at DESC LIMIT 1"`
   Compare the output to ensure the row was saved.
