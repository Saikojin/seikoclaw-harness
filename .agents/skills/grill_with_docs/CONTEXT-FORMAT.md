# CONTEXT.md Format

`CONTEXT.md` is a glossary for the project's domain terminology. It helps the agent speak the same language as the domain experts and stay concise.

## Principles

1. **Glossary only.** `CONTEXT.md` should be totally devoid of implementation details. Do not treat it as a spec, a scratch pad, or a repository for implementation decisions.
2. **Sharp terminology.** Pick the best word for a concept and use it consistently. List aliases if they help the agent understand what terms to *avoid* using.
3. **Canonical definitions.** Keep definitions short and focused on the *business* meaning, not the technical implementation.

## Template

```md
# Glossary

## {Term}
{Concise definition focusing on domain meaning.}

*   **Aliases to avoid**: {comma-separated list of vague or legacy terms}
```

## Example

```md
# Glossary

## Materialization
The process of creating a physical representation of a virtual lesson in the file system.

*   **Aliases to avoid**: publishing, making real, lesson creation

## Cascade
The propagation of a change from a course down through its sections to the individual lessons.
```

## When to update

Update `CONTEXT.md` inline as terms are clarified during a grilling session. Don't wait until the end.
