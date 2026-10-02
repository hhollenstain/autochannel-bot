"""Tests for utility functions.

These regression tests ensure utility functions continue to work correctly
after refactoring or updates.
"""

from autochannel.lib.utils import friendly_time, missing_numbers, take, to_int


def test_missing_numbers_empty_sequence():
    """Test missing numbers when sequence is empty."""
    result = missing_numbers([])
    assert result == [1]


def test_missing_numbers_all_present():
    """Test missing numbers when sequence is complete."""
    result = missing_numbers([1, 2, 3, 4, 5])
    assert result == []


def test_missing_numbers_single_missing_start():
    """Test missing numbers when first number is missing."""
    result = missing_numbers([2, 3, 4, 5])
    assert result == [1]


def test_missing_numbers_single_missing_end():
    """Test missing numbers when last number is missing."""
    result = missing_numbers([1, 2, 3, 4])
    assert result == [5]


def test_missing_numbers_single_missing_middle():
    """Test missing numbers when middle number is missing."""
    result = missing_numbers([1, 2, 4, 5])
    assert result == [3]


def test_missing_numbers_multiple_missing():
    """Test missing numbers when multiple numbers are missing."""
    result = missing_numbers([1, 2, 5, 7, 8])
    assert result == [3, 4, 6]


def test_missing_numbers_out_of_order():
    """Test missing numbers when input is out of order."""
    result = missing_numbers([5, 3, 1, 4])
    assert result == [2]


def test_missing_numbers_with_duplicates():
    """Test missing numbers when input has duplicates."""
    result = missing_numbers([1, 1, 2, 3, 5])
    assert result == [4]


def test_missing_numbers_larger_sequence():
    """Test missing numbers with a larger sequence."""
    result = missing_numbers([1, 2, 4, 5, 6, 7, 8, 9, 10])
    assert result == [3]


def test_to_int_string():
    """Test to_int with string input."""
    assert to_int("1,000") == 1000
    assert to_int("123") == 123
    assert to_int("1,234,567") == 1234567


def test_to_int_integer():
    """Test to_int with integer input."""
    assert to_int(123) == 123
    assert to_int(0) == 0


def test_take_first_n_items():
    """Test take returns first n items."""
    assert take(3, [1, 2, 3, 4, 5]) == [1, 2, 3]
    assert take(0, [1, 2, 3]) == []
    assert take(10, [1, 2, 3]) == [1, 2, 3]


def test_take_from_generator():
    """Test take works with generators."""
    assert take(3, (x for x in range(10))) == [0, 1, 2]


def test_friendly_time_zero_seconds():
    """Test friendly_time with 0 seconds."""
    assert friendly_time(0) == "0 seconds"


def test_friendly_time_seconds():
    """Test friendly_time with seconds."""
    assert friendly_time(45) == "45 seconds"


def test_friendly_time_minutes_and_seconds():
    """Test friendly_time with minutes and seconds."""
    assert friendly_time(125) == "2 minutes, 5 seconds"


def test_friendly_time_hours_and_minutes():
    """Test friendly_time with hours and minutes."""
    assert friendly_time(8000) == "2 hours, 13 minutes, 20 seconds"


def test_friendly_time_hours_only():
    """Test friendly_time when only hours are needed."""
    assert friendly_time(3720) == "1 hour, 2 minutes"
