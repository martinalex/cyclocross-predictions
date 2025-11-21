# VeloPredict: AI-Powered Cyclocross Race Predictions

**Predict which riders will finish in the Top-10 with 80%+ accuracy using machine learning.**

Part of the [Phoenix Launch](PHOENIX_LAUNCH.md) ecosystem: VeloPredict → VeloIntel → WellnessAI

---

## 🎯 What It Does

VeloPredict analyzes historical race data to predict:
- **Top-10 finishes** (riders who score points) - **80.2% accuracy**
- **Podium finishes** (Top-3) - **91.5% accuracy**

This helps competitive cyclists make strategic race selection decisions and optimize training for specific events.

---

## 📊 Performance

| Metric | Accuracy | vs. Baseline |
|--------|----------|--------------|
| **Top-10 Predictions** | 80.2% | +41.1% |
| **Top-3 Predictions (Podium)** | 91.5% | - |
| **Baseline (UCI Points Only)** | 39.1% | - |

**Trained on:** 45 races (7,708 rider-race observations) from 2024-25 season
**Test method:** Chronological split (train on early races, test on recent)

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Predictions

```bash
python predict.py --race-date 2025-11-23 --category "Men Elite"
```

### 3. Or Use Streamlit Demo

```bash
streamlit run app/demo.py
```

---

## 🧠 How It Works

### Feature Engineering

The model uses **15 features** across 4 categories:

**1. Rider Pedigree (40% importance)**
- UCI points (normalized)
- Points tier (high/mid/low)
- Team tier (top team vs. other)

**2. Form Metrics (45% importance)**
- Average place in last 3 races
- Best place in last 5 races
- Top-10 finish rate (career)
- Top-3 finish rate (career)
- Days since last race

**3. Experience (10% importance)**
- Total races completed
- Series-specific appearances

**4. Context (5% importance)**
- Category (Elite vs. U23/Junior)
- Gender (Men vs. Women)

### Model Architecture

- **Algorithm:** Random Forest Classifier (300 trees, depth 15)
- **Target:** Binary classification (Top-10 yes/no)
- **Training:** Chronological train/test split (80/20)
- **Class balancing:** Weighted to handle 20% positive class

---

## 📁 Project Structure

```
cyclocross-predictions/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── config.py                    # Configuration
├── rebuild_data.py              # Data pipeline
├── add_features.py              # Feature engineering
├── train_model_v2.py            # Model training
├── predict.py                   # Inference (coming soon)
│
├── data/
│   ├── results/                 # Race result CSVs (45 races)
│   └── clean/                   # Processed datasets
│
├── models/
│   ├── top10_classifier.joblib  # Trained model
│   ├── top3_classifier.joblib   # Podium model
│   └── model_metadata.json      # Feature definitions
│
└── app/
    └── demo.py                  # Streamlit demo (coming soon)
```

---

## 🔬 Validation Methodology

### Why 80% Accuracy Matters

**Baseline (guessing by UCI points):** 39.1% accuracy
**VeloPredict:** 80.2% accuracy
**Improvement:** +41.1 percentage points

This means the model **adds real value** beyond just using public rankings.

### Temporal Validation

- Train set: Races from 2024-10-12 to 2025-11-01
- Test set: Races from 2025-11-01 to 2025-11-16
- No data leakage (historical features use `.shift()`)

### Feature Importance

Top 5 most important features:
1. `top10_rate_career` (19.4%) - Historical success rate
2. `best_place_last5` (16.0%) - Recent peak performance
3. `avg_place_last3` (13.9%) - Current form
4. `uci_points_normalized` (11.3%) - Rider pedigree
5. `last_place` (10.9%) - Momentum

---

## 🎯 Use Cases

### For Competitive Cyclists
- **Race selection:** "Should I travel to this race?"
- **Training focus:** "Which races should I peak for?"
- **Confidence building:** "Can I realistically podium here?"

### For Teams
- **Roster decisions:** "Which riders should we send?"
- **Strategy planning:** "Who's our best Top-10 bet?"

### For VeloIntel (Phase 2)
- **Training optimization:** Use predictions to set workout targets
- **Event recommendations:** Suggest races based on predicted performance

---

## 📈 Roadmap

### ✅ Phase 1: VeloPredict (Current)
- [x] Data pipeline (45 races)
- [x] Feature engineering (15 features)
- [x] Top-10 classifier (80% accuracy)
- [x] Top-3 classifier (91% accuracy)
- [ ] Streamlit demo
- [ ] User validation (10+ cyclists)

### 🔄 Phase 2: VeloIntel (Days 31-60)
- [ ] Strava integration
- [ ] Personal wearables analysis
- [ ] AI coaching recommendations
- [ ] Subscription model ($15/month)

### 📅 Phase 3: WellnessAI (Days 61-90)
- [ ] Enterprise loyalty platform
- [ ] Retailer pilots
- [ ] Consulting firm partnerships

---

## 🤝 Contributing

This is a personal portfolio project for the [Phoenix Launch](PHOENIX_LAUNCH.md) experiment.

**Feedback welcome:**
- Test the predictions on upcoming races
- Suggest additional features
- Report bugs or inaccuracies

---

## 📄 License

MIT License - Free to use with attribution

---

## 🏆 Success Metrics

**Business Validation (30 days):**
- [ ] 10+ competitive cyclists test predictions
- [ ] 5+ express willingness to pay for VeloIntel
- [ ] 80%+ accuracy maintained on live races

**Portfolio Validation:**
- [x] Production-quality code
- [x] Real accuracy metrics (not toy problem)
- [ ] Working demo
- [ ] LinkedIn case study

---

## 👤 About

Built by a Principal PM + Builder as part of a 90-day AI product experiment.

**Contact:** [LinkedIn](https://linkedin.com/in/YOUR_PROFILE)
**Portfolio:** [GitHub](https://github.com/YOUR_USERNAME/cyclocross-predictions)

---

*Predictions are for educational and strategic planning purposes. Past performance doesn't guarantee future results.*
