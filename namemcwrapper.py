import time
import cloudscraper
from bs4 import BeautifulSoup
import random

BASE_URL = "https://namemc.com/profile/"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
]

ACCEPT_LANGS = [
    "en-US,en;q=0.9",
    "en-GB,en;q=0.8",
    "en;q=0.7",
    "en-US,en;q=0.9,fr;q=0.8",
    "en-US,en;q=0.9,de;q=0.8",
]

def randomHeaders():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": random.choice(ACCEPT_LANGS),
        "Referer": "https://namemc.com/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

scraper = cloudscraper.create_scraper()  # handles Cloudflare
scraper.get("https://namemc.com")  # warm up session

def get_profile(username: str):
    time.sleep(random.uniform(1, 3))  # 1–3 second delay
    url = f"{BASE_URL}{username}"
    res = scraper.get(url, headers=randomHeaders())
    if res.status_code != 200:
        raise Exception(f"Failed to fetch profile ({res.status_code})")

    soup = BeautifulSoup(res.text, "html.parser")

    # --- Username history ---
    usernames = []
    for row in soup.select("table.table-borderless tbody tr"):
        name_tag = row.select_one("td.text-nowrap a")
        if name_tag:
            usernames.append(name_tag.text.strip())

    # --- Capes ---
    capes = []
    for cape in soup.select("div[style*='text-align: center;'] a[href*='/cape/']"):
        title = cape.get("title", "Unknown Cape")
        href = cape.get("href", "")
        cape_id = href.split("/")[-1] if href else None
        capes.append({
            "name": title,
            "cape_id": cape_id,
            "url": f"https://namemc.com{href}" if href else None
        })

    return {
        "username": username,
        "history": usernames,
        "capes": capes
    }

# Example
if __name__ == "__main__":
    from pprint import pprint
    profile = get_profile("goldenGR")
    pprint(profile)
