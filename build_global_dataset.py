import requests
import pandas as pd

BASE_URL = "https://fantasy.premierleague.com/api/"
print("🔄 Building GLOBAL dataset (short + mid + season memory)...")

bootstrap = requests.get(BASE_URL + "bootstrap-static/").json()
fixtures = requests.get(BASE_URL + "fixtures/").json()

elements = pd.DataFrame(bootstrap["elements"])
teams_df = pd.DataFrame(bootstrap["teams"]).set_index("id")

# =========================
# Detect NEXT GW
# =========================
next_gw = next(ev["id"] for ev in bootstrap["events"] if ev["is_next"])

# =========================
# Helpers
# =========================
def get_next_fixture(team_id):
    for f in fixtures:
        if f["event"] == next_gw:
            if f["team_h"] == team_id:
                return 1, f["team_h_difficulty"], f["team_a"]
            if f["team_a"] == team_id:
                return 0, f["team_a_difficulty"], f["team_h"]
    return None, None, None


def get_opponent_strength(opp_id, is_home):
    t = teams_df.loc[opp_id]
    if is_home:
        return t["strength_attack_away"], t["strength_defence_away"], t["strength_overall_away"]
    else:
        return t["strength_attack_home"], t["strength_defence_home"], t["strength_overall_home"]

NUM_COLS = [
    "minutes", "expected_goals", "expected_assists",
    "influence", "creativity", "threat", "ict_index", "total_points"
]

rows = []

# =========================
# Build dataset
# =========================
for _, p in elements.iterrows():

    r = requests.get(BASE_URL + f"element-summary/{p['id']}/")
    if r.status_code != 200:
        continue

    history = pd.DataFrame(r.json()["history"])
    if len(history) < 10:
        continue

    for col in NUM_COLS:
        history[col] = pd.to_numeric(history[col], errors="coerce")

    is_home, difficulty, opp_id = get_next_fixture(p["team"])
    if difficulty is None:
        continue

    opp_att, opp_def, opp_overall = get_opponent_strength(opp_id, is_home)

    for i in range(10, len(history) - 1):

        last = history.iloc[i]
        w3 = history.iloc[i-3:i]
        w10 = history.iloc[i-10:i]
        season = history.iloc[:i]

        rows.append({
            # Last match
            "minutes": last["minutes"],
            "expected_goals": last["expected_goals"],
            "expected_assists": last["expected_assists"],
            "influence": last["influence"],
            "creativity": last["creativity"],
            "threat": last["threat"],
            "ict_index": last["ict_index"],

            # Rolling 3
            "avg_minutes_3": w3["minutes"].mean(),
            "avg_xg_3": w3["expected_goals"].mean(),
            "avg_xa_3": w3["expected_assists"].mean(),
            "avg_influence_3": w3["influence"].mean(),
            "avg_creativity_3": w3["creativity"].mean(),
            "avg_threat_3": w3["threat"].mean(),
            "avg_ict_3": w3["ict_index"].mean(),

            # Rolling 10
            "avg_minutes_10": w10["minutes"].mean(),
            "avg_xg_10": w10["expected_goals"].mean(),
            "avg_xa_10": w10["expected_assists"].mean(),
            "avg_ict_10": w10["ict_index"].mean(),

            # Season baseline
            "season_avg_minutes": season["minutes"].mean(),
            "season_avg_xg": season["expected_goals"].mean(),
            "season_avg_xa": season["expected_assists"].mean(),
            "season_avg_ict": season["ict_index"].mean(),

            # Fixture
            "is_home_next": is_home,
            "fixture_difficulty": difficulty,

            # Opponent
            "opp_strength_attack": opp_att,
            "opp_strength_defence": opp_def,
            "opp_strength_overall": opp_overall,

            # Target
            "target_points": history.iloc[i+1]["total_points"],
        })

df = pd.DataFrame(rows)
df.to_csv("global_dataset.csv", index=False)

print("✅ global_dataset.csv ready")
print("Shape:", df.shape)
