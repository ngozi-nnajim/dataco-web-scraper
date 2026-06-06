"""
dataco_web_scraper
------------------
DataCo automated web scraping pipeline.
"""

import logging
import yaml


def setup_logging(config_path: str = "config/settings.yaml") -> None:
    """
    Configure logging for the entire pipeline.
    Writes logs to both the terminal and a log file.

    Args:
        config_path: Path to the settings file.
    """
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    log_level = config["logging"]["level"]
    log_file  = config["logging"]["file"]

    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            # Write to terminal
            logging.StreamHandler(),
            # Write to log file
            logging.FileHandler(log_file),
        ],
    )