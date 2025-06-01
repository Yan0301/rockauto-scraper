# RockAuto Suspension Parts Scraper

A robust, fully-resumable two-stage Python scraping toolkit (using Playwright) to collect suspension part data for any make/model/year from RockAuto’s online catalog. All output is in clean CSV format and anti-blocking logic is included.

---

## Workflow Overview

**1. Stage 1:**
Use `url_scrape.py` to crawl RockAuto’s catalog and collect all URLs for suspension parts, by year/make/model/engine/subcategory.

**2. Stage 2:**
Run `main.py` to visit each collected URL and extract all available part numbers, brands, and prices.

This two-step process is robust for large catalogs and lets you resume either step at any point.

---

## Features

* **Fully automated:** Scrapes all relevant RockAuto pages for specified years, makes, models, and categories.
* **Two-stage design:** Decouples URL discovery and part data scraping for speed and flexibility.
* **Resumable:** Both steps can safely resume from where they left off, no lost progress.
* **Anti-blocking:** Random wait times, User-Agent rotation, and error detection built-in.
* **CSV output:** Data is always saved in CSV, ready for further analysis.
* **Easy to adapt:** Change target categories or years with simple config changes.

---

## Requirements

* Python 3.8+
* [Playwright](https://playwright.dev/python/)
* pandas

Install all dependencies with:

```bash
pip install -r requirements.txt
```

Set up Playwright browsers (if you haven't yet):

```bash
playwright install
```

---

## Usage

### 1. **Collect URLs from RockAuto**

Run the URL collector:

```bash
python url_scrape.py
```

This will create `rockauto_allmakes_suspension_urls_ALL.csv`
Each row contains:
\| Year | Make | Model | Engine | Subcategory | URL |

---

### 2. **Scrape Parts Data**

Run the main scraper to extract part data from the collected URLs:

```bash
python main.py
```

This will generate `rockauto_suspension_parts.csv`
Each row contains:
\| Year | Make | Model | Engine | Subcategory | Part Number | Manufacturer | Price |

---

## Output Format

* **URL CSV:** All jobs to be scraped, one per row.
* **Parts CSV:** One row per part found, or clearly labeled as “NO PARTS FOUND” / “LOAD ERROR”.

---

## Troubleshooting

* **Getting blocked or banned?**
  Slow down waits or change your IP (VPN, etc.).
* **Want to resume?**
  Both scripts automatically pick up where they left off based on the output files.
* **Want to start from a specific row?**
  Remove all later rows from your output CSV and rerun.

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Disclaimer

This project is for educational and personal research use only. Please respect RockAuto’s terms of service and scrape responsibly.

---

## Credits

Project by [Yan0301](https://github.com/Yan0301).
Powered by Playwright and the open source Python community.
