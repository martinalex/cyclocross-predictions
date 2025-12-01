# Exploration Notebooks (Archive)

These Jupyter notebooks were used for initial exploration and prototyping.

**Production code is in `/src` and root `.py` files.**

## Notebooks

- `01_merge_results.ipynb` - Initial data merging exploration
- `02_extract_startlists.ipynb` - Startlist extraction prototypes
- `03_build_model_dataset.ipynb` - Dataset construction experiments
- `04_train_baseline_model.ipynb` - Initial model training
- `05_predict_upcoming_races.ipynb` - Early prediction logic

## Migration Status

All notebook logic has been refactored into production modules:
- Data pipeline → `rebuild_data.py`, `add_features.py`
- Model training → `train_model_v2.py`
- Predictions → `predict_race.py`
- API → `src/api/main.py`
