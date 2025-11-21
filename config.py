"""
Configuration file for VeloPredict
Centralizes all paths, hyperparameters, and settings
"""
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = DATA_DIR / "results"
CLEAN_DIR = DATA_DIR / "clean"
RAW_DIR = DATA_DIR / "raw"
MODELS_DIR = PROJECT_ROOT / "models"
APP_DIR = PROJECT_ROOT / "app"

# Data files
RESULTS_ALL = CLEAN_DIR / "results_all.csv"
RESULTS_WITH_FEATURES = CLEAN_DIR / "results_with_features.csv"

# Model files
TOP10_MODEL = MODELS_DIR / "top10_classifier.joblib"
TOP3_MODEL = MODELS_DIR / "top3_classifier.joblib"
MODEL_METADATA = MODELS_DIR / "model_metadata.json"

# Feature configuration
NUMERIC_FEATURES = [
    "uci_points_normalized",
    "races_so_far",
    "avg_place_last3",
    "best_place_last5",
    "last_place",
    "days_since_last_race",
    "last_carried_points",
    "last_scored_points",
    "top3_rate_career",
    "top10_rate_career",
    "series_appearances",
    "is_elite",
    "is_women"
]

CATEGORICAL_FEATURES = [
    "points_tier",
    "team_tier"
]

# Top teams in cyclocross (for team_tier feature)
TOP_TEAMS = [
    "ALPECIN", "DECEUNINCK", "BALOISE", "TREK", "LIONS",
    "PAUWELS", "SAUZEN", "CRELAN", "CORENDON",
    "VISMA", "LEASE", "BIKE", "INTERMARCHE", "CIRCUS"
]

# Model hyperparameters
MODEL_PARAMS = {
    "n_estimators": 300,
    "max_depth": 15,
    "min_samples_split": 10,
    "random_state": 42,
    "n_jobs": -1,
    "class_weight": "balanced"
}

# Training configuration
TRAIN_TEST_SPLIT = 0.8  # 80% train, 20% test
MEDIAN_PLACE_DEFAULT = 25  # For missing historical data

# NaN fill values for features
FILL_VALUES = {
    "uci_points_normalized": 0,
    "races_so_far": 0,
    "avg_place_last3": MEDIAN_PLACE_DEFAULT,
    "best_place_last5": MEDIAN_PLACE_DEFAULT,
    "last_place": MEDIAN_PLACE_DEFAULT,
    "days_since_last_race": 14,
    "last_carried_points": 0,
    "last_scored_points": 0,
    "top3_rate_career": 0,
    "top10_rate_career": 0,
    "series_appearances": 0,
    "is_elite": 0,
    "is_women": 0
}

# Categories
ELITE_CATEGORIES = ["Men Elite", "Women Elite"]
U23_CATEGORIES = ["Men U23", "Women U23"]
JUNIOR_CATEGORIES = ["Men Junior", "Women Junior"]

# Business metrics
TARGET_TOP10_ACCURACY = 0.80  # 80% accuracy goal
TARGET_TOP3_ACCURACY = 0.70  # 70% podium accuracy goal

# Streamlit app settings
APP_TITLE = "VeloPredict: Cyclocross Race Predictions"
APP_DESCRIPTION = "AI-powered predictions for cyclocross races with 80%+ Top-10 accuracy"
