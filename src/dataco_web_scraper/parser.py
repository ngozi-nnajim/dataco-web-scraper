"""
parser.py
---------
This module is responsible for:
Reading raw HTML and extracting structured data points.
"""

import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def parse_categories(html: str, base_url: str) -> list[dict]:
    """
    Extract all category names and URLs from the categories page.

    Args:
        html:     Raw HTML of the categories listing page.
        base_url: The base URL of the website.

    Returns:
        List of dicts with 'name' and 'url' for each category.
    """
    soup = BeautifulSoup(html, "lxml")
    categories = []

    # Find the sidebar containing the category list
    sidebar = soup.find("div", class_="sidebar py-8 px-10 bg-grey")

    if not sidebar:
        logger.warning("Could not find category sidebar on page.")
        return categories

    # Find all category links inside the sidebar
    links = sidebar.find_all("a", class_="text-black")

    for link in links:
        name = link.get_text(strip=True)
        path = link.get("href", "")

        # Build the full URL if we only got a relative path
        url = path if path.startswith("http") else f"{base_url}{path}"

        if name and url:
            categories.append({"name": name, "url": url})
            logger.info("Found category: %s → %s", name, url)

    logger.info("Total categories found: %d", len(categories))
    return categories


def parse_business_cards(html: str, base_url: str, category: str) -> list[dict]:
    """
    Extract all business cards from a category page.

    Args:
        html:     Raw HTML of the category page.
        base_url: The base URL of the website.
        category: The category name (added to each record).

    Returns:
        List of dicts with business name, url, phone, email,
        website, and link to the full business page.
    """
    soup = BeautifulSoup(html, "lxml")
    businesses = []

    # Find all business cards
    cards = soup.find_all("div", class_="col-span-1")

    if not cards:
        logger.warning("No business cards found for category: %s", category)
        return businesses

    for card in cards:
        # Find the main info container
        info = card.find("div", class_="pl-4")
        if not info:
            continue

        business = {"category": category}

        # --- Business name and link to full page ---
        name_tag = info.find("a")
        if name_tag:
            business["business_name"] = name_tag.get_text(strip=True)
            path = name_tag.get("href", "")
            business["business_url"] = (
                path if path.startswith("http") else f"{base_url}{path}"
            )
        else:
            business["business_name"] = None
            business["business_url"] = None

        # --- Website, Phone, Email ---
        # All three share the same class — we tell them apart
        # by their href prefix which is part of the HTML standard
        # and guaranteed never to change
        business["website"]       = None
        business["phone_number"]  = None
        business["email_address"] = None

        all_links = info.find_all("a")
        for link in all_links:
            href = link.get("href", "")

            if href.startswith("mailto:"):
                # Email is cleanly in the href
                business["email_address"] = href.replace("mailto:", "").strip()

            elif href.startswith("tel:"):
                # Strip "tel:" prefix — may contain multiple numbers
                # separated by " / " which transformer.py handles
                business["phone_number"] = href.replace("tel:", "").strip()

            elif href.startswith("http") and href != business.get("business_url"):
                business["website"] = href.strip()

        businesses.append(business)

    logger.info(
        "Found %d businesses in category: %s", len(businesses), category
    )
    return businesses


def parse_business_address(html: str) -> str | None:
    """
    Extract the office address from an individual business page.

    The address is found by:
    1. Locating the main info container
    2. Finding all field rows inside it
    3. Identifying the row whose label span says "Address"
    4. Extracting the <p> tag content from the sibling div,
       joining lines separated by <br> tags

    Args:
        html: Raw HTML of the individual business page.

    Returns:
        Address as a single clean string, or None if not found.
    """
    soup = BeautifulSoup(html, "lxml")

    # ── Step 1: Find the main information container ──────────
    main_container = soup.find(
        "div",
        class_="col-span-1 lg:col-span-2 shadow-custom p-8"
    )

    if not main_container:
        logger.warning("Could not find main info container on business page.")
        return None

    # ── Step 2: Find all field rows inside the container ────
    field_rows = main_container.find_all(
        "div",
        class_="mb-4 sm:mb-3 grid sm:grid-cols-3 md:grid-cols-5 xl:grid-cols-12"
    )

    if not field_rows:
        logger.warning("No field rows found in main container.")
        return None

    # ── Step 3: Find the row whose label says "Address" ─────
    for row in field_rows:
        label = row.find(
            "span",
            class_="font-medium col-span-1 md:col-span-2"
        )

        # Skip rows whose label is not "Address"
        if not label or label.get_text(strip=True) != "Address":
            continue

        # ── Step 4: Find the sibling div containing the address
        address_div = row.find(
            "div",
            class_="col-span-2 md:col-span-3 xl:col-span-10 flex flex-col"
        )

        if not address_div:
            logger.warning("Found Address label but no content div.")
            return None

        # ── Step 5: Extract the <p> tag and join <br> lines ─
        p_tag = address_div.find("p")

        if not p_tag:
            logger.warning("Found address div but no <p> tag inside.")
            return None

        # stripped_strings automatically handles <br> tags
        # by treating each line as a separate string
        parts = [
            text.strip()
            for text in p_tag.stripped_strings
            if text.strip()
        ]

        if not parts:
            logger.warning("Address <p> tag was empty.")
            return None

        # Join all lines into one clean comma-separated string
        address = ", ".join(parts)
        logger.info("Address extracted: %s", address)
        return address

    logger.warning("Address field row not found on business page.")
    return None