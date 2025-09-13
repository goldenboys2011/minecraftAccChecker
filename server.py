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
specialDicti = {"notch", "herobrine", "steve", "Dl0ze"}  # Dl0ze easter egg

cape_values = {
    "Migrator": 9, "15th Anniversary": 15, "Pan": 0,
    "Vanilla": 18, "Cherry Blossom": 19, "Purple Heart": 5,
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
    try:
        res = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{username}", timeout=5)
        if res.status_code != 200:
            return {"error": "Invalid username"}
        return {"uuid": res.json()["id"]}
    except Exception as e:
        return {"error": f"Mojang API failed: {str(e)}"}


def get_creation_date(uuid, username):
    try:
        res = requests.get(f"https://gadgets.faav.top/namemc-info/{uuid}?url=https://namemc.com/profile/{username}", timeout=5)
        match = re.search(r'"creationDate":\s*"([\d-]+)"', res.text)
        if match:
            return {"creation_date": match.group(1)}
        return {"error": "No creation date found"}
    except Exception as e:
        return {"error": f"Creation date API failed: {str(e)}"}


def english_word(username):
    try:
        res = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{username}", timeout=5)
        return {"is_word": res.status_code == 200}
    except Exception as e:
        return {"error": f"Dictionary API failed: {str(e)}"}


def get_hypixel(uuid):
    try:
        res = requests.get(f"https://api.hypixel.net/player?uuid={uuid}&key={HYPX_API_KEY}", timeout=5)
        if res.status_code == 200:
            return {"player": res.json().get("player")}
        return {"error": "Invalid Hypixel response"}
    except Exception as e:
        return {"error": f"Hypixel API failed: {str(e)}"}


def getSkinHash(uuid):
    try:
        url = f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}"
        res = requests.get(url, timeout=5).json()
        b64_value = res["properties"][0]["value"]
        decoded = json.loads(base64.b64decode(b64_value))
        skin_url = decoded["textures"]["SKIN"]["url"]
        cape_url = decoded.get("textures", {}).get("CAPE", {}).get("url", "")
        return {"skin_hash": skin_url.split("/")[-1], "cape_hash": cape_url.split("/")[-1] if cape_url else ""}
    except Exception as e:
        return {"error": f"Skin API failed: {str(e)}"}

# -------------------
# Main calculation
# -------------------
def calculate(username):
    worth, warnings, details = 0, [], []

    try:
        profile = get_profile(username)
    except Exception as e:
        return {"error": f"Profile fetch failed: {str(e)}"}

    # UUID
    uuid_data = get_uuid(username)
    if "error" in uuid_data:
        return uuid_data
    uuid = uuid_data["uuid"]

    # Small username bonus
    if len(username) <= 3:
        bonus = int(2000 / len(username))
        worth += bonus
        details.append(f"Small username [{len(username)}] (+{bonus})")

    # Special dict / English word
    if username.lower() in specialDicti:
        worth += 1000
        details.append("Special dictionary match (+1000)")
    else:
        word_data = english_word(username)
        if "error" in word_data:
            warnings.append(word_data["error"])
        elif word_data["is_word"]:
            length = len(username)
            if 6 <= length <= 16:
                bonus = int(600 - ((length - 6) * (300 / 10)))
            elif length < 6:
                bonus = int(700 + ((6 - length) * (300 / 5)))
            else:
                bonus = 200
            worth += bonus
            details.append(f"English dictionary word (+{bonus})")

    # Creation date
    creation_data = get_creation_date(uuid, username)
    if "error" in creation_data:
        warnings.append(creation_data["error"])
    else:
        years = datetime.now().year - int(creation_data["creation_date"][:4])
        yearly_bonus = int((years * 6 + years ** 1.2) if years >= 10 else years ** 1.5)
        worth += yearly_bonus
        details.append(f"Account age bonus (+{yearly_bonus})")

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
    worth += 3 * len(capes)
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
    hyp_data = get_hypixel(uuid)
    if "error" in hyp_data:
        warnings.append(hyp_data["error"])
    else:
        hyp = hyp_data["player"]
        if hyp:
            if hyp.get("banned", False):
                worth -= 1
                warnings.append("Hypixel banned")
            else:
                worth += 1
                details.append("Good Hypixel standing (+1)")
            if "newPackageRank" in hyp:
                rank_value = int(8.67 / 2.3)
                worth += rank_value
                details.append(f"Hypixel rank {hyp['newPackageRank']} (+{rank_value})")

    return {
        "username": username,
        "worth": worth,
        "warnings": warnings,
        "details": details,
        "capes": cape_details
    }

# -------------------
# Routes
# -------------------
@app.route("/")
def home():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/tos")
def tos():
    return send_from_directory(app.static_folder, "tos.html")

@app.route("/api/patchnotes")
def patchNotes():
    with open("patchNotes.json", "r", encoding="utf-8") as f:
        return jsonify(json.load(f))

@app.route("/api/analyze")
def analyze():
    username = request.args.get("username")
    if not username:
        return jsonify({"error": "Missing username"}), 400

    data = calculate(username)
    if "error" in data:
        return jsonify(data), 502  # external API failure

    # Add skin hash
    uuid_data = get_uuid(username)
    if "error" not in uuid_data:
        skin_data = getSkinHash(uuid_data["uuid"])
        if "error" not in skin_data:
            data["hash"] = skin_data["skin_hash"]
            data["hashCape"] = skin_data["cape_hash"]

    return jsonify(data), 200

# -------------------
# Run
# -------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
