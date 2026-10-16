# Development Narrative: AI Smart Workflow

This document provides a concise development narrative for both the **original submission** and the **revision iteration**, detailing the methodology, sequence of work, tools used, key engineering decisions, and evaluation of AI-generated output.

---

## 1. Original Submission Narrative

### 1.1 Approach & Initial Exploration
The core vision was to create a modular, reusable development workflow powered by AI agent skills that could transform Python code into production-ready software without locking into a rigid, monolithic CLI framework.

To establish the architecture:
- I researched AI agent frameworks and skill-based designs.
- I prompted several frontier AI models (including Claude and others) to propose competing workflow models.
- **Why Claude's proposal was selected:**
  1. **Low Complexity:** The operational logic was encapsulated within modular markdown-based `SKILL.md` files rather than complex orchestration middleware.
  2. **High Reusability & Zero Project Lock-in:** The skills were decoupled from any single codebase, meaning they could be copied and reused across any future Python project.
  3. **Human Readability & Auditability:** Skills expressed as Markdown are transparent, version-controllable, and easily editable by developers.

### 1.2 Sequence of Work (Original Submission)
1. **Model Adaptation:** Implemented the selected skill architecture in Google Antigravity.
2. **Skill Suite Implementation:** Created the core skill bundle:
   - `skills/orchestrator/`: Natural language intent routing.
   - `skills/analyze-project/`: Codebase inspection.
   - `skills/validate-code/`: Linting, typing, and security scanning.
   - `skills/generate-tests/`: Pytest suite generation.
   - `skills/generate-docs/`: Google-style docstrings and architecture documentation.
3. **Demo Project Setup (`PlaylistPirate`):**
   - Built a real-world messy prototype (`demo/before/`) combining OpenCV OCR and YouTube Music downloading.
   - Used the workflow to generate an enhanced version (`demo/after/`) with type hints, modular structure, docstrings, and a test suite.
4. **Initial Submission:** Packaged the repository and submitted.

### 1.3 Key Decisions & Alternatives (Original Submission)
- **Decision: Zero Unsupervised Git Automation.**
  - *Alternative Considered:* The AI proposed automated git hooks to auto-stage and commit code changes autonomously.
  - *Rationale for Rejection:* AI code should never commit directly without human oversight and code review. Automated git operations were completely stripped out.
- **Decision: Stripped Setup Scripts.**
  - *Alternative Considered:* Auxiliary Python setup scripts to bootstrap dependencies and configurations.
  - *Rationale for Rejection:* Setup scripts added unnecessary bloat. A standard `requirements.txt` and explicit copy commands (`cp -r skills/ ...`) provided a simpler, cleaner experience.

### 1.4 AI Output Evaluation (Original Submission)
- **Accepted:**
  - The markdown-centric skill directory layout (`SKILL.md`, `resources/`, `examples/`).
  - Google-style docstring format and general test structure patterns.
- **Rejected:**
  - Automated git/GitHub commit and PR automation.
  - Custom Python installation scripts.
- **Overlooked / Flaws not caught initially:**
  - Accepted the AI-generated unit tests in `demo/after/tests/test_main.py` without noticing that external dependencies (`MusicFinder`, `DatabaseHandler`) were unmocked.
  - Accepted coordinate fixtures in `test_ocr_handler.py` without verifying the math behind line-grouping thresholds.
  - Left configuration loading disconnected between `workflow_config.yaml` and the skill prompts.

---

## 2. Revision Iteration Narrative

### 2.1 Reviewer Feedback & Baseline Verification
The reviewer requested improvements focused on:
1. Running and verifying tests, linting, and type checking while resolving inconsistencies.
2. Clarifying configuration loading, overrides, and skill consistency.
3. Reviewing AI-generated code for correctness (specifically missing API fields and test isolation).
4. Aligning documentation claims with actual demonstrated results.

#### Baseline Verification (Before Fixes)
Before making any code modifications, all verification suites were executed and recorded:
- **Pytest:** `3 failed, 28 passed` out of 31 tests.
  - `test_main_creates_dir` & `test_main_skips_processed_image`: Failed with `FileNotFoundError` (leaking into unmocked `ytmusicapi` locale files).
  - `test_extract_clean_tracks_basic`: Failed with `AssertionError: assert 1 == 2`.
- **Ruff:** **152 errors** reported (trailing whitespace, unused imports, bad function variable casing).
- **MyPy:** **3 errors** reported (`[import-untyped]` for `requests`, `yt_dlp`, `pytesseract`).

### 2.2 Sequence of Work (Revision)
1. **Baseline Documentation:** Created `docs/verification_and_workflow_improvements.md` recording all baseline failures and root causes.
2. **Test Isolation Remediation:** Refactored `demo/after/tests/test_main.py` with `@patch` decorators covering all external classes (`DatabaseHandler`, `OCRHandler`, `MusicFinder`, `Downloader`).
3. **API Payload Schema Synchronization:**
   - Completed the mock API return dictionary in `test_main.py` to include `yt_id`, `cover_url`, `duration`, and `type`.
   - Refactored `demo/after/database.py` defensively using `.get()` with safe defaults and explicit `yt_id` validation.
   - Refactored `demo/after/music_api.py` to require non-empty `videoId` matches.
4. **OCR Bounding Box Fix:** Corrected mock coordinate spacing in `test_ocr_handler.py` (`top: [10, 10, 10, 50, 50]`) to exceed the $2.5\times$ height grouping threshold.
5. **Code Style & Type Cleanliness:**
   - Ran `ruff check demo/after --fix --unsafe-fixes` and resolved bare `except` blocks.
   - Modernized `demo/after/pyproject.toml` with `[tool.ruff.lint]` and comprehensive MyPy third-party module overrides.
6. **Workflow & Skill Enhancements:**
   - Updated `skills/generate-tests/SKILL.md` with strict Test Isolation & API Payload Completeness rules and a mandatory zero-failure verification gate.
   - Updated `skills/validate-code/SKILL.md` with an automated fix & re-verification loop.
   - Updated `skills/orchestrator/SKILL.md` with the 3-tier configuration hierarchy and quality gate commands.
7. **Documentation Alignment:**
   - Added `## Configuration Loading & Overrides Protocol` to `docs/customization.md` and `README.md`.
   - Updated architecture sequence diagrams in `docs/how-it-works.md`.
   - Removed unverified claims (e.g. "GitHub Actions CI") from `demo/after/README.md`.
   - Added reproducible verification commands and verified metrics to all README files.

### 2.3 Key Decisions & Alternatives (Revision)
- **Decision: 100% Mock Isolation over Live Integration Tests.**
  - *Alternative Considered:* Setting up live test databases and pre-fetching YouTube Music credentials.
  - *Rationale for Rejection:* Unit tests must be fast, deterministic, and completely decoupled from network volatility or local filesystem side-effects. Full mock isolation ensures reproducible test runs in any environment.
- **Decision: 3-Tier Configuration Precedence Hierarchy.**
  - *Alternative Considered:* Strict file-only configuration or prompt-only configuration.
  - *Rationale for Adoption:* Establishing `Prompt Overrides > Project Config File > Built-in Skill Defaults` provides both team-wide standardized defaults and developer flexibility for targeted tasks.



## 3. Verified Verification Commands & Results

All verification suites have been executed and confirmed with zero errors:

```bash
# 1. Pytest Unit Tests & Coverage
pytest demo/after/tests
# Result: 31 passed in 3.53s (Coverage: 92% Total, 100% on all test suites)

# 2. Ruff Linter
ruff check demo/after
# Result: All checks passed! (0 errors)

# 3. MyPy Static Type Checker
mypy --config-file demo/after/pyproject.toml demo/after
# Result: Success: no issues found in 11 source files (0 errors)
```

---

## 4. Remaining Limitations

* **External Binaries for Live Execution:** While unit tests run with 100% offline isolation, running `demo/after/main.py` for live end-to-end execution requires locally installed binaries for **Tesseract-OCR** and **FFmpeg** on the system `PATH`.
* **YouTube Upstream Anti-Bot Measures:** Live audio downloading relies on `yt-dlp` and YouTube's public web endpoints, which are subject to upstream throttling or layout changes outside this project's control.

