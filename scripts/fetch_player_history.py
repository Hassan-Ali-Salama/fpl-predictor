import requests
import json
import time

BASE_URL = "https://fantasy.premierleague.com/api/element-summary/"
PLAYER_ID = 1  # هنبدأ بلاعب واحد (مثلاً)

response = requests.get(BASE_URL + str(PLAYER_ID) + "/")

if response.status_code == 200:
    data = response.json()
    with open("player_1_history.json", "w") as f:
        json.dump(data, f, indent=2)
    print("✅ Player history fetched")
else:
    print("❌ Error")

