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
from src.features.builder import FeatureBuilder
from src.features.names import standardize_name
import config

# Initialize FastAPI app
app = FastAPI(
    title="VeloPredict API",
    description="AI-powered cyclocross race predictions with 90% Top-10 accuracy",
    version="2.0.0",
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

# Global storage
models = {
    "top10": None,
    "top3": None,
    "metadata": None,
    "feature_builder": None
}


@app.on_event("startup")
async def load_models():
    """Load models and initialize FeatureBuilder on startup"""
    try:
        models["top10"] = joblib.load(config.TOP10_MODEL)
        models["top3"] = joblib.load(config.TOP3_MODEL)

        with open(config.MODEL_METADATA, 'r') as f:
            models["metadata"] = json.load(f)

        # Initialize unified FeatureBuilder (includes H2H)
        models["feature_builder"] = FeatureBuilder(load_h2h=True)

        print("Models loaded successfully")
        print(f"   Top-10 accuracy: {models['metadata']['top10_accuracy']*100:.1f}%")
        print(f"   Calibration: {models['metadata']['calibration_method']}")
        print(f"   H2H matrix: loaded")

    except Exception as e:
        print(f"Error loading models: {e}")
        raise


@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API info"""
    return {
        "name": "VeloPredict API",
        "version": "2.0.0",
        "description": "AI-powered cyclocross race predictions with H2H analysis",
        "accuracy": "90% Top-10 (validated at Tabor UCI World Cup)",
        "features": ["H2H analysis", "New rider discount", "DNS filtering"],
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

    - **riders**: List of riders with names (required), UCI rank (optional)
    - **category**: Race category (default: "Men Elite")
    - **confidence_threshold**: Minimum probability for Top-10 prediction (default from config)
    - **enable_dns_filter**: Filter riders unlikely to start (default: True)
    - **enable_new_rider_discount**: Apply discount to new riders (default: True)

    Returns predictions with probabilities, H2H scores, confidence levels, and podium forecast.
    """
    if models["top10"] is None:
        raise HTTPException(status_code=503, detail="Models not loaded")

    builder: FeatureBuilder = models["feature_builder"]
    threshold = request.confidence_threshold or config.CONFIDENCE_THRESHOLD

    # Build field list for H2H calculations
    field_names = [r.rider_name for r in request.riders]

    predictions = []

    for rider_input in request.riders:
        # Get features using unified FeatureBuilder
        rider_features = builder.get_rider_features(
            rider_input.rider_name,
            request.category,
            startlist_uci_rank=rider_input.uci_rank
        )

        # Add H2H features
        builder.add_h2h_features(rider_features, rider_input.rider_name, field_names)

        # Prepare model input (handles alignment and NaN filling)
        X = builder.prepare_model_input(rider_features)

        # Predict with calibrated models
        top10_prob = float(models["top10"].predict_proba(X)[0][1])
        top3_prob = float(models["top3"].predict_proba(X)[0][1])

        # Apply new rider discount (v6 feature)
        if request.enable_new_rider_discount and rider_features.is_new_rider:
            top10_prob *= config.NEW_RIDER_DISCOUNT
            top3_prob *= config.NEW_RIDER_DISCOUNT

        # Check DNS risk
        dns_risk = False
        dns_reason = ""
        if request.enable_dns_filter:
            dns_risk, dns_reason = builder.check_dns_risk(rider_features)

        # Determine prediction
        if dns_risk:
            predicted_finish = "DNS Risk"
        elif top10_prob > threshold:
            predicted_finish = "Top-10"
        else:
            predicted_finish = "Outside Top-10"

        # Confidence level
        if top10_prob > 0.7:
            confidence = "HIGH"
        elif top10_prob > 0.4:
            confidence = "MED"
        else:
            confidence = "LOW"

        # Get H2H score for response
        h2h_score = rider_features.features.get("h2h_field_score", 0.5)
        h2h_confidence = getattr(rider_features, 'h2h_confidence', 0.0)

        predictions.append(RiderPrediction(
            rider=rider_input.rider_name,
            top10_probability=round(top10_prob, 4),
            top3_probability=round(top3_prob, 4),
            predicted_finish=predicted_finish,
            confidence=confidence,
            h2h_field_score=round(h2h_score, 4),
            h2h_confidence=round(h2h_confidence, 4),
            is_new_rider=rider_features.is_new_rider,
            dns_risk=dns_risk,
            dns_reason=dns_reason if dns_risk else None,
            recent_form=rider_features.features.get("avg_place_last3"),
            career_top10_rate=rider_features.features.get("top10_rate_career")
        ))

    # Sort by Top-10 probability
    predictions_sorted = sorted(predictions, key=lambda x: x.top10_probability, reverse=True)

    # Get Top-10 predictions (excluding DNS risks)
    predicted_top10 = [
        p.rider for p in predictions_sorted
        if p.top10_probability > threshold and not p.dns_risk
    ]

    # Get podium predictions (top 3 by Top-3 probability, excluding DNS and requiring threshold)
    podium_candidates = [
        p for p in predictions_sorted
        if not p.dns_risk and p.top3_probability >= config.PODIUM_THRESHOLD
    ]
    podium_sorted = sorted(podium_candidates, key=lambda x: x.top3_probability, reverse=True)
    predicted_podium = [p.rider for p in podium_sorted[:3]]

    return PredictionResponse(
        predictions=predictions_sorted,
        predicted_top10=predicted_top10,
        predicted_podium=predicted_podium,
        model_version="v6-unified",
        calibration_method=models["metadata"]["calibration_method"],
        confidence_threshold=threshold
    )


@app.post("/predict/narrative")
async def predict_with_narrative(request: PredictionRequest, race_name: str = "Race"):
    """
    Predict Top-10 finishers with LLM-generated narrative analysis.

    Same as /predict but includes AI-generated race preview and rider insights.
    Requires ANTHROPIC_API_KEY environment variable.
    """
    # First get standard predictions
    prediction_response = await predict_race(request)

    # Convert to DataFrame for narrative generation
    predictions_data = []
    for p in prediction_response.predictions:
        predictions_data.append({
            "Rider": p.rider,
            "Top-10 Probability": p.top10_probability,
            "Top-3 Probability": p.top3_probability,
            "H2H Field Score": p.h2h_field_score,
            "H2H Confidence": p.h2h_confidence,
            "Recent Form": p.recent_form or 25,
            "Career Top-10 Rate": p.career_top10_rate or 0,
            "Status": "new_rider" if p.is_new_rider else "found"
        })

    df = pd.DataFrame(predictions_data)

    try:
        from src.llm.narratives import explain_predictions
        narratives = explain_predictions(df, race_name)

        return {
            "predictions": prediction_response.predictions,
            "predicted_top10": prediction_response.predicted_top10,
            "predicted_podium": prediction_response.predicted_podium,
            "model_version": prediction_response.model_version,
            "narrative": {
                "race_preview": narratives["race_preview"],
                "podium_prediction": narratives["podium_prediction"],
                "top_insights": narratives["top_insights"]
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=503,
            detail=f"LLM not configured: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Narrative generation failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
