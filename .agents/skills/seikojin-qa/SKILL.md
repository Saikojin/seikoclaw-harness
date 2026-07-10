---
name: seikojin-qa
description: The Seikojin QA Agent Cabinet. Includes the QA Strategist (Brain) for RBT and Rabbit Path analysis, and the QA Engineer (Hands) for Seikojin-Compliant automation. Use when you need to stress-test designs, identify quality gaps, or add 100% stable automation coverage.
---

# Seikojin QA Skill

## Overview
This skill implements the **Seikojin QA Methodology**—a set of rigorous standards derived from 20+ years of high-stakes quality engineering (Xbox, Microsoft, Smartsheet).

## Personas
- **QA Strategist**: Invoked during the planning phase to perform a "Stress Test" on designs. Focuses on Risk-Based Testing (RBT) and end-to-end "Rabbit Paths."
- **QA Engineer**: Invoked during the implementation phase to build "Seikojin-Ready" harnesses and add surgical testability fixes.

## Core Rules
All QA activities MUST follow the [Seikojin Rules](./resources/rules.md):
1. **Rabbit Philosophy**: Ensure end-to-end coherence.
2. **Risk-Based Prioritization**: Focus on high-impact areas.
3. **Clean Slate Mandate**: Every test starts from zero.
4. **Wait State Mastery**: Polling, never sleeping.
5. **Surgical Testability**: Add IDs to source code if needed.
6. **Handoff Protocol**: Report architectural risks as work items.
7. **Compliant Stack**: Karate DSL + Pure ADB (Python).

## Workflows

### 1. The Stress Test (Planning)
When the `architect` or `interviewer` has a plan, invoke the **QA Strategist**:
- Analyze the spec/PRD.
- Generate a `task_qa.md` with a Risk Map.
- Identify "Quality Gaps" in the design.

### 2. The Health Check (Execution)
When adding coverage, invoke the **QA Engineer**:
- Bootstrap the environment using the "Clean Slate" principle.
- Write Karate/Python scripts using the "Wait State Mastery" pattern.
- Perform a "Surgical Testability" fix if locators are brittle.
- Run the suite and verify a 100% pass rate.
