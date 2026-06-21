---
name: seikoclaw-frontend-taste
description: Enforces a project's design system, checks for consistent spacing/typography, and removes chaotic inline styles during UI tasks.
---

# Seikoclaw Frontend Taste System

## Goal
To replace generic frontend defaults with stronger layout, typography, component discipline, and strict adherence to the project's design system.

## Workflow
1. **Design System Discovery**: Analyze the project's existing CSS/Tokens (e.g., `index.css`, Tailwind config, or theme files).
2. **Code Audit**: Review the UI components modified by the Executor.
3. **Enforcement**: 
   - Remove hardcoded generic colors or ad-hoc inline styles.
   - Apply design system variables (e.g., `var(--color-primary)`).
   - Ensure responsive breakpoints are respected.
4. **Visual Verification Handoff**: Request `seikoclaw-browser-qa-workflow` to generate screenshots of the modified UI.

## Required Inputs
- Target HTML/CSS/JS/JSX files to review.
- Path to the primary design system file.

## Output Format
- Refactored frontend code enforcing design tokens.
- A checklist of aesthetic corrections made.

## Boundaries
- Do not redesign the UX structure. Only enforce the visual design system and CSS discipline.
