import requests
import pandas as pd
import joblib

BASE_URL = "https://fantasy.premierleague.com/api/"
ENTRY_ID = 7552960   # 👈 فريقك

print("🔍 Analyzing my team...")

# =========================
# Load model
# =========================
model = joblib.load("fpl_model.pkl")

# =========================
# Load base data
# =========================
bootstrap = requests.get(BASE_URL + "bootstrap-static/").json()
fixtures = requests.get(BASE_URL + "fixtures/").json()

players_df = pd.DataFrame(bootstrap["elements"]).set_index("id")
teams_df = pd.DataFrame(bootstrap["teams"]).set_index("id")

# =========================
# Get NEXT Gameweek
# =========================
next_gw = next(ev["id"] for ev in bootstrap["events"] if ev["is_next"])

# =========================
# Get my team picks
# =========================
picks_url = f"{BASE_URL}entry/{ENTRY_ID}/event/{next_gw-1}/picks/"
picks = requests.get(picks_url).json()["picks"]
picks_df = pd.DataFrame(picks)

# =========================
# Helpers
# =========================
def get_next_fixture(team_id):
    for f in fixtures:
        if f["event"] == next_gw:
            if f["team_h"] == team_id:
                return 1, f["team_h_difficulty"]
            if f["team_a"] == team_id:
                return 0, f["team_a_difficulty"]
    return None, None


def rolling_form(player_id, window=3):
    r = requests.get(BASE_URL + f"element-summary/{player_id}/")
    if r.status_code != 200:
        return None

    history = pd.DataFrame(r.json()["history"])
    if len(history) == 0:
        return None

    numeric_cols = [
        "minutes",
        "expected_goals",
        "expected_assists",
        "influence",
        "creativity",
        "threat",
        "ict_index",
    ]

    for col in numeric_cols:
        history[col] = pd.to_numeric(history[col], errors="coerce")

    recent = history.tail(window)

    return {
        "last_match": history.iloc[-1],
        "avg_minutes_3": recent["minutes"].mean(),
        "avg_xg_3": recent["expected_goals"].mean(),
        "avg_xa_3": recent["expected_assists"].mean(),
        "avg_influence_3": recent["influence"].mean(),
        "avg_creativity_3": recent["creativity"].mean(),
        "avg_threat_3": recent["threat"].mean(),
        "avg_ict_3": recent["ict_index"].mean(),
    }


# =========================
# Build team analysis
# =========================
rows = []

for _, row in picks_df.iterrows():
    pid = row["element"]
    player = players_df.loc[pid]

    form = rolling_form(pid)
    if not form:
        continue

    is_home, difficulty = get_next_fixture(player["team"])
    if difficulty is None:
        continue

    # Prepare model input
    X = pd.DataFrame([{
    "minutes": form["last_match"]["minutes"],
    "expected_goals": form["last_match"]["expected_goals"],
    "expected_assists": form["last_match"]["expected_assists"],
    "influence": form["last_match"]["influence"],
    "creativity": form["last_match"]["creativity"],
    "threat": form["last_match"]["threat"],
    "ict_index": form["last_match"]["ict_index"],

    "avg_minutes_3": form["avg_minutes_3"],
    "avg_xg_3": form["avg_xg_3"],
    "avg_xa_3": form["avg_xa_3"],
    "avg_influence_3": form["avg_influence_3"],
    "avg_creativity_3": form["avg_creativity_3"],
    "avg_threat_3": form["avg_threat_3"],
    "avg_ict_3": form["avg_ict_3"],

    "is_home_next": is_home,
    "fixture_difficulty": difficulty,
    "opp_strength_attack": 0,
    "opp_strength_defence": 0,
    "opp_strength_overall": 0,
	}])


    pred = model.predict(X)[0]

    rows.append({
        "player": player["web_name"],
        "player_id": pid,
        "team_id": player["team"],
        "position": {1:"GK",2:"DEF",3:"MID",4:"FWD"}[player["element_type"]],
        "price": player["now_cost"] / 10,
        "is_starter": row["position"] <= 11,
        "avg_minutes_3": round(form["avg_minutes_3"], 1),
        "avg_xg_3": round(form["avg_xg_3"], 2),
        "avg_xa_3": round(form["avg_xa_3"], 2),
        "fixture_difficulty": difficulty,
        "is_home_next": is_home,
        "expected_points_next_gw": round(pred, 2)
    })

# =========================
# Save
# =========================
df = pd.DataFrame(rows)
df.to_csv("my_team_analysis.csv", index=False)

print(f"✅ Team analysis ready for GW {next_gw}")
print(df[["player","position","expected_points_next_gw"]].sort_values(
    "expected_points_next_gw", ascending=False
))
