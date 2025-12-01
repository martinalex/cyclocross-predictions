"""
FastAPI application for VeloPredict
Serves calibrated ML models for cyclocross race predictions
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import joblib
import json
import pandas as pd
from pathlib import Path
from typing import List
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.api.schemas import (
    PredictionRequest,
    PredictionResponse,
    RiderPrediction,
    HealthResponse
)
import config

# Initialize FastAPI app
app = FastAPI(
    title="VeloPredict API",
    description="AI-powered cyclocross race predictions with 90% Top-10 accuracy",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model storage
models = {
    "top10": None,
    "top3": None,
    "metadata": None,
    "historical_data": None
}


def normalize_name(name: str) -> str:
    """Normalize rider name for matching"""
    if pd.isna(name):
        return ""
    name = str(name).strip().lower()
    name = (
        name.replace("é", "e").replace("è", "e").replace("ë", "e")
            .replace("ó", "o").replace("ò", "o").replace("ö", "o")
            .replace("á", "a").replace("à", "a").replace("ä", "a")
            .replace("ü", "u").replace("ï", "i").replace("ř", "r")
            .replace("ž", "z").replace("š", "s").replace("č", "c")
    )
    return name


def get_rider_features(rider_name: str, historical_data: pd.DataFrame, category: str = "Men Elite"):
    """Get latest features for a rider from historical data"""
    norm_name = normalize_name(rider_name)
    historical_data["rider_name_norm"] = historical_data["rider_name"].apply(normalize_name)

    # Try different name formats
    parts = norm_name.split()
    if len(parts) >= 2:
        reversed_name = f"{parts[-1]} {' '.join(parts[:-1])}"
    else:
        reversed_name = norm_name

    # Find rider's most recent race
    rider_history = historical_data[
        (
            (historical_data["rider_name_norm"] == norm_name) |
            (historical_data["rider_name_norm"] == reversed_name)
        ) &
        (historical_data["Category Name"].str.contains(category.split()[0], case=False, na=False))
    ].sort_values("race_date", ascending=False)

    if len(rider_history) > 0:
        latest = rider_history.iloc[0]
        features = {
            "uci_points_normalized": latest["uci_points_normalized"],
            "races_so_far": latest["races_so_far"] + 1,
            "avg_place_last3": latest["avg_place_last3"],
            "best_place_last5": latest["best_place_last5"],
            "last_place": latest["Place"],
            "days_since_last_race": 7,
            "last_carried_points": latest["Carried Points"],
            "last_scored_points": latest["Scored Points"],
            "top3_rate_career": latest["top3_rate_career"],
            "top10_rate_career": latest["top10_rate_career"],
            "series_appearances": 0,
            "is_elite": 1 if "Elite" in category else 0,
            "is_women": 1 if "Women" in category else 0,
            "points_tier": latest["points_tier"],
            "team_tier": latest["team_tier"]
        }
        return features, "found"
    else:
        # New rider - UCI-based inference
        uci_match = historical_data[
            (historical_data["rider_name_norm"] == norm_name) |
            (historical_data["rider_name_norm"] == reversed_name)
        ]

        uci_points_norm = uci_match.iloc[0]["uci_points_normalized"] if len(uci_match) > 0 else 0.1

        if uci_points_norm > 0:
            inferred_place = config.UCI_PLACE_INTERCEPT + config.UCI_PLACE_SLOPE * uci_points_norm
            inferred_place = max(5, min(70, inferred_place))
        else:
            inferred_place = config.MEDIAN_PLACE_DEFAULT

        features = {
            "uci_points_normalized": uci_points_norm,
            "races_so_far": 0,
            "avg_place_last3": inferred_place,
            "best_place_last5": inferred_place,
            "last_place": inferred_place,
            "days_since_last_race": 14,
            "last_carried_points": 0,
            "last_scored_points": 0,
            "top3_rate_career": 0,
            "top10_rate_career": 0,
            "series_appearances": 0,
            "is_elite": 1 if "Elite" in category else 0,
            "is_women": 1 if "Women" in category else 0,
            "points_tier": "low",
            "team_tier": "no_team"
        }
        return features, "new_rider"


@app.on_event("startup")
async def load_models():
    """Load models on startup"""
    try:
        models["top10"] = joblib.load(config.TOP10_MODEL)
        models["top3"] = joblib.load(config.TOP3_MODEL)

        with open(config.MODEL_METADATA, 'r') as f:
            models["metadata"] = json.load(f)

        models["historical_data"] = pd.read_csv(
            config.RESULTS_WITH_FEATURES,
            parse_dates=["race_date"]
        )

        print("✅ Models loaded successfully")
        print(f"   Top-10 accuracy: {models['metadata']['top10_accuracy']*100:.1f}%")
        print(f"   Calibration: {models['metadata']['calibration_method']}")

    except Exception as e:
        print(f"❌ Error loading models: {e}")
        raise


@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API info"""
    return {
        "name": "VeloPredict API",
        "version": "1.0.0",
        "description": "AI-powered cyclocross race predictions",
        "accuracy": "90% Top-10 (validated at Tabor UCI World Cup)",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "predict": "/predict"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy" if models["top10"] is not None else "unhealthy",
        model_loaded=models["top10"] is not None,
        model_accuracy=models["metadata"]["top10_accuracy"] if models["metadata"] else None,
        last_trained=models["metadata"]["training_date"] if models["metadata"] else None
    )


@app.post("/predict", response_model=PredictionResponse)
async def predict_race(request: PredictionRequest):
    """
    Predict Top-10 finishers for a cyclocross race

    - **riders**: List of riders with names (required), UCI points, and teams (optional)
    - **category**: Race category (default: "Men Elite")
    - **confidence_threshold**: Minimum probability for Top-10 prediction (default: 0.55)

    Returns predictions with probabilities, confidence levels, and podium forecast.
    """
    if models["top10"] is None:
        raise HTTPException(status_code=503, detail="Models not loaded")

    predictions = []

    for rider_input in request.riders:
        # Get features
        features, status = get_rider_features(
            rider_input.rider_name,
            models["historical_data"],
            request.category
        )

        # Prepare feature vector
        X = pd.DataFrame([features])
        X = pd.get_dummies(X, columns=["points_tier", "team_tier"], drop_first=True)

        # Align with training features
        for feat in models["metadata"]["features"]:
            if feat not in X.columns:
                X[feat] = 0
        X = X[models["metadata"]["features"]]

        # Fill any remaining NaN
        X = X.fillna(config.FILL_VALUES)

        # Predict with calibrated models
        top10_prob = models["top10"].predict_proba(X)[0][1]
        top3_prob = models["top3"].predict_proba(X)[0][1]

        # Determine prediction
        predicted_finish = "Top-10" if top10_prob > request.confidence_threshold else "Outside Top-10"

        # Confidence level
        if top10_prob > 0.7:
            confidence = "HIGH"
        elif top10_prob > 0.4:
            confidence = "MED"
        else:
            confidence = "LOW"

        predictions.append(RiderPrediction(
            rider=rider_input.rider_name,
            top10_probability=round(top10_prob, 4),
            top3_probability=round(top3_prob, 4),
            predicted_finish=predicted_finish,
            confidence=confidence,
            recent_form=features.get("avg_place_last3"),
            career_top10_rate=features.get("top10_rate_career")
        ))

    # Sort by Top-10 probability
    predictions_sorted = sorted(predictions, key=lambda x: x.top10_probability, reverse=True)

    # Get Top-10 predictions
    predicted_top10 = [
        p.rider for p in predictions_sorted
        if p.top10_probability > request.confidence_threshold
    ]

    # Get podium predictions (top 3 by Top-3 probability)
    podium_sorted = sorted(predictions, key=lambda x: x.top3_probability, reverse=True)
    predicted_podium = [p.rider for p in podium_sorted[:3]]

    return PredictionResponse(
        predictions=predictions_sorted,
        predicted_top10=predicted_top10,
        predicted_podium=predicted_podium,
        model_version="v4-calibrated",
        calibration_method=models["metadata"]["calibration_method"]
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
