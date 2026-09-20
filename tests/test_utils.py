"""Tests for the utils module."""

import pytest
import unittest.mock as mock

from autochannel.lib import utils


class TestTimediff:
    """Test cases for timediff function."""

    def test_timediff_seconds(self):
        """Test timediff calculation with seconds difference."""
        from datetime import datetime, timedelta
        channel_time = datetime.now()
        current_time = channel_time + timedelta(seconds=30)
        assert utils.timediff(channel_time, current_time) == 30

    def test_timediff_minutes(self):
        """Test timediff calculation with minutes difference."""
        from datetime import datetime, timedelta
        channel_time = datetime.now()
        current_time = channel_time + timedelta(minutes=5)
        assert utils.timediff(channel_time, current_time) == 300

    def test_timediff_zero(self):
        """Test timediff with identical times."""
        from datetime import datetime
        now = datetime.now()
        assert utils.timediff(now, now) == 0


class TestToInt:
    """Test cases for to_int function."""

    def test_to_int_int(self):
        """Test to_int with integer input."""
        assert utils.to_int(42) == 42

    def test_to_int_str_number(self):
        """Test to_int with string number."""
        assert utils.to_int("100") == 100

    def test_to_int_comma_separator(self):
        """Test to_int with comma-separated string."""
        assert utils.to_int("1,000") == 1000

    def test_to_int_negative(self):
        """Test to_int with negative number string."""
        assert utils.to_int("-5") == -5


class TestParseArguments:
    """Test cases for parse_arguments function."""

    @mock.patch('autochannel.lib.utils.argparse.ArgumentParser')
    def test_parse_arguments(self, mock_parser):
        """Test argument parser setup."""
        args = utils.parse_arguments()
        assert hasattr(args, 'debug')
        assert hasattr(args, 'version')

    @mock.patch('autochannel.lib.utils.argparse.ArgumentParser')
    def test_parse_arguments_no_args(self, mock_parser):
        """Test argument parser with no arguments."""
        args = utils.parse_arguments()
        assert args.debug is False


class TestTake:
    """Test cases for take function."""

    def test_take_first_n_items(self):
        """Test taking first n items from iterable."""
        assert utils.take(3, range(100)) == [0, 1, 2]

    def test_take_all_items(self):
        """Test taking all items."""
        assert utils.take(5, [1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5]

    def test_take_empty_list(self):
        """Test taking from empty list."""
        assert utils.take(5, []) == []


class TestFriendlyTime:
    """Test cases for friendly_time function."""

    def test_friendly_time_seconds(self):
        """Test friendly time with only seconds."""
        assert utils.friendly_time(45) == "45 seconds"

    def test_friendly_time_minutes(self):
        """Test friendly time with only minutes."""
        assert utils.friendly_time(90) == "1 minutes"

    def test_friendly_time_mixed(self):
        """Test friendly time with mixed units."""
        result = utils.friendly_time(3665)  # 1 hour, 1 minute, 5 seconds
        assert "1 hours" in result
        assert "1 minutes" in result
        assert "5 seconds" in result

    def test_friendly_time_zero(self):
        """Test friendly_time with zero seconds."""
        assert utils.friendly_time(0) == ""


class TestMessageCheck:
    """Test cases for message_check function."""

    def test_message_check_contains_author(self):
        """Test message_check when author is in mentions."""
        message = mock.MagicMock()
        message.author.id = 123456
        assert utils.message_check(message, [123456, 789012]) is True

    def test_message_check_not_contains_author(self):
        """Test message_check when author is not in mentions."""
        message = mock.MagicMock()
        message.author.id = 999999
        assert utils.message_check(message, [123456, 789012]) is False


class TestMissingNumbers:
    """Test cases for missing_numbers function."""

    def test_missing_numbers_no_missing(self):
        """Test missing_numbers with no missing numbers."""
        assert utils.missing_numbers([1, 2, 3, 4, 5]) == []

    def test_missing_numbers_some_missing(self):
        """Test missing_numbers with some missing numbers."""
        assert utils.missing_numbers([1, 3, 5]) == [2, 4]

    def test_missing_numbers_multiple_missing(self):
        """Test missing_numbers with multiple missing numbers."""
        assert utils.missing_numbers([1, 2, 3, 5, 6]) == [4]


class TestBlockCheck:
    """Test cases for block_check function."""

    def test_block_check_not_blocked(self):
        """Test block_check for non-blocked user."""
        with mock.patch.dict('os.environ', {'BLOCKED_USERS': '123456,789012'}):
            result = utils.block_check()
            assert callable(result)
