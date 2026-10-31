# Implementation Readiness Standard

This standard defines the quality bar for implementation plans, task lists, and work decomposition prior to code execution.

## Core Principle

A plan passes if a competent engineer (or fresh AI session) who is unfamiliar with the codebase can execute the plan and produce the correct changes on the first attempt, without guessing, asking clarifying questions, or making independent design choices.

## 1. The Zero-Decision Rule

* The implementation plan must leave **zero architectural or design choices to the implementer**.
* If an implementer must choose a database schema, design an API endpoint path, select a new external dependency, or invent error recovery behavior on the fly, the plan **fails** this standard. All such decisions must be finalized in the specification.

## 2. Concrete Scope & Target Files

* **Explicit File Paths**: List exact absolute or repo-relative paths for all files to be created, modified, or deleted.
* **Component Boundaries**: Name the specific classes, functions, or modules being updated, with proposed signature contracts.

## 3. Phasing & Verifiable Units

* **Sequence Work into Verifiable Units (Principle 19)**: Partition the work into small, atomic tasks where each step ends in an independently verifiable check (test execution, visual check, CLI run).
* **Test Plan**: Detail exact behavioral unit/integration tests and automated test commands (`pytest ...`, `cargo test ...`, or headed non-headless E2E contracts).
