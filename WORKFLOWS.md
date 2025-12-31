# VeloPredict Workflows

**Single source of truth for all prediction and validation processes.**

**Last Updated:** December 27, 2025

---

## Quick Reference

| Task | Command | Time |
|------|---------|------|
| Generate predictions | `python pipeline.py predict <startlist.csv>` | ~30s |
| Validate race | `python pipeline.py validate-race ...` | ~15s |
| Add results to training | `python pipeline.py add-results <results.csv>` | ~45s |
| Retrain model | `python pipeline.py retrain` | ~60s |

---

## Terminology

To avoid confusion, here's what each term means:

| Term | Definition |
|------|------------|
| **Pipeline** | The main entry point (`pipeline.py`) - runs all workflows |
| **Workflow** | A complete end-to-end process (e.g., "Prediction Workflow") |
| **Command** | A specific action you run (e.g., `predict`, `validate-race`) |
| **Function** | Internal Python code that a command calls |

---

## Workflow 1: Generate Predictions

**When:** Before a race, once you have the startlist.

### Prerequisites

- Startlist CSV in `data/startlists/`
- Trained model in `models/`

### Steps

```
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 1: Add startlist file                                          │
├─────────────────────────────────────────────────────────────────────┤
│ Place your startlist CSV in data/startlists/                        │
│                                                                     │
│ Naming convention:                                                  │
│   Startlist__Series__City__Category__Date.csv                       │
│                                                                     │
│ Example:                                                            │
│   Startlist__X2O-Trofee__Hofstade__Men-Elite__2025-12-22.csv       │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 2: Run predict command                                         │
├─────────────────────────────────────────────────────────────────────┤
│ python pipeline.py predict \                                        │
│   data/startlists/Startlist__X2O-Trofee__Hofstade__Men-Elite__2025-12-22.csv │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ OUTPUTS                                                              │
├─────────────────────────────────────────────────────────────────────┤
│ 1. data/predictions/hofstade_men_elite_2025-12-22.csv               │
│    └── Raw predictions with probabilities                           │
│                                                                     │
│ 2. HOFSTADE_PREDICTIONS_2025-12-22.md                               │
│    └── Formatted report with top-10, podium, borderline            │
│                                                                     │
│ 3. data/clean/race_registry.json                                    │
│    └── Race registered (prediction_file path saved)                 │
└─────────────────────────────────────────────────────────────────────┘
```

### What Happens Internally

| Step | Function | File |
|------|----------|------|
| 1 | `parse_startlist_filename()` | Extracts race name, date, category |
| 2 | `load_startlist()` | Reads CSV, standardizes rider names |
| 3 | `predict_race()` | Runs model, calculates probabilities |
| 4 | `generate_predictions_report()` | Creates markdown report |
| 5 | `register_race()` | Adds to race_registry.json |

### Repeat for Each Category

Run the command twice - once for Men Elite, once for Women Elite:

```bash
# Men Elite
python pipeline.py predict data/startlists/Startlist__X2O-Trofee__Hofstade__Men-Elite__2025-12-22.csv

# Women Elite
python pipeline.py predict data/startlists/Startlist__X2O-Trofee__Hofstade__Women-Elite__2025-12-22.csv
```

Both categories are combined into one prediction report (e.g., `HOFSTADE_PREDICTIONS_2025-12-22.md`).

---

## Workflow 2: Validate Race Results

**When:** After a race, once you have the official results.

### Prerequisites

- Results CSV in `data/results/`
- Predictions CSV from Workflow 1

### Steps

```
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 1: Add results file                                            │
├─────────────────────────────────────────────────────────────────────┤
│ Place results CSV in data/results/                                  │
│                                                                     │
│ Naming convention:                                                  │
│   Results__Series__City__Category__Date.csv                         │
│                                                                     │
│ Example:                                                            │
│   Results__X2O-Trofee__Hofstade__Men-Elite__2025-12-22.csv         │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 2: Run validate-race command (Men Elite)                       │
├─────────────────────────────────────────────────────────────────────┤
│ python pipeline.py validate-race \                                  │
│   --predictions data/predictions/hofstade_men_elite_2025-12-22.csv \│
│   --results "data/results/Results__X2O-Trofee__Hofstade__Men-Elite__2025-12-22.csv" \│
│   --race-name Hofstade \                                            │
│   --race-date 2025-12-22 \                                          │
│   --category "Men Elite" \                                          │
│   --series "X2O-Trofee"                                             │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 3: Run validate-race command (Women Elite)                     │
├─────────────────────────────────────────────────────────────────────┤
│ python pipeline.py validate-race \                                  │
│   --predictions data/predictions/hofstade_women_elite_2025-12-22.csv\│
│   --results "data/results/Results__X2O-Trofee__Hofstade__Women-Elite__2025-12-22.csv" \│
│   --race-name Hofstade \                                            │
│   --race-date 2025-12-22 \                                          │
│   --category "Women Elite" \                                        │
│   --series "X2O-Trofee"                                             │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ OUTPUTS (auto-updated)                                               │
├─────────────────────────────────────────────────────────────────────┤
│ 1. SEASON_TRACKER.md                                                │
│    ├── Live Predictions table (adds row)                            │
│    ├── Race Details section (adds ME/WE breakdown)                  │
│    ├── Season Summary table (adds row)                              │
│    ├── Season Averages (auto-calculated)                            │
│    ├── Targets table (auto-updated)                                 │
│    ├── Distribution by Race table (adds row)                        │
│    ├── Distribution vs Accuracy table (adds row)                    │
│    └── ASCII trend charts (adds entry)                              │
│                                                                     │
│ 2. VERSION_HISTORY.md                                               │
│    └── Current Status - Season Totals table (adds row)              │
│                                                                     │
│ 3. HOFSTADE_VALIDATION_RESULTS.md                                   │
│    └── Detailed validation report                                   │
│                                                                     │
│ 4. data/clean/race_registry.json                                    │
│    └── Validation results saved                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### What Happens Internally

| Step | Function | What It Updates |
|------|----------|-----------------|
| 1 | `validate()` | Calculates Hits@10, Hits@3, Spearman, MAE |
| 2 | `update_registry_validation()` | race_registry.json |
| 3 | `update_season_tracker()` | SEASON_TRACKER.md - Live Predictions table |
| 4 | `add_race_details_to_tracker()` | SEASON_TRACKER.md - Details section |
| 5 | `update_season_summary_table()` | SEASON_TRACKER.md - Season Summary + calls #6 |
| 6 | `update_season_averages()` | SEASON_TRACKER.md - Averages + Targets tables |
| 7 | `update_distribution_tables()` | SEASON_TRACKER.md - Both distribution tables |
| 8 | `update_season_trend_charts()` | SEASON_TRACKER.md - ASCII charts |
| 9 | `update_version_history_current()` | VERSION_HISTORY.md - Season Totals |
| 10 | `generate_validation_report()` | Creates validation report markdown |

---

## Workflow 3: Add Results & Retrain Model

**When:** After validation, to incorporate new race data into the model.

### Prerequisites

- Validation complete (Workflow 2)
- Results CSVs in `data/results/`

### Steps

```
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 1: Add Men Elite results to training data                      │
├─────────────────────────────────────────────────────────────────────┤
│ python pipeline.py add-results \                                    │
│   "data/results/Results__X2O-Trofee__Hofstade__Men-Elite__2025-12-22.csv" \│
│   --skip-retrain                                                    │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 2: Add Women Elite results to training data                    │
├─────────────────────────────────────────────────────────────────────┤
│ python pipeline.py add-results \                                    │
│   "data/results/Results__X2O-Trofee__Hofstade__Women-Elite__2025-12-22.csv" \│
│   --skip-retrain                                                    │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 3: Retrain model                                                │
├─────────────────────────────────────────────────────────────────────┤
│ python pipeline.py retrain                                          │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ OUTPUTS (auto-updated)                                               │
├─────────────────────────────────────────────────────────────────────┤
│ 1. data/clean/results_with_features.csv                             │
│    └── Updated with new race observations                           │
│                                                                     │
│ 2. models/top10_classifier.joblib                                   │
│    └── Retrained model                                              │
│                                                                     │
│ 3. models/top3_classifier.joblib                                    │
│    └── Retrained model                                              │
│                                                                     │
│ 4. models/model_metadata.json                                       │
│    └── Updated version (v6.6 → v6.7), observations, accuracy        │
│                                                                     │
│ 5. SEASON_TRACKER.md                                                │
│    ├── Model version updated (header + footer)                      │
│    ├── Model Version History table (adds new version row)           │
│    └── Retraining History table (adds new version row)              │
│                                                                     │
│ 6. VERSION_HISTORY.md                                               │
│    ├── Evolution Overview table (adds new version row)              │
│    └── Training Metrics table (adds new version row)                │
│                                                                     │
│ 7. data/clean/race_registry.json                                    │
│    └── current_version bumped (v6.8→v6.9)                           │
└─────────────────────────────────────────────────────────────────────┘
```

### What Happens Internally

| Step | Function | What It Does |
|------|----------|--------------|
| 1 | `parse_results_file()` | Extracts race metadata from filename |
| 2 | `extract_features()` | Builds features for each rider |
| 3 | `append_to_training_data()` | Adds rows to results_with_features.csv |
| 4 | `update_h2h_matrix()` | Expands head-to-head pairs |
| 5 | `train_classifiers()` | Trains RandomForest models |
| 6 | `calibrate_probabilities()` | Applies Platt scaling |
| 7 | `save_models()` | Writes .joblib files |
| 8 | `update_model_metadata()` | Records stats in metadata |
| 9 | `update_model_version()` | Bumps version in registry (v6.8→v6.9) |
| 10 | `update_tracker_model_version()` | Updates SEASON_TRACKER.md header + footer |
| 11 | `update_evolution_overview_table()` | Adds row to VERSION_HISTORY Evolution |
| 12 | `update_training_metrics_table()` | Adds row to VERSION_HISTORY Metrics |
| 13 | `update_season_tracker_version_table()` | Adds row to SEASON_TRACKER Model Version History |
| 14 | `update_retraining_history_table()` | Adds row to SEASON_TRACKER Retraining History |

---

## Complete Race Day Workflow

Here's the full sequence from race day to model update:

```
RACE DAY MORNING                              AFTER RACE
─────────────────                             ───────────

┌──────────────┐                              ┌──────────────┐
│ 1. Get       │                              │ 4. Get       │
│    Startlist │                              │    Results   │
└──────┬───────┘                              └──────┬───────┘
       │                                             │
       ▼                                             ▼
┌──────────────┐                              ┌──────────────┐
│ 2. predict   │                              │ 5. validate- │
│    (ME)      │                              │    race (ME) │
└──────┬───────┘                              └──────┬───────┘
       │                                             │
       ▼                                             ▼
┌──────────────┐                              ┌──────────────┐
│ 3. predict   │                              │ 6. validate- │
│    (WE)      │                              │    race (WE) │
└──────┬───────┘                              └──────┬───────┘
       │                                             │
       ▼                                             ▼
┌──────────────┐                              ┌──────────────┐
│ Predictions  │                              │ 7. add-      │
│ Published    │                              │    results   │
└──────────────┘                              └──────┬───────┘
                                                     │
                                                     ▼
                                              ┌──────────────┐
                                              │ 8. retrain   │
                                              └──────┬───────┘
                                                     │
                                                     ▼
                                              ┌──────────────┐
                                              │ Model v6.N+1 │
                                              │ Ready        │
                                              └──────────────┘
```

---

## File Structure

```
cyclocross-predictions/
├── pipeline.py                    # Main entry point for all commands
├── predict_race.py                # Core prediction logic
├── config.py                      # Paths and settings
│
├── data/
│   ├── startlists/                # Input: startlist CSVs
│   ├── results/                   # Input: results CSVs
│   ├── predictions/               # Output: prediction CSVs
│   └── clean/
│       ├── results_with_features.csv   # Training data
│       └── race_registry.json          # Race tracking
│
├── models/
│   ├── top10_classifier.joblib   # Top-10 prediction model
│   ├── top3_classifier.joblib    # Podium prediction model
│   └── model_metadata.json       # Version, accuracy, features
│
├── src/
│   ├── features/
│   │   ├── builder.py            # Feature extraction
│   │   └── names.py              # Name standardization
│   └── models/
│       └── train.py              # Training logic
│
├── SEASON_TRACKER.md             # Season metrics (auto-updated)
├── VERSION_HISTORY.md            # Model history (auto-updated)
├── *_PREDICTIONS_*.md            # Prediction reports (generated)
└── *_VALIDATION_RESULTS.md       # Validation reports (generated)
```

---

## Metrics Reference

| Metric | What It Measures | Target |
|--------|------------------|--------|
| **Hits@10** | How many of our 10 predictions finished in actual top-10 | 7+/10 |
| **Hits@3** | How many of our 3 podium picks made actual podium | 2+/3 |
| **Spearman ρ** | Rank correlation between predicted and actual order | >0.5 |
| **MAE Rank** | Average positions off for our predicted top-10 | <3 |

---

## Workflow 4: LTR A/B Test Validation

**When:** After validating with v6.x model, compare LTR predictions.

### Prerequisites

- LTR predictions generated with `predict_race_ltr.py`
- v6.x predictions generated with `pipeline.py predict`
- Results CSVs in `data/results/`

### Steps

```
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 1: Generate LTR predictions (before race)                      │
├─────────────────────────────────────────────────────────────────────┤
│ python predict_race_ltr.py \                                        │
│   data/startlists/Startlist__Superprestige__Diegem__Men-Elite__2025-12-30.csv│
│                                                                     │
│ python predict_race_ltr.py \                                        │
│   data/startlists/Startlist__Superprestige__Diegem__Women-Elite__2025-12-30.csv│
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 2: Run validate-race-ltr command (Men Elite)                   │
├─────────────────────────────────────────────────────────────────────┤
│ python pipeline.py validate-race-ltr \                              │
│   --ltr-predictions data/clean/predictions_ltr_diegem_men_elite_*.csv \│
│   --v6-predictions data/clean/predictions_diegem_men_elite_*.csv \  │
│   --results "data/results/Results__Superprestige__Diegem__Men-Elite__*.csv" \│
│   --race-name Diegem \                                              │
│   --race-date 2025-12-30 \                                          │
│   --category "Men Elite" \                                          │
│   --series Superprestige                                            │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 3: Run validate-race-ltr command (Women Elite)                 │
├─────────────────────────────────────────────────────────────────────┤
│ python pipeline.py validate-race-ltr \                              │
│   --ltr-predictions data/clean/predictions_ltr_diegem_women_elite_*.csv \│
│   --v6-predictions data/clean/predictions_diegem_women_elite_*.csv \│
│   --results "data/results/Results__Superprestige__Diegem__Women-Elite__*.csv" \│
│   --race-name Diegem \                                              │
│   --race-date 2025-12-30 \                                          │
│   --category "Women Elite" \                                        │
│   --series Superprestige                                            │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ OUTPUTS (auto-updated)                                               │
├─────────────────────────────────────────────────────────────────────┤
│ 1. LTR_EXPERIMENT.md                                                │
│    ├── Validation Summary table (adds rows for ME/WE)               │
│    └── Aggregate Results table (recalculated)                       │
│                                                                     │
│ 2. data/clean/ltr_validation_results.json                           │
│    └── Complete validation data for all races                       │
│                                                                     │
│ 3. DIEGEM_LTR_PREDICTIONS_2025-12-30.md                             │
│    └── Validation results section appended                          │
└─────────────────────────────────────────────────────────────────────┘
```

### What Happens Internally

| Step | Function | What It Updates |
|------|----------|-----------------|
| 1 | `validate()` | Validates v6.x predictions, returns metrics |
| 2 | `validate_ltr_predictions()` | Validates LTR predictions, returns metrics |
| 3 | `update_ltr_experiment()` | Calls `add_validation()` from update_ltr_experiment.py |
| 4 | `generate_ltr_validation_report()` | Appends validation to LTR predictions MD |

### Files Involved

| File | Purpose |
|------|---------|
| `predict_race_ltr.py` | Generate LTR predictions |
| `train_model_ltr.py` | Train/retrain LTR model |
| `update_ltr_experiment.py` | Update experiment documentation |
| `models/ltr_ranker.joblib` | Trained LTR model |
| `models/ltr_metadata.json` | LTR model metadata |
| `LTR_EXPERIMENT.md` | A/B test results summary |
| `data/clean/ltr_validation_results.json` | Raw validation data |

---

## Troubleshooting

### "Rider not found" during validation

The name in predictions doesn't match results. Check:
- Accented characters (ZEMANOVÁ vs ZEMANOVA)
- Name order (FIRST LAST vs LAST FIRST)
- Spaces and hyphens

### Model accuracy dropped after retrain

Normal variance. The model incorporates new data which may shift weights. Monitor over multiple races.

### Prediction report has wrong filename

Check `parse_startlist_filename()` in pipeline.py. It expects format:
`Startlist__Series__City__Category__Date.csv`

### validate-race doesn't update SEASON_TRACKER.md

Check that section headers match exactly:
- `### Live Predictions (v6.4+)`
- `| Race        | Low (<30%) |` for distribution table

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Dec 22, 2025 | Initial documentation |
| 1.1 | Dec 30, 2025 | Added Workflow 4: LTR A/B Test Validation |

---

*This document is the single source of truth for VeloPredict workflows.*
