import pandas as pd

print("🔥 TOP 10 transfer suggestions...")

team = pd.read_csv("my_team_analysis.csv")
candidates = pd.read_csv("all_candidates.csv")

BANK = 0.0

team["is_starter"] = team["is_starter"].astype(bool)
team["expected_points_next_gw"] = pd.to_numeric(team["expected_points_next_gw"])
team["price"] = pd.to_numeric(team["price"])

candidates["predicted_points_next_gw"] = pd.to_numeric(
    candidates["predicted_points_next_gw"]
)
candidates["price"] = pd.to_numeric(candidates["price"])

team_counts = team["team_id"].value_counts().to_dict()
team_players = set(team["player"].tolist())

results = []

for _, sell in team[team["is_starter"]].iterrows():

    budget = sell["price"] + BANK
    sell_team = sell["team_id"]

    pool = candidates[
        (candidates["position"] == sell["position"]) &
        (candidates["price"] <= budget) &
        (~candidates["player"].isin(team_players))
    ]

    for _, buy in pool.iterrows():

        count = team_counts.get(buy["team_id"], 0)
        if buy["team_id"] == sell_team:
            count -= 1
        if count >= 3:
            continue

        gain = buy["predicted_points_next_gw"] - sell["expected_points_next_gw"]

        results.append({
            "SELL": sell["player"],
            "BUY": buy["player"],
            "Net_Gain": round(gain, 2)
        })

df = pd.DataFrame(results).sort_values("Net_Gain", ascending=False).head(10)

print("\n🔥 TOP 10:")
print(df)

df.to_csv("top10_transfer_suggestions.csv", index=False)
print("\n✅ Saved to top10_transfer_suggestions.csv")
