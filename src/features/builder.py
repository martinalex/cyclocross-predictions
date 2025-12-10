"""
Unified FeatureBuilder for VeloPredict.

This module provides consistent feature extraction across CLI, API, and Streamlit.
All feature building logic is centralized here to ensure predictions are identical
regardless of which interface is used.
"""
import pandas as pd
import numpy as np
import json
import joblib
from pathlib import Path
from dataclasses import dataclass

import config
from src.features.names import normalize_name, standardize_name
from head_to_head import get_h2h_matrix, calculate_h2h_features


@dataclass
class RiderFeatures:
    """Container for rider features and metadata."""
    features: dict
    status: str  # 'found', 'new_rider'
    is_new_rider: bool
    inference_source: str | None = None


class FeatureBuilder:
    """
    Unified feature extraction for race predictions.

    Handles:
    - Historical data lookup
    - UCI rankings integration
    - Head-to-head calculations
    - New rider inference
    - Feature alignment with trained model

    Usage:
        builder = FeatureBuilder()
        features = builder.get_rider_features("LASTNAME Firstname", "Men Elite")
        X = builder.prepare_model_input(features, field_names)
    """

    def __init__(self, load_h2h: bool = True):
        """
        Initialize FeatureBuilder with all required data.

        Args:
            load_h2h: Whether to load H2H matrix (set False for faster init if not needed)
        """
        self.historical_data = self._load_historical_data()
        self.uci_rankings = self._load_uci_rankings()
        self.model_metadata = self._load_model_metadata()
        self.h2h_matrix = get_h2h_matrix() if load_h2h else None

        # Pre-compute standardized names for faster lookup
        if "rider_name_norm" not in self.historical_data.columns:
            self.historical_data["rider_name_norm"] = self.historical_data["rider_name"].apply(standardize_name)

    def _load_historical_data(self) -> pd.DataFrame:
        """Load historical rider data for feature lookup."""
        return pd.read_csv(config.RESULTS_WITH_FEATURES, parse_dates=["race_date"])

    def _load_uci_rankings(self) -> dict:
        """Load centralized UCI rankings."""
        rankings = {}

        # Men Elite
        men_path = config.CLEAN_DIR / "uci_rankings_men_elite.csv"
        if men_path.exists():
            men = pd.read_csv(men_path)
            for _, row in men.iterrows():
                name_norm = standardize_name(row["Rider"])
                if name_norm:
                    rankings[name_norm] = {
                        "rank": row["Rank"],
                        "points": row["Points"],
                        "category": "Men Elite"
                    }

        # Women Elite
        women_path = config.CLEAN_DIR / "uci_rankings_women_elite.csv"
        if women_path.exists():
            women = pd.read_csv(women_path)
            for _, row in women.iterrows():
                name_norm = standardize_name(row["Rider"])
                if name_norm:
                    rankings[name_norm] = {
                        "rank": row["Rank"],
                        "points": row["Points"],
                        "category": "Women Elite"
                    }

        return rankings

    def _load_model_metadata(self) -> dict:
        """Load trained model metadata for feature alignment."""
        with open(config.MODEL_METADATA, 'r') as f:
            return json.load(f)

    def get_rider_features(
        self,
        rider_name: str,
        category: str = "Men Elite",
        startlist_uci_rank: float | None = None
    ) -> RiderFeatures:
        """
        Get features for a rider from historical data or infer for new riders.

        Args:
            rider_name: Rider name from startlist (any format)
            category: Race category (e.g., "Men Elite", "Women Elite")
            startlist_uci_rank: UCI rank from startlist (fallback for new riders)

        Returns:
            RiderFeatures with extracted/inferred features and status
        """
        std_name = standardize_name(rider_name)

        # Extract first/last name for partial matching
        parts = std_name.split() if std_name else []
        if len(parts) >= 2:
            first_name = parts[0]
            last_name = parts[-1]
        else:
            first_name = std_name or ""
            last_name = std_name or ""

        # Build match conditions
        category_mask = self.historical_data["Category Name"].str.contains(
            category.split()[0], case=False, na=False
        )

        # Exact match on standardized name
        exact_match = (self.historical_data["rider_name_norm"] == std_name) & category_mask

        # Partial match: both first name AND last name appear in historical name
        if first_name and last_name:
            partial_match = (
                self.historical_data["rider_name_norm"].str.contains(first_name, na=False, regex=False) &
                self.historical_data["rider_name_norm"].str.contains(last_name, na=False, regex=False)
            ) & category_mask
        else:
            partial_match = exact_match

        rider_history = self.historical_data[
            exact_match | partial_match
        ].sort_values("race_date", ascending=False)

        if len(rider_history) > 0:
            return self._extract_known_rider_features(
                rider_history, category, std_name, startlist_uci_rank
            )
        else:
            return self._infer_new_rider_features(
                category, std_name, first_name, last_name, startlist_uci_rank
            )

    def _extract_known_rider_features(
        self,
        rider_history: pd.DataFrame,
        category: str,
        std_name: str,
        startlist_uci_rank: float | None
    ) -> RiderFeatures:
        """Extract features for a rider with historical data."""
        latest = rider_history.iloc[0]

        # Get UCI points normalized - prefer centralized rankings over historical data
        max_uci_rank = 700
        if std_name in self.uci_rankings:
            uci_rank = self.uci_rankings[std_name]["rank"]
            uci_points_norm = min(uci_rank / max_uci_rank, 1.0)
        elif startlist_uci_rank is not None and not pd.isna(startlist_uci_rank) and startlist_uci_rank > 0:
            uci_points_norm = min(startlist_uci_rank / max_uci_rank, 1.0)
        else:
            uci_points_norm = latest["uci_points_normalized"]

        # Cap races_so_far to avoid penalizing experienced riders
        races_so_far = min(latest["races_so_far"] + 1, 10)

        features = {
            "uci_points_normalized": uci_points_norm,
            "races_so_far": races_so_far,
            "avg_place_last3": latest["avg_place_last3"],
            "best_place_last5": latest["best_place_last5"],
            "last_place": latest["Place"],
            "days_since_last_race": 7,  # Assume weekly racing
            "last_carried_points": latest["Carried Points"],
            "last_scored_points": latest["Scored Points"],
            "top3_rate_career": latest["top3_rate_career"],
            "top10_rate_career": latest["top10_rate_career"],
            "series_appearances": 0,  # Reset for new series
            "is_elite": 1 if "Elite" in category else 0,
            "is_women": 1 if "Women" in category else 0,
            "is_new_rider": 0,  # Known rider with history
            "points_tier": latest["points_tier"],
            "team_tier": latest["team_tier"]
        }

        return RiderFeatures(
            features=features,
            status="found",
            is_new_rider=False
        )

    def _infer_new_rider_features(
        self,
        category: str,
        std_name: str,
        first_name: str,
        last_name: str,
        startlist_uci_rank: float | None
    ) -> RiderFeatures:
        """Infer features for a rider with no historical data."""
        max_uci_points = 3500
        max_uci_rank = 700

        # Priority order for UCI data:
        # 1. Centralized UCI rankings
        # 2. Startlist UCI rank
        # 3. Historical data match
        # 4. Default (weak rider)

        if std_name in self.uci_rankings:
            uci_rank = self.uci_rankings[std_name]["rank"]
            uci_points = self.uci_rankings[std_name]["points"]
            uci_points_norm = min(uci_rank / max_uci_rank, 1.0)
            inference_source = f"UCI rankings (rank {int(uci_rank)}, {int(uci_points)} pts)"

        elif startlist_uci_rank is not None and not pd.isna(startlist_uci_rank) and startlist_uci_rank > 0:
            uci_points_norm = min(startlist_uci_rank / max_uci_rank, 1.0)
            inference_source = f"startlist UCI rank {int(startlist_uci_rank)}"

        else:
            # Try partial match in historical data
            if first_name and last_name:
                uci_partial = (
                    self.historical_data["rider_name_norm"].str.contains(first_name, na=False, regex=False) &
                    self.historical_data["rider_name_norm"].str.contains(last_name, na=False, regex=False)
                )
            else:
                uci_partial = pd.Series([False] * len(self.historical_data))

            uci_match = self.historical_data[
                (self.historical_data["rider_name_norm"] == std_name) | uci_partial
            ]

            if len(uci_match) > 0:
                uci_points_norm = uci_match.iloc[0]["uci_points_normalized"]
                inference_source = f"historical UCI (norm={uci_points_norm:.3f})"
            else:
                uci_points_norm = 0.8  # High default = weak rider
                inference_source = "generic default (weak)"

        # Infer expected place from UCI points
        inferred_place = config.UCI_PLACE_INTERCEPT + config.UCI_PLACE_SLOPE * uci_points_norm
        inferred_place = max(5, min(70, inferred_place))

        features = {
            "uci_points_normalized": uci_points_norm,
            "races_so_far": 10,  # Neutral value
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
            "is_new_rider": 1,  # Flag as new rider
            "points_tier": "low",
            "team_tier": "no_team"
        }

        return RiderFeatures(
            features=features,
            status="new_rider",
            is_new_rider=True,
            inference_source=inference_source
        )

    def add_h2h_features(
        self,
        rider_features: RiderFeatures,
        rider_name: str,
        field_names: list[str]
    ) -> RiderFeatures:
        """
        Add head-to-head features against the race field.

        Args:
            rider_features: Existing rider features
            rider_name: Rider name (will be standardized)
            field_names: List of all rider names in the field

        Returns:
            Updated RiderFeatures with H2H score added
        """
        if self.h2h_matrix is None:
            rider_features.features["h2h_field_score"] = config.FILL_VALUES["h2h_field_score"]
            return rider_features

        std_name = standardize_name(rider_name)
        field_std = [standardize_name(n) for n in field_names if standardize_name(n)]

        h2h_result = calculate_h2h_features(std_name, field_std)
        rider_features.features["h2h_field_score"] = h2h_result["h2h_field_score"]

        # Store H2H metadata (not used by model, but useful for display)
        rider_features.h2h_confidence = h2h_result["h2h_confidence"]
        rider_features.h2h_known_opponents = h2h_result["h2h_known_opponents"]

        return rider_features

    def prepare_model_input(self, rider_features: RiderFeatures) -> pd.DataFrame:
        """
        Prepare feature vector aligned with trained model.

        Args:
            rider_features: RiderFeatures with all features populated

        Returns:
            DataFrame with single row, columns aligned to model's expected features
        """
        X = pd.DataFrame([rider_features.features])
        X = pd.get_dummies(X, columns=["points_tier", "team_tier"], drop_first=True)

        # Align with training features
        for feat in self.model_metadata['features']:
            if feat not in X.columns:
                X[feat] = 0
        X = X[self.model_metadata['features']]

        # Fill any remaining NaN
        X = X.fillna(config.FILL_VALUES)

        return X

    def check_dns_risk(self, rider_features: RiderFeatures) -> tuple[bool, str]:
        """
        Check if rider is at risk of DNS (Did Not Start).

        Args:
            rider_features: Rider features to check

        Returns:
            Tuple of (is_dns_risk, reason)
        """
        days_since = rider_features.features.get("days_since_last_race", 7)
        races_count = rider_features.features.get("races_so_far", 0)

        if days_since > 21:
            return True, f"DNS Risk: {days_since} days since last race"
        elif races_count < 2 and not rider_features.is_new_rider:
            return True, "DNS Risk: Only 1 race this season"

        return False, ""
