import requests
import json

BASE_URL = "https://fantasy.premierleague.com/api/"

print("🔄 Fetching latest FPL data...")

# =========================
# 1️⃣ Bootstrap (players, prices, teams, events)
# =========================
bootstrap = requests.get(BASE_URL + "bootstrap-static/").json()

with open("bootstrap.json", "w") as f:
    json.dump(bootstrap, f)

print("✅ bootstrap.json updated")

# =========================
# 2️⃣ Fixtures
# =========================
fixtures = requests.get(BASE_URL + "fixtures/").json()

with open("fixtures.json", "w") as f:
    json.dump(fixtures, f)

print("✅ fixtures.json updated")

# =========================
# 3️⃣ Detect current Gameweek
# =========================
current_gw = None
for event in bootstrap["events"]:
    if event["is_current"]:
        current_gw = event["id"]
        break

if current_gw is None:
    raise Exception("❌ Could not detect current gameweek")

with open("current_gw.txt", "w") as f:
    f.write(str(current_gw))

print(f"📅 Current Gameweek: {current_gw}")

print("🚀 FPL data refresh complete")

