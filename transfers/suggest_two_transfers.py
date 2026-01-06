import pandas as pd
from itertools import combinations

print("🔥 Calculating best TWO transfers (-4 hit)...")

# =========================
# Load data
# =========================
team = pd.read_csv("my_team_analysis.csv")
candidates = pd.read_csv("all_candidates.csv")

BANK = 0.0

# =========================
# Required columns
# =========================
team_cols = [
    "player",
    "position",
    "price",
    "expected_points_next_gw",
    "is_starter"
]

cand_cols = [
    "player",
    "position",
    "now_cost",
    "predicted_points"
]

for c in team_cols:
    if c not in team.columns:
        raise ValueError(f"❌ Missing column in my_team_analysis.csv: {c}")

for c in cand_cols:
    if c not in candidates.columns:
        raise ValueError(f"❌ Missing column in all_candidates.csv: {c}")

# =========================
# Numeric safety
# =========================
team["expected_points_next_gw"] = pd.to_numeric(
    team["expected_points_next_gw"], errors="coerce"
)
team["price"] = pd.to_numeric(team["price"], errors="coerce")
team["is_starter"] = team["is_starter"].astype(bool)

candidates["predicted_points"] = pd.to_numeric(
    candidates["predicted_points"], errors="coerce"
)
candidates["now_cost"] = pd.to_numeric(
    candidates["now_cost"], errors="coerce"
)

# =========================
# Only starters can be sold
# =========================
starters = team[team["is_starter"] == True].copy()

team_players = set(team["player"].tolist())

results = []

# =========================
# Generate SELL pairs
# =========================
for sell1, sell2 in combinations(starters.iterrows(), 2):

    s1 = sell1[1]
    s2 = sell2[1]

    sell_players = {s1["player"], s2["player"]}

    sell_price = s1["price"] + s2["price"]
    sell_xp = s1["expected_points_next_gw"] + s2["expected_points_next_gw"]

    budget = sell_price + BANK

    buy_pool1 = candidates[
        (candidates["position"] == s1["position"]) &
        (candidates["now_cost"] <= budget)
    ]

    buy_pool2 = candidates[
        (candidates["position"] == s2["position"]) &
        (candidates["now_cost"] <= budget)
    ]

    for _, b1 in buy_pool1.iterrows():
        for _, b2 in buy_pool2.iterrows():

            # =========================
            # Validity checks
            # =========================
            if b1["player"] == b2["player"]:
                continue

            if b1["player"] in team_players:
                continue

            if b2["player"] in team_players:
                continue

            if b1["player"] in sell_players:
                continue

            if b2["player"] in sell_players:
                continue

            buy_price = b1["now_cost"] + b2["now_cost"]
            if buy_price > budget:
                continue

            buy_xp = b1["predicted_points"] + b2["predicted_points"]

            net_gain = buy_xp - sell_xp - 4

            results.append({
                "SELL_1": s1["player"],
                "SELL_2": s2["player"],
                "BUY_1": b1["player"],
                "BUY_2": b2["player"],
                "Net_Gain": round(net_gain, 2)
            })

# =========================
# Output
# =========================
df = pd.DataFrame(results)

if df.empty:
    print("⚠️ No valid two-transfer options found.")
    exit()

df = df.sort_values("Net_Gain", ascending=False).head(10)

print("\n🔥 Best TWO Transfers (-4):\n")
print(df)

df.to_csv("top_two_transfers.csv", index=False)
print("\n✅ Saved to top_two_transfers.csv")
