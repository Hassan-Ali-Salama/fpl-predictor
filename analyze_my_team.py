import json, requests, pandas as pd, joblib

BASE_URL = "https://fantasy.premierleague.com/api/"
ENTRY_ID = 7552960

print("🔍 Analyzing MY TEAM...")

model = joblib.load("fpl_model.pkl")
MODEL_FEATURES = json.load(open("model_features.json"))

bootstrap = requests.get(BASE_URL + "bootstrap-static/").json()
fixtures = requests.get(BASE_URL + "fixtures/").json()

players_df = pd.DataFrame(bootstrap["elements"]).set_index("id")
teams_df = pd.DataFrame(bootstrap["teams"]).set_index("id")

next_gw = next(ev["id"] for ev in bootstrap["events"] if ev["is_next"])

picks = requests.get(
    f"{BASE_URL}entry/{ENTRY_ID}/event/{next_gw-1}/picks/"
).json()["picks"]

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
    return (
        (t["strength_attack_away"], t["strength_defence_away"], t["strength_overall_away"])
        if is_home else
        (t["strength_attack_home"], t["strength_defence_home"], t["strength_overall_home"])
    )

rows = []

for pick in picks:
    pid = pick["element"]
    hist = requests.get(BASE_URL + f"element-summary/{pid}/").json()["history"]
    history = pd.DataFrame(hist)
    if len(history) < 10:
        continue

    for c in ["minutes","expected_goals","expected_assists","influence","creativity","threat","ict_index"]:
        history[c] = pd.to_numeric(history[c], errors="coerce")

    is_home, diff, opp_id = get_next_fixture(players_df.loc[pid]["team"])
    if diff is None:
        continue

    opp_att, opp_def, opp_overall = get_opponent_strength(opp_id, is_home)

    last = history.iloc[-1]
    w3 = history.tail(3)
    w10 = history.tail(10)

    X = pd.DataFrame([{
        "minutes": last["minutes"],
        "expected_goals": last["expected_goals"],
        "expected_assists": last["expected_assists"],
        "influence": last["influence"],
        "creativity": last["creativity"],
        "threat": last["threat"],
        "ict_index": last["ict_index"],

        "avg_minutes_3": w3["minutes"].mean(),
        "avg_xg_3": w3["expected_goals"].mean(),
        "avg_xa_3": w3["expected_assists"].mean(),
        "avg_influence_3": w3["influence"].mean(),
        "avg_creativity_3": w3["creativity"].mean(),
        "avg_threat_3": w3["threat"].mean(),
        "avg_ict_3": w3["ict_index"].mean(),

        "avg_minutes_10": w10["minutes"].mean(),
        "avg_xg_10": w10["expected_goals"].mean(),
        "avg_xa_10": w10["expected_assists"].mean(),
        "avg_ict_10": w10["ict_index"].mean(),

        "season_avg_minutes": history["minutes"].mean(),
        "season_avg_xg": history["expected_goals"].mean(),
        "season_avg_xa": history["expected_assists"].mean(),
        "season_avg_ict": history["ict_index"].mean(),

        "is_home_next": is_home,
        "fixture_difficulty": diff,
        "opp_strength_attack": opp_att,
        "opp_strength_defence": opp_def,
        "opp_strength_overall": opp_overall,
    }])[MODEL_FEATURES]

    pred = model.predict(X)[0]
    player = players_df.loc[pid]

    rows.append({
    "player": player["web_name"],
    "player_id": pid,
    "team_id": player["team"],
    "position": {1:"GK",2:"DEF",3:"MID",4:"FWD"}[player["element_type"]],
    "price": player["now_cost"] / 10,
    "is_starter": pick["position"] <= 11,

    # 👇 مهمين للـ Captain & Bench logic
    "fixture_difficulty": diff,
    "is_home_next": is_home,

    "expected_points_next_gw": round(pred, 2),
    })


pd.DataFrame(rows).to_csv("my_team_analysis.csv", index=False)
print("✅ my_team_analysis.csv updated")
