"""
test_transformer.py
-------------------
Tests for the transformer module.

Each test follows the AAA pattern:
    Arrange  → set up inputs
    Act      → call the function
    Assert   → verify the output
"""

import pandas as pd
from dataco_web_scraper.transformer import (
    EMPTY_FILL_VALUE,
    clean_phone_number,
    clean_text,
    is_empty,
    transform,
)


# ── Tests for is_empty() ─────────────────────────────────────

class TestIsEmpty:
    """Tests for the is_empty() guard function."""

    def test_none_is_empty(self):
        assert is_empty(None) is True

    def test_float_nan_is_empty(self):
        # pandas fills missing values with float NaN
        assert is_empty(float("nan")) is True

    def test_empty_string_is_empty(self):
        assert is_empty("") is True

    def test_whitespace_string_is_empty(self):
        assert is_empty("   ") is True

    def test_valid_string_is_not_empty(self):
        assert is_empty("Acme Ltd") is False

    def test_zero_is_not_empty(self):
        # 0 is a valid value — not empty
        assert is_empty(0) is False


# ── Tests for clean_text() ───────────────────────────────────

class TestCleanText:
    """Tests for the clean_text() function."""

    def test_strips_leading_whitespace(self):
        assert clean_text("  Acme Ltd") == "Acme Ltd"

    def test_strips_trailing_whitespace(self):
        assert clean_text("Acme Ltd  ") == "Acme Ltd"

    def test_strips_both_ends(self):
        assert clean_text("  Acme Ltd  ") == "Acme Ltd"

    def test_returns_none_for_none(self):
        assert clean_text(None) is None

    def test_returns_none_for_empty_string(self):
        assert clean_text("") is None

    def test_returns_none_for_whitespace(self):
        assert clean_text("   ") is None

    def test_returns_none_for_nan(self):
        assert clean_text(float("nan")) is None

    def test_preserves_internal_spaces(self):
        # Internal spaces should not be touched
        assert clean_text("  Acme Plumbers Ltd  ") == "Acme Plumbers Ltd"

    def test_converts_non_string_to_string(self):
        # Should handle non-string input gracefully
        assert clean_text(12345) == "12345"


# ── Tests for clean_phone_number() ───────────────────────────

class TestCleanPhoneNumber:
    """Tests for the clean_phone_number() function."""

    def test_cleans_single_number(self):
        result = clean_phone_number("07700900123")
        assert result == "07700900123"

    def test_preserves_spaces_in_number(self):
        result = clean_phone_number("07700 900123")
        assert result == "07700 900123"

    def test_handles_two_numbers_with_slash(self):
        # Multiple numbers separated by "/" should be
        # split and rejoined with " | "
        result = clean_phone_number("07700900123 / 01747590387")
        assert result == "07700900123 | 01747590387"

    def test_handles_two_numbers_with_spaces(self):
        result = clean_phone_number("07700 900123 / 01747 590387")
        assert result == "07700 900123 | 01747 590387"

    def test_returns_not_listed_for_none(self):
        assert clean_phone_number(None) == EMPTY_FILL_VALUE

    def test_returns_not_listed_for_empty_string(self):
        assert clean_phone_number("") == EMPTY_FILL_VALUE

    def test_returns_not_listed_for_nan(self):
        assert clean_phone_number(float("nan")) == EMPTY_FILL_VALUE

    def test_removes_non_numeric_characters(self):
    # Hyphens and parentheses are removed
    # Spaces that were between digits close up when separators removed
        result = clean_phone_number("+44 (0) 207-123-4567")
        assert result == "+44 0 2071234567"

    def test_preserves_leading_plus_for_international(self):
        # Leading + for international dialling codes must be kept
        result = clean_phone_number("+447700900123")
        assert result == "+447700900123"


# ── Tests for transform() ────────────────────────────────────

class TestTransform:
    """Tests for the transform() function."""

    def _make_record(self, **kwargs) -> dict:
        """
        Helper that creates a valid business record.
        Any field can be overridden via kwargs.
        """
        base = {
            "category": "Construction",
            "business_name": "Acme Builders Ltd",
            "address": "123 High Street, London, SW1 1AA",
            "phone_number": "07700 900123",
            "email_address": "info@acme.com",
            "website": "https://acme.com",
            "business_url": "https://ukbusinessportal.co.uk/business/acme/",
        }
        base.update(kwargs)
        return base

    def test_returns_dataframe(self):
        records = [self._make_record()]
        df = transform(records)
        assert isinstance(df, pd.DataFrame)

    def test_correct_number_of_records(self):
        records = [self._make_record(), self._make_record()]
        df = transform(records)
        assert len(df) == 2

    def test_correct_columns_present(self):
        records = [self._make_record()]
        df = transform(records)
        expected_columns = [
            "category", "business_name", "address",
            "phone_number", "email_address", "website", "business_url"
        ]
        assert list(df.columns) == expected_columns

    def test_empty_records_returns_empty_dataframe(self):
        df = transform([])
        assert df.empty

    def test_drops_rows_with_no_business_name(self):
        records = [
            self._make_record(business_name=None),
            self._make_record(business_name="Valid Business"),
        ]
        df = transform(records)
        # Only the valid record should remain
        assert len(df) == 1
        assert df.iloc[0]["business_name"] == "Valid Business"

    def test_fills_missing_address_with_not_listed(self):
        records = [self._make_record(address=None)]
        df = transform(records)
        assert df.iloc[0]["address"] == EMPTY_FILL_VALUE

    def test_fills_missing_email_with_not_listed(self):
        records = [self._make_record(email_address=None)]
        df = transform(records)
        assert df.iloc[0]["email_address"] == EMPTY_FILL_VALUE

    def test_fills_missing_website_with_not_listed(self):
        records = [self._make_record(website=None)]
        df = transform(records)
        assert df.iloc[0]["website"] == EMPTY_FILL_VALUE

    def test_fills_nan_values_with_not_listed(self):
        # pandas NaN should also be caught and filled
        records = [self._make_record(address=float("nan"))]
        df = transform(records)
        assert df.iloc[0]["address"] == EMPTY_FILL_VALUE

    def test_cleans_whitespace_from_business_name(self):
        records = [self._make_record(business_name="  Acme Ltd  ")]
        df = transform(records)
        assert df.iloc[0]["business_name"] == "Acme Ltd"

    def test_handles_multiple_phone_numbers(self):
        records = [self._make_record(phone_number="07700900123 / 01747590387")]
        df = transform(records)
        assert df.iloc[0]["phone_number"] == "07700900123 | 01747590387"

    def test_index_is_reset(self):
        records = [self._make_record(), self._make_record()]
        df = transform(records)
        assert list(df.index) == [0, 1]