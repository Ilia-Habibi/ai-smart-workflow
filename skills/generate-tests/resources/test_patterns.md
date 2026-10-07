# Test Patterns Reference Guide

This guide provides standard patterns for generating robust Python tests using `pytest` and `unittest.mock`.

## 1. Database Mocking & Testing

Avoid hitting real databases. Use mocks for simple CRUD or in-memory databases (like SQLite) for complex queries.

### SQLAlchemy Mocking Pattern
```python
from unittest.mock import MagicMock

def test_get_user():
    mock_session = MagicMock()
    mock_user = MagicMock(id=1, name="Alice")
    mock_session.query.return_value.filter.return_value.first.return_value = mock_user
    
    # Pass mock_session to your function
    # user = fetch_user(mock_session, user_id=1)
    # assert user.name == "Alice"
```

## 2. API Mocking

Never make real HTTP requests in tests.

### Requests Library
```python
from unittest.mock import patch, MagicMock

@patch('requests.post')
def test_api_call(mock_post):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"status": "success"}
    mock_resp.status_code = 200
    mock_post.return_value = mock_resp

    # result = submit_data()
    # assert result['status'] == 'success'
```

## 3. File System Mocking

Mock `open` or use the `tmp_path` fixture.

### Using `mock_open`
```python
from unittest.mock import patch, mock_open

@patch('builtins.open', new_callable=mock_open, read_data="line1\nline2")
def test_read_file(mock_file):
    # result = read_my_file('path.txt')
    # assert result == ["line1", "line2"]
```

### Using `tmp_path` fixture (pytest built-in)
```python
def test_write_file(tmp_path):
    test_file = tmp_path / "test.txt"
    # write_to_file(test_file, "hello")
    # assert test_file.read_text() == "hello"
```

## 4. Subprocess Mocking

Mock external CLI tools and scripts.

```python
from unittest.mock import patch, MagicMock
import subprocess

@patch('subprocess.run')
def test_cli_command(mock_run):
    mock_run.return_value = subprocess.CompletedProcess(
        args=['ls'], returncode=0, stdout=b"file1.txt\n", stderr=b""
    )
    # result = list_files()
    # assert "file1.txt" in result
```

## 5. Async Testing

Use `pytest-asyncio` for async functions.

```python
import pytest

@pytest.mark.asyncio
async def test_async_fetch():
    # result = await async_fetch_data()
    # assert result is not None
```

## 6. Fixture Scoping

Control fixture lifecycle to optimize test speed.

```python
import pytest

# session: initialized once per test run
@pytest.fixture(scope="session")
def db_connection():
    # setup
    conn = connect_db()
    yield conn
    # teardown
    conn.close()

# module, class, function (default) scopes are also available.
```

## 7. Mocking Time

Ensure time-dependent functions are deterministic. Use `freezegun`.

```python
from freezegun import freeze_time
import datetime

@freeze_time("2025-01-01 12:00:00")
def test_timestamp_generation():
    assert datetime.datetime.now().strftime("%Y-%m-%d") == "2025-01-01"
```
