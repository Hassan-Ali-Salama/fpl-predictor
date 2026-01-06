import pandas as pd
import itertools

print("🧩 Optimizing Starting XI...")

# =========================
# Load team analysis
# =========================
df = pd.read_csv("my_team_analysis.csv")

required_cols = [
    "player",
    "position",
    "expected_points_next_gw"
]

for col in required_cols:
    if col not in df.columns:
        raise ValueError(f"❌ Missing column: {col}")

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

# =========================
# FPL constraints
# =========================
best_team = None
best_score = -1

for d in range(3, 6):        # DEF 3-5
    for m in range(2, 6):    # MID 2-5
        f = 11 - (1 + d + m) # GK = 1
        if f < 1 or f > 3:
            continue

        for gk in itertools.combinations(gks.index, 1):
            for d_ids in itertools.combinations(defs.index, d):
                for m_ids in itertools.combinations(mids.index, m):
                    for f_ids in itertools.combinations(fwds.index, f):

                        ids = list(gk) + list(d_ids) + list(m_ids) + list(f_ids)
                        score = df.loc[ids, "expected_points_next_gw"].sum()

                        if score > best_score:
                            best_score = score
                            best_team = df.loc[ids]

# =========================
# Output
# =========================
best_team = best_team.sort_values(
    ["position", "expected_points_next_gw"],
    ascending=[True, False]
)

print("\n🏆 Best Starting XI:")
print(best_team[["player", "position", "expected_points_next_gw"]])

print(f"\n📈 Total Expected Points: {round(best_score, 2)}")

# Save
best_team.to_csv("optimized_starting_xi.csv", index=False)
print("\n✅ Saved to optimized_starting_xi.csv")
