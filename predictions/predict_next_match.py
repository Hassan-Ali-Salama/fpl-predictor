import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

df = pd.read_csv("training_data.csv")

X = df.drop("target_points", axis=1)
y = df["target_points"]

model = RandomForestRegressor(n_estimators=200, random_state=42)
model.fit(X, y)

print("✅ Model trained")

# مثال prediction (آخر مباراة)
latest_match = X.iloc[-1:].values
predicted_points = model.predict(latest_match)

print("🔮 Expected points next match:", round(predicted_points[0], 2))

