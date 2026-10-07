---
name: "analyze-project"
description: "Comprehensive static analysis of any Python project, evaluating architecture, quality, and dependencies."
triggers:
  - "analyze this project"
  - "review the codebase"
  - "give me an architecture overview"
  - "check code quality metrics"
  - "what is the structure of this python project"
---

# Analyze Project

## Purpose
To provide a comprehensive, structured analysis of a Python codebase, evaluating its architecture, dependencies, code quality metrics, and adherence to best practices.

## When to Use
- When onboarding to a new, unfamiliar Python codebase.
- When requested to review or document the overall state of a project.
- Prior to major refactoring efforts to establish a baseline.

## Prerequisites
- Access to the project's root directory.
- Basic text search tools (like `grep`, `fd`, or standard IDE search).
- No execution privileges are required (this is purely static analysis).

## Instructions
1. **Scan Directory Structure:**
   - Identify the main application modules and packages.
   - Locate configuration files, `tests/`, and `docs/`.
2. **Analyze Dependencies:**
   - Read `requirements.txt`, `Pipfile`, `poetry.lock`, or `pyproject.toml`.
   - List core dependencies (e.g., Flask, Django, FastAPI, SQLAlchemy, Pandas).
   - Identify the core framework type based on these dependencies (e.g., Web API, Data Science script, CLI tool).
3. **Evaluate Code Quality Indicators:**
   - **Type Hints:** Sample random `.py` files to check for the presence of standard Python type hints.
   - **Testing:** Check the `tests/` directory. Look for `pytest`, `unittest`, or missing tests.
   - **Documentation:** Look for README files, `docs/` folders (Sphinx/MkDocs), and inline docstrings.
4. **Assess Code Metrics and Smells:**
   - Skim the largest files to evaluate cyclomatic complexity, coupling, and cohesion.
   - Identify common anti-patterns: God objects, overly long functions, excessive nested loops, or hardcoded secrets.
5. **Compile the Report:**
   - Use the provided template at `resources/analysis_report_template.md`.
   - Fill in the findings objectively. Provide actionable recommendations based on the findings.

## Output
A detailed Markdown report named `analysis_report.md` structured according to the `analysis_report_template.md`.

## Quality Checklist
- [ ] All major architectural components are identified.
- [ ] Framework and Python version requirements are accurately detected.
- [ ] Quality scores (0-10) are justified in the 'Findings' section.
- [ ] Report uses the exact template structure specified.
