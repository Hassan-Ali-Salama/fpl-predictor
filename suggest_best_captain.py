import pandas as pd

print("🧢 Selecting Captain & Vice-Captain...")

# =========================
# Load XI only
# =========================
xi = pd.read_csv("optimized_starting_xi.csv")

required_cols = [
    "player",
    "position",
    "expected_points_next_gw",
    "fixture_difficulty",
    "is_home_next"
]

for col in required_cols:
    if col not in xi.columns:
        raise ValueError(f"❌ Missing column: {col}")

# =========================
# Numeric safety
# =========================
xi["expected_points_next_gw"] = pd.to_numeric(
    xi["expected_points_next_gw"], errors="coerce"
)
xi["fixture_difficulty"] = pd.to_numeric(
    xi["fixture_difficulty"], errors="coerce"
)
xi["is_home_next"] = pd.to_numeric(
    xi["is_home_next"], errors="coerce"
)

# =========================
# Captain score
# =========================
xi["captain_score"] = (
    xi["expected_points_next_gw"]
    + xi["is_home_next"] * 0.8
    - xi["fixture_difficulty"] * 0.3
)

# =========================
# Sort & select
# =========================
xi = xi.sort_values("captain_score", ascending=False)

captain = xi.iloc[0]
vice = xi.iloc[1]

# =========================
# Output
# =========================
print("\n🧢 Captain:")
print(
    f"⭐ {captain['player']} ({captain['position']}) "
    f"| XP: {round(captain['expected_points_next_gw'], 2)}"
)

print("\n🎖 Vice Captain:")
print(
    f"🔹 {vice['player']} ({vice['position']}) "
    f"| XP: {round(vice['expected_points_next_gw'], 2)}"
)

# =========================
# Save
# =========================
pd.DataFrame([
    {"role": "Captain", "player": captain["player"]},
    {"role": "Vice Captain", "player": vice["player"]},
]).to_csv("captain_suggestion.csv", index=False)

print("\n✅ Saved to captain_suggestion.csv")
