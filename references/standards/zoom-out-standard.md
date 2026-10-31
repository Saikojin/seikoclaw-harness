# Zoom Out Standard

This standard defines the quality bar for evaluating high-level designs, architectures, and technical specifications from a high-altitude perspective.

## Core Principle

A design passes if it solves the root problem in the simplest possible way, leverages existing infrastructure and codebase conventions, avoids premature optimization or speculative features (YAGNI), and maintains appropriate abstraction boundaries without getting bogged down in low-level code implementation details.

## 0. Context Sufficiency (Prerequisite Check)

* **Understanding the Objective**: The document must contain enough information to define the overall objective. If the reviewer cannot determine *what* we are trying to achieve and *why*, the review must fail immediately with a request for context.

## 1. Root Problem Focus

* **Symptom vs. Root Cause**: The design must solve the underlying problem, not just apply a local band-aid to symptoms.
* **Project Alignment**: The design must align with high-level architectural principles (Principle 1: Laziness Protocol, Principle 3: Redesign from First Principles, Principle 11: Model the Domain).

## 2. Simplicity & Extensibility

* **YAGNI (You Aren't Gonna Need It)**: Reject abstractions, code paths, or features built solely for speculative future requirements.
* **Premature Optimization**: Avoid introducing complexity (caching, sharding, async queues) before performance bottlenecks are proven.
* **Minimalist Data Flow**: Ensure data passes through the minimal number of components.
* **No Architectural Dead-Ends**: Use clean interfaces and boundaries to allow future expansion without blocking it, without implementing speculative features now.

## 3. Anti-Weeds (Altitude Control)

* **Altitude Discipline**: High-level sections must focus on architecture, interfaces, and data flows, not code-level implementation details (e.g., helper functions or loop variables).
* **Workarounds vs. Structural Fixes**: Avoid complex local workarounds; propose changes to the root component if that is cleaner.
* **Right Placement (Architectural Fit)**: Ensure new logic is placed in the correct layer/component according to separation of concerns.

## 4. Leverage Existing

* **Codebase Reuse**: Search the codebase and reuse existing utilities, classes, or modules instead of reinventing them. Ensure candidates for reuse are stable and do not violate dependency boundaries.
* **Pattern Consistency**: Follow established design patterns in the codebase.
* **Platform Standards**: Use established ecosystem frameworks and standard libraries instead of bespoke or ad-hoc custom solutions.
* **Identify Anti-Patterns**: Actively flag known anti-patterns (e.g., bypassing standard authentication, hardcoding deployment configurations, redundant wrapper layers).
