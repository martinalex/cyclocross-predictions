# VeloPredict Dashboard Update Guide

**All dashboard stats are now auto-calculated!** You only need to add file paths to `RACE_CONFIG`.

---

## Quick Reference: What to Update After Each Race

| Task | Location | What to Do |
|------|----------|------------|
| Add race data | `RACE_CONFIG` in `app/demo.py` (~line 321) | Add prediction & result file paths |
| Add model version | `VERSIONS` list (~line 366) | Only if you trained a new model |
| Add feature importance | `FEATURE_IMPORTANCE` dict (~line 376) | Only if you trained a new model |

**That's it!** All race stats (recall, precision, podium, predictions count) are auto-calculated from the files.

---

## Step 1: Add Race to RACE_CONFIG

Find `RACE_CONFIG` in `app/demo.py` (around line 321) and add your new race:

```python
RACE_CONFIG = {
    # ADD NEW RACE HERE (newest first):
    "Dublin (Dec 15)": {
        "name": "Dublin",
        "date": "Dec 15",
        "version": "v6",           # Model version used for predictions
        "threshold": 0.55,          # Confidence threshold used
        "predictions": {
            "M": "data/clean/predictions_dublin_men_elite.csv",
            "W": "data/clean/predictions_dublin_women_elite.csv",
        },
        "results": {
            "M": "data/results/Results__UCI-World-Cup__Dublin__Men-Elite__2025-12-15__Dublin-IRELAND.csv",
            "W": "data/results/Results__UCI-World-Cup__Dublin__Women-Elite__2025-12-15__Dublin-IRELAND.csv",
        }
    },
    # Existing races...
    "Sardinia (Dec 7)": { ... },
    "Flamanville (Nov 30)": { ... },
    "Tabor (Nov 23)": { ... },
}
```

### Required Files:

1. **Prediction files** (generate BEFORE race using `predict_race.py`):
   - Save predictions to `data/clean/predictions_<race>_<category>.csv`
   - Must have columns: `Rider`, `Top-10 Probability`, `Top-3 Probability`

2. **Result files** (download AFTER race):
   - Save to `data/results/Results__UCI-World-Cup__<Race>__<Category>__<Date>__<Location>.csv`
   - Must have columns: `Place` (or `Position`), `Name`

---

## Step 2: Update Model Version (Only If Training New Model)

If you trained a new model version, update `VERSIONS` (~line 366):

```python
VERSIONS = [
    # Existing versions...
    {"version": "v6", "accuracy": 77.6, "auc": 0.835, "observations": 8357, "innovation": "+New Rider"},
    # ADD NEW VERSION:
    {"version": "v7", "accuracy": 78.5, "auc": 0.842, "observations": 8500, "innovation": "+Feature Name"},
]
```

And update `FEATURE_IMPORTANCE` (~line 376) with feature importance from your new model:

```python
FEATURE_IMPORTANCE = {
    # Existing versions...
    "v6": {"avg_place_last3": 12.8, ...},
    # ADD NEW VERSION:
    "v7": {"h2h_field_score": 23.0, "avg_place_last3": 12.5, "best_place_last5": 12.0, "top10_rate_career": 12.0, "uci_points_normalized": 6.0},
}
```

---

## What Gets Auto-Calculated

The dashboard automatically calculates these stats from your prediction/result files:

| Stat | How It's Calculated |
|------|---------------------|
| **Recall (Accuracy)** | `correct Top-10 predictions / actual Top-10 finishers matched` |
| **Precision** | `correct predictions / total predictions above threshold` |
| **Podium** | `correct podium predictions / predictions with >30% Top-3 probability` |
| **Predictions** | Count of predictions above threshold |
| **Correct** | Count of predictions that finished Top-10 |

The "Key Insights" section also auto-calculates:
- Season average recall
- Best performing race
- AUC improvement trend
- Dataset growth percentage
- Top feature by importance

---

## Supported Result File Formats

The dashboard automatically handles various CSV formats:

| Format | Example | Source |
|--------|---------|--------|
| Standard UCI | `VANTHOURENHOUT Michael` | Most races |
| Multiline names | `THIBAU\nNYS` | Some exported results |
| All caps firstname-first | `LUCINDA BRAND` | Some exported results |

---

## Verification

After updating, run the demo to verify:

```bash
python -m streamlit run app/demo.py
```

Check:
- [ ] Season Tracker tab loads without errors
- [ ] New race appears in the 6-panel charts with correct stats
- [ ] New race is selectable in the Race-by-Race dropdown
- [ ] Scatter plot displays correctly
- [ ] Key Insights show updated averages

---

## Complete Workflow: Race Day to Dashboard

### Before Race:
1. Get startlist CSV
2. Run: `python predict_race.py --startlist data/startlists/race_startlist.csv`
3. Save predictions to `data/clean/predictions_<race>_<category>.csv`

### After Race:
1. Download results CSV to `data/results/`
2. Add race to `RACE_CONFIG` in `app/demo.py`
3. Run demo to verify: `streamlit run app/demo.py`
4. Commit changes

### If Training New Model:
1. Run: `python update_results.py` (add new race to training data)
2. Run: `python train_model_v2.py`
3. Update `VERSIONS` and `FEATURE_IMPORTANCE` in `app/demo.py`

---

## Notes

- Keep races in reverse chronological order (newest first) in `RACE_CONFIG`
- The scatter plot uses the same `RACE_CONFIG` - no duplicate data entry needed
- All charts update automatically when you add a new race
- Name matching uses `standardize_name()` for consistent rider identification across different CSV formats
