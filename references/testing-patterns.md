# Core Engineering Reference: Testing Patterns & Methodologies

> **Core Axiom**: "If you liked it, then you should have put a test on it" (The Beyoncé Rule). Tests are executable proof of behavior, not ceremonial checkboxes.

---

## 🏗️ 1. The Test Pyramid (80 / 15 / 5)

Maintain a healthy ratio of test scopes to ensure lightning-fast CI feedback, high stability, and robust integration:

| Tier | Share | Target Scope | Execution Speed | Primary Role |
| :--- | :--- | :--- | :--- | :--- |
| **Unit Tests** | $\sim 80\%$ | Pure logic, domain entities, utility functions, edge-case permutations | Sub-millisecond to seconds | Exhaustive algorithmic verification, instant developer feedback |
| **Integration Tests** | $\sim 15\%$ | Database queries, subsystem seams, API endpoints, serialization | Seconds | Seam correctness, contract adherence, network/disk boundary checks |
| **End-to-End / Journey Tests** | $\sim 5\%$ | Critical user flows (Rabbit Path), browser journeys, visual rendering | Tens of seconds | Production sanity, cross-system synthesis, zero regressions on top user paths |

---

## 📐 2. Essential Testing Principles

### A. DAMP Over DRY in Test Suites
- **Descriptive And Meaningful Phrases (DAMP)**: Tests should be readable top-to-bottom as self-contained specifications.
- **Avoid Over-Abstraction**: Do not build complex test helper hierarchies that hide test data setup. Favor explicit, local test fixtures over convoluted shared state.

### B. Seam-Based Testing & Mocking Discipline
- **Mock at the Boundary, Not Internal Implementation**: Mock external I/O (Stripe API, SendGrid, S3), never private internal classes. Mocking internal implementation details couples tests to refactoring churn.
- **Deterministic Fakes**: Prefer in-memory fake repositories or deterministic local test databases (e.g. SQLite `:memory:`) over heavy mocking frameworks when validating persistence logic.

### C. Red-Green-Refactor Discipline
1. **Red**: Write a focused test that fails for the specific reason intended (proving test sensitivity).
2. **Green**: Write the minimal production code necessary to turn the test green.
3. **Refactor**: Clean up implementation without altering behavior, ensuring tests stay green throughout.

---

## 🏷️ 3. Test Structure & Naming Conventions

Adopt the standard **Given-When-Then** or **Arrange-Act-Assert (AAA)** structure:

```python
def test_task_graph_blocks_unclaimed_child_when_parent_fails():
    # Arrange (Given)
    graph = TaskGraph()
    parent_id = graph.add_task(title="Parent Migration")
    child_id = graph.add_task(title="Child Consumer", depends_on=[parent_id])

    # Act (When)
    graph.fail_task(parent_id, reason="Database timeout")

    # Assert (Then)
    assert child_id not in graph.get_ready_frontier()
    assert graph.get_task(child_id).status == "blocked"
```

### Naming Formula:
`test_<component>_<scenario>_<expected_behavior>()`
- Good: `test_auth_expired_jwt_returns_401_unauthorized()`
- Bad: `test_token()` or `test_auth_error()`

---

## 🚨 4. Anti-Patterns to Eliminate
- ❌ **Flaky Sleep Timers**: Using arbitrary `time.sleep(2)` to wait for async events. Use polling with exponential backoff and timeout assertion (`wait_until(...)`).
- ❌ **Test Interdependence**: Tests relying on side-effects or database rows created by previous tests. Every test must be completely isolated and idempotent.
- ❌ **Assertionless Tests**: Tests that execute code but fail to assert on state or output.
- ❌ **Silenced Exceptions**: Blank `try: ... except: pass` in tests masking assertions.
