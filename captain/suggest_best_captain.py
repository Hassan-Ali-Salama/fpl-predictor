import pandas as pd

print("🧢 Selecting best captain...")

# =========================
# Load team analysis
# =========================
team = pd.read_csv("my_team_analysis.csv")

# =========================
# Required columns check
# =========================
required_cols = [
    "player",
    "position",
    "is_starter",
    "expected_points_next_gw",
    "fixture_difficulty",
    "is_home_next"
]

for col in required_cols:
    if col not in team.columns:
        raise ValueError(f"❌ Missing column: {col}")

# =========================
# Ensure numeric columns
# =========================
numeric_cols = [
    "expected_points_next_gw",
    "fixture_difficulty",
    "is_home_next"
]

for col in numeric_cols:
    team[col] = pd.to_numeric(team[col], errors="coerce")

team["is_starter"] = team["is_starter"].astype(bool)

# =========================
# Starting XI only
# =========================
starters = team[team["is_starter"] == True].copy()

if starters.empty:
    raise ValueError("❌ No starting XI players found")

# =========================
# Captain score formula
# =========================
starters["captain_score"] = (
    starters["expected_points_next_gw"]
    + starters["is_home_next"] * 1.0
    - starters["fixture_difficulty"] * 0.3
)

# =========================
# Sort & select
# =========================
starters = starters.sort_values(
    "captain_score", ascending=False
)

captain = starters.iloc[0]
vice_captain = starters.iloc[1]

# =========================
# Output
# =========================
print("\n🧢 Best Captain Choice:")
print(
    f"⭐ {captain['player']} ({captain['position']}) "
    f"| Expected: {round(captain['expected_points_next_gw'], 2)} "
    f"| Difficulty: {captain['fixture_difficulty']}"
)

print("\n🎖 Vice Captain:")
print(
    f"🔹 {vice_captain['player']} ({vice_captain['position']}) "
    f"| Expected: {round(vice_captain['expected_points_next_gw'], 2)}"
)

# =========================
# Save result
# =========================
captain_df = pd.DataFrame([
    {"role": "Captain", "player": captain["player"]},
    {"role": "Vice Captain", "player": vice_captain["player"]},
])

captain_df.to_csv("captain_suggestion.csv", index=False)
print("\n✅ Saved to captain_suggestion.csv")
