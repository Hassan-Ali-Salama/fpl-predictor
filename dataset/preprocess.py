import json
import pandas as pd

with open("bootstrap_data.json") as f:
    data = json.load(f)

df = pd.DataFrame(data["elements"])

features = [
    "minutes",
    "goals_scored",
    "assists",
    "expected_goals",
    "expected_assists",
    "clean_sheets",
    "total_points",
    "now_cost",
    "selected_by_percent"
]

df = df[features]

df["selected_by_percent"] = df["selected_by_percent"].astype(float)

df.to_csv("players_features.csv", index=False)

print("✅ Features saved to players_features.csv")

