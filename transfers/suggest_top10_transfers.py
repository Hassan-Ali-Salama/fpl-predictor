import pandas as pd

print("🔥 Calculating Top 10 Transfer Suggestions (Starters only)...")

# =========================
# Load data
# =========================
team = pd.read_csv("my_team_analysis.csv")
candidates = pd.read_csv("all_candidates.csv")

BANK = 0.0  # عدّلها لو عندك فلوس في البنك

# =========================
# Required columns (base)
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
# Check team_id availability
# =========================
use_team_limit = False

if "team_id" in team.columns and "team_id" in candidates.columns:
    print("✅ Team limit (3 players) ENABLED")
    use_team_limit = True
    team_counts = team["team_id"].value_counts().to_dict()
else:
    print("⚠ Team limit DISABLED (team_id not found)")

# =========================
# Only starters can be sold
# =========================
starters = team[team["is_starter"] == True].copy()

results = []

# =========================
# Generate transfer options
# =========================
for _, sell in starters.iterrows():

    sell_name = sell["player"]
    sell_pos = sell["position"]
    sell_price = sell["price"]
    sell_xp = sell["expected_points_next_gw"]

    sell_team = sell["team_id"] if use_team_limit else None

    budget = sell_price + BANK

    buy_pool = candidates[
        (candidates["position"] == sell_pos) &
        (candidates["now_cost"] <= budget) &
        (candidates["player"] != sell_name)
    ].copy()

    for _, buy in buy_pool.iterrows():

        # =========================
        # 3-player-per-team rule (optional)
        # =========================
        if use_team_limit:
            buy_team = buy["team_id"]
            current_count = team_counts.get(buy_team, 0)

            if buy_team == sell_team:
                current_count -= 1

            if current_count >= 3:
                continue

        net_gain = buy["predicted_points"] - sell_xp

        results.append({
            "SELL": sell_name,
            "SELL_Pos": sell_pos,
            "SELL_Price": sell_price,
            "SELL_Exp": round(sell_xp, 2),
            "BUY": buy["player"],
            "BUY_Price": buy["now_cost"],
            "BUY_Exp": round(buy["predicted_points"], 2),
            "Net_Gain": round(net_gain, 2)
        })

# =========================
# Output Top 10
# =========================
df = pd.DataFrame(results)

if df.empty:
    print("⚠️ No valid transfer options found.")
    exit()

df = df.sort_values("Net_Gain", ascending=False).head(10)

print("\n🔥 Top 10 Transfer Suggestions:\n")
print(df)

df.to_csv("top10_transfer_suggestions.csv", index=False)
print("\n✅ Saved to top10_transfer_suggestions.csv")
