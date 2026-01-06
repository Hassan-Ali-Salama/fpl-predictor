import pandas as pd
import itertools

print("🧩 Optimizing Starting XI (FPL-legal, full features)...")

# =========================
# Load team analysis
# =========================
df = pd.read_csv("my_team_analysis.csv")

required_cols = [
    "player",
    "position",
    "team_id",
    "expected_points_next_gw"
]

missing = set(required_cols) - set(df.columns)
if missing:
    raise ValueError(f"❌ Missing columns: {missing}")

df["expected_points_next_gw"] = pd.to_numeric(
    df["expected_points_next_gw"], errors="coerce"
)

# =========================
# Split by position
# =========================
gks  = df[df["position"] == "GK"]
defs = df[df["position"] == "DEF"]
mids = df[df["position"] == "MID"]
fwds = df[df["position"] == "FWD"]

best_team = None
best_score = -1

# =========================
# Formation search
# =========================
for d in range(3, 6):
    for m in range(2, 6):
        f = 11 - (1 + d + m)
        if f < 1 or f > 3:
            continue

        for gk in itertools.combinations(gks.index, 1):
            for d_ids in itertools.combinations(defs.index, d):
                for m_ids in itertools.combinations(mids.index, m):
                    for f_ids in itertools.combinations(fwds.index, f):

                        ids = list(gk) + list(d_ids) + list(m_ids) + list(f_ids)
                        team = df.loc[ids]

                        # Max 3 players per team
                        if team["team_id"].value_counts().max() > 3:
                            continue

                        score = team["expected_points_next_gw"].sum()

                        if score > best_score:
                            best_score = score
                            best_team = team.copy()

# =========================
# Output (KEEP ALL COLUMNS)
# =========================
best_team = best_team.sort_values(
    ["position", "expected_points_next_gw"],
    ascending=[True, False]
)

best_team.to_csv("optimized_starting_xi.csv", index=False)

print("\n🏆 Best Starting XI:")
print(best_team[["player", "position", "expected_points_next_gw"]])
print(f"\n📈 Total Expected Points: {round(best_score, 2)}")
print("\n✅ Saved to optimized_starting_xi.csv")
