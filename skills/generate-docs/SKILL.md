---
name: "generate-docs"
description: "Generates professional documentation for Python projects, including docstrings, READMEs, and architecture diagrams."
triggers:
  - "generate docs"
  - "document project"
  - "add docstrings"
  - "create readme"
  - "write documentation"
---

# Generate Documentation

## Purpose
This skill equips the AI agent with the ability to generate comprehensive, professional documentation for any Python project. This includes writing proper Google-style docstrings, structuring a robust README, creating architectural diagrams, and writing supplementary documentation like CONTRIBUTING and CHANGELOG files.

## When to Use
Activate this skill when a user requests:
- Adding or updating docstrings in Python files.
- Creating or updating a `README.md`.
- Generating architecture diagrams or data flow diagrams.
- Bootstrapping project documentation (e.g., API reference, contribution guidelines).

## Prerequisites
- A Python project with source code.
- Basic understanding of the project's purpose and functionality (can be inferred from `setup.py`, `pyproject.toml`, or source code).

## Instructions

Follow these step-by-step instructions to document the project:

### 1. Docstring Generation
When writing docstrings for Python files, adhere to the **Google-style docstring format**.
- **Coverage**: Add or update docstrings for ALL public functions, classes, and modules.
- **Description**: Write meaningful, context-rich descriptions. Do not simply restate the function's name. Explain *why* and *how*, not just *what*.
- **Sections**: Use `Args:`, `Returns:`, `Raises:`, `Yields:`, and `Examples:` sections appropriately.
- **Types**: If the codebase uses type hints (PEP 484), do not duplicate type information in the docstring's `Args` or `Returns` sections unless explicitly requested. If type hints are absent, include types in the docstring.
- **Examples**: Provide minimal, reproducible examples in the `Examples:` section for complex functions.

### 2. README Generation
Create or update `README.md` to serve as the primary entry point for the project.
- **Structure**: Ensure the README includes: Title, Badges, Description, Features, Installation, Usage, Architecture, Contributing, and License.
- **Auto-detection**: Extract project information (name, description, dependencies) from `setup.py`, `pyproject.toml`, or `requirements.txt` to automatically populate the README.
- **Badges**: Generate appropriate shields.io badges for CI status, code coverage, supported Python versions, and License.
- **Updates vs. Creation**: If a README already exists, update relevant sections instead of overwriting the entire file, unless a complete rewrite is requested.

### 3. Architecture Documentation
For complex projects or when explicitly requested, generate architectural documentation.
- **Mermaid Diagrams**: Use Mermaid.js syntax (` ```mermaid `) within markdown to create visual diagrams.
- **Module Relationships**: Create class diagrams or flowchart diagrams showing how core modules interact.
- **Data Flow**: Create sequence diagrams or flowcharts to illustrate how data moves through the system.
- **Component Diagrams**: Show high-level system architecture, especially for web services or multi-component applications.

### 4. Supplementary Docs
Generate additional documentation files to support a robust open-source or professional project:
- **CONTRIBUTING.md**: Outline steps for setting up the development environment, running tests, linting, and submitting Pull Requests.
- **CHANGELOG.md**: Structure a changelog using Keep a Changelog formatting.
- **API Reference**: If requested, generate markdown files documenting the API structure, or set up a documentation generator configuration (like Sphinx or MkDocs).

## Output
- Python files updated with complete, formatted Google-style docstrings.
- A well-structured `README.md`.
- Architecture diagrams embedded in markdown files using Mermaid syntax.
- Supplementary files (`CONTRIBUTING.md`, `CHANGELOG.md`).

## Quality Checklist
- [ ] All public modules, classes, and methods have Google-style docstrings.
- [ ] Docstring descriptions add value beyond the function name.
- [ ] README includes all essential sections (Installation, Usage, Features, License).
- [ ] Badges in the README are correctly formatted and relevant.
- [ ] Mermaid diagrams render correctly without syntax errors.
- [ ] Supplementary docs match the project's actual workflow and structure.
