---
name: "generate-tests"
description: "Generate comprehensive pytest test suites for any Python project, with support for user-provided test cases, mocking, and coverage reporting."
triggers:
  - "generate tests"
  - "write tests"
  - "add test coverage"
  - "test this module"
  - "test this project"
  - "write unit tests"
  - "run tests"
---

# 🧪 Generate Tests Skill

## Purpose

Generate a comprehensive, well-structured pytest test suite for any Python project or module. This skill handles everything from scanning testable code to writing tests, mocking dependencies, running the suite, and reporting coverage.

---

## When to Use

- A project has no tests or insufficient test coverage
- A user asks to "test this" (project, module, function, or feature)
- A user provides specific test cases to implement
- After writing new code that needs verification
- As part of the full workflow (called by the orchestrator)

---

## Prerequisites

- Python 3.10+ installed
- The project must be runnable (dependencies installed or installable)
- Access to the project's source code

---

## Instructions

### Phase 1: Setup Test Infrastructure

#### 1.1 Install Testing Dependencies
```bash
pip install pytest pytest-cov pytest-mock
```

If not already present, add them to `requirements-dev.txt` or `pyproject.toml` under `[project.optional-dependencies.dev]`.

#### 1.2 Create Test Directory Structure
```
project_root/
├── tests/
│   ├── __init__.py          # Make tests a package
│   ├── conftest.py          # Shared fixtures
│   ├── test_module1.py      # Tests for module1.py
│   ├── test_module2.py      # Tests for module2.py
│   └── integration/         # Integration tests (if needed)
│       ├── __init__.py
│       └── test_pipeline.py
```

#### 1.3 Create conftest.py
The `conftest.py` should contain:
- Shared fixtures used across multiple test files
- Setup/teardown for databases, temp files, mock servers
- Custom pytest markers registration

```python
"""Shared test fixtures and configuration."""
import pytest


# Register custom markers
def pytest_configure(config):
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "integration: marks integration tests")
    config.addinivalue_line("markers", "user_specified: marks user-provided test cases")


# Example shared fixture
@pytest.fixture
def sample_data():
    """Provide sample test data."""
    return {"key": "value"}


# Example temp directory fixture
@pytest.fixture
def temp_dir(tmp_path):
    """Provide a temporary directory for test outputs."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir
```

---

### Phase 2: Scan and Analyze Testable Code

#### 2.1 Identify Testable Units
Scan each Python file in the project for:
- **Functions**: All `def` statements (focus on public functions, skip `_private` unless complex)
- **Classes**: All `class` statements and their methods
- **Module-level logic**: Main blocks, initialization code
- **Entry points**: `if __name__ == "__main__"` blocks

#### 2.2 Classify Each Unit
For each testable unit, determine:

| Classification | Description | Test Strategy |
|---------------|-------------|---------------|
| **Pure function** | No side effects, returns a value | Direct input/output testing |
| **Stateful method** | Modifies object state | Test state transitions |
| **I/O function** | Reads/writes files, network, DB | Mock I/O, test logic |
| **Integration point** | Connects multiple modules | Integration test with selective mocking |
| **CLI/subprocess** | Calls external commands | Mock subprocess, test argument construction |

#### 2.3 Identify Dependencies to Mock
For each testable unit, identify external dependencies:
- **Database calls** → Mock with `sqlite3` in-memory or `MagicMock`
- **HTTP requests** → Mock with `unittest.mock.patch` on `requests.get/post`
- **File system** → Use `tmp_path` fixture or mock `open`
- **Subprocess calls** → Mock `subprocess.run` / `subprocess.Popen`
- **Third-party APIs** → Mock the API client class
- **Time-dependent** → Mock `time.time`, `datetime.now`
- **Environment variables** → Use `monkeypatch.setenv`

---

### Phase 3: Handle User-Provided Test Cases

#### 3.1 Detect Test Cases in User Prompt
Look for these patterns in the user's prompt:

**Explicit test cases:**
- "Test that X returns Y when given Z"
- "Make sure X handles the case where Y"
- "Verify that X raises an error when Z"
- "Test case: input A → expected output B"
- Code blocks containing assertions

**Behavioral requirements:**
- "It should reject duplicates"
- "Downloads should fail gracefully when..."
- "The function must handle empty input"

**Edge cases:**
- "What happens when the input is None?"
- "Test with very large files"
- "Handle the case where the API is down"

#### 3.2 Convert to Pytest Functions

**User says**: "Make sure add_raw_track rejects duplicates"
**You write**:
```python
@pytest.mark.user_specified
def test_add_raw_track_rejects_duplicate_entries(db_handler):
    """User requirement: add_raw_track should reject duplicate raw_text entries."""
    db_handler.add_raw_track("Song A - Artist A")
    # Adding the same track again should not raise but should not create duplicate
    db_handler.add_raw_track("Song A - Artist A")
    # Verify only one entry exists
    tracks = db_handler.get_pending_tracks()
    matching = [t for t in tracks if t[1] == "Song A - Artist A"]
    assert len(matching) == 1
```

#### 3.3 Organization
- Place user-specified tests at the TOP of each test file
- Mark them with `@pytest.mark.user_specified`
- Add a comment: `# User-specified test case`
- Generate additional auto-generated tests BELOW them

---

### Phase 4: Generate Tests

#### 4.1 Test Categories

For EACH testable unit, generate tests in these categories:

##### Happy Path Tests
Test the expected, normal behavior:
```python
def test_function_returns_expected_result():
    """Verify function works correctly with valid input."""
    result = function_under_test(valid_input)
    assert result == expected_output
```

##### Edge Case Tests
Test boundary conditions:
```python
@pytest.mark.parametrize("input_val,expected", [
    ("", None),           # Empty string
    (None, None),         # None input
    ("a", "a"),           # Single character
    ("a" * 10000, ...),   # Very long string
])
def test_function_edge_cases(input_val, expected):
    """Verify function handles edge cases gracefully."""
    result = function_under_test(input_val)
    assert result == expected
```

##### Error/Exception Tests
Test that errors are handled properly:
```python
def test_function_raises_on_invalid_input():
    """Verify function raises appropriate error for invalid input."""
    with pytest.raises(ValueError, match="expected error message"):
        function_under_test(invalid_input)
```

##### Integration Tests
Test module interactions:
```python
@pytest.mark.integration
def test_pipeline_end_to_end(mock_api, mock_db, tmp_path):
    """Verify the complete pipeline from input to output."""
    # Setup
    mock_api.search.return_value = sample_result
    # Execute
    result = pipeline.run(input_data)
    # Verify
    assert result.status == "completed"
    mock_db.save.assert_called_once()
```

#### 4.2 Mocking Patterns

##### Mock External APIs
```python
from unittest.mock import patch, MagicMock

@patch("module.requests.get")
def test_api_call(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "value"}
    mock_get.return_value = mock_response
    
    result = function_that_calls_api()
    assert result == expected
    mock_get.assert_called_once_with("expected_url")
```

##### Mock Database
```python
import sqlite3
import pytest

@pytest.fixture
def in_memory_db():
    """Create an in-memory SQLite database for testing."""
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE tracks (id INTEGER PRIMARY KEY, raw_text TEXT UNIQUE)")
    conn.commit()
    yield conn
    conn.close()
```

##### Mock Subprocess
```python
@patch("module.subprocess.run")
def test_command_execution(mock_run):
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout="success output",
        stderr=""
    )
    
    result = function_that_runs_command()
    assert result == expected
    mock_run.assert_called_once_with(
        expected_command, capture_output=True, text=True
    )
```

##### Mock File System
```python
def test_file_processing(tmp_path):
    """Test file operations using pytest's tmp_path fixture."""
    # Create test file
    test_file = tmp_path / "test_input.txt"
    test_file.write_text("test content")
    
    result = process_file(str(test_file))
    assert result == expected
```

##### Mock Third-Party Libraries
```python
@patch("module.YTMusic")
def test_music_search(mock_ytmusic_class):
    mock_instance = MagicMock()
    mock_ytmusic_class.return_value = mock_instance
    mock_instance.search.return_value = [
        {"resultType": "song", "title": "Test Song", "artists": [{"name": "Artist"}],
         "videoId": "abc123", "album": {"name": "Album"}, "thumbnails": [{"url": "http://img.jpg"}]}
    ]
    
    finder = MusicFinder()
    result = finder.find_best_match("test query")
    assert result["title"] == "Test Song"
```

##### Strict Test Isolation & API Payload Rules (CRITICAL)
1. **Total Isolation for Unit Tests:**
   - Any test targeting a function or orchestration entry point (e.g. `main()`) MUST mock all external services instantiated within that scope (`DatabaseHandler`, `MusicFinder`, `Downloader`, `OCRHandler`, etc.).
   - Unit tests must NEVER leak into live network requests, host file system modifications, external binaries (`tesseract`, `ffmpeg`), or unmocked package internal files (`locales`, `gettext`).
2. **API Payload Completeness:**
   - When mocking return values across module boundaries (e.g., API search results or database records), verify the downstream consumer contracts.
   - Do NOT return partial objects (e.g. only `{title, artist}`). Always supply all fields expected by consumers (such as `yt_id`, `cover_url`, `duration`, `status`, etc.) to prevent latent `KeyError` or schema bugs.

#### 4.3 Naming Convention
Use descriptive test names that explain WHAT is being tested:
```python
# ✅ Good
def test_add_raw_track_rejects_duplicate_entries():
def test_download_audio_returns_false_for_missing_ffmpeg():
def test_preprocess_image_inverts_dark_mode_screenshots():

# ❌ Bad
def test_add():
def test_download():
def test_1():
```

---

### Phase 5: Execute Tests

#### 5.1 Run Test Suite
```bash
# Run all tests with verbose output
pytest tests/ -v --tb=short

# Run with coverage report
pytest tests/ -v --cov=. --cov-report=term-missing --cov-report=html

# Run only user-specified tests
pytest tests/ -v -m user_specified

# Run tests for a specific module
pytest tests/test_database.py -v
```

#### 5.2 Handle Failures
When tests fail:
1. **Read the error message carefully** — understand what went wrong
2. **Check if it's a test issue** (wrong assertion, missing mock) → fix the test
3. **Check if it's a code issue** (actual bug found) → report to user, optionally fix
4. **Check if it's an environment issue** (missing dependency) → install and retry

#### 5.3 Iterate & Verify Gate (MANDATORY)
- Fix failing tests one at a time.
- Re-run after each fix to verify.
- **Verification Gate:** The agent MUST re-run `pytest tests/` and achieve a **Zero Exit Code (0 failures)** before concluding this phase. Never declare test generation complete if any test is failing.
- Maximum 3 iterations per failing test before escalating to human review if an underlying architectural issue is identified.

---

### Phase 6: Coverage Analysis

#### 6.1 Generate Coverage Report
```bash
pytest tests/ --cov=. --cov-report=term-missing
```

#### 6.2 Interpret Results
- **Lines covered**: Actual code lines executed during tests
- **Lines missing**: Code paths not tested — consider adding tests
- **Branch coverage**: Whether all if/else paths are tested

#### 6.3 Coverage Targets
| Project Type | Minimum Target | Ideal |
|-------------|---------------|-------|
| New project | 70% | 85%+ |
| Existing project (first tests) | 50% | 70%+ |
| Critical module | 80% | 95%+ |
| Utility/helper | 60% | 80%+ |

If coverage is below target:
1. Identify the largest uncovered modules
2. Generate additional tests for those modules
3. Focus on branches and error paths

---

## Output

This skill produces:
1. **`tests/` directory** — Complete test suite
2. **`tests/conftest.py`** — Shared fixtures
3. **`tests/test_*.py`** — Test files for each module
4. **Coverage report** — Terminal output + HTML report
5. **Test summary** — Number of tests, pass/fail, coverage percentage

## Quality Checklist

Before marking tests as complete, verify:
- [ ] All tests pass (`pytest tests/ -v` shows all green)
- [ ] Coverage meets minimum threshold
- [ ] User-provided test cases are all implemented and passing
- [ ] External dependencies are properly mocked (tests run without network/DB)
- [ ] Test names are descriptive and follow naming convention
- [ ] No test relies on execution order (each test is independent)
- [ ] Fixtures clean up after themselves (no leftover files/connections)
- [ ] Edge cases are covered (empty input, None, boundary values)
