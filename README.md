# RockAuto Suspension Parts Scraper

A robust, fully-resumable Python scraper using Playwright that extracts suspension part data (brand, part number, manufacturer, price, etc.) for any make/model/year from RockAuto’s online catalog. Output is CSV-friendly and anti-blocking logic is included.

---

## Features

* **Automated scraping** of suspension parts for all years, makes, models, and engines available on RockAuto.
* **Resumable**: Picks up exactly where it left off, so you never repeat or miss a row.
* **Anti-blocking**: Random wait times and human-like behavior help avoid bans.
* **CSV Output**: Cleanly formatted results, ready for analysis or price comparison.
* **Error Handling**: Marks failed or empty pages so you can review them later.
* **Easy to run and modify** for other RockAuto categories.

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

1. **Clone this repository:**

   ```bash
   git clone https://github.com/Yan0301/rockauto-scraper.git
   cd rockauto-scraper
   ```

2. **Prepare your input file:**

   Place your `rockauto_allmakes_suspension_urls_ALL.csv` in the repo folder.

3. **Run the scraper:**

   ```bash
   python main.py
   ```

   * The script will automatically resume where it last stopped.
   * Output will be written to `rockauto_suspension_parts.csv`.

---

## Output Format

Each row of the CSV contains:

| Year | Make | Model | Engine | Subcategory | Part Number | Manufacturer | Price |
| ---- | ---- | ----- | ------ | ----------- | ----------- | ------------ | ----- |
| ...  | ...  | ...   | ...    | ...         | ...         | ...          | ...   |

Rows with no parts found or load errors are clearly labeled.

---

## Troubleshooting

* **Getting blocked or banned?**

  * Slow down the scrape or try from a new IP.
* **Resuming isn’t working?**

  * Ensure you’re not editing the output CSV while running.
  * The script resumes based on the output file's last row.
* **Need to start from a specific row?**

  * Remove all rows after your desired resume point from the output CSV, then restart the script.

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Disclaimer

This project is intended for educational and personal research use only. Please respect RockAuto’s terms of service and scrape responsibly.

---

## Credits

Project by [Yan0301](https://github.com/Yan0301).
Big thanks to Playwright and the open source Python community!
