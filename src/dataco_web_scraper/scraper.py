"""
scraper.py
----------
This module is responsible for:
Fetching raw HTML from a target URL.
"""

import logging
import time

import requests
import yaml

# Set up logging for this module
logger = logging.getLogger(__name__)


def load_config(config_path: str = "config/settings.yaml") -> dict:
    """
    Load the project configuration from settings.yaml.

    Args:
        config_path: Path to the settings file.

    Returns:
        Dictionary of configuration settings.
    """
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def fetch_page(url: str, config: dict) -> str | None:
    """
    Fetch the raw HTML content of a single page.

    Args:
        url:    The full URL to fetch.
        config: The project configuration dictionary.

    Returns:
        Raw HTML as a string, or None if the request failed.
    """
    headers = config["scraper"]["headers"]
    timeout = config["scraper"]["timeout_seconds"]
    delay  = config["scraper"]["delay_seconds"]

    try:
        logger.info("Fetching URL: %s", url)

        # Polite delay before every request
        time.sleep(delay)

        response = requests.get(url, headers=headers, timeout=timeout)

        # Raise an error for bad status codes (404, 500, etc.)
        response.raise_for_status()

        logger.info("Successfully fetched: %s [%s]", url, response.status_code)
        return response.text

    except requests.exceptions.HTTPError as e:
        logger.error("HTTP error for %s: %s", url, e)
        return None

    except requests.exceptions.ConnectionError:
        logger.error("Connection failed for %s. Check your internet.", url)
        return None

    except requests.exceptions.Timeout:
        logger.error("Request timed out for %s.", url)
        return None

    except requests.exceptions.RequestException as e:
        logger.error("Unexpected error fetching %s: %s", url, e)
        return None