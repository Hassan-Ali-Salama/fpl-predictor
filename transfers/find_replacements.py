import json
import pandas as pd

# =========================
# Load fresh FPL data
# =========================
with open("bootstrap.json") as f:
    bootstrap = json.load(f)

elements = pd.DataFrame(bootstrap["elements"])

# =========================
# Map positions
# =========================
position_map = {
    1: "GK",
    2: "DEF",
    3: "MID",
    4: "FWD"
}

elements["position"] = elements["element_type"].map(position_map)

# =========================
# (اختياري) استبعاد الحراس
# =========================
elements = elements[elements["position"] != "GK"]

# =========================
# Predicted points (Baseline)
# =========================
# نستخدم points_per_game كبداية (Live ومتاح)
elements["predicted_points"] = elements["points_per_game"].astype(float)

# =========================
# Build candidates table
# =========================
candidates = elements[
    [
        "web_name",
        "position",
        "predicted_points",
        "now_cost"
    ]
].copy()

candidates.columns = [
    "player",
    "position",
    "predicted_points",
    "now_cost"
]

# تحويل السعر من int (مثلاً 54) → 5.4
candidates["now_cost"] = candidates["now_cost"] / 10

# =========================
# Save
# =========================
candidates.to_csv("all_candidates.csv", index=False)

print("✅ all_candidates.csv updated with live data")
