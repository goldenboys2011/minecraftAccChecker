from flask import Flask, request, jsonify, send_from_directory, Response
import os
from flask_cors import CORS
from datetime import datetime
import requests, re
from namemcwrapper import get_profile
import json
import base64

app = Flask(__name__, static_folder="static")
CORS(app)
# -------------------
# Config
# -------------------
specialDicti = {"notch", "herobrine", "steve", "Dl0ze"} #Dl0ze is now easter egg as it will never 

cape_values = {
    "Migrator": 9, "15th Anniversary": 15, "Pan": 0,
    "Vanilla":18, "Cherry Blossom": 19, "Purple Heart": 5,
    "Follower’s": 55, "Common": 0.50, "Menace": 0.99,
    "Mojang Office": 17, "Home": 0.95, "Yearn": 22,
    "MCC 15th Year": 26, "Founder’s": 33, "Minecraft Experience": 35,
    "MineCon 2016": 2979, "MineCon 2015": 3999, "MineCon 2013": 4499,
    "MineCon 2012": 4749, "MineCon 2011": 4999, "Realms Mapmaker": 5100,
    "Mojang": 35000, "Mojang Studios": 25000, "Translator": 50000,
    "Mojira Moderator": 50700, "Mojang (Classic)": 72000,
    "Cobalt": 85000, "Scrolls": 90000, "Translator (Chinese)": 100000,
    "Turtle": 100000, "Test": 150000, "Valentine": 100000,
    "Birthday": 100000, "dB": 100000, "Millionth Customer": 100000,
    "Oxeye": 150000, "Prismarine": 100000, "Snowman": 100000,
    "Spade": 100000, "Translator (Japanese)": 100000
}

HYPX_API_KEY = "75a5343b-23a6-44d3-928b-4838b5364364"

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
    match = re.search(r'"creationDate":\s*"([\d-]+)"', res.text)
    return match.group(1) if match else None

def english_word(username):
    res = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{username}")
    return res.status_code == 200

def get_hypixel(uuid):
    res = requests.get(f"https://api.hypixel.net/player?uuid={uuid}&key={HYPX_API_KEY}")
    return res.json().get("player") if res.status_code == 200 else None

# -------------------
# Main calculation
# -------------------
def calculate(username):
    worth = 0
    notes = []
    warnings = []
    details = []

    profile = get_profile(username)
    uuid = get_uuid(username)
    if not uuid:
        return {"error": "Invalid username"}

    if len(username) <= 3:
        bonus = int(2000 / len(username))
        worth += bonus
        details.append(f"Small username [{len(username)}] ({bonus})")
    # Special dictionary
    if username.lower() in specialDicti:
        worth += 500
        details.append("Special dictionary match (+500)")
    else:
        if english_word(username):
            worth += 300
            details.append("English dictionary word (+300)")

    # Creation date
    creation_date = get_creation_date(uuid, username)
    if creation_date:
        years = datetime.now().year - int(creation_date[:4])
        yearly_bonus = int(years ** 1.5)
        worth += yearly_bonus
        details.append(f"Account age bonus (+{yearly_bonus})")
    else:
        warnings.append("Missing creation date")

    # Username changes
    history = profile.get("history", [])
    changes = len(history) - 1
    if changes > 0:
        worth -= 5 * changes
        details.append(f"Username changes penalty (-{5*changes})")
    else:
        details.append("No username changes")

    # Capes
    capes = profile.get("capes", [])
    worth += 2 * len(capes)
    cape_details = []
    for cape in capes:
        cape_name = cape.get("name")
        bonus = 2
        if cape_name in cape_values:
            bonus += cape_values[cape_name]
            worth += cape_values[cape_name]
        cape_details.append({"name": cape_name, "bonus": bonus})
    details.append(f"Cape count: {len(capes)}")

    # Hypixel
    hyp = get_hypixel(uuid)
    if hyp:
        if hyp.get("banned", False):
            worth -= 1
            warnings.append("Hypixel banned")
        else:
            worth += 1
            details.append("Good Hypixel standing (+1)")
        if "newPackageRank" in hyp:
            rank = hyp["newPackageRank"]
            rank_value = int(8.67/2.3)
            worth += rank_value
            details.append(f"Hypixel rank {rank} (+{rank_value})")
    else:
        warnings.append("Could not fetch Hypixel data")

    return {
        "username": username,
        "worth": worth,
        "warnings": warnings,
        "details": details,
        "capes": cape_details
    }

def getSkinHash(uuid):
    url = f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}"
    res = requests.get(url).json()
    b64_value = res["properties"][0]["value"]
    decoded = json.loads(base64.b64decode(b64_value))
    skin_url = decoded["textures"]["SKIN"]["url"]
    cape_url = decoded["textures"]["CAPE"]["url"]
    return skin_url.split("/")[-1] + "," + cape_url.split("/")[-1]  # just the hash

@app.route("/")
def home():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/tos")
def tos():
    return send_from_directory(app.static_folder, "tos.html")

@app.route("/analyze")
def analyze():
    username = request.args.get("username")
    if not username:
        return jsonify({"error": "Missing username"}), 400

    data = calculate(username)

    # Add skin hash
    uuid = get_uuid(username)
    if uuid:
        hashes = getSkinHash(uuid)
        skin_hash = hashes.split(",")[0]
        cape_hash = hashes.split(",")[1]
        data["hash"] = skin_hash
        data["hashCape"] = cape_hash

    return jsonify(data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)