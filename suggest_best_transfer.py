import pandas as pd

print("🔁 Best SINGLE transfer (Starter only)...")

# =========================
# Load data
# =========================
team = pd.read_csv("my_team_analysis.csv")
candidates = pd.read_csv("all_candidates.csv")

BANK = 0.0  # ← عدّل لو عندك فلوس

# =========================
# Safety
# =========================
team["is_starter"] = team["is_starter"].astype(bool)
team["expected_points_next_gw"] = pd.to_numeric(team["expected_points_next_gw"])
team["price"] = pd.to_numeric(team["price"])

candidates["predicted_points_next_gw"] = pd.to_numeric(
    candidates["predicted_points_next_gw"]
)
candidates["price"] = pd.to_numeric(candidates["price"])

# =========================
# Team counts
# =========================
team_counts = team["team_id"].value_counts().to_dict()
team_players = set(team["player"].tolist())

# =========================
# Only starters can be sold
# =========================
starters = team[team["is_starter"]]

best = None
best_gain = -999

for _, sell in starters.iterrows():

    budget = sell["price"] + BANK
    sell_team = sell["team_id"]

    pool = candidates[
        (candidates["position"] == sell["position"]) &
        (candidates["price"] <= budget) &
        (~candidates["player"].isin(team_players))
    ]

    for _, buy in pool.iterrows():

        # 3-player-per-team
        count = team_counts.get(buy["team_id"], 0)
        if buy["team_id"] == sell_team:
            count -= 1
        if count >= 3:
            continue

        gain = buy["predicted_points_next_gw"] - sell["expected_points_next_gw"]

        if gain > best_gain:
            best_gain = gain
            best = (sell, buy, gain)

# =========================
# Output
# =========================
if not best:
    print("⚠️ No valid transfer found.")
    exit()

sell, buy, gain = best

print("\n🔁 BEST TRANSFER:")
print(f"❌ SELL: {sell['player']} ({sell['position']}) | XP: {sell['expected_points_next_gw']}")
print(f"✅ BUY : {buy['player']} ({buy['position']}) | XP: {buy['predicted_points_next_gw']}")
print(f"📈 Net Gain: +{round(gain,2)}")
