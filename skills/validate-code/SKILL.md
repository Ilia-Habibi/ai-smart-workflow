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
   - Copy the default `ruff.toml` and `mypy.ini` from the skill's `resources` directory to the target project root if they do not already possess their own configurations.
2. **Execution Phase:**
   - Run Ruff: `ruff check .` (note the errors).
   - Run MyPy: `mypy .` (note the type errors).
   - Run Bandit: `bandit -r . -c pyproject.toml` or standalone (note high/medium severity issues).
3. **Decision Tree for Remediation:**
   - **Auto-Fixable Issues (Proceed directly):**
     - Unused imports (Ruff: `F401`).
     - Formatting issues (Ruff format).
     - Adding simple missing type hints (e.g., `def func(x: int) -> None:`).
   - **Requires Human Review (Flag in report):**
     - Complex architectural refactoring.
     - Resolving `Any` types that require deep domain knowledge.
     - Security vulnerabilities (Bandit alerts) modifying core logic.
4. **Action Phase:**
   - Run `ruff check . --fix` to auto-resolve basic issues.
   - Manually edit files to add obvious type hints to untyped functions.
5. **Reporting Phase:**
   - Produce a Markdown `validation_report.md` summarizing the issues found, the issues auto-fixed, and the manual interventions required.

## Output
- Modified code files (cleaner, typed, linted).
- `validation_report.md` detailing the before/after state and pending human actions.

## Quality Checklist
- [ ] All three tools (Ruff, MyPy, Bandit) were executed.
- [ ] Auto-fixes were applied safely without breaking existing business logic.
- [ ] Type hints added are accurate and do not misuse `Any` excessively.
- [ ] The validation report clearly delineates fixed vs. outstanding issues.
