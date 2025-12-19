"""
Pydantic schemas for API request/response validation
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class RiderInput(BaseModel):
    """Single rider for prediction"""
    rider_name: str = Field(..., description="Full name of the rider")
    uci_rank: Optional[int] = Field(None, description="UCI ranking position")
    uci_points: Optional[float] = Field(None, description="UCI points carried (deprecated, use uci_rank)")
    team: Optional[str] = Field(None, description="Team name")

    class Config:
        json_schema_extra = {
            "example": {
                "rider_name": "Thibau Nys",
                "uci_rank": 5,
                "team": "Baloise Trek Lions"
            }
        }


class PredictionRequest(BaseModel):
    """Request for race predictions"""
    riders: List[RiderInput] = Field(..., description="List of riders in the race")
    category: str = Field("Men Elite", description="Race category")
    confidence_threshold: Optional[float] = Field(
        None, ge=0.0, le=1.0,
        description="Minimum probability for Top-10 prediction (default from config)"
    )
    enable_dns_filter: bool = Field(False, description="DEPRECATED - DNS filter disabled (was causing false flags)")
    enable_new_rider_discount: bool = Field(True, description="Apply discount to new riders")

    class Config:
        json_schema_extra = {
            "example": {
                "riders": [
                    {"rider_name": "Thibau Nys", "uci_rank": 5, "team": "Baloise Trek Lions"},
                    {"rider_name": "Laurens Sweeck", "uci_rank": 8, "team": "Crelan Corendon"}
                ],
                "category": "Men Elite",
                "confidence_threshold": 0.55,
                "enable_dns_filter": False,
                "enable_new_rider_discount": True
            }
        }


class RiderPrediction(BaseModel):
    """Prediction result for a single rider"""
    rider: str
    top10_probability: float = Field(..., ge=0.0, le=1.0)
    top3_probability: float = Field(..., ge=0.0, le=1.0)
    predicted_finish: str = Field(..., description="Top-10, Outside Top-10, or DNS Risk")
    confidence: str = Field(..., description="HIGH, MED, or LOW")
    h2h_field_score: float = Field(..., ge=0.0, le=1.0, description="Head-to-head win rate vs field")
    h2h_confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in H2H score (% of field with data)")
    is_new_rider: bool = Field(..., description="True if rider has no historical data")
    dns_risk: bool = Field(..., description="True if rider flagged as unlikely to start")
    dns_reason: Optional[str] = Field(None, description="Reason for DNS risk flag")
    recent_form: Optional[float] = Field(None, description="Average place in last 3 races")
    career_top10_rate: Optional[float] = Field(None, description="Career Top-10 finish rate")


class PredictionResponse(BaseModel):
    """Response with all predictions"""
    predictions: List[RiderPrediction]
    predicted_top10: List[str] = Field(..., description="Riders predicted to finish Top-10")
    predicted_podium: List[str] = Field(..., description="Top 3 podium predictions")
    model_version: str = Field(..., description="Model version used")
    calibration_method: str = Field(..., description="Calibration method applied")
    confidence_threshold: float = Field(..., description="Threshold used for predictions")

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
                        "h2h_field_score": 0.78,
                        "h2h_confidence": 0.85,
                        "is_new_rider": False,
                        "dns_risk": False,
                        "dns_reason": None,
                        "recent_form": 1.3,
                        "career_top10_rate": 0.92
                    }
                ],
                "predicted_top10": ["Thibau Nys", "Laurens Sweeck"],
                "predicted_podium": ["Thibau Nys", "Laurens Sweeck", "Joris Nieuwenhuis"],
                "model_version": "v6-unified",
                "calibration_method": "sigmoid (Platt scaling)",
                "confidence_threshold": 0.55
            }
        }


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    model_loaded: bool
    model_accuracy: Optional[float] = None
    last_trained: Optional[str] = None
