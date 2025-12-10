"""
Tests for FeatureBuilder and feature alignment.

Ensures features match what the trained model expects.
"""
import pytest
import pandas as pd
import json
from pathlib import Path


# Skip tests if data files don't exist
@pytest.fixture
def check_data_files():
    """Check if required data files exist."""
    import config
    if not config.RESULTS_WITH_FEATURES.exists():
        pytest.skip("Historical data not found - run add_features.py first")
    if not config.MODEL_METADATA.exists():
        pytest.skip("Model metadata not found - run train_model_v2.py first")


@pytest.fixture
def feature_builder(check_data_files):
    """Create a FeatureBuilder instance."""
    from src.features.builder import FeatureBuilder
    return FeatureBuilder(load_h2h=True)


@pytest.fixture
def model_metadata(check_data_files):
    """Load model metadata."""
    import config
    with open(config.MODEL_METADATA, 'r') as f:
        return json.load(f)


class TestFeatureAlignment:
    """Tests that features align with trained model expectations."""

    def test_model_input_has_expected_columns(self, feature_builder, model_metadata):
        """Prepared input should have exactly the columns the model expects."""
        rider_features = feature_builder.get_rider_features("Eli Iserbyt", "Men Elite")
        rider_features.features["h2h_field_score"] = 0.5  # Add H2H manually
        X = feature_builder.prepare_model_input(rider_features)

        expected_features = set(model_metadata['features'])
        actual_features = set(X.columns.tolist())

        assert actual_features == expected_features, (
            f"Feature mismatch!\n"
            f"Missing: {expected_features - actual_features}\n"
            f"Extra: {actual_features - expected_features}"
        )

    def test_model_input_column_order(self, feature_builder, model_metadata):
        """Columns should be in exact order model expects."""
        rider_features = feature_builder.get_rider_features("Eli Iserbyt", "Men Elite")
        rider_features.features["h2h_field_score"] = 0.5
        X = feature_builder.prepare_model_input(rider_features)

        assert X.columns.tolist() == model_metadata['features']

    def test_no_nan_in_output(self, feature_builder):
        """Prepared input should have no NaN values."""
        rider_features = feature_builder.get_rider_features("Eli Iserbyt", "Men Elite")
        rider_features.features["h2h_field_score"] = 0.5
        X = feature_builder.prepare_model_input(rider_features)

        assert not X.isna().any().any(), f"NaN values found in: {X.columns[X.isna().any()].tolist()}"

    def test_new_rider_has_correct_flag(self, feature_builder):
        """New riders should have is_new_rider=1."""
        # Use a name unlikely to exist in data
        rider_features = feature_builder.get_rider_features(
            "NONEXISTENT Rider XYZ123",
            "Men Elite"
        )
        assert rider_features.is_new_rider == True
        assert rider_features.features["is_new_rider"] == 1

    def test_known_rider_has_correct_flag(self, feature_builder):
        """Known riders should have is_new_rider=0."""
        # Eli Iserbyt should definitely be in the data
        rider_features = feature_builder.get_rider_features("ISERBYT Eli", "Men Elite")
        if rider_features.status == "found":
            assert rider_features.is_new_rider == False
            assert rider_features.features["is_new_rider"] == 0


class TestFeatureValues:
    """Tests for reasonable feature values."""

    def test_uci_points_normalized_range(self, feature_builder):
        """UCI points should be normalized to [0, 1]."""
        rider_features = feature_builder.get_rider_features("ISERBYT Eli", "Men Elite")
        uci = rider_features.features["uci_points_normalized"]
        assert 0 <= uci <= 1, f"UCI points normalized out of range: {uci}"

    def test_category_flags_correct(self, feature_builder):
        """is_elite and is_women should match category."""
        # Men Elite
        rf = feature_builder.get_rider_features("ISERBYT Eli", "Men Elite")
        assert rf.features["is_elite"] == 1
        assert rf.features["is_women"] == 0

        # Women Elite
        rf = feature_builder.get_rider_features("BRAND Lucinda", "Women Elite")
        assert rf.features["is_elite"] == 1
        assert rf.features["is_women"] == 1

    def test_races_so_far_capped(self, feature_builder):
        """races_so_far should be capped at 10."""
        rider_features = feature_builder.get_rider_features("ISERBYT Eli", "Men Elite")
        if rider_features.status == "found":
            races = rider_features.features["races_so_far"]
            assert races <= 10, f"races_so_far not capped: {races}"


class TestH2HFeatures:
    """Tests for head-to-head feature calculation."""

    def test_h2h_score_range(self, feature_builder):
        """H2H score should be in [0, 1]."""
        rider_features = feature_builder.get_rider_features("ISERBYT Eli", "Men Elite")
        field = ["Eli Iserbyt", "Laurens Sweeck", "Thibau Nys"]
        feature_builder.add_h2h_features(rider_features, "Eli Iserbyt", field)

        h2h = rider_features.features["h2h_field_score"]
        assert 0 <= h2h <= 1, f"H2H score out of range: {h2h}"

    def test_h2h_confidence_stored(self, feature_builder):
        """H2H confidence should be stored on rider_features."""
        rider_features = feature_builder.get_rider_features("ISERBYT Eli", "Men Elite")
        field = ["Eli Iserbyt", "Laurens Sweeck", "Thibau Nys"]
        feature_builder.add_h2h_features(rider_features, "Eli Iserbyt", field)

        assert hasattr(rider_features, 'h2h_confidence')
        assert 0 <= rider_features.h2h_confidence <= 1


class TestDNSRiskDetection:
    """Tests for DNS risk detection."""

    def test_dns_not_flagged_for_normal_rider(self, feature_builder):
        """Active riders should not be flagged as DNS risk."""
        rider_features = feature_builder.get_rider_features("ISERBYT Eli", "Men Elite")
        # Override with normal values
        rider_features.features["days_since_last_race"] = 7
        rider_features.features["races_so_far"] = 5

        is_dns, reason = feature_builder.check_dns_risk(rider_features)
        assert not is_dns

    def test_dns_flagged_for_long_absence(self, feature_builder):
        """Riders with long absence should be flagged."""
        rider_features = feature_builder.get_rider_features("ISERBYT Eli", "Men Elite")
        rider_features.features["days_since_last_race"] = 30  # Over threshold

        is_dns, reason = feature_builder.check_dns_risk(rider_features)
        assert is_dns
        assert "days since last race" in reason.lower()
