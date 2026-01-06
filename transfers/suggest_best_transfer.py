import pandas as pd

print("🔁 Suggesting best single transfer (Starter only)...")

# =========================
# Load data
# =========================
team = pd.read_csv("my_team_analysis.csv")
candidates = pd.read_csv("all_candidates.csv")

# =========================
# Bank (free money)
# =========================
BANK = 0.0  # عدّلها لو عندك فلوس في البنك

# =========================
# Required columns
# =========================
required_team_cols = [
    "player",
    "position",
    "price",
    "expected_points_next_gw",
    "is_starter"
]

for col in required_team_cols:
    if col not in team.columns:
        raise ValueError(f"❌ Missing column in my_team_analysis.csv: {col}")

required_cand_cols = [
    "player",
    "position",
    "now_cost",
    "predicted_points"
]

for col in required_cand_cols:
    if col not in candidates.columns:
        raise ValueError(f"❌ Missing column in all_candidates.csv: {col}")

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
# 1️⃣ Sell candidate: WORST STARTER
# =========================
sell_candidates = team[
    team["is_starter"] == True
].sort_values("expected_points_next_gw")

sell_player = sell_candidates.iloc[0]

sell_name = sell_player["player"]
sell_pos = sell_player["position"]
sell_price = sell_player["price"]
sell_xp = sell_player["expected_points_next_gw"]

# =========================
# Budget
# =========================
budget = sell_price + BANK

# =========================
# 2️⃣ Buy candidate: BEST UPGRADE
# =========================
buy_candidates = candidates[
    (candidates["position"] == sell_pos) &
    (candidates["now_cost"] <= budget) &
    (candidates["player"] != sell_name)  # ما نشتريش نفس اللاعب
].copy()

buy_candidates = buy_candidates.sort_values(
    "predicted_points", ascending=False
)

if buy_candidates.empty:
    print("\n⚠️ No upgrade found for a STARTER within budget.")
    print(f"❌ SELL Candidate: {sell_name} ({sell_pos})")
    exit()

best_buy = buy_candidates.iloc[0]

buy_name = best_buy["player"]
buy_price = best_buy["now_cost"]
buy_xp = best_buy["predicted_points"]

# =========================
# Output
# =========================
net_gain = round(buy_xp - sell_xp, 2)

print("\n🔁 Best Single Transfer (Starter Only):\n")

print(f"❌ SELL: {sell_name} ({sell_pos})")
print(f"   Price: {sell_price} | Expected: {round(sell_xp,2)}")

print(f"\n✅ BUY: {buy_name} ({sell_pos})")
print(f"   Price: {buy_price} | Expected: {round(buy_xp,2)}")

print(f"\n📈 Net Expected Gain: +{net_gain} pts")
