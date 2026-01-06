import json
import pandas as pd

with open("bootstrap_data.json") as f:
    data = json.load(f)

players = data["elements"]

df = pd.DataFrame(players)

print(df.head())
print("\nColumns:\n", df.columns)

