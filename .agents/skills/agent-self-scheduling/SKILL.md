---
name: agent-self-scheduling
description: Schedule AI agent tasks on intervals, crons, or background heartbeats using cross-platform Bash and PowerShell wrappers. Trigger when set up recurring agent runs, loops, or heartbeats.
disable-model-invocation: false
---

# Agent Self-Scheduling & Recurring Heartbeats

## Goal
To provide reliable, cross-platform external scheduling patterns for running AI agent commands on recurring intervals or cron schedules.

## Universal Floor
- Cron / Scheduled Tasks minimum resolution is **1 minute**.
- For sub-minute intervals, use a controlled loop with `sleep` rather than high-frequency timers.

## Execution Wrappers

### 1. Linux / macOS / WSL (Cron or Loop)
```bash
# Cron (every 10 mins)
*/10 * * * * cd /path/to/project && agy run "check status" >> ~/agent.log 2>&1

# Sub-minute loop
while true; do agy run "check queue"; sleep 30; done
```

### 2. Windows (PowerShell Scheduled Task or Loop)
```powershell
# Windows Scheduled Task (Every 15 mins)
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -Command `"`$env:PATH += ';C:\Users\saiko\.gemini\antigravity\bin'; agy run 'check status'`""
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 15)
Register-ScheduledTask -TaskName "AGY_Scheduled_Check" -Action $action -Trigger $trigger

# Sub-minute loop
while ($true) { agy run "check queue"; Start-Sleep -Seconds 30 }
```
