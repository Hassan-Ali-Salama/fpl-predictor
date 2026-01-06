# ⚽ FPL Predictor – Fantasy Premier League AI Assistant

A comprehensive, end-to-end automation tool designed to leverage machine learning for optimizing your Fantasy Premier League (FPL) team every Gameweek.

---

## ✨ Key Features

| Icon | Feature | Description |
| :---: | :--- | :--- |
| 🔮 | **Gameweek Point Prediction** | Predicts the next Gameweek points for all players using a trained ML model. |
| 🧠 | **Machine Learning Model** | Utilizes a **Random Forest** model trained on historical FPL data, rolling form, and fixture difficulty. |
| 👥 | **Team Analysis** | Analyzes your current FPL team (via Entry ID) to identify weaknesses and opportunities. |
| 🔁 | **Transfer Optimization** | Suggests the best 1-transfer and 2-transfer (-4 hit) options, focusing exclusively on **starting XI players**. |
| 🧢 | **Captain Suggestion** | Recommends the optimal captain choice based on predicted points. |
| 📊 | **Data-Driven Insights** | Incorporates metrics like rolling form, fixture difficulty, and consistency scores into predictions. |

---

## 🚀 Getting Started

Follow these steps to set up the project and run the FPL prediction workflow.

### Prerequisites

You need **Python 3.8+** installed on your system.

### 1. Installation

Clone the repository and set up your environment.

```bash
# 1. Clone the repository
git clone https://github.com/Hassan-Ali-Salama/fpl-predictor.git
cd fpl-predictor

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

### 2. Usage Workflow

The project is designed to be run in a sequential, 7-step workflow.

#### Step 1: Fetch Live FPL Data
Download the latest player and fixture data from the FPL API.

```bash
python scripts/fetch_fpl_data.py
python scripts/fetch_player_history.py
```

#### Step 2: Build the Dataset
Process the raw data to create the feature set for the ML model, including fixture difficulty and consistency scores.

```bash
python dataset/build_fixture_difficulty.py
python dataset/build_global_dataset.py
python dataset/build_consistency_scores.py
python dataset/preprocess.py
```

#### Step 3: Train the Prediction Model
Train the Random Forest model on the newly built dataset. **It is recommended to retrain the model weekly.**

```bash
python model/train_model.py
```

#### Step 4: Analyze Your Team
Analyze your specific FPL team. **Remember to replace `7552960` with your actual FPL Entry ID.**

```bash
# Replace 7552960 with your FPL Entry ID
python scripts/get_team_picks.py --entry YOUR_ENTRY_ID
python team/analyze_my_team.py
```

#### Step 5: Generate Predictions
Predict the next Gameweek points for the top players.

```bash
python predictions/predict_top10.py
```

#### Step 6: Suggest Transfers
Identify the optimal 1-transfer and 2-transfer options based on predicted points and team analysis.

```bash
python transfers/suggest_best_transfer.py
python transfers/suggest_top10_transfers.py
python transfers/suggest_two_transfers.py
```

#### Step 7: Pick the Best Captain
Determine the best captain choice from your current squad for the next Gameweek.

```bash
python captain/suggest_best_captain.py
```

---

## ⚠️ Important Notes

*   **Weekly Retraining:** The model is highly sensitive to recent form and fixture changes. Weekly retraining (Step 3) is strongly recommended for optimal performance.
*   **Gameweek Awareness:** All predictions and suggestions are automatically aware of the next upcoming Gameweek.
*   **Starter-Only Transfers:** Transfer suggestions are limited to improving your starting XI; bench players are excluded from the transfer logic.

---

## 💡 Future Enhancements

The following features are planned for future development:

*   **Automation:** Integration with n8n for workflow automation.
*   **User Interface:** Development of a web dashboard for easier interaction.
*   **Notifications:** Creation of a Telegram bot for instant alerts and suggestions.
*   **Chip Optimization:** Logic for optimizing the use of chips (Wildcard, Bench Boost, Triple Captain).

---

## ❤️ Attribution

Built with love for FPL nerds.
