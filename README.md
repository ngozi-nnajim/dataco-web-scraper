# DataCo Web Scraper 🌐

> Automated web scraping pipeline for collecting and structuring 
> business listing data from public sources.

Built by a Data Engineer at **DataCo** — a data collection firm 
specialising in automated web data collection to empower businesses 
with real-time, accurate, and actionable insights.

---

## Table of Contents

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
[UK Business Portal](https://ukbusinessportal.co.uk/) and structures
it into clean, analysis-ready CSV files.

**Data points collected:**
- Business names
- Business addresses
- Business phone numbers

**Tech stack:**
- Python 3.10+
- BeautifulSoup4 (HTML parsing)
- Requests (HTTP)
- Pandas (data structuring)

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

```text
Step 1 → Identify target website and categories
Step 2 → Inspect page structure (HTML tags)
Step 3 → Scrape raw HTML from target pages
Step 4 → Parse and extract required data points
Step 5 → Clean and transform extracted data
Step 6 → Save structured output to CSV
```

---

## Project Structure

```
dataco-web-scraper/
├── config/             → Settings and configuration
├── data/
│   ├── raw/            → Untouched scraped data
│   └── processed/      → Cleaned, analysis-ready output
├── logs/               → Runtime logs and error records
├── notebooks/          → Exploration and analysis notebooks
├── src/
│   └── dataco_web_scraper/
│       ├── scraper.py      → Fetches web pages
│       ├── parser.py       → Extracts data from HTML
│       ├── transformer.py  → Cleans and structures data
│       └── pipeline.py     → Orchestrates all steps
├── tests/              → Automated tests
├── .env.example        → Secrets template
├── Makefile            → Command shortcuts
└── pyproject.toml      → Project dependencies
```

---

## Quick Start

> For non-technical users — run the scraper in three steps.

**Step 1:** Make sure Python 3.10+ is installed on your machine.

**Step 2:** Open your terminal, navigate to this folder, and run:
```bash
make install
```

**Step 3:** Run the scraper:
```bash
make run
```

Your output CSV file will appear in `data/processed/`.

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

## Running the Scraper

```bash
make run
```

Or directly:
```bash
python -m src.dataco_web_scraper.pipeline
```

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
  target_url: "https://ukbusinessportal.co.uk/"
  delay_seconds: 5

output:
  format: "csv"
  directory: "data/processed"
```

Adjust `delay_seconds` to control how politely the scraper 
behaves toward the target website.

---

## Data Output

Processed data is saved to `data/processed/` as a CSV file with 
the following columns:

| Column | Description |
|---|---|
| `business_name` | Name of the business |
| `address` | Full business address |
| `phone_number` | Contact phone number |

---

## Best Practices & Ethics

This scraper is built with responsible scraping principles:

- ✅ Respects `robots.txt`
- ✅ Adds delays between requests
- ✅ Only collects publicly available data
- ✅ Does not collect personal or private information
- ✅ Complies with website terms of service

---

## Contributing

1. Create a new branch:
```bash
git checkout -b feature/your-feature-name
```
2. Make your changes
3. Run tests: `make test`
4. Run linter: `make lint`
5. Push and open a Pull Request

---

*Built with ❤️ at DataCo — Data is everywhere. We help you harness it.*