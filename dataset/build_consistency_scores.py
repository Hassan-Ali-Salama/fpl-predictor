import requests
import pandas as pd

BASE_URL = "https://fantasy.premierleague.com/api/"

bootstrap = requests.get(BASE_URL + "bootstrap-static/").json()
players = bootstrap["elements"]

records = []

for p in players:
    pid = p["id"]
    name = p["web_name"]

    r = requests.get(BASE_URL + f"element-summary/{pid}/")
    if r.status_code != 200:
        continue

    history = pd.DataFrame(r.json()["history"])
    if len(history) == 0:
        continue

    recent = history.tail(6)

    # عدد الجولات اللي فيها 5 نقاط أو أكتر
    consistency = (recent["total_points"] >= 5).sum()

    records.append({
        "player": name,
        "consistency": consistency
    })

df = pd.DataFrame(records)
df.to_csv("player_consistency.csv", index=False)

print("✅ Consistency scores saved to player_consistency.csv")

