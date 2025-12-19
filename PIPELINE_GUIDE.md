# VeloPredict Pipeline Guide

**Purpose:** Step-by-step operational tasks for validating predictions and updating the model after each race.

---

## Full Pipeline Task List (After Race Results)

When race results come in, execute these tasks in order:

| # | Task | Files Modified | Auto/Manual |
|---|------|----------------|-------------|
| 1 | **Load predictions** | Read `data/clean/predictions_*.csv` | Manual |
| 2 | **Load results** | Read `data/results/Results_*.csv` | Manual |
| 3 | **Match & calculate metrics** | Calculate recall, precision, high-conf | Manual |
| 4 | **Generate validation report** | Create `{RACE}_VALIDATION_RESULTS.md` | Manual |
| 5 | **Add results to training data** | `data/clean/results_with_features.csv` | `pipeline.py` |
| 6 | **Retrain model** | `models/*.joblib`, `models/model_metadata.json` | `pipeline.py` |
| 7 | **Update registry** | `data/clean/race_registry.json` | Manual (+ validation) |
| 8 | **Update VERSION_HISTORY.md** | Add new version section + validation | Manual |
| 9-11 | **Demo updates** | `app/demo.py` | **AUTO** (reads registry) |

**Key Change:** Demo (header, sidebar, footer) now auto-updates from registry!

---

## Demo Auto-Update System

As of v6.3, `app/demo.py` is **fully dynamic** - reads from:
- `data/clean/race_registry.json` - version, races, validation metrics
- `models/model_metadata.json` - accuracy, training date, feature importance, observations

**What's now automatic (ALL TABS):**

| Component | Source | Example |
|-----------|--------|---------|
| **Header** | registry + metadata | Version, race count, observations, precision |
| **Sidebar** | registry | Live validation for last 3 races |
| **Tab 3: Model Insights** | `metadata.feature_importance` | Top 5 features with percentages |
| **Tab 4: Season Tracker** | registry | Caption, chart axis ranges |
| **Tab 5: About** | metadata + registry | Accuracy, observations, races, validation |
| **Footer** | registry + metadata | Version, accuracy, H2H importance |

**What you still need to update manually:**
1. `race_registry.json` - add `validation` block with metrics after each race
2. `VERSION_HISTORY.md` - detailed version documentation (for portfolio)

**What auto-updates when you retrain:**
- `metadata.feature_importance` - all feature percentages
- `metadata.total_observations` - training data size
- `metadata.total_races` - number of races
- `metadata.top10_accuracy`, `top10_auc` - model metrics

---

## Registry Validation Schema

When adding validation results to registry, include:

```json
{
  "id": "namur_2025-12-14",
  "name": "Namur",
  "date": "2025-12-14",
  "series": "UCI World Cup",
  "version": "v6.1",
  "predictions": { ... },
  "results": { ... },
  "validation": {
    "precision": 75,
    "recall": 60,
    "high_conf_accuracy": 80,
    "notes": "Belgian depth, NEFF surprise",
    "distribution": {
      "low_pct": 84.3,
      "mid_pct": 0.8,
      "high_pct": 14.9,
      "mean_prob": 0.163,
      "std_prob": 0.318,
      "new_rider_count": 5,
      "field_size": 121
    }
  }
}
```

Once this is added, demo.py automatically displays it in the sidebar and Race-by-Race Analysis.

---

## Distribution Metrics

**New in v6.3:** Probability distribution analysis helps understand model confidence patterns.

### What It Measures

| Metric | Description |
|--------|-------------|
| `low_pct` | % of riders with <30% probability (non-contenders) |
| `mid_pct` | % of riders with 30-60% probability (uncertain zone) |
| `high_pct` | % of riders with >60% probability (likely contenders) |
| `mean_prob` | Average probability across all riders |
| `std_prob` | Standard deviation - higher = more variance |
| `new_rider_count` | Riders with no prior history (is_new_rider=1) |
| `field_size` | Total number of riders |

### Distribution Patterns

| Pattern | Mid-Range % | Meaning | Trust Level |
|---------|-------------|---------|-------------|
| **Bimodal** | <10% | Model is confident - clear favorites vs non-contenders | Higher |
| **Balanced** | >20% | Model is uncertain - many "coin flip" riders | Lower |
| **Moderate** | 10-20% | Typical race - some favorites, some uncertainty | Normal |

### Calculating Distribution Metrics

**For new races (automatic):**
```bash
python pipeline.py validate --predictions <file> --results <file>
# Distribution is calculated and printed automatically
```

**For backfilling existing races:**
```bash
python pipeline.py backfill-distribution
# Updates all races in registry with distribution metrics
```

### Where Distribution Appears

1. **Registry** - `validation.distribution` block in `race_registry.json`
2. **Demo Tab 3** - Race-by-Race Analysis section (auto-loaded from registry)
3. **Validation Reports** - Add to `{RACE}_VALIDATION_RESULTS.md` manually

---

## Detailed Task Breakdown

### 1. Load Predictions

```bash
# Find latest predictions for the race
ls data/clean/predictions_{race_name}*.csv
```

Use the most recent timestamp version (format: `YYYYMMDD_HHMM`).

### 2. Load Results

Results files follow format:
```
data/results/Results__{Series}__{Race}__{Category}__{Date}__{Location}.csv
```

Expected columns: `Position, Name, Team, Nationality, YOB, Time`

### 3. Match & Calculate Metrics

Key metrics to calculate:
- **Recall**: % of actual Top-10 we predicted (true positives / actual Top-10)
- **Precision**: % of predictions correct (true positives / predictions made)
- **High Confidence Accuracy**: % of >70% predictions correct
- **Podium Accuracy**: How many Top-3 predictions were correct

Threshold: 55% probability = predicted Top-10

### 4. Generate Validation Report

Create `{RACE}_VALIDATION_RESULTS.md` with:
- Combined metrics table
- Correct predictions (rider, position, probability)
- Missed Top-10 (false negatives)
- False positives (predicted but outside Top-10)
- Key insights and learnings

### 5. Add Results to Training Data

```bash
python pipeline.py add-results "data/results/{results_file}.csv" --skip-retrain
```

This:
- Parses results file
- Appends to `results_with_features.csv`
- Recomputes features (form, H2H, career rates)
- Registers race in registry

**Note:** For both Men + Women, run twice or handle Women manually if same race_id.

### 6. Retrain Model

```bash
python pipeline.py retrain
```

This:
- Loads updated training data
- Trains Top-10 and Top-3 classifiers
- Applies Platt scaling calibration
- Saves models and metadata

Record new metrics:
- Accuracy (%)
- AUC-ROC
- Observations count
- Feature importance (especially H2H %)

### 7. Update Registry

Edit `data/clean/race_registry.json`:

**A. Add validation metrics to race entry:**
```json
"validation": {
  "precision": 75,
  "recall": 60,
  "high_conf_accuracy": 80,
  "notes": "Brief note"
}
```

**B. Add new model version:**
```json
{
  "version": "v6.4",
  "accuracy": 82.6,
  "auc": 0.833,
  "observations": 9000,
  "innovation": "+RaceX Results"
}
```

**C. Update current_version:**
```json
"current_version": "v6.4"
```

### 8. Update VERSION_HISTORY.md

Add to:
1. **Evolution Overview table** - New row with version, accuracy, live validation
2. **Training Metrics table** - New row with full metrics
3. **Live Validation table** - New row with race results
4. **New version section** - Full breakdown (context, results, insights)
5. **Current Status section** - Update version, validation results, season totals

### 9-11. Demo Updates (NOW AUTOMATIC!)

No manual demo.py edits needed! Once you update the registry:
- Header auto-updates with version, race count, observations, precision
- Sidebar auto-shows last 3 validated races
- Footer auto-updates with version and accuracy

**To verify:** Run `streamlit run app/demo.py` and check all values match.

---

## Pre-Race Prediction Tasks

Before a race, run predictions:

| # | Task |
|---|------|
| 1 | Get startlist (CSV or manual entry) |
| 2 | Run `python predict_race.py {startlist}.csv` |
| 3 | Generate prediction report (`{RACE}_PREDICTIONS.md`) |
| 4 | Register predictions in `race_registry.json` |

---

## File Locations Reference

| File | Purpose |
|------|---------|
| `data/clean/results_with_features.csv` | Training data |
| `data/clean/race_registry.json` | Race + model version registry (SOURCE OF TRUTH) |
| `data/clean/predictions_*.csv` | Prediction outputs |
| `data/results/Results_*.csv` | Race results |
| `models/top10_classifier.joblib` | Top-10 model |
| `models/top3_classifier.joblib` | Top-3 model |
| `models/model_metadata.json` | Model metrics |
| `app/demo.py` | Streamlit dashboard (dynamic) |
| `VERSION_HISTORY.md` | Complete version documentation |
| `{RACE}_VALIDATION_RESULTS.md` | Per-race validation reports |
| `{RACE}_PREDICTIONS.md` | Per-race prediction reports |

---

## Quick Checklist

After each race:

- [ ] Load predictions + results
- [ ] Calculate recall, precision, high-conf accuracy
- [ ] Calculate distribution metrics (`python pipeline.py validate` does this automatically)
- [ ] Create `{RACE}_VALIDATION_RESULTS.md` (include distribution section)
- [ ] Add results to training data (Men + Women)
- [ ] Retrain model (new version)
- [ ] Update `race_registry.json`:
  - [ ] Add `validation` block to race (including `distribution`)
  - [ ] Add new model version
  - [ ] Update `current_version`
- [ ] Update `VERSION_HISTORY.md` (tables + new section)
- [ ] ~~Update demo.py~~ **(NOW AUTOMATIC!)**
- [ ] Verify demo displays correctly (check Race-by-Race Analysis for distribution)

---

*Last updated: 2025-12-14 (v6.3) - Demo now dynamic, distribution metrics added*
