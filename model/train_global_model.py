import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import joblib

print("🧠 Training model with advanced features...")

# =========================
# Load dataset
# =========================
df = pd.read_csv("global_dataset.csv")

FEATURES = [
    "minutes",
    "expected_goals",
    "expected_assists",
    "influence",
    "creativity",
    "threat",
    "ict_index",

    "avg_minutes_3",
    "avg_xg_3",
    "avg_xa_3",
    "avg_influence_3",
    "avg_creativity_3",
    "avg_threat_3",
    "avg_ict_3",

    "is_home_next",
    "fixture_difficulty",

    "opp_strength_attack",
    "opp_strength_defence",
    "opp_strength_overall"
]

X = df[FEATURES]
y = df["target_points"]

# =========================
# Train / Test split
# =========================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# =========================
# Model
# =========================
model = RandomForestRegressor(
    n_estimators=300,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

# =========================
# Evaluation
# =========================
preds = model.predict(X_test)
mae = mean_absolute_error(y_test, preds)

print("✅ Model trained")
print("MAE:", round(mae, 2))

# =========================
# Save
# =========================
joblib.dump(model, "fpl_model.pkl")
print("💾 Model saved")
