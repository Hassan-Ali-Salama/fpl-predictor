import requests
import pandas as pd

BASE_URL = "https://fantasy.premierleague.com/api/"

team_id = 7552960   # من اللي بعتته
gw = 20             # الجيم ويك اللي عايزينها

url = f"{BASE_URL}entry/{team_id}/event/{gw}/picks/"

resp = requests.get(url)

if resp.status_code != 200:
    print("❌ Error fetching team picks")
else:
    data = resp.json()
    picks = data["picks"]

    df = pd.DataFrame(picks)
    print("\n🧠 Your Team Picks (GW20):\n", df)

    df.to_csv("my_team_gw20.csv", index=False)
    print("\n✅ Saved to my_team_gw20.csv")

