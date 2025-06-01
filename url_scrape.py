from playwright.sync_api import sync_playwright
import csv
import time
import os
import re
import random

YEARS = ["2005"]
TARGET_CATEGORIES = ["Coil Spring", "Shock / Strut", "Shock / Strut Mount", "Suspension Kit"]
OUTPUT_FILE = f"rockauto_allmakes_suspension_urls_ALL.csv"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:121.0) Gecko/20100101 Firefox/121.0",
    # Add more real user agents if you want
]

def wait(short=False):
    if short:
        time.sleep(random.uniform(1, 3))
    else:
        time.sleep(random.uniform(5, 12))

CATEGORY_WORDS = {
    "Brake", "Hub", "System", "Drivetrain", "Electrical", "Connector",
    "Exhaust", "Emission", "Fuel", "Air", "Heat", "Cooling", "Wheel",
    "Body", "Lighting", "Steering", "Transfer Case", "Differential"
}
def looks_like_category(name):
    name_up = name.upper()
    if " & " in name or any(word.upper() in name_up for word in CATEGORY_WORDS):
        return True
    return False

def is_year_string(s):
    return s.isdigit() and 1900 <= int(s) <= 2100

ENGINE_PATTERN = re.compile(r"^\d+\.\d+[lLvV]")
EXTRA_EXCLUDE = {
    "Ignition", "Transmission", "Transmission-Automatic",
    "Transmission-Manual", "Engine"
}

def uncheck_2005_checkbox(page):
    for cb in page.query_selector_all('input[type="checkbox"]'):
        label = cb.evaluate('el => el.nextSibling && el.nextSibling.textContent')
        if label and "<2005" in label:
            if cb.is_checked():
                cb.click()
                wait(short=True)
            break

def get_last_completed_key(output_file):
    if not os.path.exists(output_file):
        return None
    with open(output_file, "r", encoding="utf-8") as f:
        rows = list(csv.reader(f))
        if len(rows) < 2:
            return None
        last = rows[-1]
        return tuple(last[:5])

def detect_block(page):
    content = page.content()
    if "Access Denied" in content or "verify you are human" in content or "blocked" in content.lower():
        print("\n🚨 Blocked or Captcha detected. Stopping script.")
        return True
    return False

write_header = not os.path.exists(OUTPUT_FILE)
LAST_DONE = get_last_completed_key(OUTPUT_FILE)
passed_last_done = False if LAST_DONE else True

start_time = time.time()
try:
    with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["Year", "Make", "Model", "Engine", "Subcategory", "URL"])

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            user_agent = random.choice(USER_AGENTS)
            page = browser.new_page(user_agent=user_agent)
            page.goto("https://www.rockauto.com/en/catalog")
            wait()

            if detect_block(page):
                browser.close()
                exit()

            make_links = [ml for ml in page.query_selector_all("a.navlabellink") if ml.inner_text().strip() and not ml.inner_text().strip().isdigit()]
            all_makes = [ml.inner_text().strip() for ml in make_links]
            makes_set = set(all_makes)
            YEARS_SET = set(YEARS)
            EXCLUDE_WORDS = {"Engine", "Suspension", "Transmission", "Transfer Case", "Differential"}

            for make in all_makes:
                for year in YEARS:
                    if not passed_last_done:
                        if (year, make) < (LAST_DONE[0], LAST_DONE[1]):
                            continue
                        if (year, make) > (LAST_DONE[0], LAST_DONE[1]):
                            passed_last_done = True
                    page.goto("https://www.rockauto.com/en/catalog")
                    wait()
                    if detect_block(page):
                        browser.close()
                        exit()

                    make_link = page.locator(f'a.navlabellink:has-text("{make}")').first
                    if not make_link or not make_link.is_visible():
                        continue
                    print(f"\n=== Scraping Make: {make} ===")
                    make_link.click()
                    wait(short=True)
                    if detect_block(page):
                        browser.close()
                        exit()

                    year_link = page.locator(f'a.navlabellink:has-text("{year}")').first
                    if not year_link or not year_link.is_visible():
                        print(f"  No year {year} for {make}. Skipping...")
                        continue
                    year_link.click()
                    wait(short=True)
                    if detect_block(page):
                        browser.close()
                        exit()

                    uncheck_2005_checkbox(page)

                    model_links = [ml for ml in page.query_selector_all("a.navlabellink") if ml.inner_text().strip()]
                    model_names = [ml.inner_text().strip() for ml in model_links]
                    filtered_models = [
                        m for m in model_names
                        if not looks_like_category(m)
                        and m not in makes_set
                        and not is_year_string(m)
                        and not ENGINE_PATTERN.match(m)
                        and m not in EXTRA_EXCLUDE
                        and m not in YEARS_SET
                        and m not in EXCLUDE_WORDS
                        and not m.isdigit()
                    ]
                    if not filtered_models:
                        print(f"  No real models for {make} {year}. Skipping...")
                        continue

                    for model in filtered_models:
                        if not passed_last_done:
                            if (year, make, model) < (LAST_DONE[0], LAST_DONE[1], LAST_DONE[2]):
                                continue
                            if (year, make, model) > (LAST_DONE[0], LAST_DONE[1], LAST_DONE[2]):
                                passed_last_done = True
                        page.goto("https://www.rockauto.com/en/catalog")
                        wait()
                        if detect_block(page):
                            browser.close()
                            exit()
                        page.locator(f'a.navlabellink:has-text("{make}")').first.click()
                        wait(short=True)
                        page.locator(f'a.navlabellink:has-text("{year}")').first.click()
                        wait(short=True)
                        uncheck_2005_checkbox(page)
                        model_link = page.locator(f'a.navlabellink:has-text("{model}")').first
                        if not model_link or not model_link.is_visible():
                            continue
                        print(f"  Year: {year} | Model: {model}")
                        model_link.click()
                        wait(short=True)
                        if detect_block(page):
                            browser.close()
                            exit()

                        engine_links = [
                            e for e in page.query_selector_all("a.navlabellink")
                            if e.is_visible() and (
                                re.search(r"\d+\.\d+\s*[lvLV]", e.inner_text())
                                or "engine" in e.inner_text().lower()
                            )
                        ]
                        engine_names = [e.inner_text().strip() for e in engine_links]

                        if engine_names:
                            for engine in engine_names:
                                if not passed_last_done:
                                    if (year, make, model, engine) < (LAST_DONE[0], LAST_DONE[1], LAST_DONE[2], LAST_DONE[3]):
                                        continue
                                    if (year, make, model, engine) > (LAST_DONE[0], LAST_DONE[1], LAST_DONE[2], LAST_DONE[3]):
                                        passed_last_done = True
                                page.goto("https://www.rockauto.com/en/catalog")
                                wait()
                                if detect_block(page):
                                    browser.close()
                                    exit()
                                page.locator(f'a.navlabellink:has-text("{make}")').first.click()
                                wait(short=True)
                                page.locator(f'a.navlabellink:has-text("{year}")').first.click()
                                wait(short=True)
                                uncheck_2005_checkbox(page)
                                page.locator(f'a.navlabellink:has-text("{model}")').first.click()
                                wait(short=True)
                                engine_link = page.locator(f'a.navlabellink:has-text("{engine}")').first
                                if not engine_link or not engine_link.is_visible():
                                    continue
                                engine_link.click()
                                wait(short=True)
                                if detect_block(page):
                                    browser.close()
                                    exit()
                                susp_link = page.locator('a.navlabellink:has-text("Suspension")')
                                if not susp_link or not susp_link.is_visible():
                                    continue
                                susp_link.click()
                                wait(short=True)
                                for link in page.query_selector_all('a.navlabellink'):
                                    text = link.inner_text().strip()
                                    if text in TARGET_CATEGORIES and link.is_visible():
                                        if not passed_last_done:
                                            if (year, make, model, engine, text) == LAST_DONE:
                                                passed_last_done = True
                                                continue
                                            else:
                                                continue
                                        href = link.get_attribute("href")
                                        if href:
                                            url = f"https://www.rockauto.com{href}"
                                            print(f"    Engine: {engine} | {text}: {url}")
                                            writer.writerow([year, make, model, engine, text, url])
                                            f.flush()
                        else:
                            engine = "SINGLE_ENGINE"
                            susp_link = page.locator('a.navlabellink:has-text("Suspension")')
                            if not susp_link or not susp_link.is_visible():
                                continue
                            susp_link.click()
                            wait(short=True)
                            for link in page.query_selector_all('a.navlabellink'):
                                text = link.inner_text().strip()
                                if text in TARGET_CATEGORIES and link.is_visible():
                                    if not passed_last_done:
                                        if (year, make, model, engine, text) == LAST_DONE:
                                            passed_last_done = True
                                            continue
                                        else:
                                            continue
                                    href = link.get_attribute("href")
                                    if href:
                                        url = f"https://www.rockauto.com{href}"
                                        print(f"    [No engine select] {text}: {url}")
                                        writer.writerow([year, make, model, engine, text, url])
                                        f.flush()
            browser.close()
finally:
    elapsed = time.time() - start_time
    minutes, seconds = divmod(int(elapsed), 60)
    print(f"\n⏱️ Script finished. Total time: {minutes}m {seconds}s")
