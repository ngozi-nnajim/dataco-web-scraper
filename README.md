![CI](https://github.com/ngozi-nnajim/dataco-web-scraper/actions/workflows/ci.yml/badge.svg)

# DataCo Web Scraper 🌐

> Automated web scraping pipeline for collecting and structuring 
> business listing data from public sources.

Built by a Data Engineer at **DataCo** — a data collection firm 
specialising in automated web data collection to empower businesses 
with real-time, accurate, and actionable insights.

---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Business Problem](#business-problem)
- [Project Workflow](#project-workflow)
- [Project Structure](#project-structure)
- [Quick Start (Non-Technical Users)](#quick-start)
- [Developer Setup](#developer-setup)
- [Running the Scraper](#running-the-scraper)
- [Running Tests](#running-tests)
- [Configuration](#configuration)
- [Data Output](#data-output)
- [Best Practices & Ethics](#best-practices--ethics)
- [Contributing](#contributing)

---

## Project Overview

This pipeline scrapes publicly available business listing data from
[UK Business Portal](https://ukbusinessportal.co.uk/) across all
available business categories and structures it into clean,
analysis-ready CSV files.

**Data points collected:**
- Business category
- Business name
- Office address
- Phone number (handles multiple numbers per business)
- Email address
- Website

**Tech stack:**
- Python 3.10+
- BeautifulSoup4 (HTML parsing)
- Requests (HTTP)
- Pandas (data structuring)
- PyYAML (configuration)
- Python-dotenv (environment variables)

---

## Business Problem

In today's fast-paced digital economy, businesses are inundated with
vast amounts of unstructured data scattered across the web. Accessing
this data manually is time-consuming, error-prone, and inconsistent.

This pipeline bridges that gap by systematically collecting and
structuring data from public online sources — enabling faster,
smarter, data-driven decisions.

---

## Project Workflow

The pipeline runs in three stages. Each stage can be run
independently, meaning you never have to re-scrape data you
already have.

```text
Stage 1 — Extraction
  → Fetches all category URLs from the categories page
  → Scrapes all business cards from each category page
  → Visits each business page individually to extract address
  → Saves raw records to a checkpoint file (data/raw/)

Stage 2 — Transformation
  → Loads raw records from the checkpoint file
  → Cleans and normalises all fields
  → Fills missing values with "Not Listed"
  → Handles multiple phone numbers with " | " separator
  → Saves final output to CSV (data/processed/)

Stage 3 — Full Pipeline
  → Runs Stage 1 and Stage 2 back to back
```

---

## Project Structure

```text
dataco-web-scraper/
├── config/                 → Settings and configuration
├── data/
│   ├── raw/                → Raw checkpoint file (never edit)
│   └── processed/          → Cleaned, analysis-ready CSV output
├── logs/                   → Runtime logs and error records
├── notebooks/              → Exploration and analysis notebooks
├── src/
│   └── dataco_web_scraper/
│       ├── __init__.py         → Logging setup
│       ├── scraper.py          → Fetches web pages
│       ├── parser.py           → Extracts data from HTML
│       ├── transformer.py      → Cleans and structures data
│       └── pipeline.py         → Orchestrates all steps
├── tests/                  → Automated tests
├── .env.example            → Secrets template
├── Makefile                → Command shortcuts
└── pyproject.toml          → Project dependencies
```

---

## Quick Start

> For non-technical users — run the scraper in three steps.

**Step 1:** Make sure Python 3.10+ is installed on your machine.

**Step 2:** Open your terminal, navigate to this folder, and run:

```bash
make install
```

**Step 3:** Run the full pipeline:

```bash
make run
```

Your output CSV file will appear in `data/processed/`.

> ⏱ The pipeline deliberately pauses 3 seconds between each
> request to be respectful to the website. This means it will
> take several minutes to complete — this is expected and correct.

---

## Developer Setup

**Step 1:** Clone the repository:

```bash
git clone git@github.com:<your-username>/dataco-web-scraper.git
cd dataco-web-scraper
```

**Step 2:** Set up the environment:

```bash
make install
```

**Step 3:** Copy the secrets template and fill in your values:

```bash
cp .env.example .env
```

**Step 4:** Confirm everything works:

```bash
make test
```

---

## Running With Docker

Docker allows you to run the scraper in a fully isolated
environment without installing Python or any dependencies
on your machine.

**Prerequisites:** [Install Docker Desktop](https://www.docker.com/products/docker-desktop/)

**Step 1:** Build the image:
```bash
make docker-build
```

**Step 2:** Run the pipeline:
```bash
make docker-run        # full pipeline
make docker-extract    # extraction only
make docker-transform  # transformation only
```

Output files appear in `data/processed/` on your machine
automatically via volume mounting.

> The first build takes a few minutes as Docker downloads
> the base image and installs dependencies. Subsequent
> builds are much faster due to layer caching.

---

## Running the Scraper

The pipeline supports three run modes:

```bash
# Run everything from scratch (default)
make run

# Run extraction only — saves raw checkpoint to data/raw/
make extract

# Run transformation only — loads from checkpoint, no re-scraping
make transform
```

### When to Use Each Mode

| Mode | Use when |
|---|---|
| `make run` | First time setup or website data has changed |
| `make extract` | You only want to refresh the raw data |
| `make transform` | You changed cleaning logic and want to reprocess |

> **Pro tip:** If you fix a bug in `transformer.py`, you only need
> to run `make transform` — no need to hit the website again.
> If you fix a bug in `parser.py` or `scraper.py`, you must
> run `make run` or `make extract` to refresh the checkpoint.

---

## Running Tests

```bash
make test
```

---

## Configuration

All settings are controlled via `config/settings.yaml`:

```yaml
scraper:
  base_url: "https://ukbusinessportal.co.uk"
  categories_path: "/businesses/"
  delay_seconds: 3        # Pause between requests — be polite!
  timeout_seconds: 10     # How long to wait for a page to load
  headers:
    User-Agent: "DataCo-WebScraper/1.0 (educational project)"

output:
  raw_directory: "data/raw"
  processed_directory: "data/processed"
  filename: "business_listings.csv"

logging:
  level: "INFO"
  file: "logs/scraper.log"
```

**Key settings to adjust:**

| Setting | Purpose | Default |
|---|---|---|
| `delay_seconds` | Pause between requests | `3` |
| `timeout_seconds` | Max wait per page | `10` |
| `filename` | Output CSV filename | `business_listings.csv` |

---

## Data Output

The pipeline produces two output files in `data/processed/`:

| File | Format | Intended for |
|---|---|---|
| `business_listings.csv` | CSV | Technical users, databases, further processing |
| `business_listings.xlsx` | Excel | Non-technical business users |

Both files contain the following columns:

| Column | Description | Empty value |
|---|---|---|
| `category` | Business category | — |
| `business_name` | Registered business name | — |
| `address` | Full office address | `Not Listed` |
| `phone_number` | Contact number(s) — multiple separated by ` \| ` | `Not Listed` |
| `email_address` | Contact email address | `Not Listed` |
| `website` | Business website URL | `Not Listed` |
| `business_url` | Link to full business page on UK Business Portal | — |

> Phone numbers in the Excel file are explicitly formatted as
> text — leading zeros are preserved when the file is opened
> directly in Excel.
>
> Missing values appear as `"Not Listed"` — indicating the
> business exists but has not published that information.

---

## Best Practices & Ethics

This scraper is built with responsible scraping principles:

- ✅ Verified `robots.txt` — entire site permitted for crawling
- ✅ Adds a 3 second delay between every request
- ✅ Identifies itself honestly via a User-Agent header
- ✅ Only collects publicly available data
- ✅ Does not collect personal or private information
- ✅ Complies with website terms of service
- ✅ Checkpoints raw data to avoid unnecessary re-scraping

---

## Contributing

**Step 1:** Create a new branch:

```bash
git checkout -b feature/your-feature-name
```

**Step 2:** Make your changes.

**Step 3:** Run tests and linter:

```bash
make test
make lint
```

**Step 4:** Push and open a Pull Request.

> All code must pass `make lint` and `make test` before
> a Pull Request will be reviewed.

---

*Built with ❤️ at DataCo — Data is everywhere. We help you harness it.*