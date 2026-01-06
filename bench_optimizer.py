import pandas as pd

print("🪑 Optimizing Bench Order...")

# =========================
# Load data
# =========================
team = pd.read_csv("my_team_analysis.csv")
xi = pd.read_csv("optimized_starting_xi.csv")

# =========================
# Safety
# =========================
required_cols = [
    "player",
    "position",
    "expected_points_next_gw",
    "fixture_difficulty",
    "is_home_next"
]

for col in required_cols:
    if col not in team.columns:
        raise ValueError(f"❌ Missing column in my_team_analysis.csv: {col}")

# =========================
# Identify bench players
# =========================
xi_players = set(xi["player"].tolist())
bench = team[~team["player"].isin(xi_players)].copy()

# =========================
# Separate GK bench
# =========================
bench_gk = bench[bench["position"] == "GK"]
bench_outfield = bench[bench["position"] != "GK"]

if bench_gk.empty:
    raise ValueError("❌ No GK found for bench")

# =========================
# Sort outfield bench
# =========================
bench_outfield["expected_points_next_gw"] = pd.to_numeric(
    bench_outfield["expected_points_next_gw"], errors="coerce"
)
bench_outfield["fixture_difficulty"] = pd.to_numeric(
    bench_outfield["fixture_difficulty"], errors="coerce"
)

bench_outfield = bench_outfield.sort_values(
    by=[
        "expected_points_next_gw",
        "is_home_next",
        "fixture_difficulty",
    ],
    ascending=[False, False, True]
)

# =========================
# Assign bench order
# =========================
bench_outfield["bench_order"] = range(1, len(bench_outfield) + 1)

# =========================
# Output
# =========================
print("\n🪑 Bench Order (Outfield):")
print(
    bench_outfield[
        ["bench_order", "player", "position", "expected_points_next_gw"]
    ]
)

print("\n🧤 Bench GK:")
print(
    bench_gk[["player", "expected_points_next_gw"]]
)

# =========================
# Save
# =========================
bench_outfield.to_csv("bench_order.csv", index=False)
bench_gk.to_csv("bench_gk.csv", index=False)

print("\n✅ Bench ordering saved:")
print("   - bench_order.csv")
print("   - bench_gk.csv")
