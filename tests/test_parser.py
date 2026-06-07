"""
test_parser.py
--------------
Tests for the parser module.

Uses fake HTML strings instead of hitting the real website.
This is called mocking — tests run instantly, work offline,
and never depend on a third party being available.
"""

from dataco_web_scraper.parser import (
    parse_categories,
    parse_business_cards,
    parse_business_address,
)

# ── Fake HTML fixtures ───────────────────────────────────────
# These are minimal HTML snippets that mimic the real website
# structure — just enough to test our parsers correctly.

CATEGORIES_HTML = """
<html>
<body>
    <div class="sidebar py-8 px-10 bg-grey">
        <ul>
            <li>
                <a class="text-black" href="/category/construction/">
                    Construction
                </a>
            </li>
            <li>
                <a class="text-black" href="/category/manufacturing/">
                    Manufacturing
                </a>
            </li>
            <li>
                <a class="text-black" href="/category/renewable-energy/">
                    Renewable Energy
                </a>
            </li>
        </ul>
    </div>
</body>
</html>
"""

BUSINESS_CARDS_HTML = """
<html>
<body>
    <div class="col-span-1">
        <div class="pl-4">
            <a href="/business/acme-builders/">
                <h3 class="text-base">Acme Builders Ltd</h3>
            </a>
            <a class="flex items-center gap-2" href="https://acme.com">
                acme.com
            </a>
            <a class="flex items-center gap-2" href="tel:07700900123">
                07700 900123
            </a>
            <a class="flex items-center gap-2" href="mailto:info@acme.com">
                info@acme.com
            </a>
        </div>
    </div>
    <div class="col-span-1">
        <div class="pl-4">
            <a href="/business/beta-construction/">
                <h3 class="text-base">Beta Construction</h3>
            </a>
            <a class="flex items-center gap-2" href="tel:01234567890 / 09876543210">
                01234 567890 / 09876 543210
            </a>
        </div>
    </div>
</html>
"""

BUSINESS_PAGE_HTML = """
<html>
<body>
    <div class="col-span-1 lg:col-span-2 shadow-custom p-8">
        <div class="mb-4 sm:mb-3 grid sm:grid-cols-3 md:grid-cols-5 xl:grid-cols-12">
            <span class="font-medium col-span-1 md:col-span-2">Website</span>
            <div class="col-span-2 md:col-span-3 xl:col-span-10 flex flex-col">
                <p>https://acme.com</p>
            </div>
        </div>
        <div class="mb-4 sm:mb-3 grid sm:grid-cols-3 md:grid-cols-5 xl:grid-cols-12">
            <span class="font-medium col-span-1 md:col-span-2">Address</span>
            <div class="col-span-2 md:col-span-3 xl:col-span-10 flex flex-col">
                <p>123 High Street<br>London<br>SW1 1AA</p>
            </div>
        </div>
        <div class="mb-4 sm:mb-3 grid sm:grid-cols-3 md:grid-cols-5 xl:grid-cols-12">
            <span class="font-medium col-span-1 md:col-span-2">Description</span>
            <div class="col-span-2 md:col-span-3 xl:col-span-10 flex flex-col">
                <p>We are a leading construction company.</p>
            </div>
        </div>
    </div>
</body>
</html>
"""

EMPTY_HTML = "<html><body></body></html>"

BASE_URL = "https://ukbusinessportal.co.uk"


# ── Tests for parse_categories() ────────────────────────────

class TestParseCategories:
    """Tests for the parse_categories() function."""

    def test_returns_list(self):
        result = parse_categories(CATEGORIES_HTML, BASE_URL)
        assert isinstance(result, list)

    def test_correct_number_of_categories(self):
        result = parse_categories(CATEGORIES_HTML, BASE_URL)
        assert len(result) == 3

    def test_category_has_name_and_url(self):
        result = parse_categories(CATEGORIES_HTML, BASE_URL)
        assert "name" in result[0]
        assert "url" in result[0]

    def test_category_names_are_correct(self):
        result = parse_categories(CATEGORIES_HTML, BASE_URL)
        names = [cat["name"] for cat in result]
        assert "Construction" in names
        assert "Manufacturing" in names
        assert "Renewable Energy" in names

    def test_builds_full_urls_from_relative_paths(self):
        result = parse_categories(CATEGORIES_HTML, BASE_URL)
        construction = next(
            cat for cat in result if cat["name"] == "Construction"
        )
        assert construction["url"] == (
            "https://ukbusinessportal.co.uk/category/construction/"
        )

    def test_returns_empty_list_when_sidebar_missing(self):
        result = parse_categories(EMPTY_HTML, BASE_URL)
        assert result == []


# ── Tests for parse_business_cards() ────────────────────────

class TestParseBusinessCards:
    """Tests for the parse_business_cards() function."""

    def test_returns_list(self):
        result = parse_business_cards(
            BUSINESS_CARDS_HTML, BASE_URL, "Construction"
        )
        assert isinstance(result, list)

    def test_correct_number_of_businesses(self):
        result = parse_business_cards(
            BUSINESS_CARDS_HTML, BASE_URL, "Construction"
        )
        assert len(result) == 2

    def test_extracts_business_name(self):
        result = parse_business_cards(
            BUSINESS_CARDS_HTML, BASE_URL, "Construction"
        )
        assert result[0]["business_name"] == "Acme Builders Ltd"

    def test_extracts_business_url(self):
        result = parse_business_cards(
            BUSINESS_CARDS_HTML, BASE_URL, "Construction"
        )
        assert result[0]["business_url"] == (
            "https://ukbusinessportal.co.uk/business/acme-builders/"
        )

    def test_extracts_phone_number(self):
        result = parse_business_cards(
            BUSINESS_CARDS_HTML, BASE_URL, "Construction"
        )
        assert result[0]["phone_number"] == "07700900123"

    def test_extracts_email_address(self):
        result = parse_business_cards(
            BUSINESS_CARDS_HTML, BASE_URL, "Construction"
        )
        assert result[0]["email_address"] == "info@acme.com"

    def test_extracts_website(self):
        result = parse_business_cards(
            BUSINESS_CARDS_HTML, BASE_URL, "Construction"
        )
        assert result[0]["website"] == "https://acme.com"

    def test_adds_category_to_each_record(self):
        result = parse_business_cards(
            BUSINESS_CARDS_HTML, BASE_URL, "Construction"
        )
        assert result[0]["category"] == "Construction"

    def test_handles_multiple_phone_numbers_in_href(self):
        # Second business has two numbers in the href
        result = parse_business_cards(
            BUSINESS_CARDS_HTML, BASE_URL, "Construction"
        )
        assert result[1]["phone_number"] == "01234567890 / 09876543210"

    def test_missing_fields_are_none(self):
        # Second business has no email or website
        result = parse_business_cards(
            BUSINESS_CARDS_HTML, BASE_URL, "Construction"
        )
        assert result[1]["email_address"] is None
        assert result[1]["website"] is None

    def test_returns_empty_list_when_no_cards(self):
        result = parse_business_cards(EMPTY_HTML, BASE_URL, "Construction")
        assert result == []


# ── Tests for parse_business_address() ──────────────────────

class TestParseBusinessAddress:
    """Tests for the parse_business_address() function."""

    def test_extracts_address(self):
        result = parse_business_address(BUSINESS_PAGE_HTML)
        assert result == "123 High Street, London, SW1 1AA"

    def test_address_joins_br_lines_with_comma(self):
        # Lines separated by <br> should be joined with ", "
        result = parse_business_address(BUSINESS_PAGE_HTML)
        assert "," in result

    def test_does_not_return_description(self):
        # Should not accidentally return the description field
        result = parse_business_address(BUSINESS_PAGE_HTML)
        assert "leading construction company" not in result

    def test_does_not_return_website(self):
        # Should not accidentally return the website field
        result = parse_business_address(BUSINESS_PAGE_HTML)
        assert "https://acme.com" not in result

    def test_returns_none_when_no_container(self):
        result = parse_business_address(EMPTY_HTML)
        assert result is None

    def test_returns_string(self):
        result = parse_business_address(BUSINESS_PAGE_HTML)
        assert isinstance(result, str)