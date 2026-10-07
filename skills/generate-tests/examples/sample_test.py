"""
Sample Test File — Teaching Example
====================================

This file demonstrates ALL common pytest testing patterns using a fictional
Calculator class. Use this as a reference when generating tests for real projects.

Patterns demonstrated:
1. Basic assertions
2. Fixtures (function, class, module, session scope)
3. Parametrized tests
4. Exception testing
5. Mocking (patch, MagicMock)
6. Markers (slow, integration, user_specified)
7. Edge case testing
8. Setup/teardown
9. Testing with temporary files
10. Testing async code (commented example)
"""

import pytest
from unittest.mock import patch, MagicMock, PropertyMock
import os


# ============================================================================
# TARGET CODE (normally this would be imported from your project)
# ============================================================================

class Calculator:
    """A simple calculator with history tracking and external API integration."""

    def __init__(self):
        self.history: list[str] = []
        self._last_result: float | None = None

    @property
    def last_result(self) -> float | None:
        return self._last_result

    def add(self, a: float, b: float) -> float:
        result = a + b
        self._last_result = result
        self.history.append(f"{a} + {b} = {result}")
        return result

    def divide(self, a: float, b: float) -> float:
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        result = a / b
        self._last_result = result
        self.history.append(f"{a} / {b} = {result}")
        return result

    def save_history(self, filepath: str) -> None:
        with open(filepath, "w") as f:
            for entry in self.history:
                f.write(entry + "\n")

    def load_exchange_rate(self, currency: str) -> float:
        """Simulates calling an external API to get exchange rates."""
        import requests
        response = requests.get(f"https://api.example.com/rates/{currency}")
        response.raise_for_status()
        return response.json()["rate"]

    def convert_currency(self, amount: float, currency: str) -> float:
        rate = self.load_exchange_rate(currency)
        return amount * rate

    def clear_history(self) -> None:
        self.history.clear()
        self._last_result = None


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def calculator():
    """Provide a fresh Calculator instance for each test."""
    return Calculator()


@pytest.fixture
def calculator_with_history(calculator):
    """Provide a Calculator with some pre-existing history."""
    calculator.add(1, 2)
    calculator.add(3, 4)
    calculator.divide(10, 2)
    return calculator


# ============================================================================
# PATTERN 1: BASIC ASSERTIONS (Happy Path)
# ============================================================================

class TestCalculatorBasicOperations:
    """Test basic arithmetic operations."""

    def test_add_positive_numbers(self, calculator):
        """Verify addition works with positive numbers."""
        assert calculator.add(2, 3) == 5

    def test_add_negative_numbers(self, calculator):
        """Verify addition works with negative numbers."""
        assert calculator.add(-2, -3) == -5

    def test_add_updates_last_result(self, calculator):
        """Verify that last_result is updated after addition."""
        calculator.add(10, 20)
        assert calculator.last_result == 30

    def test_add_records_history(self, calculator):
        """Verify that operations are recorded in history."""
        calculator.add(5, 3)
        assert len(calculator.history) == 1
        assert "5 + 3 = 8" in calculator.history[0]

    def test_divide_returns_correct_result(self, calculator):
        """Verify division produces correct results."""
        assert calculator.divide(10, 2) == 5.0


# ============================================================================
# PATTERN 2: PARAMETRIZED TESTS
# ============================================================================

class TestCalculatorParametrized:
    """Test multiple inputs efficiently using parametrize."""

    @pytest.mark.parametrize("a, b, expected", [
        (1, 1, 2),          # Simple
        (0, 0, 0),          # Zeros
        (-1, 1, 0),         # Negative + positive
        (0.1, 0.2, 0.3),    # Floats (note: use pytest.approx for floats)
        (999999, 1, 1000000),  # Large numbers
    ])
    def test_add_various_inputs(self, calculator, a, b, expected):
        """Verify addition works with various input combinations."""
        result = calculator.add(a, b)
        assert result == pytest.approx(expected)

    @pytest.mark.parametrize("a, b, expected", [
        (10, 2, 5.0),
        (7, 3, 2.3333333),
        (0, 5, 0.0),
        (-10, 2, -5.0),
    ])
    def test_divide_various_inputs(self, calculator, a, b, expected):
        """Verify division works with various input combinations."""
        assert calculator.divide(a, b) == pytest.approx(expected, rel=1e-5)


# ============================================================================
# PATTERN 3: EXCEPTION TESTING
# ============================================================================

class TestCalculatorExceptions:
    """Test error handling and exception raising."""

    def test_divide_by_zero_raises_error(self, calculator):
        """Verify ZeroDivisionError is raised when dividing by zero."""
        with pytest.raises(ZeroDivisionError, match="Cannot divide by zero"):
            calculator.divide(10, 0)

    def test_divide_by_zero_does_not_update_history(self, calculator):
        """Verify failed operations don't pollute history."""
        with pytest.raises(ZeroDivisionError):
            calculator.divide(10, 0)
        assert len(calculator.history) == 0


# ============================================================================
# PATTERN 4: MOCKING EXTERNAL APIS
# ============================================================================

class TestCalculatorWithExternalAPI:
    """Test functionality that depends on external services."""

    @patch("__main__.Calculator.load_exchange_rate")
    def test_convert_currency_uses_exchange_rate(self, mock_rate, calculator):
        """Verify currency conversion uses the fetched exchange rate."""
        mock_rate.return_value = 0.85
        result = calculator.convert_currency(100, "EUR")
        assert result == 85.0
        mock_rate.assert_called_once_with("EUR")

    @patch("requests.get")
    def test_load_exchange_rate_parses_api_response(self, mock_get, calculator):
        """Verify API response is correctly parsed."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"rate": 1.25}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        rate = calculator.load_exchange_rate("GBP")

        assert rate == 1.25
        mock_get.assert_called_once_with("https://api.example.com/rates/GBP")

    @patch("requests.get")
    def test_load_exchange_rate_handles_api_error(self, mock_get, calculator):
        """Verify graceful handling of API failures."""
        import requests
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("503 Server Error")
        mock_get.return_value = mock_response

        with pytest.raises(requests.HTTPError):
            calculator.load_exchange_rate("INVALID")


# ============================================================================
# PATTERN 5: FILE SYSTEM TESTING (using tmp_path)
# ============================================================================

class TestCalculatorFileOperations:
    """Test file I/O operations using temporary directories."""

    def test_save_history_creates_file(self, calculator_with_history, tmp_path):
        """Verify history is saved to a file."""
        filepath = tmp_path / "history.txt"
        calculator_with_history.save_history(str(filepath))
        assert filepath.exists()

    def test_save_history_contains_all_entries(self, calculator_with_history, tmp_path):
        """Verify all history entries are written to the file."""
        filepath = tmp_path / "history.txt"
        calculator_with_history.save_history(str(filepath))
        content = filepath.read_text()
        lines = content.strip().split("\n")
        assert len(lines) == 3  # 2 additions + 1 division

    def test_save_empty_history_creates_empty_file(self, calculator, tmp_path):
        """Verify saving empty history creates an empty file."""
        filepath = tmp_path / "history.txt"
        calculator.save_history(str(filepath))
        assert filepath.exists()
        assert filepath.read_text() == ""


# ============================================================================
# PATTERN 6: EDGE CASE TESTING
# ============================================================================

class TestCalculatorEdgeCases:
    """Test boundary conditions and unusual inputs."""

    def test_add_with_float_precision(self, calculator):
        """Verify floating point precision is handled."""
        # 0.1 + 0.2 != 0.3 in floating point
        result = calculator.add(0.1, 0.2)
        assert result == pytest.approx(0.3)

    def test_add_very_large_numbers(self, calculator):
        """Verify operations work with very large numbers."""
        result = calculator.add(10**18, 10**18)
        assert result == 2 * 10**18

    def test_divide_very_small_result(self, calculator):
        """Verify division produces correct very small results."""
        result = calculator.divide(1, 10**10)
        assert result == pytest.approx(1e-10)

    def test_history_after_many_operations(self, calculator):
        """Verify history tracks many operations correctly."""
        for i in range(100):
            calculator.add(i, i + 1)
        assert len(calculator.history) == 100

    def test_clear_history_resets_state(self, calculator_with_history):
        """Verify clear_history removes all entries and resets last_result."""
        calculator_with_history.clear_history()
        assert len(calculator_with_history.history) == 0
        assert calculator_with_history.last_result is None


# ============================================================================
# PATTERN 7: USER-SPECIFIED TEST CASES
# ============================================================================

class TestUserSpecified:
    """Tests explicitly requested by the user.
    
    These tests implement specific requirements from the user's prompt.
    They are marked with @pytest.mark.user_specified for easy identification.
    """

    @pytest.mark.user_specified
    def test_division_result_is_always_float(self, calculator):
        """User requirement: Division should always return a float."""
        result = calculator.divide(10, 5)
        assert isinstance(result, float)

    @pytest.mark.user_specified
    def test_history_preserves_operation_order(self, calculator):
        """User requirement: History should maintain chronological order."""
        calculator.add(1, 2)
        calculator.divide(6, 3)
        calculator.add(4, 5)
        assert "1 + 2" in calculator.history[0]
        assert "6 / 3" in calculator.history[1]
        assert "4 + 5" in calculator.history[2]


# ============================================================================
# PATTERN 8: PROPERTY MOCKING
# ============================================================================

class TestPropertyMocking:
    """Demonstrate how to mock properties."""

    def test_mock_last_result_property(self):
        """Show how to mock a property on an object."""
        calc = Calculator()
        with patch.object(
            type(calc), "last_result",
            new_callable=PropertyMock, return_value=42.0
        ):
            assert calc.last_result == 42.0
