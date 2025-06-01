from playwright.sync_api import sync_playwright
import csv
import time
import os
import random

INPUT_FILE = "rockauto_allmakes_suspension_urls_ALL.csv"
OUTPUT_FILE = "rockauto_suspension_parts.csv"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:121.0) Gecko/20100101 Firefox/121.0",
]

def wait():
    time.sleep(random.uniform(3, 9))

def detect_block(page):
    content = page.content().lower()
    if "access denied" in content or "verify you are human" in content or "blocked" in content:
        print("\n🚨 Blocked or Captcha detected. Stopping script.")
        return True
    return False

def find_resume_index(input_rows, output_rows):
    # If no output rows, start from 0
    if not output_rows:
        return 0
    last_done = output_rows[-1][:5]  # only compare first 5 fields (Year, Make, Model, Engine, Subcategory)
    for idx, row in enumerate(input_rows):
        if row[:5] == last_done:
            return idx + 1  # resume at the next row
    return 0

start_time = time.time()
try:
    # Read all rows from input (excluding header)
    with open(INPUT_FILE, "r", encoding="utf-8") as fin:
        input_reader = list(csv.reader(fin))
        input_header = input_reader[0]
        input_rows = input_reader[1:]

    # Read all rows from output (excluding header)
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as fout:
            output_reader = list(csv.reader(fout))
            output_header = output_reader[0]
            output_rows = output_reader[1:]
    else:
        output_rows = []

    # Find where to resume
    resume_idx = find_resume_index(input_rows, output_rows)

    # Open output for appending
    with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as fout:
        writer = csv.writer(fout)
        # Write header if file is new
        if os.stat(OUTPUT_FILE).st_size == 0:
            writer.writerow(["Year", "Make", "Model", "Engine", "Subcategory", "Part Number", "Manufacturer", "Price"])

        with sync_playwright() as p:
            user_agent = random.choice(USER_AGENTS)
            browser = p.chromium.launch(headless=False)
            page = browser.new_page(user_agent=user_agent)

            for idx, row in enumerate(input_rows):
                if idx < resume_idx:
                    continue  # skip already processed

                year, make, model, engine, subcat, url = row[:6]
                print(f"\n🌐 {year} {make} {model} {engine} {subcat} - {url}")
                try:
                    page.goto(url, timeout=60000)
                    wait()
                    if detect_block(page):
                        browser.close()
                        exit()
                except Exception as e:
                    print(f"  ❌ Failed to load {url}: {e}")
                    writer.writerow([year, make, model, engine, subcat, "", "", "LOAD ERROR"])
                    fout.flush()
                    continue

                part_numbers = page.query_selector_all("span.listing-final-partnumber")
                brands = page.query_selector_all("span.listing-final-manufacturer")
                prices = page.query_selector_all("span[id^='dprice']")
                n_parts = min(len(part_numbers), len(brands), len(prices))
                if n_parts == 0:
                    writer.writerow([year, make, model, engine, subcat, "", "", "NO PARTS FOUND"])
                    fout.flush()
                else:
                    for i in range(n_parts):
                        part = part_numbers[i].inner_text().strip()
                        brand = brands[i].inner_text().strip()
                        price = prices[i].inner_text().strip()
                        writer.writerow([year, make, model, engine, subcat, part, brand, price])
                        fout.flush()

            browser.close()
finally:
    elapsed = time.time() - start_time
    minutes, seconds = divmod(int(elapsed), 60)
    print(f"\n⏱️ Script finished. Total time: {minutes}m {seconds}s")
