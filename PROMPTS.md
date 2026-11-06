```markdown
# LedgerLine Prompt Library

## Build a feature

Implement **[feature]** in LedgerLine. Inspect the existing code first and follow its architecture, naming, and UI conventions. Keep the change focused, handle loading, empty, and error states, and add or update relevant tests. Do not invent APIs, dependencies, or product requirements.

## Review a change

Review this change for correctness, regressions, security, and maintainability. Report only actionable findings, ordered by severity, with file and line references. Consider authorization, validation, data consistency, and financial calculations. Do not rewrite the code.

## Handle financial calculations

Implement **[calculation or transaction flow]** using the project's existing money representation. Avoid binary floating-point for currency; follow established decimal or integer-minor-unit conventions. Validate inputs and rounding, preserve transaction history, and make related persistence changes atomic when appropriate. Add tests for boundaries, rounding, and failures.

## Diagnose a bug

Investigate **[bug and reproduction steps]** by tracing the relevant code. Identify the root cause, make the smallest safe fix, and add a regression test. Preserve unrelated behavior.

## Add tests

Add tests for **[behavior]** using the project's existing framework and conventions. Cover expected behavior, edge cases, invalid input, and relevant failure paths. Keep tests deterministic and avoid unrelated changes.

## Explain a flow

Explain how **[feature or flow]** works, tracing its entry point, data transformations, persistence, and error handling. Reference the actual files and distinguish observed behavior from assumptions. Do not modify code.
```



# LedgerLine - AI Prompt Engineering Log

This file records actual AI interactions, mistakes identified, corrections and verification.

## Development Log

Project initialized on 6 November 2026.

Detailed prompt entries will be recorded as AI-assisted development takes place.
