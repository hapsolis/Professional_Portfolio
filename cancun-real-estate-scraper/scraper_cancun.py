"""
Day 93 - Professional Portfolio Project
Cancún Residential Properties Scraper

Uses undetected-chromedriver to bypass Cloudflare 403 errors.
"""

import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from datetime import datetime

# ========================= CONSTANTS =========================


SEARCH_URL = "https://www.inmuebles24.com/casas-en-venta-en-cancun.html"
EXCLUDE_KEYWORDS = ["hotel", "remate", "lote", "terreno", "local", "bodega"]
MAX_PRICE_MXN = 8_000_000
USD_TO_MXN_RATE = 18.5
MAX_PAGES = 3  # Testing porpoises
OUTPUT_CSV = "cancun_residential_properties.csv"




def clean_price(price_text: str) -> float | None:
    """
    Handles USD to MXN conversion.

    Args:
        price_text (str): Raw price text scraped from the site.
            Examples: "USD 250,000", "$ 3,500,000 MXN", "Desde $1,200,000"

    Returns:
        float | None: Price converted to Mexican Pesos (MXN) as a float.
            Returns None if price_text is empty or cannot be parsed to a number.
            Returns raw numeric value if currency cannot be determined.

    Conversion logic:
        1. Strips all characters except digits and decimal points.
        2. If "USD" appears in text, multiplies by USD_TO_MXN_RATE.
        3. If value < 1,000,000 and "$" appears, assumes USD and converts.
        4. Otherwise, assumes the value is already in MXN.
    """
    if not price_text: return None

    # Any character that is NOT a digit and NOT a period
    numeric_string = re.sub(r'[^\d.]', '', string= price_text)

    try:
        value = float(numeric_string)

        # Price < 1M with a $ sign → assumes USD because no house in Cancún costs $500K MXN
        if "USD" in price_text.upper() or (value < 1000000 and "$" in price_text):
            return value * USD_TO_MXN_RATE

        return value

    except ValueError:
        return None




def main():
    print("🚀 Initializing Stealth Browser...")

    # Configure Chrome options
    options = uc.ChromeOptions()
    # options.add_argument('--headless') # Uncomment this to run without a visible window

    # Chose undetected_chromedriver over requests due to Cloudflare bot protection returning 403 on standard HTTP clients.
    driver = uc.Chrome(options=options, version_main=147)

    all_data = []

    try:

        for page in range(1, MAX_PAGES + 1):


            url = f"{SEARCH_URL}?page={page}" if page > 1 else SEARCH_URL
            print(f"🔍 Visiting Page {page}...")

            driver.get(url)

            # Random sleep to mimic human reading time
            time.sleep(5)

            # Get the page source after JS has executed, lxml is significantly faster than the built-in html.parser
            soup = BeautifulSoup(markup=driver.page_source, features='lxml')

            # Inmuebles24 specific card selector
            cards = soup.find_all("div", {"data-to-posting": True})

            if not cards:
                print("⚠️ Still no cards found. Check if a CAPTCHA appeared in the browser window.")
                break

            for card in cards:

                title_tag = card.find(class_=re.compile(pattern="posting-location|location", flags=re.IGNORECASE))
                title = title_tag.get_text(strip=True) if title_tag else "N/A"

                price_tag = card.find(class_=re.compile("price", re.IGNORECASE))
                price_raw = price_tag.get_text(strip=True) if price_tag else ""

                price_mxn = clean_price(price_raw)  # <=== Helper Function

                link_tag = card.find("a", href=True)
                # When BeautifulSoup finds a tag it stores all the attributes (like href, class, id, data-qa) in a dictionary-like object
                link = link_tag['href'] if link_tag else ""

                #  Checks if the link is a full address or a relative one
                if link and not link.startswith("http"):
                    link = "https://www.inmuebles24.com" + link


                if price_mxn:
                    all_data.append({
                        "title": title,
                        "price_mxn": price_mxn,
                        "url": link,
                        "scraped_at": datetime.now().strftime("%Y-%m-%d")
                    })



        # --- DATA CLEANING ---
        # Acts on the possibility of having and empty dataframe
        if all_data:

            df = pd.DataFrame(all_data)
            df = df.drop_duplicates(subset=['url'])
            # Filter the dataframe from rows with higher prices
            df = df[df['price_mxn'] <= MAX_PRICE_MXN]

            # The method .str.contains() in Pandas is built on top of the re module so it recognizes "|" as "or"
            pattern = '|'.join(EXCLUDE_KEYWORDS)
            # ~ (NOT) contains the keywords on the title
            df = df[~df['title'].str.contains(pat=pattern, case=False, na=False)]

            df.to_csv(filepath=OUTPUT_CSV, index=False, encoding='utf-8-sig')
            print(f"\n✅ Success! {len(df)} properties saved to {OUTPUT_CSV}")

        else:
            print("❌ No data collected.")

    finally:
        #  shut down the Selenium WebDriver session.
        driver.quit()

if __name__ == "__main__":
    main()