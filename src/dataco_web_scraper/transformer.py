"""
transformer.py
--------------
This module is responsible for:
Cleaning and structuring the extracted data.
"""

import logging
import re
import pandas as pd
from pathlib import Path

logger = logging.getLogger(__name__)

# ── Constants ────────────────────────────────────────────────

# Used to fill empty fields in the final output.
# "Not Listed" is preferred over "N/A" because these fields
# DO apply to the business — the business simply hasn't
# listed them. "Not Listed" is honest and clear to any
# non-technical reader.
EMPTY_FILL_VALUE = "Not Listed"


# ── Helper Functions ─────────────────────────────────────────

def is_empty(value) -> bool:
    """
    Check if a value is empty.
    Handles None, NaN (float), and blank strings.

    Args:
        value: Any value to check.

    Returns:
        True if the value is effectively empty, False otherwise.
    """
    if value is None:
        return True
    # pandas fills missing values with NaN which is a float
    if isinstance(value, float):
        return True
    if isinstance(value, str) and not value.strip():
        return True
    return False


def clean_text(value) -> str | None:
    """
    Strip leading/trailing whitespace from any text field.

    Args:
        value: Raw text value.

    Returns:
        Cleaned string, or None if empty.
    """
    if is_empty(value):
        return None
    return str(value).strip()


def clean_phone_number(value) -> str:
    """
    Clean and normalise phone number values.

    Handles two cases:
    1. Single number:   "07700 900123"
    2. Multiple numbers listed with " / " separator:
                        "07700 900123 / 01747 590387"

    Each individual number is cleaned by removing non-numeric
    characters (except spaces and leading +), then all numbers
    are rejoined with " | " as the professional multi-value
    separator for flat CSV files.

    Args:
        value: Raw phone number string from the href attribute.

    Returns:
        Cleaned phone string or EMPTY_FILL_VALUE if empty.
    """
    if is_empty(value):
        return EMPTY_FILL_VALUE

    raw = str(value).strip()

    # Split on "/" to handle multiple numbers
    parts = raw.split("/")

    cleaned_numbers = []
    for part in parts:
        # Remove everything except digits, spaces, and leading +
        cleaned = re.sub(r"[^\d\s+]", "", part).strip()
        if cleaned:
            cleaned_numbers.append(cleaned)

    if not cleaned_numbers:
        return EMPTY_FILL_VALUE

    # Rejoin multiple numbers with pipe separator
    return " | ".join(cleaned_numbers)


# ── Main Functions ───────────────────────────────────────────

def transform(records: list[dict]) -> pd.DataFrame:
    """
    Clean and structure a list of raw business records
    into a pandas DataFrame.

    Steps:
    1. Build DataFrame from raw records
    2. Clean each column
    3. Fill empty values with EMPTY_FILL_VALUE
    4. Drop rows with no business name
    5. Reorder columns logically
    6. Reset index

    Args:
        records: List of raw business dictionaries.

    Returns:
        Cleaned pandas DataFrame ready for export.
    """
    if not records:
        logger.warning("No records to transform.")
        return pd.DataFrame()

    logger.info("Transforming %d records...", len(records))

    df = pd.DataFrame(records)

    # ── Step 1: Clean each column ────────────────────────────
    df["business_name"]  = df["business_name"].apply(clean_text)
    df["category"]       = df["category"].apply(clean_text)
    df["address"]        = df["address"].apply(clean_text)
    df["phone_number"]   = df["phone_number"].apply(clean_phone_number)
    df["email_address"]  = df["email_address"].apply(clean_text)
    df["website"]        = df["website"].apply(clean_text)

    # ── Step 2: Fill empty values ────────────────────────────
    # Apply EMPTY_FILL_VALUE to all nullable columns except
    # business_name and business_url — these either exist
    # or the row gets dropped entirely
    fill_columns = ["address", "email_address", "website"]
    for col in fill_columns:
        df[col] = df[col].fillna(EMPTY_FILL_VALUE)
        # Also catch any None values that slipped through
        df[col] = df[col].apply(
            lambda x: EMPTY_FILL_VALUE if is_empty(x) else x
        )

    # ── Step 3: Drop rows with no business name ──────────────
    before = len(df)
    df.dropna(subset=["business_name"], inplace=True)
    after = len(df)

    if before != after:
        logger.warning(
            "Dropped %d rows with missing business name.",
            before - after
        )

    # ── Step 4: Reorder columns logically ───────────────────
    column_order = [
        "category",
        "business_name",
        "address",
        "phone_number",
        "email_address",
        "website",
        "business_url",
    ]
    df = df[column_order]

    # ── Step 5: Reset index cleanly ──────────────────────────
    df.reset_index(drop=True, inplace=True)

    logger.info("Transformation complete. %d clean records.", len(df))
    return df


def save_to_csv(df: pd.DataFrame, config: dict) -> str:
    """
    Save the cleaned DataFrame to a CSV file.

    Args:
        df:     Cleaned pandas DataFrame.
        config: Project configuration dictionary.

    Returns:
        The full path of the saved CSV file as a string.
    """
    output_dir = Path(config["output"]["processed_directory"])
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / config["output"]["filename"]

    df.to_csv(output_path, index=False)

    logger.info("Data saved to: %s", output_path)
    logger.info("Total records saved: %d", len(df))

    return str(output_path)


def save_to_excel(df: pd.DataFrame, config: dict) -> str:
    """
    Save the cleaned DataFrame to an Excel (.xlsx) file.

    The phone_number column is explicitly formatted as text
    using Excel's '@' format code — this prevents Excel from
    treating numeric-looking values as numbers and stripping
    leading zeros when the file is opened directly in Excel.

    This output is intended for non-technical business users
    who open files directly in Excel.

    Args:
        df:     Cleaned pandas DataFrame.
        config: Project configuration dictionary.

    Returns:
        The full path of the saved Excel file as a string.
    """
    output_dir = Path(config["output"]["processed_directory"])
    output_dir.mkdir(parents=True, exist_ok=True)

    # Build Excel filename from the CSV filename in config
    csv_filename   = config["output"]["filename"]
    excel_filename = csv_filename.replace(".csv", ".xlsx")
    output_path    = output_dir / excel_filename

    # Write using openpyxl engine so we can directly access
    # the worksheet and set column formatting
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Business Listings")

        worksheet = writer.sheets["Business Listings"]

        # Find the phone_number column position (openpyxl is 1-based)
        phone_col_idx = df.columns.get_loc("phone_number") + 1

        # Apply Excel text format "@" to every phone cell
        # Skip row 1 which is the header
        # This tells Excel: display exactly as typed, never convert
        for row in range(2, len(df) + 2):
            cell = worksheet.cell(row=row, column=phone_col_idx)
            cell.number_format = "@"
            cell.value = str(cell.value) if cell.value else ""

    logger.info("Excel file saved to: %s", output_path)
    logger.info("Total records saved: %d", len(df))

    return str(output_path)