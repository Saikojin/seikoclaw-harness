# Seikojin Rules: The QA Constitution

These rules are absolute and must be followed by any agent performing QA tasks within the Seikojin ecosystem.

## 1. The Rabbit Philosophy (E2E Coherence)
- **Rule**: Every feature must have a "Rabbit Path"—a primary end-to-end user journey that is verified daily.
- **Goal**: Ensure that fragmented services always come together into a coherent user experience.
- **Action**: If a change breaks the end-to-end flow, it is a P0 failure, regardless of unit test passes.

## 2. Risk-Based Prioritization (RBT)
- **Rule**: Testing effort must be proportional to `Risk = Likelihood x Impact`.
- **Goal**: Maximize defect detection in critical paths (Auth, Payments, Core Data) while maintaining velocity.
- **Action**: The Strategist must explicitly define "High Risk" areas in every `task_qa.md`.

## 3. The Clean Slate Mandate
- **Rule**: Every test execution must start from a deterministic "Clean Slate."
- **Goal**: Eliminate state-leakage flakiness.
- **Action**: Use the `State Controller` (e.g., `adb shell pm clear` or DB wipe) before every suite run.

## 4. Anti-Flakiness: Wait State Mastery
- **Rule**: Never use static `sleep()` or `delay()`. Use deterministic polling.
- **Goal**: Achieve a 100% pass rate across varying network and CPU conditions.
- **Action**: The Engineer must use "Wait-for-State" patterns (logcat polling, selector visibility) for all UI interactions.

## 5. Surgical Testability
- **Rule**: Prefer adding unique `test-id` or `android:id` over complex CSS/XPath selectors.
- **Goal**: Create stable, maintainable locator strategies.
- **Action**: The Engineer has "Surgical" authority to modify source code only to add these identifiers.

## 6. The Handoff Protocol
- **Rule**: If a quality gap requires architectural changes or product fixes, the Agent must generate a "Quality Handoff" document for the Developer/Architect.
- **Goal**: Clear communication between QA and Dev.
- **Action**: Never ignore a fundamental risk; document it and hand it off.

## 7. Seikojin-Compliant Stack
- **Rule**: Default to **Karate DSL** for API/Web and **Pure ADB (Python)** for Mobile.
- **Goal**: Standardized, high-performance, and human-readable automation.
