import requests
import pandas as pd

BASE_URL = "https://fantasy.premierleague.com/api/"

bootstrap = requests.get(BASE_URL + "bootstrap-static/").json()
fixtures = requests.get(BASE_URL + "fixtures/").json()

events = bootstrap["events"]
teams = pd.DataFrame(bootstrap["teams"])[["id", "name"]]

# تحديد الجولة الجاية
for e in events:
    if e["is_next"]:
        next_gw = e["id"]
        break

records = []

for f in fixtures:
    if f["event"] != next_gw:
        continue

    # Home
    records.append({
        "team": f["team_h"],
        "difficulty": f["team_h_difficulty"]
    })

    # Away
    records.append({
        "team": f["team_a"],
        "difficulty": f["team_a_difficulty"]
    })

df = pd.DataFrame(records)
df = df.merge(teams, left_on="team", right_on="id")

df = df[["name", "difficulty"]]
df.columns = ["team", "fixture_difficulty"]

df.to_csv("fixture_difficulty.csv", index=False)
print("✅ Fixture difficulty saved to fixture_difficulty.csv")

