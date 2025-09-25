import requests
from datetime import datetime
from namemcwrapper import get_profile   # your scraper/wrapper
import re

# -------------------
# Config
# -------------------

specialDicti = {
    "notch",
    "herobrine",
    "steve",
    "Dl0ze" # easter egg, will never trigger
}

cape_values = {
    "Migrator": 9,          
    "15th Anniversary": 15,
    "Pan": 0, # worthless
    "Vanilla":18,
    "Cherry Blossom": 19,
    "Purple Heart": 5,
    "Follower’s": 55,
    "Common": 0.50,
    "Menace": 0.99,
    "Mojang Office": 17,
    "Home": 0.95,
    "Yearn": 22,
    "MCC 15th Year": 26,
    "Founder’s": 33,
    "Minecraft Experience": 35,
    "MineCon 2016": 2979,
    "MineCon 2015": 3999,
    "MineCon 2013": 4499,
    "MineCon 2012": 4749,
    "MineCon 2011": 4999,
    "Realms Mapmaker": 5100,
    "Mojang": 35000,
    "Mojang Studios": 25000,
    "Translator": 50000,
    "Mojira Moderator": 50700,
    "Mojang (Classic)": 72000,
    "Cobalt": 85000,
    "Scrolls": 90000,
    "Translator (Chinese)": 100000,
    "Turtle": 100000,
    "Test": 150000,
    "Valentine": 100000,
    "Birthday": 100000,
    "dB": 100000,
    "Millionth Customer": 100000,
    "Oxeye": 150000,
    "Prismarine": 100000,
    "Snowman": 100000,
    "Spade": 100000,
    "Translator (Japanese)": 100000
}


HYPX_API_KEY = "af9b6562-8712-4883-aad7-e0196a336e0a"

# -------------------
# Helpers
# -------------------

def get_uuid(username):
    res = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{username}")
    if res.status_code != 200:
        return None
    return res.json()["id"]

def get_creation_date(uuid, username):
    res = requests.get(f"https://gadgets.faav.top/namemc-info/{uuid}?url=https://namemc.com/profile/{username}")
    html = res.text

    # Use regex to extract creationDate
    match = re.search(r'"creationDate":\s*"([\d-]+)"', html)
    if match:
        creation_date = match.group(1)
        return(creation_date)
    else:
        return None

def english_word(username):
    res = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{username}")
    return res.status_code == 200

def get_hypixel(uuid):
    res = requests.get(f"https://api.hypixel.net/player?uuid={uuid}&key={HYPX_API_KEY}")
    if res.status_code != 200:
        return None
    return res.json()["player"]

# -------------------
# Main calculation
# -------------------

def calculate(username):
    worth = 0
    notes = []
    profile = get_profile(username)

    uuid = get_uuid(username)
    if not uuid:
        raise Exception("Invalid username")

    # Step 1
    if username.lower() in specialDicti:
        worth += 500
        notes.append("Special dictionary match (+500)")
    else:
        # Step 2
        if english_word(username):
            worth += 300
            notes.append("English dictionary word (+300)")

    # Step 3 creation date
    creation_date = get_creation_date(uuid, username)
    if creation_date:
        years = datetime.now().year - int(creation_date[:4])
        yearly_bonus = int(years ** 1.5)
        worth += yearly_bonus
        notes.append(f"Account age bonus (+{yearly_bonus})")
    else:
        notes.append("Missing creation date (no bonus)")

    # Step 4 username changes
    history = profile.get("history", [])
    changes = len(history) - 1
    if changes > 0:
        worth -= 5 * changes
        notes.append(f"Username changes penalty (-{5*changes})")
    else:
        notes.append(f"No username changes (+-0)")

    # Step 5 + 6 capes
    capes = profile.get("capes", [])
    worth += 2 * len(capes)
    notes.append(f"Cape count bonus (+{2*len(capes)})")

    # Step 7 named cape values
    for cape in capes:
        cape_name = cape.get("name")
        if cape_name in cape_values:
            worth += cape_values[cape_name]
            notes.append(f"{cape_name} cape bonus (+{cape_values[cape_name]})")

    # Step 8 Hypixel bans
    hyp = get_hypixel(uuid)
    if hyp:
        if hyp.get("banned", False):
            worth -= 1
            notes.append("Hypixel ban (-1)")
        else:
            worth += 1
            notes.append("Good Hypixel standing (+1)")

    # Step 9 Hypixel ranks
    if hyp and "newPackageRank" in hyp:
        rank = hyp["newPackageRank"]
        rank_value = 8.67  # arbitrary
        worth += int(rank_value / 2.3)
        notes.append(f"Hypixel rank {rank} (+{int(rank_value/2.3)})")

    return worth, notes


# -------------------
# Run
# -------------------

if __name__ == "__main__":
    username = input("Username to calculate price: ")
    try:
        worth, notes = calculate(username)
        print(f"\nFinal worth for {username}: ${worth}")
        print("Details:")
        for n in notes:
            print(" -", n)
    except Exception as e:
        print("Error:", e)
