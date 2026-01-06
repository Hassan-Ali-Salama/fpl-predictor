import requests
import pandas as pd

BASE_URL = "https://fantasy.premierleague.com/api/"
print("🔄 Building dataset with rolling form...")

bootstrap = requests.get(BASE_URL + "bootstrap-static/").json()
fixtures = requests.get(BASE_URL + "fixtures/").json()

elements = pd.DataFrame(bootstrap["elements"])
teams_df = pd.DataFrame(bootstrap["teams"]).set_index("id")

# =========================
# Next Gameweek
# =========================
next_gw = None
for ev in bootstrap["events"]:
    if ev["is_next"]:
        next_gw = ev["id"]
        break

if next_gw is None:
    raise Exception("❌ No next gameweek found")

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
        return (
            t["strength_attack_away"],
            t["strength_defence_away"],
            t["strength_overall_away"],
        )
    else:
        return (
            t["strength_attack_home"],
            t["strength_defence_home"],
            t["strength_overall_home"],
        )

rows = []

# الأعمدة اللي لازم تبقى أرقام
NUM_COLS = [
    "minutes",
    "expected_goals",
    "expected_assists",
    "influence",
    "creativity",
    "threat",
    "ict_index",
    "total_points"
]

# =========================
# Build dataset
# =========================
for _, p in elements.iterrows():

    r = requests.get(BASE_URL + f"element-summary/{p['id']}/")
    if r.status_code != 200:
        continue

    history = pd.DataFrame(r.json()["history"])
    if len(history) < 4:
        continue

    # 🔥 تحويل الأعمدة لأرقام
    for col in NUM_COLS:
        history[col] = pd.to_numeric(history[col], errors="coerce")

    is_home_next, difficulty, opp_id = get_next_fixture(p["team"])
    if difficulty is None:
        continue

    opp_att, opp_def, opp_overall = get_opponent_strength(
        opp_id, is_home_next
    )

    for i in range(3, len(history) - 1):
        window = history.iloc[i-3:i]

        rows.append({
            # Last match
            "minutes": history.iloc[i]["minutes"],
            "expected_goals": history.iloc[i]["expected_goals"],
            "expected_assists": history.iloc[i]["expected_assists"],
            "influence": history.iloc[i]["influence"],
            "creativity": history.iloc[i]["creativity"],
            "threat": history.iloc[i]["threat"],
            "ict_index": history.iloc[i]["ict_index"],

            # 🔥 Rolling (3 matches)
            "avg_minutes_3": window["minutes"].mean(),
            "avg_xg_3": window["expected_goals"].mean(),
            "avg_xa_3": window["expected_assists"].mean(),
            "avg_influence_3": window["influence"].mean(),
            "avg_creativity_3": window["creativity"].mean(),
            "avg_threat_3": window["threat"].mean(),
            "avg_ict_3": window["ict_index"].mean(),

            # Fixture
            "is_home_next": is_home_next,
            "fixture_difficulty": difficulty,

            # Opponent
            "opp_strength_attack": opp_att,
            "opp_strength_defence": opp_def,
            "opp_strength_overall": opp_overall,

            # Target
            "target_points": history.iloc[i+1]["total_points"]
        })

df = pd.DataFrame(rows)
df.to_csv("global_dataset.csv", index=False)

print("✅ global_dataset.csv ready")
print("Shape:", df.shape)
