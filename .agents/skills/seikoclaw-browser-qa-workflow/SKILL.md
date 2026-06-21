---
name: seikoclaw-browser-qa-workflow
description: Invokes visual and E2E testing framework (framework agnostic) to capture screenshots, check console errors, and verify layout.
---

# Seikoclaw Browser QA Workflow

## Goal
To verify frontend changes through actual browser automation, ensuring responsive design, catching console errors, and verifying UI state, independent of unit tests.

## Workflow
1. **Determine Tooling**: Check the workspace for existing E2E frameworks (Playwright, Selenium, Puppeteer, Karate, etc.).
2. **Script Generation**: If a script for the target page does not exist, generate a temporary script to open the page, navigate if needed, and capture evidence.
3. **Execution**: Run the browser automation script.
4. **Evidence Collection**: Gather screenshots, console logs, and network failures.
5. **Reporting**: Produce a visual/E2E QA report artifact.

## Required Inputs
- Local server URL or live URL.
- Routes to test.

## Output Format
A QA report artifact detailing:
- Console errors (if any).
- Visual anomalies (if any).
- Pointers to captured screenshots.

## Boundaries
- Keep this workflow framework-agnostic. Use what is available in the repository.
- Do not replace backend or unit testing workflows. This is strictly for browser/E2E verification.
