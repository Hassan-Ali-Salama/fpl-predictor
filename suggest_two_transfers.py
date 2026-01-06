import pandas as pd
from itertools import combinations

print("🔥 Best TWO transfers (-4 hit)...")

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

team_players = set(team["player"].tolist())
team_counts = team["team_id"].value_counts().to_dict()

results = []

starters = team[team["is_starter"]]

for (_, s1), (_, s2) in combinations(starters.iterrows(), 2):

    budget = s1["price"] + s2["price"] + BANK
    sell_xp = s1["expected_points_next_gw"] + s2["expected_points_next_gw"]

    pool1 = candidates[candidates["position"] == s1["position"]]
    pool2 = candidates[candidates["position"] == s2["position"]]

    for _, b1 in pool1.iterrows():
        for _, b2 in pool2.iterrows():

            if b1["player"] == b2["player"]:
                continue
            if b1["player"] in team_players or b2["player"] in team_players:
                continue
            if b1["price"] + b2["price"] > budget:
                continue

            counts = team_counts.copy()

            for s in [s1, s2]:
                counts[s["team_id"]] -= 1

            valid = True
            for b in [b1, b2]:
                if counts.get(b["team_id"], 0) >= 3:
                    valid = False
                    break
                counts[b["team_id"]] = counts.get(b["team_id"], 0) + 1

            if not valid:
                continue

            buy_xp = b1["predicted_points_next_gw"] + b2["predicted_points_next_gw"]
            net = buy_xp - sell_xp - 4

            results.append({
                "SELL_1": s1["player"],
                "SELL_2": s2["player"],
                "BUY_1": b1["player"],
                "BUY_2": b2["player"],
                "Net_Gain": round(net, 2)
            })

df = pd.DataFrame(results)

if df.empty:
    print("⚠️ No valid two-transfer options.")
    exit()

df = df.sort_values("Net_Gain", ascending=False).head(10)

print("\n🔥 BEST TWO TRANSFERS:")
print(df)

df.to_csv("top_two_transfers.csv", index=False)
print("\n✅ Saved to top_two_transfers.csv")
