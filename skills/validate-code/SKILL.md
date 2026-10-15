---
name: "validate-code"
description: "Validates Python code quality using Ruff, MyPy, and Bandit, and provides remediation."
triggers:
  - "lint this code"
  - "validate code quality"
  - "run mypy and ruff"
  - "check for security vulnerabilities"
  - "fix lint errors"
---

# Validate Code Quality

## Purpose
To systematically enforce code quality, type safety, and basic security best practices on a Python project using industry-standard tools (Ruff, MyPy, Bandit), and dynamically auto-fix issues where appropriate.

## When to Use
- When preparing a pull request.
- When the user asks to clean up, lint, or secure a Python file or project.
- Periodically during development to ensure technical debt does not accumulate.

## Prerequisites
- Python installed on the host system.
- Appropriate configurations for the tools (`ruff.toml`, `mypy.ini` in the `resources` directory).
- Permission to install packages (`pip install ruff mypy bandit`) if not already present.

## Instructions
1. **Tool Setup & Configuration:**
   - Verify if `ruff`, `mypy`, and `bandit` are installed. If not, install them in the current environment.
   - Respect project-specific configurations in `pyproject.toml` or `ruff.toml`/`mypy.ini`.
   - If third-party libraries lack typing stubs (reporting `[import-untyped]`), ensure module overrides (`ignore_missing_imports = true`) are configured in `pyproject.toml` or `mypy.ini`.
   - Copy the default `ruff.toml` and `mypy.ini` from the skill's `resources` directory to the target project root only if the project lacks its own configuration.
2. **Execution Phase:**
   - Run Ruff: `ruff check .` (note the errors).
   - Run MyPy: `mypy .` (or with `--config-file` if applicable; note type errors).
   - Run Bandit: `bandit -r . -c pyproject.toml` or standalone (note high/medium severity issues).
3. **Decision Tree for Remediation:**
   - **Auto-Fixable Issues (Proceed directly):**
     - Unused imports (Ruff: `F401`).
     - Formatting & whitespace issues (Ruff: `W291`, `W293`).
     - Import sorting (Ruff: `I001`).
     - Simple comparisons (Ruff: `E712`).
     - Adding missing type hints on public interfaces.
   - **Requires Human Review (Flag in report):**
     - Complex architectural refactoring.
     - Resolving `Any` types that require deep domain knowledge.
     - Security vulnerabilities (Bandit alerts) modifying core business logic.
4. **Action & Verification Loop (MANDATORY):**
   - Step 4.1: Run `ruff check . --fix` (and `--unsafe-fixes` if appropriate).
   - Step 4.2: Manually edit files to resolve bare `except` blocks, typing casts, or remaining linter errors.
   - Step 4.3: **Loop Verification**: Re-run `ruff check .` and `mypy .` to verify that both tools exit with code 0. Do NOT conclude the phase until clean zero-error outputs are achieved.
5. **Reporting Phase:**
   - Produce a Markdown `validation_report.md` summarizing the issues found, the issues auto-fixed, and the verified final results.

## Output
- Modified code files (cleaner, typed, linted).
- `validation_report.md` detailing the before/after state and pending human actions.

## Quality Checklist
- [ ] All three tools (Ruff, MyPy, Bandit) were executed.
- [ ] Ruff check exits with 0 (`All checks passed!`).
- [ ] MyPy check exits with 0 (`Success: no issues found`).
- [ ] Auto-fixes were applied safely without breaking existing business logic.
- [ ] Third-party libraries without stubs are appropriately handled via configuration overrides.
- [ ] Auto-fixes were applied safely without breaking existing business logic.
- [ ] Type hints added are accurate and do not misuse `Any` excessively.
- [ ] The validation report clearly delineates fixed vs. outstanding issues.
