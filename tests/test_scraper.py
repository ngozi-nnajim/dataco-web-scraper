"""
test_scraper.py
---------------
Tests for the scraper module.

We test configuration loading here.
We do NOT test fetch_page() with real HTTP requests
in unit tests — that belongs in integration tests
which are run separately and intentionally.
"""

import pytest
from dataco_web_scraper.scraper import load_config


# ── Tests for load_config() ──────────────────────────────────

class TestLoadConfig:
    """Tests for the load_config() function."""

    def test_returns_dict(self):
        config = load_config()
        assert isinstance(config, dict)

    def test_scraper_section_exists(self):
        config = load_config()
        assert "scraper" in config

    def test_output_section_exists(self):
        config = load_config()
        assert "output" in config

    def test_logging_section_exists(self):
        config = load_config()
        assert "logging" in config

    def test_base_url_is_present(self):
        config = load_config()
        assert "base_url" in config["scraper"]

    def test_base_url_is_string(self):
        config = load_config()
        assert isinstance(config["scraper"]["base_url"], str)

    def test_delay_seconds_is_present(self):
        config = load_config()
        assert "delay_seconds" in config["scraper"]

    def test_delay_seconds_is_positive(self):
        # Delay must be positive — zero delay is inconsiderate
        config = load_config()
        assert config["scraper"]["delay_seconds"] > 0

    def test_output_filename_is_csv(self):
        # Output must always be a CSV for this project
        config = load_config()
        assert config["output"]["filename"].endswith(".csv")

    def test_raises_error_for_missing_config(self):
        # Should raise an error if config file doesn't exist
        with pytest.raises(FileNotFoundError):
            load_config("config/nonexistent.yaml")