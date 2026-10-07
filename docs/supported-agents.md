# Supported AI Agents

## Overview

The AI Smart Workflow is designed to work with modern AI coding agents that support **skill-based instruction loading**. Skills are written as markdown files that any capable AI agent can read and follow.

---

## Fully Supported Agents

### Google Antigravity

| Feature | Support |
|---------|---------|
| Skill Loading (SKILL.md) | ✅ Native |
| Sub-agent Dispatch | ✅ Native |
| File Read/Write | ✅ Native |
| Command Execution | ✅ Native |
| Progressive Context | ✅ Native |

**Setup:**
1. Clone this repo
2. Install skills globally: Copy `skills/` to `~/.gemini/skills/`
3. Or install per-project: Copy `skills/` to your project root

**Usage:**
Open your project in Antigravity and use natural language:
> "Run the full workflow on this project"
> "Generate tests for the database module"

---

### Claude Code

| Feature | Support |
|---------|---------|
| CLAUDE.md Instructions | ✅ Compatible |
| Sub-agent Dispatch | ✅ Native |
| File Read/Write | ✅ Native |
| Command Execution | ✅ Native |
| Tool Use | ✅ Native |

**Setup:**
1. Clone this repo
2. Copy skills to your project
3. Reference skills in your `CLAUDE.md`:
```markdown
## Development Workflow
When asked to improve code quality, follow the instructions in:
- `skills/orchestrator/SKILL.md` for workflow coordination
- `skills/generate-tests/SKILL.md` for test generation
- `skills/validate-code/SKILL.md` for code validation
- `skills/generate-docs/SKILL.md` for documentation
```

---

## Partially Supported Agents

### Cursor AI
- Can read and follow SKILL.md instructions via `.cursorrules`
- No native sub-agent dispatch (orchestrator runs sequentially)
- Reference skills in `.cursorrules` file

### GitHub Copilot (Agent Mode)
- Can follow SKILL.md instructions via `.github/copilot-instructions.md`
- Limited sub-agent support
- Best for individual skills rather than full orchestration

### Windsurf / Codeium
- Can read SKILL.md as context files
- Follow instructions from `.windsurfrules`

---

## Agent-Agnostic Design

The skills in this workflow are written as **plain markdown** with clear, unambiguous instructions. This means:

1. **Any AI agent** that can read files and follow instructions can use them
2. **No vendor lock-in** — switch between agents freely
3. **Human-readable** — developers can read skills to understand the workflow
4. **Version-controlled** — skills evolve with your project via Git

The key requirement is that the AI agent must be able to:
- Read markdown files from the filesystem
- Execute shell commands (for running tests, linters, etc.)
- Create and modify files (for generating tests, docs, etc.)
- Follow multi-step instructions autonomously
