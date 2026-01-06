import json
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

print("🧠 Training GLOBAL model (multi-memory)...")

MODEL_FEATURES = [
    "minutes","expected_goals","expected_assists",
    "influence","creativity","threat","ict_index",

    "avg_minutes_3","avg_xg_3","avg_xa_3",
    "avg_influence_3","avg_creativity_3","avg_threat_3","avg_ict_3",

    "avg_minutes_10","avg_xg_10","avg_xa_10","avg_ict_10",

    "season_avg_minutes","season_avg_xg","season_avg_xa","season_avg_ict",

    "is_home_next","fixture_difficulty",
    "opp_strength_attack","opp_strength_defence","opp_strength_overall"
]

TARGET = "target_points"

df = pd.read_csv("global_dataset.csv")

missing = set(MODEL_FEATURES + [TARGET]) - set(df.columns)
if missing:
    raise ValueError(f"❌ Missing columns: {missing}")

X = df[MODEL_FEATURES]
y = df[TARGET]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = RandomForestRegressor(
    n_estimators=400,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

preds = model.predict(X_test)
mae = mean_absolute_error(y_test, preds)

print(f"✅ Model trained | MAE = {round(mae, 2)}")

joblib.dump(model, "fpl_model.pkl")
with open("model_features.json", "w") as f:
    json.dump(MODEL_FEATURES, f, indent=2)

print("💾 Saved model & features")
