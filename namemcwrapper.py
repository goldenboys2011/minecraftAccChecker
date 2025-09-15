import cloudscraper
from bs4 import BeautifulSoup

BASE_URL = "https://namemc.com/profile/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://namemc.com/",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

scraper = cloudscraper.create_scraper()  # handles Cloudflare
scraper.get("https://namemc.com")  # warm up session

def get_profile(username: str):
    url = f"{BASE_URL}{username}"
    res = scraper.get(url, headers=HEADERS)
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
