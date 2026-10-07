# Google-Style Docstrings Guide

This is a concise reference guide for writing Google-style docstrings in Python.

## Module Docstrings
Should be at the very top of the file, explaining the module's purpose and contents.

```python
"""A one-line summary of the module.

A more detailed description of the module, explaining its purpose,
primary classes/functions, and any relevant context.
"""
```

## Class Docstrings
Explain what the class does and list its attributes.

```python
class ExampleClass:
    """A brief description of the class.

    Longer explanation of the class functionality and usage.

    Attributes:
        attribute_one (int): Description of attribute one.
        attribute_two (str): Description of attribute two.
    """
```

## Function/Method Docstrings
Explain what the function does, its arguments, return values, and exceptions.

```python
def fetch_data(url: str, timeout: int = 10) -> dict:
    """Fetches data from the given URL.

    Detailed description of how the fetching works, caching mechanisms,
    or expected data formats.

    Args:
        url: The endpoint to fetch data from. (Note: type is omitted here because type hints are used in the signature)
        timeout: Maximum time to wait for a response in seconds.

    Returns:
        A dictionary containing the parsed JSON response.

    Raises:
        ConnectionError: If the server cannot be reached.
        ValueError: If the URL is malformed.

    Examples:
        >>> fetch_data("https://api.example.com/data")
        {'status': 'success', 'items': []}
    """
```

## Key Sections
- **Args:** List each parameter by name, followed by a colon and description.
- **Returns:** Describe the return value (type and semantic meaning).
- **Yields:** Used instead of Returns for generators.
- **Raises:** List exceptions that may be intentionally raised by this function.
- **Examples:** Provide interactive examples using the `>>>` prompt format.
