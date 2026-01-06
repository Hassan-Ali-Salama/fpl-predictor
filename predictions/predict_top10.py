import requests
import pandas as pd
import joblib

BASE_URL = "https://fantasy.premierleague.com/api/"
print("🔮 Predicting next gameweek points with rolling form...")

# =========================
# Load model
# =========================
model = joblib.load("fpl_model.pkl")

# =========================
# Load API data
# =========================
bootstrap = requests.get(BASE_URL + "bootstrap-static/").json()
fixtures = requests.get(BASE_URL + "fixtures/").json()

players = bootstrap["elements"]
teams_df = pd.DataFrame(bootstrap["teams"]).set_index("id")

# =========================
# Get NEXT Gameweek
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
    team = teams_df.loc[opp_id]
    if is_home:
        return (
            team["strength_attack_away"],
            team["strength_defence_away"],
            team["strength_overall_away"],
        )
    else:
        return (
            team["strength_attack_home"],
            team["strength_defence_home"],
            team["strength_overall_home"],
        )

results = []

NUM_COLS = [
    "minutes",
    "expected_goals",
    "expected_assists",
    "influence",
    "creativity",
    "threat",
    "ict_index"
]

# =========================
# Predict loop
# =========================
for p in players:

    if p["element_type"] not in [2, 3, 4]:
        continue

    r = requests.get(BASE_URL + f"element-summary/{p['id']}/")
    if r.status_code != 200:
        continue

    history = pd.DataFrame(r.json()["history"])
    if len(history) < 3:
        continue

    # 🔥 FIX: convert to numeric
    for col in NUM_COLS:
        history[col] = pd.to_numeric(history[col], errors="coerce")

    is_home_next, difficulty, opp_id = get_next_fixture(p["team"])
    if difficulty is None:
        continue

    opp_att, opp_def, opp_overall = get_opponent_strength(
        opp_id, is_home_next
    )

    last_match = history.iloc[-1]
    recent = history.tail(3)

    X = pd.DataFrame([{
        # Last match
        "minutes": last_match["minutes"],
        "expected_goals": last_match["expected_goals"],
        "expected_assists": last_match["expected_assists"],
        "influence": last_match["influence"],
        "creativity": last_match["creativity"],
        "threat": last_match["threat"],
        "ict_index": last_match["ict_index"],

        # Rolling (3)
        "avg_minutes_3": recent["minutes"].mean(),
        "avg_xg_3": recent["expected_goals"].mean(),
        "avg_xa_3": recent["expected_assists"].mean(),
        "avg_influence_3": recent["influence"].mean(),
        "avg_creativity_3": recent["creativity"].mean(),
        "avg_threat_3": recent["threat"].mean(),
        "avg_ict_3": recent["ict_index"].mean(),

        # Fixture
        "is_home_next": is_home_next,
        "fixture_difficulty": difficulty,

        # Opponent
        "opp_strength_attack": opp_att,
        "opp_strength_defence": opp_def,
        "opp_strength_overall": opp_overall
    }])

    pred = model.predict(X)[0]

    results.append({
        "player": p["web_name"],
        "position": p["element_type"],
        "predicted_points": round(pred, 2)
    })

# =========================
# Output
# =========================
df = pd.DataFrame(results)
df["position"] = df["position"].map({2: "DEF", 3: "MID", 4: "FWD"})

print(f"\n🔮 Predictions for Gameweek {next_gw}")
print(df.sort_values("predicted_points", ascending=False).head(10))
