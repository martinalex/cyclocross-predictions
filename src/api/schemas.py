"""
Pydantic schemas for API request/response validation
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class RiderInput(BaseModel):
    """Single rider for prediction"""
    rider_name: str = Field(..., description="Full name of the rider")
    uci_points: Optional[float] = Field(None, description="UCI points carried")
    team: Optional[str] = Field(None, description="Team name")

    class Config:
        json_schema_extra = {
            "example": {
                "rider_name": "Thibau Nys",
                "uci_points": 850.0,
                "team": "Baloise Trek Lions"
            }
        }


class PredictionRequest(BaseModel):
    """Request for race predictions"""
    riders: List[RiderInput] = Field(..., description="List of riders in the race")
    category: str = Field("Men Elite", description="Race category")
    confidence_threshold: float = Field(0.55, ge=0.0, le=1.0, description="Minimum probability for Top-10 prediction")

    class Config:
        json_schema_extra = {
            "example": {
                "riders": [
                    {"rider_name": "Thibau Nys", "uci_points": 850.0, "team": "Baloise Trek Lions"},
                    {"rider_name": "Laurens Sweeck", "uci_points": 720.0, "team": "Crelan Corendon"}
                ],
                "category": "Men Elite",
                "confidence_threshold": 0.55
            }
        }


class RiderPrediction(BaseModel):
    """Prediction result for a single rider"""
    rider: str
    top10_probability: float = Field(..., ge=0.0, le=1.0)
    top3_probability: float = Field(..., ge=0.0, le=1.0)
    predicted_finish: str = Field(..., description="Top-10, Outside Top-10, or DNS Risk")
    confidence: str = Field(..., description="HIGH, MED, or LOW")
    recent_form: Optional[float] = Field(None, description="Average place in last 3 races")
    career_top10_rate: Optional[float] = Field(None, description="Career Top-10 finish rate")


class PredictionResponse(BaseModel):
    """Response with all predictions"""
    predictions: List[RiderPrediction]
    predicted_top10: List[str] = Field(..., description="Riders predicted to finish Top-10")
    predicted_podium: List[str] = Field(..., description="Top 3 podium predictions")
    model_version: str = Field(..., description="Model version used")
    calibration_method: str = Field(..., description="Calibration method applied")

    class Config:
        json_schema_extra = {
            "example": {
                "predictions": [
                    {
                        "rider": "Thibau Nys",
                        "top10_probability": 0.95,
                        "top3_probability": 0.87,
                        "predicted_finish": "Top-10",
                        "confidence": "HIGH",
                        "recent_form": 1.3,
                        "career_top10_rate": 0.92
                    }
                ],
                "predicted_top10": ["Thibau Nys", "Laurens Sweeck"],
                "predicted_podium": ["Thibau Nys", "Laurens Sweeck", "Joris Nieuwenhuis"],
                "model_version": "v4-calibrated",
                "calibration_method": "sigmoid (Platt scaling)"
            }
        }


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    model_loaded: bool
    model_accuracy: Optional[float] = None
    last_trained: Optional[str] = None
