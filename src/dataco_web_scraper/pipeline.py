"""
pipeline.py
-----------
This module is responsible for:
Orchestrating all steps of the scraping pipeline.

Supports three run modes:
    full        → extract + transform (default)
    extract     → extraction only, saves raw data
    transform   → transformation only, loads saved raw data
"""

import json
import logging
import sys
from pathlib import Path

from dataco_web_scraper import setup_logging
from dataco_web_scraper.scraper import load_config, fetch_page
from dataco_web_scraper.parser import (
    parse_categories,
    parse_business_cards,
    parse_business_address,
)
from dataco_web_scraper.transformer import transform, save_to_csv, save_to_excel

logger = logging.getLogger(__name__)

# Where we save raw records between stages
RAW_CHECKPOINT = Path("data/raw/raw_records.json")


def save_checkpoint(records: list[dict]) -> None:
    """
    Save raw extracted records to a JSON checkpoint file.
    This allows transformation to run independently without
    re-scraping the website.

    Args:
        records: List of raw business dictionaries.
    """
    RAW_CHECKPOINT.parent.mkdir(parents=True, exist_ok=True)
    with open(RAW_CHECKPOINT, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
    logger.info("Checkpoint saved: %d records → %s", len(records), RAW_CHECKPOINT)


def load_checkpoint() -> list[dict]:
    """
    Load raw records from the checkpoint file.

    Returns:
        List of raw business dictionaries.

    Raises:
        FileNotFoundError: If no checkpoint exists yet.
    """
    if not RAW_CHECKPOINT.exists():
        raise FileNotFoundError(
            f"No checkpoint found at {RAW_CHECKPOINT}. "
            "Run extraction first with: python -m src.dataco_web_scraper.pipeline extract"
        )
    with open(RAW_CHECKPOINT, "r", encoding="utf-8") as f:
        records = json.load(f)
    logger.info("Checkpoint loaded: %d records from %s", len(records), RAW_CHECKPOINT)
    return records


def run_extraction(config: dict) -> list[dict]:
    """
    Run the extraction stage only.
    Fetches all categories, business cards, and addresses.
    Saves results to a raw checkpoint file.

    Args:
        config: Project configuration dictionary.

    Returns:
        List of raw business dictionaries.
    """
    base_url       = config["scraper"]["base_url"]
    categories_url = base_url + config["scraper"]["categories_path"]

    # ── Step 1: Fetch categories page ────────────────────────
    logger.info("Step 1: Fetching categories page...")
    categories_html = fetch_page(categories_url, config)

    if not categories_html:
        logger.error("Failed to fetch categories page. Aborting.")
        return []

    # ── Step 2: Extract all category URLs ───────────────────
    logger.info("Step 2: Extracting category URLs...")
    categories = parse_categories(categories_html, base_url)

    if not categories:
        logger.error("No categories found. Aborting.")
        return []

    logger.info("Found %d categories to scrape.", len(categories))

    # ── Step 3 & 4: Scrape each category and business ───────
    all_records = []

    for i, category in enumerate(categories, start=1):
        logger.info(
            "Step 3 [%d/%d]: Scraping category: %s",
            i, len(categories), category["name"]
        )

        category_html = fetch_page(category["url"], config)
        if not category_html:
            logger.warning("Skipping category: %s", category["name"])
            continue

        businesses = parse_business_cards(
            category_html, base_url, category["name"]
        )

        for j, business in enumerate(businesses, start=1):
            logger.info(
                "  Step 4 [%d/%d]: Fetching address for: %s",
                j, len(businesses), business["business_name"]
            )

            if not business.get("business_url"):
                business["address"] = None
                all_records.append(business)
                continue

            business_html = fetch_page(business["business_url"], config)
            business["address"] = (
                parse_business_address(business_html)
                if business_html else None
            )
            all_records.append(business)

    # ── Save checkpoint ──────────────────────────────────────
    save_checkpoint(all_records)
    return all_records


def run_transformation(config: dict) -> None:
    """
    Run the transformation stage only.
    Loads raw records from checkpoint and saves clean CSV.

    Args:
        config: Project configuration dictionary.
    """
    # ── Step 5: Load checkpoint ──────────────────────────────
    logger.info("Step 5: Loading raw records from checkpoint...")
    try:
        all_records = load_checkpoint()
    except FileNotFoundError as e:
        logger.error(str(e))
        return

    # ── Step 6: Transform ────────────────────────────────────
    logger.info("Step 6: Transforming %d records...", len(all_records))
    df = transform(all_records)

    if df.empty:
        logger.error("No data to save after transformation. Aborting.")
        return

    # ── Step 7: Save ─────────────────────────────────────────
    logger.info("Step 7: Saving outputs...")
    csv_path   = save_to_csv(df, config)
    excel_path = save_to_excel(df, config)

    logger.info("=" * 60)
    logger.info("Transformation complete.")
    logger.info("CSV output:    %s", csv_path)
    logger.info("Excel output:  %s", excel_path)
    logger.info("Total records: %d", len(df))
    logger.info("=" * 60)


def run(mode: str = "full") -> None:
    """
    Execute the pipeline in the specified mode.

    Modes:
        full      → extract + transform (default)
        extract   → extraction only
        transform → transformation only (uses checkpoint)

    Args:
        mode: Pipeline run mode.
    """
    setup_logging()
    config = load_config()

    logger.info("=" * 60)
    logger.info("DataCo Web Scraper — Pipeline Starting [mode: %s]", mode)
    logger.info("=" * 60)

    if mode == "extract":
        run_extraction(config)

    elif mode == "transform":
        run_transformation(config)

    elif mode == "full":
        all_records = run_extraction(config)
        if all_records:
            df = transform(all_records)
            if not df.empty:
                csv_path   = save_to_csv(df, config)
                excel_path = save_to_excel(df, config)
                logger.info("Pipeline complete.")
                logger.info("CSV output:    %s", csv_path)
                logger.info("Excel output:  %s", excel_path)
                logger.info("Total records: %d", len(df))
    else:
        logger.error(
            "Unknown mode: '%s'. Use: full, extract, or transform.", mode
        )

    logger.info("=" * 60)


if __name__ == "__main__":
    # Read mode from command line argument, default to "full"
    mode = sys.argv[1] if len(sys.argv) > 1 else "full"
    run(mode)