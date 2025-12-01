# Quick Start Guide - VeloPredict v4

**5-minute setup to test the calibrated model**

---

## Prerequisites

- Python 3.12+
- pip installed
- Git (optional, for deployment)

---

## Step 1: Install Dependencies (2 min)

```bash
# Clone repository (if not already done)
git clone https://github.com/YOUR_USERNAME/cyclocross-predictions.git
cd cyclocross-predictions

# Install requirements
pip install -r requirements.txt
```

Expected packages:
- pandas, numpy, scikit-learn (ML)
- fastapi, uvicorn, pydantic (API)
- streamlit, plotly (demo UI)

---

## Step 2: Retrain Model with Calibration (1 min)

```bash
python3 train_model_v2.py
```

**What this does:**
- Loads 45 races (7,708 observations)
- Trains Random Forest (300 trees, depth 15)
- Applies Platt scaling calibration
- Saves to `models/top10_classifier.joblib` and `models/top3_classifier.joblib`

**Expected output:**
```
✓ TOP-10 ACCURACY: 80.2%
✓ Brier Score: 0.1834 (lower is better, 0.2 is good)
✓ Model calibrated
```

---

## Step 3: Test Predictions (CLI) (1 min)

```bash
# Option A: Use existing startlist
python3 predict_race.py \
  --startlist data/startlists/tabor_men_elite_2025-11-23.csv \
  --category "Men Elite"

# Option B: Create your own startlist CSV
# Format: rider_name,uci_points,team
# Then: python3 predict_race.py --startlist your_race.csv
```

**What you'll see:**
- Top-10 probability for each rider
- Predicted Top-10 finishers (threshold: 55%)
- Podium predictions (top 3)
- DNS risk warnings

---

## Step 4: Start API Server (1 min)

```bash
# Start server
./run_api.sh

# Or manually:
python3 -m uvicorn src.api.main:app --reload --port 8000
```

**Test it:**
1. Open http://localhost:8000
2. Go to http://localhost:8000/docs for Swagger UI
3. Try `/health` endpoint
4. Try `/predict` with sample data

**Sample API request:**
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "riders": [
      {"rider_name": "Thibau Nys", "uci_points": 850.0, "team": "Baloise Trek Lions"},
      {"rider_name": "Laurens Sweeck", "uci_points": 720.0}
    ],
    "category": "Men Elite",
    "confidence_threshold": 0.55
  }'
```

---

## Step 5: Run Streamlit Demo (Optional)

```bash
streamlit run app/demo.py
```

Opens browser at http://localhost:8501

**Features:**
- Interactive rider selection
- Probability predictions
- Model performance metrics
- Live validation results (Tabor)

---

## Common Issues

### Issue: `ModuleNotFoundError: No module named 'pandas'`
**Fix:** Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: `FileNotFoundError: models/top10_classifier.joblib`
**Fix:** Train the model first
```bash
python3 train_model_v2.py
```

### Issue: `ImportError: cannot import name 'CalibratedClassifierCV'`
**Fix:** Update scikit-learn
```bash
pip install --upgrade scikit-learn
```

### Issue: API returns 503 "Models not loaded"
**Fix:** Ensure models exist and paths are correct
```bash
ls models/  # Should see top10_classifier.joblib, top3_classifier.joblib
```

---

## Validate Against Live Race

After a race completes:

```bash
# 1. Generate predictions beforehand
python3 predict_race.py \
  --startlist data/startlists/upcoming_race.csv \
  --output predictions.csv

# 2. After race, download results and validate
python3 validate_predictions.py \
  --predictions predictions.csv \
  --results data/results/actual_results.csv
```

**Validation output:**
- Top-10 accuracy (%)
- Precision (%)
- Podium accuracy
- False positives/negatives breakdown

---

## Deploy Streamlit Demo (Free)

### Option 1: Streamlit Cloud (Easiest)

1. Push code to GitHub
2. Go to https://share.streamlit.io
3. Connect repository
4. Select `app/demo.py`
5. Deploy (takes 2-3 minutes)

### Option 2: Railway (API Deployment)

1. Install Railway CLI: `npm install -g @railway/cli`
2. Login: `railway login`
3. Init: `railway init`
4. Deploy: `railway up`
5. Get public URL from dashboard

---

## File Structure Reference

```
cyclocross-predictions/
├── train_model_v2.py          # 👈 Start here (retrain model)
├── predict_race.py            # 👈 CLI predictions
├── validate_predictions.py    # 👈 Validate against actuals
├── run_api.sh                 # 👈 Start API server
│
├── src/api/main.py            # FastAPI application
├── app/demo.py                # Streamlit demo
│
├── models/                    # Trained models (generated)
├── data/                      # Race data
└── notebooks/                 # Archived explorations
```

---

## Next Steps

### For Users
1. Test predictions on upcoming races
2. Compare against actual results
3. Provide feedback on accuracy

### For Developers
1. Read [CURRENT_VERSION.md](CURRENT_VERSION.md) for version details
2. Read [PHOENIX_LAUNCH.md](PHOENIX_LAUNCH.md) for ecosystem context
3. Read [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for recent changes

### For Reviewers (McKinsey/Deloitte)
1. Read [README.md](README.md) section "Why Classical ML"
2. Test API at http://localhost:8000/docs
3. Review [CURRENT_VERSION.md](CURRENT_VERSION.md) for technical decisions

---

## Performance Benchmarks

**Current model (v4-calibrated):**
- Training accuracy: 80.2%
- Tabor live validation: 90.0% (18/20 Top-10 correct)
- Flamanville validation: 80.0% (8/10 Top-10 correct)
- Expected precision: 60%+ (with 55% threshold)

---

## Support

**Questions?**
- Check [CURRENT_VERSION.md](CURRENT_VERSION.md)
- Check [README.md](README.md)
- GitHub Issues: [repository]/issues

**Want to contribute?**
- Test predictions on live races
- Report accuracy metrics
- Suggest feature improvements

---

*Ready in 5 minutes. Production-ready AI predictions for cyclocross races.*
