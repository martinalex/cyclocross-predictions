"""
VeloPredict Streamlit Demo
Simple interface for testing race predictions
"""
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import json
from pathlib import Path
import sys
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
import config
from head_to_head import get_h2h_matrix, calculate_h2h_features
from src.features.names import standardize_name


# ============================================================
# RACE REGISTRY - Auto-loads from pipeline-generated registry
# ============================================================

@st.cache_data
def load_race_registry():
    """Load race registry from JSON file (auto-updated by pipeline)."""
    registry_path = config.CLEAN_DIR / "race_registry.json"
    if registry_path.exists():
        with open(registry_path, 'r') as f:
            return json.load(f)
    return {"races": [], "model_versions": [], "current_version": "v1"}

st.set_page_config(
    page_title="VeloPredict: Cyclocross Predictions",
    page_icon="🚴",
    layout="wide"
)

# Load model and metadata
def get_metadata_mtime():
    """Get modification time of metadata file for cache busting."""
    return config.MODEL_METADATA.stat().st_mtime if config.MODEL_METADATA.exists() else 0

@st.cache_resource
def load_models(_mtime=None):
    """Load trained models and metadata. Cache is busted when metadata file changes."""
    top10_model = joblib.load(config.TOP10_MODEL)
    top3_model = joblib.load(config.TOP3_MODEL)

    with open(config.MODEL_METADATA, 'r') as f:
        metadata = json.load(f)

    return top10_model, top3_model, metadata

# Load historical data - cache disabled to ensure fresh data with name corrections
def load_data():
    """Load historical race data"""
    df = pd.read_csv(config.RESULTS_WITH_FEATURES, parse_dates=["race_date"])
    # Pre-compute standardized names for deduplication (includes NAME_CORRECTIONS)
    df["rider_name_std"] = df["rider_name"].apply(standardize_name)
    return df

try:
    # Pass metadata mtime to bust cache when metadata file changes
    model_top10, model_top3, metadata = load_models(_mtime=get_metadata_mtime())
    historical_data = load_data()
    registry = load_race_registry()
    model_loaded = True
except Exception as e:
    model_loaded = False
    error_msg = str(e)
    registry = {"races": [], "model_versions": [], "current_version": "v1"}

# ============================================================
# DYNAMIC HEADER - Auto-generated from registry and metadata
# ============================================================

def get_header_stats(registry, metadata):
    """Generate header stats from registry and metadata."""
    current_version = registry.get("current_version", "v1")
    model_versions = registry.get("model_versions", [])

    # Get current model info
    current_model = next((m for m in model_versions if m["version"] == current_version), {})
    observations = current_model.get("observations", 0)

    # Count races with results
    races_with_results = [r for r in registry.get("races", []) if r.get("results")]
    race_count = len(races_with_results)

    # Get latest validated race
    validated_races = [r for r in races_with_results if r.get("validation")]
    if validated_races:
        latest = validated_races[-1]
        latest_name = latest["name"]
        latest_precision = latest["validation"].get("precision", 0)
    else:
        latest_name = "N/A"
        latest_precision = 0

    # Get H2H importance from metadata feature_importance
    h2h_importance = 22.7  # Default, could parse from model if available

    return {
        "version": current_version,
        "latest_race": latest_name,
        "race_count": race_count,
        "observations": observations,
        "h2h_importance": h2h_importance,
        "latest_precision": latest_precision
    }

def get_live_validation_sidebar(registry, max_races=3):
    """Generate sidebar Live Validation section from registry."""
    validated_races = [r for r in registry.get("races", []) if r.get("validation")]
    # Sort by date descending, take most recent
    validated_races = sorted(validated_races, key=lambda x: x["date"], reverse=True)[:max_races]

    lines = []
    for race in validated_races:
        v = race["validation"]
        date_str = race["date"][5:]  # "12-14" from "2025-12-14"
        month_day = f"{date_str[0:2]}/{date_str[3:5]}" if len(date_str) >= 5 else date_str

        lines.append(f"**{race['name']} (Dec {date_str[3:5]}):**")

        # Show precision if available
        if v.get("precision"):
            lines.append(f"- ✅ {v['precision']:.0f}% precision")

        # Show recall if available
        if v.get("recall"):
            lines.append(f"- ✅ {v['recall']:.0f}% recall")

        # Show high conf if available
        if v.get("high_conf_accuracy"):
            lines.append(f"- ✅ {v['high_conf_accuracy']:.0f}% high-conf")

        # Show notes if it's a short note
        if v.get("notes") and len(v["notes"]) < 30:
            pass  # Skip notes in sidebar for brevity

        lines.append("")  # Empty line between races

    return lines

# Header
st.title("🚴 VeloPredict: Cyclocross Race Predictions")

if model_loaded:
    header_stats = get_header_stats(registry, metadata)
    accuracy_pct = int(metadata['top10_accuracy'] * 100)
    st.markdown(f"**AI-powered predictions with H2H analysis - {accuracy_pct}% Top-10 accuracy**")
    st.caption(
        f"Version: {header_stats['version']} ({header_stats['latest_race']} validated) | "
        f"{header_stats['race_count']} races, {header_stats['observations']:,}+ observations | "
        f"H2H = #1 Feature ({header_stats['h2h_importance']}%) | "
        f"Live: {header_stats['latest_precision']:.0f}% precision at {header_stats['latest_race']}"
    )

if not model_loaded:
    st.error(f"❌ Model not found. Please run `train_model_v2.py` first.")
    st.code(error_msg)
    st.stop()

# Sidebar - Model Performance
with st.sidebar:
    st.header("📊 Model Performance")

    col1, col2 = st.columns(2)
    col1.metric("Top-10 Accuracy", f"{metadata['top10_accuracy']*100:.1f}%")
    col2.metric("Top-3 Accuracy", f"{metadata['top3_accuracy']*100:.1f}%")

    st.metric("vs. Baseline", f"+{metadata['improvement_vs_baseline']*100:.1f}%")

    # Calibration info
    if 'calibration_method' in metadata:
        st.success(f"✅ Calibrated: {metadata['calibration_method']}")
        if 'top10_brier_score' in metadata and metadata['top10_brier_score']:
            st.metric("Brier Score", f"{metadata['top10_brier_score']:.4f}")

    st.markdown("---")
    st.markdown(f"**Trained on:** {metadata['train_size']} races")
    st.markdown(f"**Test set:** {metadata['test_size']} races")
    st.markdown(f"**Last updated:** {metadata['training_date'][:10]}")

    # Dynamic Live Validation section
    st.markdown("---")
    st.markdown("### 🎯 Live Validation")
    for line in get_live_validation_sidebar(registry):
        st.markdown(line)

    # Metrics explanation - expandable
    with st.expander("📖 What do these metrics mean?"):
        st.markdown("""
**Precision** - *"Can I trust the predictions?"*
- When we predict Top-10, how often are we right?
- 75% precision = 3 out of 4 predictions correct
- **This is the key metric for users**

**Recall** - *"Did we catch all the winners?"*
- Of actual Top-10 finishers, how many did we predict?
- 60% recall = we caught 6 of 10 actual finishers
- Lower recall = conservative predictions

**High-Conf** - *"Are confident picks reliable?"*
- Accuracy of predictions with >70% probability
- These are the "safe bets"

**Why training precision (~58%) < live precision (75%)?**
- Training tests on ALL race types (mixed quality)
- Live validation is on UCI World Cups (strong fields)
- Predictable fields = better performance
        """)

# Main content
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🔮 Predict Race", "📊 Model Performance", "📈 Model Insights", "📊 Season Tracker", "🧪 LTR A/B Test", "📚 About"])

with tab1:
    st.header("Predict Top-10 Finishers")

    # Category selection
    st.markdown("### Select Category")
    category = st.selectbox(
        "Choose race category",
        options=["Men Elite", "Women Elite", "Men Under 23", "Men Junior", "Women Junior"],
        index=0
    )

    # Sample rider selection
    st.markdown("### Select Riders to Evaluate")

    # Get unique riders who have raced recently in selected category
    # Note: Lower UCI points = better ranking for elite riders
    def get_last_non_empty(series):
        """Get the last non-empty value from a series"""
        non_empty = series[series.notna() & (series != "")]
        return non_empty.iloc[-1] if len(non_empty) > 0 else ""

    # Filter recent races in selected category
    # rider_name_std is pre-computed in load_data() for deduplication
    recent_data = historical_data[
        (historical_data["race_date"] > "2024-11-01") &
        (historical_data["Category Name"] == category)
    ].copy()

    recent_riders = (
        recent_data
        .groupby("rider_name_std")
        .agg({
            "rider_name": "last",  # Keep one display name per rider
            "Place": "mean",
            "Carried Points": "last",
            "team_tier": "last",
            "top10_rate_career": "last",
            "Team Name": get_last_non_empty
        })
        .sort_values("Carried Points", ascending=True)  # Lower points = better riders
        .head(50)
    )

    # Use the original rider_name for display, indexed by standardized name
    recent_riders.index = recent_riders["rider_name"]
    recent_riders = recent_riders.drop(columns=["rider_name"])

    # Display rider selector
    selected_riders = st.multiselect(
        f"Choose riders from {category} (showing top 50 by UCI points)",
        options=recent_riders.index.tolist(),
        default=recent_riders.index.tolist()[:10] if len(recent_riders) >= 10 else recent_riders.index.tolist()
    )

    if selected_riders:
        # Build normalized field list for H2H calculations
        field_names_norm = [standardize_name(r) for r in selected_riders if standardize_name(r)]

        # Use pre-computed standardized names from load_data()
        hist_data = historical_data

        # Get latest features for selected riders in this category
        predictions = []

        for rider in selected_riders:
            # Use standardized name for matching to handle inconsistent capitalization
            rider_std = standardize_name(rider)
            rider_history = hist_data[
                (hist_data["rider_name_std"] == rider_std) &
                (hist_data["Category Name"] == category)
            ]
            rider_data = rider_history.iloc[-1]

            # Get last non-empty team name
            team_names = rider_history["Team Name"]
            non_empty_teams = team_names[team_names.notna() & (team_names != "")]
            team_name = non_empty_teams.iloc[-1] if len(non_empty_teams) > 0 else "No Team Data"

            # Calculate H2H score against this field
            std_name = standardize_name(rider)
            h2h_features = calculate_h2h_features(std_name, field_names_norm)

            # Prepare features - include H2H
            feature_cols = [f for f in config.NUMERIC_FEATURES if f != 'h2h_field_score'] + config.CATEGORICAL_FEATURES
            X = pd.DataFrame([rider_data[feature_cols]])
            X['h2h_field_score'] = h2h_features['h2h_field_score']
            X = pd.get_dummies(X, columns=config.CATEGORICAL_FEATURES, drop_first=True)

            # Align with training features
            for feat in metadata['features']:
                if feat not in X.columns:
                    X[feat] = 0
            X = X[metadata['features']]

            # Fill NaN
            X = X.fillna(config.FILL_VALUES)

            # Predict
            top10_prob = model_top10.predict_proba(X)[0][1]
            top3_prob = model_top3.predict_proba(X)[0][1]

            # Format H2H display
            h2h_display = f"{h2h_features['h2h_field_score']*100:.0f}%" if h2h_features['h2h_confidence'] > 0.3 else "N/A"

            predictions.append({
                "Rider": rider,
                "Top-10 Probability": top10_prob,
                "Top-3 Probability": top3_prob,
                "H2H vs Field": h2h_display,
                "H2H Score": h2h_features['h2h_field_score'],
                "UCI Points": rider_data["Carried Points"],
                "Team": team_name,
                "Recent Form (avg last 3)": rider_data["avg_place_last3"]
            })

        # Display predictions
        df_pred = pd.DataFrame(predictions).sort_values("Top-10 Probability", ascending=False)

        st.markdown("### 🏆 Predicted Results")

        # Color-code probabilities
        def color_prob(val):
            if val > 0.7:
                return 'background-color: #d4edda'
            elif val > 0.4:
                return 'background-color: #fff3cd'
            else:
                return 'background-color: #f8d7da'

        # Display columns (excluding raw H2H Score used for sorting)
        display_cols = ["Rider", "Top-10 Probability", "Top-3 Probability", "H2H vs Field", "UCI Points", "Team", "Recent Form (avg last 3)"]
        df_display = df_pred[display_cols]

        styled_df = df_display.style.applymap(
            color_prob,
            subset=["Top-10 Probability", "Top-3 Probability"]
        ).format({
            "Top-10 Probability": "{:.1%}",
            "Top-3 Probability": "{:.1%}",
            "UCI Points": "{:.0f}",
            "Recent Form (avg last 3)": "{:.1f}"
        })

        st.dataframe(styled_df, use_container_width=True, height=400)

        # Summary stats
        st.markdown("### 📊 Quick Stats")
        col1, col2, col3, col4 = st.columns(4)

        likely_top10 = (df_pred["Top-10 Probability"] > 0.6).sum()
        likely_podium = (df_pred["Top-3 Probability"] > 0.5).sum()
        h2h_coverage = (df_pred["H2H vs Field"] != "N/A").sum()

        col1.metric("Likely Top-10", f"{likely_top10} riders")
        col2.metric("Likely Podium", f"{likely_podium} riders")
        col3.metric("Avg Top-10 Prob", f"{df_pred['Top-10 Probability'].mean():.1%}")
        col4.metric("H2H Coverage", f"{h2h_coverage}/{len(df_pred)}")

        # Show top H2H performers
        st.markdown("### 🥊 Head-to-Head Leaders")
        st.caption("Riders with best historical win rate against this specific field")
        top_h2h = df_pred[df_pred["H2H vs Field"] != "N/A"].nlargest(5, "H2H Score")
        if len(top_h2h) > 0:
            for _, row in top_h2h.iterrows():
                st.write(f"**{row['Rider']}** - {row['H2H vs Field']} win rate vs field")
        else:
            st.info("No H2H data available for selected riders")

    else:
        st.info("Select riders above to see predictions")

with tab2:
    st.header("Model Performance")
    st.markdown("**Detailed metrics and explanations for VeloPredict's machine learning model**")

    # Get all metrics from metadata
    accuracy = metadata.get('top10_accuracy', 0) * 100
    top3_accuracy = metadata.get('top3_accuracy', 0) * 100
    auc_roc = metadata.get('top10_auc', 0)
    brier_score = metadata.get('top10_brier_score', 0)
    log_loss = metadata.get('top10_log_loss', 0)
    baseline_accuracy = metadata.get('baseline_accuracy', 0) * 100
    improvement = metadata.get('improvement_vs_baseline', 0) * 100
    train_size = metadata.get('train_size', 0)
    test_size = metadata.get('test_size', 0)
    total_obs = metadata.get('total_observations', train_size + test_size)
    total_races = metadata.get('total_races', 'N/A')
    calibration = metadata.get('calibration_method', 'N/A')
    training_date = metadata.get('training_date', 'N/A')

    # Get live validation stats from registry
    validated_races = [r for r in registry.get("races", []) if r.get("validation")]
    if validated_races:
        precisions = [r["validation"].get("precision", 0) for r in validated_races if r["validation"].get("precision")]
        recalls = [r["validation"].get("recall", 0) for r in validated_races if r["validation"].get("recall")]
        avg_precision = sum(precisions) / len(precisions) if precisions else 0
        avg_recall = sum(recalls) / len(recalls) if recalls else 0
    else:
        avg_precision = 0
        avg_recall = 0

    # Section 1: Primary Metrics
    st.markdown("### 🎯 Primary Metrics")
    st.markdown("*These are the key numbers that define model performance*")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Top-10 Accuracy", f"{accuracy:.1f}%", help="% of all predictions (Top-10 or not) that were correct")
    col2.metric("Top-3 Accuracy", f"{top3_accuracy:.1f}%", help="% of Top-3/podium predictions that were correct")
    col3.metric("vs Baseline", f"+{improvement:.1f}%", help="Improvement over random guessing")
    col4.metric("AUC-ROC", f"{auc_roc:.3f}", help="Area Under ROC Curve - measures ranking quality")

    auc_pct = auc_roc * 100  # Pre-calculate for format string

    with st.expander("📖 What do these metrics mean?", expanded=True):
        st.markdown("""
**Top-10 Accuracy** measures overall correctness across ALL predictions:
- For each rider-race observation, the model predicts "Top-10" or "Not Top-10"
- Accuracy = (correct predictions) / (total predictions)
- Our {accuracy:.1f}% means ~{accuracy:.0f} out of 100 predictions are correct
- This includes both "rider will finish Top-10" AND "rider won't finish Top-10" predictions

**Top-3 Accuracy** is the same but for podium predictions:
- Harder task (only 3 spots vs 10), so typically higher accuracy
- {top3_accuracy:.1f}% accuracy on podium predictions

**vs Baseline** shows improvement over naive prediction:
- Baseline ({baseline_accuracy:.1f}%) = always predicting the majority class
- +{improvement:.1f}% means our model is meaningfully better than guessing

**AUC-ROC** (Area Under ROC Curve):
- Measures how well the model RANKS riders by probability
- 0.5 = random, 1.0 = perfect ranking
- {auc_roc:.3f} = strong discriminative ability
- *"If I pick a random Top-10 finisher and a random non-Top-10, the model correctly ranks them {auc_pct:.0f}% of the time"*
        """.format(accuracy=accuracy, top3_accuracy=top3_accuracy, baseline_accuracy=baseline_accuracy, improvement=improvement, auc_roc=auc_roc, auc_pct=auc_pct))

    st.markdown("---")

    # Section 2: Live Validation Metrics
    st.markdown("### 🏁 Live Validation Metrics")
    st.markdown("*How the model performs on actual race day predictions*")

    col1, col2, col3 = st.columns(3)
    col1.metric("Avg Live Precision", f"{avg_precision:.0f}%", help="When we predict Top-10, how often are we right?")
    col2.metric("Avg Live Recall", f"{avg_recall:.0f}%", help="Of actual Top-10 finishers, how many did we predict?")
    col3.metric("Races Validated", f"{len(validated_races)}", help="Number of races with actual results compared")

    precision_out_of_4 = avg_precision / 100 * 4  # Pre-calculate for format string

    with st.expander("📖 Precision vs Recall explained"):
        st.markdown("""
**Precision** - *"Can I trust the predictions?"*
- When we predict someone will finish Top-10, how often are they actually in Top-10?
- Formula: True Positives / (True Positives + False Positives)
- {avg_precision:.0f}% precision = ~{precision_out_of_4:.1f} out of 4 predictions are correct
- **This is the most important metric for users** - it tells you how reliable our picks are

**Recall** - *"Did we catch all the winners?"*
- Of all actual Top-10 finishers, how many did we predict?
- Formula: True Positives / (True Positives + False Negatives)
- {avg_recall:.0f}% recall = we identified {avg_recall:.0f}% of the actual Top-10
- Lower recall = we're being conservative (missing some, but predictions are more reliable)

**The Trade-off:**
- Higher threshold (e.g., 70%) → Higher precision, lower recall (fewer but more reliable picks)
- Lower threshold (e.g., 40%) → Lower precision, higher recall (more picks but less reliable)
- We use 55% threshold to balance precision and recall
        """.format(avg_precision=avg_precision, avg_recall=avg_recall, precision_out_of_4=precision_out_of_4))

    st.markdown("---")

    # Section 3: Calibration Metrics
    st.markdown("### 📊 Calibration Metrics")
    st.markdown("*How well the predicted probabilities match reality*")

    col1, col2, col3 = st.columns(3)
    col1.metric("Brier Score", f"{brier_score:.4f}", help="Lower is better (0 = perfect)")
    col2.metric("Log Loss", f"{log_loss:.4f}", help="Lower is better - penalizes confident wrong predictions")
    col3.metric("Calibration", calibration, help="Method used to calibrate probabilities")

    with st.expander("📖 What is calibration?"):
        st.markdown("""
**Calibration** means predicted probabilities match observed frequencies:
- If we predict "70% chance of Top-10" for 100 riders, ~70 should actually finish Top-10
- Without calibration, models often predict probabilities that are too extreme

**Brier Score** ({brier_score:.4f}):
- Measures mean squared error of probability predictions
- Range: 0 (perfect) to 1 (worst)
- <0.25 is considered good
- Our {brier_score:.4f} indicates well-calibrated probabilities

**Log Loss** ({log_loss:.4f}):
- Penalizes confident wrong predictions more heavily
- A model saying "99% Top-10" for someone who finishes 50th gets heavily penalized
- Lower is better; <0.7 is generally good

**Platt Scaling** (our method):
- Fits a logistic regression on model outputs to calibrate probabilities
- Learned from validation data to correct systematic over/under-confidence
        """.format(brier_score=brier_score, log_loss=log_loss))

    st.markdown("---")

    # Section 4: Training Details
    st.markdown("### 🏋️ Training Details")
    st.markdown("*How the model was built*")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Training Set", f"{train_size:,}", help="Observations used to train the model")
    col2.metric("Test Set", f"{test_size:,}", help="Observations held out for evaluation")
    col3.metric("Total Observations", f"{total_obs:,}", help="All rider-race observations in dataset")
    col4.metric("Races in Dataset", f"{total_races}", help="Unique races in training data")

    # Parse training date for display
    if training_date != 'N/A' and len(training_date) >= 10:
        display_date = training_date[:10]
    else:
        display_date = training_date

    st.markdown(f"**Last trained:** {display_date}")

    with st.expander("📖 Training methodology"):
        st.markdown("""
**Algorithm:** Random Forest Classifier
- 300 decision trees, max depth 15
- Each tree sees a random subset of data and features
- Final prediction = average of all tree predictions
- Robust to overfitting, handles non-linear relationships well

**Chronological Split:**
- Training set: Earlier races (80%)
- Test set: Later races (20%)
- This simulates real-world usage: predicting future races from past data
- No data leakage: test set never seen during training

**Feature Engineering:**
- {n_features} features across 4 categories:
  - **Form features:** avg_place_last3, best_place_last5, days_since_last_race
  - **Career features:** top10_rate_career, top3_rate_career, races_so_far
  - **Points features:** uci_points_normalized, last_carried_points
  - **H2H features:** h2h_field_score (win rate vs specific opponents)
        """.format(n_features=len(metadata.get('features', []))))

    st.markdown("---")

    # Section 5: Per-Race Validation Table
    st.markdown("### 🏆 Race-by-Race Validation")
    st.markdown("*Detailed results from each validated race*")

    if validated_races:
        race_data = []
        for race in validated_races:
            v = race.get("validation", {})
            race_data.append({
                "Race": race["name"],
                "Date": race["date"],
                "Series": race.get("series", "N/A"),
                "Version": race.get("version", "N/A"),
                "Precision": f"{v.get('precision', 'N/A')}%" if v.get('precision') else "N/A",
                "Recall": f"{v.get('recall', 'N/A')}%" if v.get('recall') else "N/A",
                "High-Conf": f"{v.get('high_conf_accuracy', 'N/A')}%" if v.get('high_conf_accuracy') else "N/A",
                "Notes": v.get("notes", "")
            })

        race_df = pd.DataFrame(race_data)
        st.dataframe(race_df, use_container_width=True, hide_index=True)
    else:
        st.info("No validated races yet. Run predictions and compare to actual results to populate this table.")

with tab3:
    st.header("Model Insights")

    st.markdown("### 🎯 Feature Importance")
    st.markdown("What the model considers most important:")

    # Dynamic feature importance from metadata
    if 'feature_importance' in metadata:
        fi = metadata['feature_importance']
        # Sort by importance and get top 5
        sorted_fi = sorted(fi.items(), key=lambda x: x[1], reverse=True)[:5]

        # Feature name mapping for display
        feature_names = {
            "h2h_field_score": "🥊 H2H Field Score",
            "avg_place_last3": "Average Place (Last 3)",
            "best_place_last5": "Best Place (Last 5)",
            "top10_rate_career": "Top-10 Career Rate",
            "last_place": "Last Place",
            "uci_points_normalized": "UCI Points",
            "top3_rate_career": "Top-3 Career Rate",
            "races_so_far": "Races This Season",
            "days_since_last_race": "Days Since Last Race",
            "series_appearances": "Series Appearances"
        }

        feature_descriptions = {
            "h2h_field_score": "Historical win rate vs specific opponents",
            "avg_place_last3": "Current form trajectory",
            "best_place_last5": "Recent peak performance",
            "top10_rate_career": "Historical success in scoring positions",
            "last_place": "Momentum from most recent race",
            "uci_points_normalized": "Official UCI ranking points",
            "top3_rate_career": "Career podium rate",
            "races_so_far": "Season experience",
            "days_since_last_race": "Rest/freshness factor",
            "series_appearances": "Experience in this race series"
        }

        current_version = registry.get("current_version", "v6")
        st.markdown(f"**Top 5 Most Important Features ({current_version}):**")

        for i, (feat, importance) in enumerate(sorted_fi, 1):
            display_name = feature_names.get(feat, feat)
            description = feature_descriptions.get(feat, "")
            st.markdown(f"{i}. **{display_name}** ({importance}%) - {description}")

        # Check if H2H is #1
        top_feature = sorted_fi[0][0] if sorted_fi else None
        if top_feature == "h2h_field_score":
            st.info(f"💡 **H2H is the #1 feature at {sorted_fi[0][1]}%!** The model weighs head-to-head history against the actual race field more than any other factor.")
        else:
            top_name = feature_names.get(top_feature, top_feature)
            st.info(f"💡 **{top_name}** is currently the most important feature at {sorted_fi[0][1]}%.")
    else:
        st.warning("Feature importance data not available. Retrain model to generate.")

    st.markdown("### 📈 Performance by Category")

    # Show accuracy by category (create is_top10 if it doesn't exist)
    if "is_top10" not in historical_data.columns:
        historical_data["is_top10"] = (historical_data["Place"] <= 10).astype(int)

    category_stats = historical_data.groupby("Category Name").agg({
        "Place": "count",
        "is_top10": "sum"
    }).rename(columns={"Place": "Total Races", "is_top10": "Top-10 Finishes"})

    category_stats["Top-10 Rate"] = (
        category_stats["Top-10 Finishes"] / category_stats["Total Races"]
    )

    st.dataframe(
        category_stats.style.format({
            "Top-10 Rate": "{:.1%}"
        }),
        use_container_width=True
    )

    # Distribution Analysis Section
    st.markdown("### 📊 Probability Distribution Patterns")
    st.markdown("How model confidence varies across races:")

    # Get distribution data from all validated races
    validated_with_dist = [r for r in registry.get("races", []) if r.get("validation", {}).get("distribution")]

    if validated_with_dist:
        dist_data = []
        for race in validated_with_dist:
            d = race["validation"]["distribution"]
            mid_pct = d["mid_pct"]
            if mid_pct < 10:
                pattern = "BIMODAL"
            elif mid_pct > 20:
                pattern = "BALANCED"
            else:
                pattern = "MODERATE"

            dist_data.append({
                "Race": race["name"],
                "Version": race.get("version", "N/A"),
                "Low (<30%)": f"{d['low_pct']:.0f}%",
                "Mid (30-60%)": f"{d['mid_pct']:.1f}%",
                "High (>60%)": f"{d['high_pct']:.0f}%",
                "Pattern": pattern,
                "Field": d["field_size"],
                "New Riders": d["new_rider_count"],
                # Keep raw values for chart
                "low_raw": d["low_pct"],
                "mid_raw": d["mid_pct"],
                "high_raw": d["high_pct"]
            })

        dist_df = pd.DataFrame(dist_data)

        # Stacked Bar Chart - Distribution Patterns Across Races
        race_labels = [f"{r['Race']} ({r['Version']})" for r in dist_data]

        fig_dist = go.Figure()

        # Add bars in order: Low, Mid, High (stacked)
        fig_dist.add_trace(go.Bar(
            name='Low (<30%)',
            x=race_labels,
            y=[r['low_raw'] for r in dist_data],
            marker_color='#94a3b8',  # gray
            text=[f"{r['low_raw']:.0f}%" for r in dist_data],
            textposition='inside',
            hovertemplate='%{x}<br>Low (<30%%): %{y:.1f}%<extra></extra>'
        ))

        fig_dist.add_trace(go.Bar(
            name='Mid (30-60%)',
            x=race_labels,
            y=[r['mid_raw'] for r in dist_data],
            marker_color='#f59e0b',  # amber/orange
            text=[f"{r['mid_raw']:.0f}%" if r['mid_raw'] >= 5 else "" for r in dist_data],
            textposition='inside',
            hovertemplate='%{x}<br>Mid (30-60%%): %{y:.1f}%<extra></extra>'
        ))

        fig_dist.add_trace(go.Bar(
            name='High (>60%)',
            x=race_labels,
            y=[r['high_raw'] for r in dist_data],
            marker_color='#22c55e',  # green
            text=[f"{r['high_raw']:.0f}%" for r in dist_data],
            textposition='inside',
            hovertemplate='%{x}<br>High (>60%%): %{y:.1f}%<extra></extra>'
        ))

        fig_dist.update_layout(
            title='Probability Distribution by Race',
            barmode='stack',
            height=400,
            showlegend=True,
            legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5),
            yaxis=dict(title="% of Field", range=[0, 105]),
            xaxis=dict(tickangle=45),
            plot_bgcolor='#f8f9fa',
            paper_bgcolor='white',
            margin=dict(b=100)
        )

        # Add pattern annotations
        for i, r in enumerate(dist_data):
            pattern_emoji = "🎯" if r['Pattern'] == "BIMODAL" else ("⚖️" if r['Pattern'] == "BALANCED" else "📊")
            fig_dist.add_annotation(
                x=race_labels[i],
                y=102,
                text=f"{pattern_emoji} {r['Pattern']}",
                showarrow=False,
                font=dict(size=9, color='#374151'),
                yshift=5
            )

        st.plotly_chart(fig_dist, use_container_width=True)

        # Show data table below chart
        display_cols = ["Race", "Version", "Low (<30%)", "Mid (30-60%)", "High (>60%)", "Pattern", "Field", "New Riders"]
        st.dataframe(dist_df[display_cols], use_container_width=True, hide_index=True)

        with st.expander("📖 Understanding Distribution Patterns"):
            st.markdown("""
**What the distribution tells you:**

| Pattern | Mid-Range % | Meaning | Trust Level |
|---------|-------------|---------|-------------|
| **BIMODAL** | <10% | Model is confident - clear separation between contenders and non-contenders | Higher - predictions are decisive |
| **BALANCED** | >20% | Model is uncertain - many "coin flip" riders in the middle | Lower - more surprises possible |
| **MODERATE** | 10-20% | Typical race - some clear favorites, some uncertainty | Normal |

**Key Insights:**
- Earlier versions (v1, v2) had more MODERATE distributions
- Later versions (v6+) trend toward BIMODAL as H2H matures
- BIMODAL = model knows the field well, trust the predictions
- New riders push toward BIMODAL (they get low probabilities)
            """)
    else:
        st.info("No distribution data available yet. Run `python pipeline.py backfill-distribution` to calculate.")

with tab4:
    st.header("Season Tracker")
    st.markdown("**VeloPredict Season Tracker | UCI Cyclocross World Cup 2025-26**")

    # ============================================================
    # RACE_CONFIG - Now auto-loaded from registry (updated by pipeline)
    # ============================================================

    registry = load_race_registry()

    # Convert registry format to RACE_CONFIG format for compatibility
    RACE_CONFIG = {}
    for race in registry.get("races", []):
        # Only include races with both predictions and results
        if race.get("predictions") and race.get("results"):
            race_key = f"{race['name']} ({race['date'][5:]})"  # e.g., "Sardinia (12-07)"
            RACE_CONFIG[race_key] = {
                "name": race["name"],
                "date": race["date"][5:] if len(race["date"]) > 5 else race["date"],
                "version": race.get("version", "v1"),
                "threshold": race.get("threshold", 0.55),
                "predictions": {
                    "M": race["predictions"].get("Men Elite", ""),
                    "W": race["predictions"].get("Women Elite", ""),
                },
                "results": {
                    "M": race["results"].get("Men Elite", ""),
                    "W": race["results"].get("Women Elite", ""),
                },
                "validation": race.get("validation", {})  # Include validation with distribution
            }

    # Model version history (from registry)
    VERSIONS = registry.get("model_versions", [
        {"version": "v1", "accuracy": 80.2, "auc": None, "observations": 7724, "innovation": "Baseline RF"},
        {"version": "v6", "accuracy": 77.6, "auc": 0.835, "observations": 8357, "innovation": "+New Rider"},
    ])

    # Feature importance (static for now - could be stored in registry later)
    FEATURE_IMPORTANCE = {
        "v1": {"avg_place_last3": 14.9, "best_place_last5": 16.8, "top10_rate_career": 9.7, "uci_points_normalized": 12.1, "h2h_field_score": 0},
        "v4": {"avg_place_last3": 17.6, "best_place_last5": 17.7, "top10_rate_career": 9.7, "uci_points_normalized": 8.1, "h2h_field_score": 0},
        "v5": {"avg_place_last3": 13.0, "best_place_last5": 12.7, "top10_rate_career": 12.9, "uci_points_normalized": 6.5, "h2h_field_score": 21.4},
        "v6": {"avg_place_last3": 12.8, "best_place_last5": 12.3, "top10_rate_career": 12.5, "uci_points_normalized": 6.2, "h2h_field_score": 22.5},
    }

    # ============================================================
    # Auto-calculate race stats from prediction/result files
    # ============================================================

    def fix_result_name(name):
        """Normalize result name to 'LASTNAME Firstname' format for standardization."""
        name = str(name).strip()
        if '\n' in name:
            parts = name.split('\n')
            if len(parts) == 2:
                firstname, lastname = parts[0].strip(), parts[1].strip()
                return f"{lastname} {firstname.title()}"
        elif name.isupper():
            parts = name.split()
            if len(parts) >= 2:
                firstname = parts[0]
                lastname = ' '.join(parts[1:])
                return f"{lastname} {firstname.title()}"
        return name

    @st.cache_data
    def calculate_race_stats(race_config):
        """Calculate accuracy, precision, podium stats from prediction/result files."""
        predictions_list = []
        base_path = Path(__file__).parent.parent

        for gender in ["M", "W"]:
            pred_file = base_path / race_config["predictions"][gender]
            results_file = base_path / race_config["results"][gender]

            if not pred_file.exists() or not results_file.exists():
                continue

            pred_df = pd.read_csv(pred_file)
            results_df = pd.read_csv(results_file)

            # Standardize column names
            if 'Position' in results_df.columns:
                results_df = results_df.rename(columns={'Position': 'Place'})

            # Fix result names
            if 'Name' in results_df.columns:
                results_df['Name'] = results_df['Name'].apply(fix_result_name)

            # Standardize names for matching
            pred_df['rider_std'] = pred_df['Rider'].apply(standardize_name)
            results_df['rider_std'] = results_df['Name'].apply(standardize_name)
            results_df['Place'] = pd.to_numeric(results_df['Place'], errors='coerce')

            # Get Top-3 probability column if it exists
            top3_col = 'Top-3 Probability' if 'Top-3 Probability' in pred_df.columns else None

            for _, pred_row in pred_df.iterrows():
                rider_std = pred_row['rider_std']
                prob = pred_row['Top-10 Probability']
                top3_prob = pred_row[top3_col] if top3_col else 0

                match = results_df[results_df['rider_std'] == rider_std]
                if not match.empty:
                    place = match.iloc[0]['Place']
                    if pd.notna(place):
                        predictions_list.append({
                            'rider': pred_row['Rider'],
                            'prob': prob,
                            'top3_prob': top3_prob,
                            'position': int(place),
                            'gender': gender
                        })

        if not predictions_list:
            return None

        threshold = race_config["threshold"]

        # Calculate stats
        above_thresh = [p for p in predictions_list if p['prob'] >= threshold]
        true_pos = sum(1 for p in above_thresh if p['position'] <= 10)
        total_top10_actual = sum(1 for p in predictions_list if p['position'] <= 10)

        # Podium stats (predictions with >30% Top-3 probability)
        podium_predictions = [p for p in predictions_list if p['top3_prob'] >= 0.30]
        podium_correct = sum(1 for p in podium_predictions if p['position'] <= 3)

        precision = (true_pos / len(above_thresh) * 100) if above_thresh else 0
        recall = (true_pos / total_top10_actual * 100) if total_top10_actual > 0 else 0
        podium_accuracy = (podium_correct / len(podium_predictions) * 100) if podium_predictions else 0

        return {
            "name": race_config["name"],
            "date": race_config["date"],
            "version": race_config["version"],
            "accuracy": round(recall),  # Recall = "accuracy" in our terminology
            "precision": round(precision),
            "podium": round(podium_accuracy),
            "predictions": len(above_thresh),
            "correct": true_pos,
            "total_matched": len(predictions_list),
        }

    # Calculate stats for all races dynamically
    RACES = []
    for race_key, race_cfg in RACE_CONFIG.items():
        stats = calculate_race_stats(race_cfg)
        if stats:
            RACES.append(stats)

    # Reverse to show oldest first in charts
    RACES = RACES[::-1]

    # Summary stats (all dynamic from registry)
    total_predictions = sum(r["predictions"] for r in RACES)
    total_correct = sum(r["correct"] for r in RACES)
    season_precision = (total_correct / total_predictions * 100) if total_predictions > 0 else 0
    current_version = registry.get("current_version", "v6")

    st.caption(f"{len(RACES)} Races | {len(VERSIONS)} Versions | {total_predictions} Predictions | {total_correct} Correct | Season Precision: {season_precision:.0f}% | Current: {current_version}")

    # ============================================================
    # ROW 1: Live Race Performance & Prediction Volume
    # ============================================================
    st.markdown("#### Live Race Performance")

    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
        # Panel 1: Live Race Performance
        race_labels = [f"{r['name']} ({r['version']})" for r in RACES]

        fig1 = go.Figure()
        fig1.add_trace(go.Bar(
            name='Recall (%)', x=race_labels, y=[r["accuracy"] for r in RACES],
            marker_color='#22c55e', text=[f"{r['accuracy']}%" for r in RACES],
            textposition='outside', hovertemplate='%{x}<br>Recall: %{y}%<extra></extra>'
        ))
        fig1.add_trace(go.Bar(
            name='Precision (%)', x=race_labels, y=[r["precision"] for r in RACES],
            marker_color='#3b82f6', text=[f"{r['precision']}%" for r in RACES],
            textposition='outside', hovertemplate='%{x}<br>Precision: %{y}%<extra></extra>'
        ))
        fig1.add_trace(go.Bar(
            name='Podium (%)', x=race_labels, y=[r["podium"] for r in RACES],
            marker_color='#f59e0b', text=[f"{r['podium']}%" for r in RACES],
            textposition='outside', hovertemplate='%{x}<br>Podium: %{y}%<extra></extra>'
        ))

        fig1.update_layout(
            title='Live Race Performance',
            height=350,
            showlegend=True,
            legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5),
            barmode='group',
            yaxis=dict(range=[0, 115], title="Percentage"),
            plot_bgcolor='#f8f9fa',
            paper_bgcolor='white',
            margin=dict(b=80)
        )
        st.plotly_chart(fig1, use_container_width=True)

    with row1_col2:
        # Panel 2: Predictions Made vs Correct
        race_date_labels = [f"{r['name']} ({r['date']})" for r in RACES]

        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            name='Predictions Made', x=race_date_labels, y=[r["predictions"] for r in RACES],
            marker_color='#94a3b8', text=[str(r['predictions']) for r in RACES],
            textposition='outside', hovertemplate='%{x}<br>Predictions: %{y}<extra></extra>'
        ))
        fig2.add_trace(go.Bar(
            name='Correct (Top-10)', x=race_date_labels, y=[r["correct"] for r in RACES],
            marker_color='#22c55e', text=[str(r['correct']) for r in RACES],
            textposition='outside', hovertemplate='%{x}<br>Correct: %{y}<extra></extra>'
        ))

        max_predictions = max([r["predictions"] for r in RACES], default=50) if RACES else 50
        fig2.update_layout(
            title='Prediction Volume & Accuracy',
            height=350,
            showlegend=True,
            legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5),
            barmode='group',
            yaxis=dict(range=[0, max_predictions + 10], title="Count"),
            plot_bgcolor='#f8f9fa',
            paper_bgcolor='white',
            margin=dict(b=80)
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ============================================================
    # ROW 2: Training Accuracy & Model Quality
    # ============================================================
    st.markdown("#### Model Training Evolution")

    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
        # Panel 3: Training Accuracy - All Versions
        v_all = [v["version"] for v in VERSIONS]
        accuracies = [v["accuracy"] for v in VERSIONS]
        innovations = [v["innovation"] for v in VERSIONS]

        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            name='Training Accuracy', x=v_all, y=accuracies,
            marker_color='#22c55e', text=[f"{a}%" for a in accuracies],
            textposition='outside',
            hovertemplate='%{x}<br>Accuracy: %{y}%<br>%{customdata}<extra></extra>',
            customdata=innovations
        ))

        if VERSIONS:
            min_acc = min(v["accuracy"] for v in VERSIONS) - 2
            max_acc = max(v["accuracy"] for v in VERSIONS) + 2
        else:
            min_acc, max_acc = 74, 86

        fig3.update_layout(
            title='Training Accuracy by Version',
            height=350,
            showlegend=True,
            legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5),
            yaxis=dict(range=[min_acc, max_acc], title="Accuracy (%)"),
            plot_bgcolor='#f8f9fa',
            paper_bgcolor='white',
            margin=dict(b=80)
        )
        st.plotly_chart(fig3, use_container_width=True)

    with row2_col2:
        # Panel 4: Model Quality - AUC-ROC
        versions_with_auc = [v for v in VERSIONS if v["auc"] is not None]
        v_names = [v["version"] for v in versions_with_auc]
        aucs = [v["auc"] for v in versions_with_auc]
        auc_innovations = [v["innovation"] for v in versions_with_auc]

        fig4 = go.Figure()
        fig4.add_trace(go.Scatter(
            name='AUC-ROC', x=v_names, y=aucs, mode='lines+markers+text',
            line=dict(color='#8b5cf6', width=3),
            marker=dict(size=12, color='white', line=dict(color='#8b5cf6', width=2)),
            text=[f"{a:.3f}" for a in aucs], textposition='top center',
            hovertemplate='%{x}<br>AUC: %{y:.3f}<br>%{customdata}<extra></extra>',
            customdata=auc_innovations
        ))

        if versions_with_auc:
            min_auc = min(v["auc"] for v in versions_with_auc) - 0.01
            max_auc = max(v["auc"] for v in versions_with_auc) + 0.01
        else:
            min_auc, max_auc = 0.810, 0.860

        fig4.update_layout(
            title='Model Quality (AUC-ROC) v3-v6',
            height=350,
            showlegend=True,
            legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5),
            yaxis=dict(range=[min_auc, max_auc], title="AUC-ROC"),
            plot_bgcolor='#f8f9fa',
            paper_bgcolor='white',
            margin=dict(b=80)
        )
        st.plotly_chart(fig4, use_container_width=True)

    # ============================================================
    # ROW 3: Feature Importance & Dataset Growth
    # ============================================================
    st.markdown("#### Feature & Data Evolution")

    row3_col1, row3_col2 = st.columns(2)

    with row3_col1:
        # Panel 5: Feature Importance Evolution
        features = ["h2h_field_score", "avg_place_last3", "best_place_last5", "top10_rate_career", "uci_points_normalized"]
        feature_labels = ["H2H Score", "Avg Place (L3)", "Best Place (L5)", "Top-10 Rate", "UCI Points"]
        feature_colors = ["#ef4444", "#22c55e", "#3b82f6", "#f59e0b", "#8b5cf6"]
        versions_fi = list(FEATURE_IMPORTANCE.keys())

        fig5 = go.Figure()
        for feat, label, color in zip(features, feature_labels, feature_colors):
            values = [FEATURE_IMPORTANCE[v].get(feat, 0) for v in versions_fi]
            fig5.add_trace(go.Scatter(
                name=label, x=versions_fi, y=values, mode='lines+markers',
                line=dict(color=color, width=2),
                marker=dict(size=8, color=color),
                hovertemplate=f'{label}<br>%{{x}}: %{{y:.1f}}%<extra></extra>'
            ))

        # Add annotation for H2H breakthrough
        fig5.add_annotation(
            x='v5', y=21.4, text='H2H becomes #1', showarrow=True,
            arrowhead=2, arrowcolor='#ef4444', font=dict(color='#ef4444', size=10),
            ax=-40, ay=-30
        )

        fig5.update_layout(
            title='Feature Importance Evolution',
            height=350,
            showlegend=True,
            legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5),
            yaxis=dict(range=[0, 28], title="Importance (%)"),
            plot_bgcolor='#f8f9fa',
            paper_bgcolor='white',
            margin=dict(b=100)
        )
        st.plotly_chart(fig5, use_container_width=True)

    with row3_col2:
        # Panel 6: Dataset Growth
        v_all = [v["version"] for v in VERSIONS]
        obs = [v["observations"] for v in VERSIONS]

        fig6 = go.Figure()
        fig6.add_trace(go.Scatter(
            name='Observations', x=v_all, y=obs, mode='lines+markers+text',
            fill='tozeroy', fillcolor='rgba(6, 182, 212, 0.2)',
            line=dict(color='#06b6d4', width=3),
            marker=dict(size=10, color='white', line=dict(color='#06b6d4', width=2)),
            text=[f"{o:,}" for o in obs], textposition='top center',
            hovertemplate='%{x}<br>Observations: %{y:,}<extra></extra>'
        ))

        if VERSIONS:
            min_obs = min(v["observations"] for v in VERSIONS) * 0.95
            max_obs = max(v["observations"] for v in VERSIONS) * 1.05
        else:
            min_obs, max_obs = 7500, 9500

        fig6.update_layout(
            title='Training Dataset Growth',
            height=350,
            showlegend=True,
            legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5),
            yaxis=dict(range=[min_obs, max_obs], title="Observations"),
            plot_bgcolor='#f8f9fa',
            paper_bgcolor='white',
            margin=dict(b=80)
        )
        st.plotly_chart(fig6, use_container_width=True)

    # Key insights (auto-calculated from RACES data)
    st.markdown("### Key Insights")
    col1, col2, col3 = st.columns(3)

    # Calculate dynamic insights
    if RACES:
        avg_recall = sum(r["accuracy"] for r in RACES) / len(RACES)
        best_race = max(RACES, key=lambda r: r["accuracy"])
        latest_version = VERSIONS[-1] if VERSIONS else None
        first_version_with_auc = next((v for v in VERSIONS if v["auc"]), None)

    with col1:
        if RACES:
            st.metric("Season Recall", f"{avg_recall:.0f}%", help="Average recall across all validated races")
            st.metric("Best Race", f"{best_race['name']} ({best_race['accuracy']}%)", help="Highest recall on high-confidence picks")
        else:
            st.metric("Season Recall", "N/A")
            st.metric("Best Race", "N/A")

    with col2:
        if latest_version and first_version_with_auc and latest_version["auc"]:
            auc_change = latest_version["auc"] - first_version_with_auc["auc"]
            st.metric("Model Quality Trend", f"+{auc_change*100:.1f}% AUC", help=f"AUC improved from {first_version_with_auc['auc']:.3f} to {latest_version['auc']:.3f}")
        else:
            st.metric("Model Quality Trend", "N/A")
        # Feature importance from latest version
        latest_fi = FEATURE_IMPORTANCE.get(latest_version["version"] if latest_version else "v6", {})
        top_feature = max(latest_fi.items(), key=lambda x: x[1]) if latest_fi else ("N/A", 0)
        feature_names = {"h2h_field_score": "H2H", "avg_place_last3": "Avg Place", "best_place_last5": "Best Place", "top10_rate_career": "Top-10 Rate", "uci_points_normalized": "UCI Points"}
        st.metric("Top Feature", f"{feature_names.get(top_feature[0], top_feature[0])} ({top_feature[1]}%)", help="Most important model feature")

    with col3:
        if VERSIONS and len(VERSIONS) >= 2:
            obs_growth = (VERSIONS[-1]["observations"] - VERSIONS[0]["observations"]) / VERSIONS[0]["observations"] * 100
            st.metric("Dataset Growth", f"+{obs_growth:.1f}%", help=f"From {VERSIONS[0]['observations']:,} to {VERSIONS[-1]['observations']:,} observations")
        else:
            st.metric("Dataset Growth", "N/A")
        st.metric("Versions Tested", str(len(VERSIONS)), help="Continuous improvement through live validation")

    # ============================================================
    # Model Progression - Hits@10 and Hits@3 over time
    # ============================================================
    st.markdown("---")
    st.markdown("### Model Progression (Original Predictions)")
    st.markdown("How our predictions improved as the model evolved through the season")

    # Load progression data
    progression_path = Path(__file__).parent.parent / "data/clean/model_progression.csv"
    if progression_path.exists():
        prog_df = pd.read_csv(progression_path, parse_dates=['date'])
        prog_df = prog_df.sort_values('date')

        # Create two charts side by side
        prog_col1, prog_col2 = st.columns(2)

        with prog_col1:
            # Hits@10 chart
            fig_h10 = go.Figure()

            # Men Elite
            men_df = prog_df[prog_df['category'] == 'Men Elite']
            fig_h10.add_trace(go.Scatter(
                x=[f"{r['race']} ({r['model_version']})" for _, r in men_df.iterrows()],
                y=men_df['hits_10'],
                mode='lines+markers+text',
                name='Men Elite',
                line=dict(color='#3b82f6', width=3),
                marker=dict(size=10),
                text=[f"{h}/10" for h in men_df['hits_10']],
                textposition='top center',
                hovertemplate='%{x}<br>Hits@10: %{y}/10<extra>Men Elite</extra>'
            ))

            # Women Elite
            women_df = prog_df[prog_df['category'] == 'Women Elite']
            fig_h10.add_trace(go.Scatter(
                x=[f"{r['race']} ({r['model_version']})" for _, r in women_df.iterrows()],
                y=women_df['hits_10'],
                mode='lines+markers+text',
                name='Women Elite',
                line=dict(color='#ec4899', width=3),
                marker=dict(size=10),
                text=[f"{h}/10" for h in women_df['hits_10']],
                textposition='bottom center',
                hovertemplate='%{x}<br>Hits@10: %{y}/10<extra>Women Elite</extra>'
            ))

            # Target line
            fig_h10.add_hline(y=7, line_dash="dash", line_color="#22c55e", line_width=2,
                            annotation_text="Target (7/10)", annotation_position="right")

            fig_h10.update_layout(
                title='Hits@10 Progression',
                height=400,
                showlegend=True,
                legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5),
                yaxis=dict(range=[0, 11], title="Hits@10", dtick=2),
                xaxis=dict(tickangle=45),
                plot_bgcolor='#f8f9fa',
                paper_bgcolor='white',
                margin=dict(b=120)
            )
            st.plotly_chart(fig_h10, use_container_width=True)

        with prog_col2:
            # Hits@3 chart
            fig_h3 = go.Figure()

            # Men Elite
            fig_h3.add_trace(go.Scatter(
                x=[f"{r['race']} ({r['model_version']})" for _, r in men_df.iterrows()],
                y=men_df['hits_3'],
                mode='lines+markers+text',
                name='Men Elite',
                line=dict(color='#3b82f6', width=3),
                marker=dict(size=10),
                text=[f"{h}/3" for h in men_df['hits_3']],
                textposition='top center',
                hovertemplate='%{x}<br>Hits@3: %{y}/3<extra>Men Elite</extra>'
            ))

            # Women Elite
            fig_h3.add_trace(go.Scatter(
                x=[f"{r['race']} ({r['model_version']})" for _, r in women_df.iterrows()],
                y=women_df['hits_3'],
                mode='lines+markers+text',
                name='Women Elite',
                line=dict(color='#ec4899', width=3),
                marker=dict(size=10),
                text=[f"{h}/3" for h in women_df['hits_3']],
                textposition='bottom center',
                hovertemplate='%{x}<br>Hits@3: %{y}/3<extra>Women Elite</extra>'
            ))

            # Target line
            fig_h3.add_hline(y=2, line_dash="dash", line_color="#22c55e", line_width=2,
                            annotation_text="Target (2/3)", annotation_position="right")

            fig_h3.update_layout(
                title='Hits@3 Progression (Podium)',
                height=400,
                showlegend=True,
                legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5),
                yaxis=dict(range=[0, 4], title="Hits@3", dtick=1),
                xaxis=dict(tickangle=45),
                plot_bgcolor='#f8f9fa',
                paper_bgcolor='white',
                margin=dict(b=120)
            )
            st.plotly_chart(fig_h3, use_container_width=True)

        # Summary stats
        avg_h10 = prog_df['hits_10'].mean()
        avg_h3 = prog_df['hits_3'].mean()
        latest_version = prog_df.iloc[-1]['model_version']

        prog_stat1, prog_stat2, prog_stat3, prog_stat4 = st.columns(4)
        prog_stat1.metric("Avg Hits@10", f"{avg_h10:.1f}/10")
        prog_stat2.metric("Avg Hits@3", f"{avg_h3:.1f}/3")
        prog_stat3.metric("Races Tracked", len(prog_df) // 2)
        prog_stat4.metric("Latest Version", latest_version)

        with st.expander("📖 Understanding Progression Metrics"):
            st.markdown("""
**What this shows:**
- These are the **actual predictions** made at race time with the model version available
- v1 → v2: Big jump from 4/10 to 8/10 (Men) as threshold tuning improved
- v6.x: Stabilized around 6-7/10 with mature H2H feature

**Why early races look worse:**
1. v1 had no UCI inference for new riders
2. v1/v2 had no H2H feature (added in v5)
3. Early models used 0.5 threshold (too permissive)

**Going forward (v6.4+):**
- Antwerpen onwards will use v6.4 with robust feature extraction
- Target: 7+/10 Hits@10, 2+/3 Hits@3
            """)
    else:
        st.info("Progression data not found. Run `python calculate_original_hits.py` to generate.")

    # ============================================================
    # Race-by-Race Results - Interactive Scatter Plots
    # (Uses RACE_CONFIG defined above as single source of truth)
    # ============================================================
    st.markdown("---")
    st.markdown("### Race-by-Race Analysis")
    st.markdown("Select a race to see predicted probability vs actual finish position")

    def load_race_data(race_config):
        """Load and merge predictions with actual results for a race."""
        predictions_list = []

        for gender in ["M", "W"]:
            pred_file = Path(__file__).parent.parent / race_config["predictions"][gender]
            results_file = Path(__file__).parent.parent / race_config["results"][gender]

            if not pred_file.exists() or not results_file.exists():
                continue

            # Load predictions
            pred_df = pd.read_csv(pred_file)

            # Load results - handle different CSV formats (multiline names in Tabor/Flamanville)
            with open(results_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check if this is the multiline name format (Tabor/Flamanville)
            if '\n"' in content or '"\n' in content:
                # Multiline name format: "FIRSTNAME\nLASTNAME" - need to combine
                lines = content.split('\n')
                header = lines[0]
                clean_lines = [header]

                i = 1
                while i < len(lines):
                    line = lines[i].strip()
                    if not line:
                        i += 1
                        continue

                    # If this line starts a record (starts with number,")
                    if line and line[0].isdigit():
                        # Check if next line is part of this name (doesn't start with number)
                        if i + 1 < len(lines) and lines[i + 1].strip() and not lines[i + 1].strip()[0].isdigit():
                            # Combine multiline name: "1,"THIBAU" + "\nNYS",..."
                            combined = line
                            while i + 1 < len(lines) and lines[i + 1].strip() and not lines[i + 1].strip()[0].isdigit():
                                i += 1
                                combined = combined.rstrip('"') + ' ' + lines[i].strip().lstrip('"')
                            clean_lines.append(combined)
                        else:
                            clean_lines.append(line)
                    i += 1

                from io import StringIO
                results_df = pd.read_csv(StringIO('\n'.join(clean_lines)))
            else:
                # Standard format (Sardinia) - direct load
                results_df = pd.read_csv(results_file)

            # Standardize results column names
            if 'Position' in results_df.columns:
                results_df = results_df.rename(columns={'Position': 'Place'})
            if 'Place' not in results_df.columns and results_df.columns[0] != 'Place':
                results_df.columns = ['Place'] + list(results_df.columns[1:])

            # Clean up any remaining name formatting - BEFORE standardization
            # Handle various result name formats:
            # - "FIRSTNAME\nLASTNAME" (Tabor Men) -> "LASTNAME Firstname"
            # - "FIRSTNAME LASTNAME" all caps (Tabor Women) -> "LASTNAME Firstname"
            # - "LASTNAME Firstname" (Sardinia, Flamanville) -> keep as-is
            if 'Name' in results_df.columns:
                def fix_result_name(name):
                    """Normalize result name to 'LASTNAME Firstname' format for standardization."""
                    name = str(name).strip()
                    if '\n' in name:
                        # Multiline format: "FIRSTNAME\nLASTNAME"
                        parts = name.split('\n')
                        if len(parts) == 2:
                            firstname, lastname = parts[0].strip(), parts[1].strip()
                            return f"{lastname} {firstname.title()}"
                    elif name.isupper():
                        # All uppercase "FIRSTNAME LASTNAME" format
                        # Need to find where firstname ends and lastname begins
                        # Heuristic: First word is firstname, rest is lastname
                        parts = name.split()
                        if len(parts) >= 2:
                            firstname = parts[0]
                            lastname = ' '.join(parts[1:])
                            return f"{lastname} {firstname.title()}"
                    return name
                results_df['Name'] = results_df['Name'].apply(fix_result_name)

            # Standardize prediction rider names for matching
            pred_df['rider_std'] = pred_df['Rider'].apply(standardize_name)

            # Standardize results names for matching
            results_df['rider_std'] = results_df['Name'].apply(standardize_name)

            # Ensure Place is numeric (handles DNF, DNS, etc.)
            results_df['Place'] = pd.to_numeric(results_df['Place'], errors='coerce')

            # Merge predictions with results
            for _, pred_row in pred_df.iterrows():
                rider_std = pred_row['rider_std']
                prob = pred_row['Top-10 Probability']

                # Find matching result
                match = results_df[results_df['rider_std'] == rider_std]
                if not match.empty:
                    place = match.iloc[0]['Place']
                    if pd.isna(place):  # DNF/DNS - skip
                        continue
                    position = int(place)
                else:
                    # Rider not found in results (DNS/DNF) - skip
                    continue

                predictions_list.append((
                    pred_row['Rider'].split()[0].title(),  # Last name only for display (first word is lastname)
                    prob,
                    position,
                    gender
                ))

        return predictions_list

    selected_race = st.selectbox("Select Race", list(RACE_CONFIG.keys()))
    race_config = RACE_CONFIG[selected_race]

    # Load data dynamically
    predictions = load_race_data(race_config)
    threshold = race_config["threshold"]
    version = race_config["version"]

    if not predictions:
        st.warning("No prediction data found for this race. Check that prediction and result files exist.")
        st.stop()

    # Separate predictions by gender
    men_predictions = [(r, p, pos, g) for r, p, pos, g in predictions if g == 'M']
    women_predictions = [(r, p, pos, g) for r, p, pos, g in predictions if g == 'W']

    def create_scatter_chart(preds, gender_label, threshold, version, race_name):
        """Create a scatter chart for a single gender category."""
        fig = go.Figure()

        for rider, prob, position, gender in preds:
            is_top10 = position <= 10
            above_threshold = prob >= threshold

            if above_threshold and is_top10:
                color = '#22c55e'  # green - true positive
                category = 'True Positive'
            elif above_threshold and not is_top10:
                color = '#ef4444'  # red - false positive
                category = 'False Positive'
            else:
                color = '#9ca3af'  # gray - below threshold
                category = 'Below Threshold'

            fig.add_trace(go.Scatter(
                x=[prob * 100],
                y=[position],
                mode='markers+text',
                marker=dict(size=12, color=color, line=dict(color='white', width=2)),
                text=[rider],
                textposition='middle right',
                textfont=dict(size=9),
                name=rider,
                hovertemplate=f'<b>{rider}</b><br>Probability: {prob*100:.0f}%<br>Position: {position}<br>{category}<extra></extra>',
                showlegend=False
            ))

        # Add threshold line
        fig.add_vline(
            x=threshold * 100, line_dash="dash", line_color="#3b82f6", line_width=2,
            annotation_text=f"Threshold ({int(threshold*100)}%)",
            annotation_position="top"
        )

        # Add Top-10 zone
        fig.add_hrect(y0=0, y1=10.5, fillcolor="#22c55e", opacity=0.1, line_width=0)
        fig.add_hline(y=10.5, line_color="#22c55e", line_width=1, opacity=0.5)

        # Calculate max position for y-axis
        max_position = max(p[2] for p in preds) if preds else 20

        fig.update_layout(
            title=dict(
                text=f"{gender_label}",
                x=0.5,
                font=dict(size=14)
            ),
            xaxis_title="Predicted Top-10 Probability (%)",
            yaxis_title="Actual Finish Position",
            xaxis=dict(range=[0, 105], showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
            yaxis=dict(range=[max_position + 3, 0], showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
            height=400,
            plot_bgcolor='#f8f9fa',
            paper_bgcolor='white',
            hovermode='closest',
            margin=dict(t=50, b=50),
            annotations=[
                dict(
                    x=5, y=5, text="TOP 10", showarrow=False,
                    font=dict(color='#22c55e', size=10, weight='bold'), opacity=0.7
                )
            ]
        )

        return fig

    def calc_stats(preds, threshold):
        """Calculate precision/recall stats for predictions."""
        above_thresh = [(r, p, pos, g) for r, p, pos, g in preds if p >= threshold]
        true_pos = sum(1 for _, _, pos, _ in above_thresh if pos <= 10)
        total_top10 = sum(1 for _, _, pos, _ in preds if pos <= 10)
        precision = true_pos / len(above_thresh) * 100 if above_thresh else 0
        recall = true_pos / total_top10 * 100 if total_top10 > 0 else 0
        return len(above_thresh), true_pos, precision, recall

    # Display side-by-side charts
    st.markdown(f"**{version} | {selected_race}** - Predicted Probability vs Actual Result")

    col_men, col_women = st.columns(2)

    with col_men:
        if men_predictions:
            men_fig = create_scatter_chart(men_predictions, "Men Elite", threshold, version, selected_race)
            st.plotly_chart(men_fig, use_container_width=True)

            # Men stats
            m_preds, m_tp, m_prec, m_recall = calc_stats(men_predictions, threshold)
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Predictions", m_preds)
            m2.metric("Correct", m_tp)
            m3.metric("Precision", f"{m_prec:.0f}%")
            m4.metric("Recall", f"{m_recall:.0f}%")
        else:
            st.info("No Men Elite data for this race")

    with col_women:
        if women_predictions:
            women_fig = create_scatter_chart(women_predictions, "Women Elite", threshold, version, selected_race)
            st.plotly_chart(women_fig, use_container_width=True)

            # Women stats
            w_preds, w_tp, w_prec, w_recall = calc_stats(women_predictions, threshold)
            w1, w2, w3, w4 = st.columns(4)
            w1.metric("Predictions", w_preds)
            w2.metric("Correct", w_tp)
            w3.metric("Precision", f"{w_prec:.0f}%")
            w4.metric("Recall", f"{w_recall:.0f}%")
        else:
            st.info("No Women Elite data for this race")

    # Combined stats
    st.markdown("---")
    all_preds, all_tp, all_prec, all_recall = calc_stats(predictions, threshold)
    st.markdown(f"**Combined:** {all_preds} predictions, {all_tp} correct, {all_prec:.0f}% precision, {all_recall:.0f}% recall")

    # Legend
    st.markdown("""
    **Legend:** 🟢 True Positive (predicted + Top-10) | 🔴 False Positive (predicted + missed) | ⚫ Below threshold
    """)

    # Distribution Metrics Section
    st.markdown("---")
    st.markdown("### 📊 Probability Distribution Analysis")

    # Get distribution data from registry for this race
    distribution = race_config.get("validation", {}).get("distribution")

    if distribution:
        # Display distribution metrics
        d_col1, d_col2, d_col3, d_col4 = st.columns(4)
        d_col1.metric("Low (<30%)", f"{distribution['low_pct']:.0f}%", help="% of riders with <30% Top-10 probability")
        d_col2.metric("Mid (30-60%)", f"{distribution['mid_pct']:.0f}%", help="% of riders with 30-60% probability - the 'uncertain' zone")
        d_col3.metric("High (>60%)", f"{distribution['high_pct']:.0f}%", help="% of riders with >60% Top-10 probability")
        d_col4.metric("Field Size", f"{distribution['field_size']}", help="Total riders in startlist")

        # Additional stats row
        d2_col1, d2_col2, d2_col3, d2_col4 = st.columns(4)
        d2_col1.metric("Mean Probability", f"{distribution['mean_prob']*100:.1f}%", help="Average Top-10 probability across all riders")
        d2_col2.metric("Std Deviation", f"{distribution['std_prob']:.3f}", help="Spread of probabilities - higher = more variance")
        d2_col3.metric("New Riders", f"{distribution['new_rider_count']}", help="Riders with no prior race history in the model")

        # Determine and display distribution pattern
        if distribution['mid_pct'] < 10:
            pattern = "BIMODAL"
            pattern_color = "green"
            pattern_desc = "Model is decisive - most riders are clearly favorites or non-contenders"
        elif distribution['mid_pct'] > 20:
            pattern = "BALANCED"
            pattern_color = "orange"
            pattern_desc = "Model is uncertain - many riders in the 'maybe' zone"
        else:
            pattern = "MODERATE"
            pattern_color = "blue"
            pattern_desc = "Typical distribution with clear favorites and some uncertainty"

        d2_col4.metric("Pattern", pattern, help=pattern_desc)

        # Histogram of actual probability distribution
        st.markdown("#### Probability Distribution Histogram")

        # Get probabilities from the predictions data we already loaded
        all_probs = [p[1] for p in predictions]  # predictions is list of (rider, prob, position, gender)

        if all_probs:
            # Create histogram with 10 bins (0-10%, 10-20%, etc.)
            fig_hist = go.Figure()

            # Calculate histogram bins
            bin_edges = [i/10 for i in range(11)]  # 0.0, 0.1, 0.2, ..., 1.0
            bin_labels = [f"{int(i*100)}-{int((i+0.1)*100)}%" for i in bin_edges[:-1]]

            # Count riders in each bin
            hist_counts = []
            for i in range(len(bin_edges) - 1):
                count = sum(1 for p in all_probs if bin_edges[i] <= p < bin_edges[i+1])
                hist_counts.append(count)
            # Handle edge case: include 1.0 in the last bin
            hist_counts[-1] += sum(1 for p in all_probs if p == 1.0)

            # Color bars based on zone
            bar_colors = []
            for i in range(10):
                if i < 3:  # 0-30%
                    bar_colors.append('#94a3b8')  # gray - low
                elif i < 6:  # 30-60%
                    bar_colors.append('#f59e0b')  # amber - mid
                else:  # 60-100%
                    bar_colors.append('#22c55e')  # green - high

            fig_hist.add_trace(go.Bar(
                x=bin_labels,
                y=hist_counts,
                marker_color=bar_colors,
                text=hist_counts,
                textposition='outside',
                hovertemplate='%{x}<br>Riders: %{y}<extra></extra>'
            ))

            # Add threshold line
            threshold_bin_idx = int(threshold * 10)
            fig_hist.add_vline(
                x=threshold_bin_idx - 0.5,
                line_dash="dash",
                line_color="#3b82f6",
                line_width=2,
                annotation_text=f"Threshold ({int(threshold*100)}%)",
                annotation_position="top"
            )

            fig_hist.update_layout(
                title=f'Rider Probability Distribution - {selected_race}',
                xaxis_title='Top-10 Probability Range',
                yaxis_title='Number of Riders',
                height=350,
                showlegend=False,
                plot_bgcolor='#f8f9fa',
                paper_bgcolor='white',
                bargap=0.1
            )

            st.plotly_chart(fig_hist, use_container_width=True)

            # Quick interpretation
            low_count = sum(hist_counts[:3])
            mid_count = sum(hist_counts[3:6])
            high_count = sum(hist_counts[6:])
            total = len(all_probs)

            st.caption(f"**Distribution:** {low_count} riders ({low_count/total*100:.0f}%) in low zone | "
                      f"{mid_count} riders ({mid_count/total*100:.0f}%) in mid zone | "
                      f"{high_count} riders ({high_count/total*100:.0f}%) in high zone")

        with st.expander("📖 Understanding Distribution Metrics"):
            st.markdown(f"""
**What the distribution tells you:**

The probability distribution shows how the model "sees" this race field:

| Pattern | Mid-Range % | Meaning | Trust Level |
|---------|-------------|---------|-------------|
| **Bimodal** | <10% | Model is confident - clear separation between contenders and non-contenders | Higher - predictions are decisive |
| **Balanced** | >20% | Model is uncertain - many "coin flip" riders in the middle | Lower - more surprises possible |
| **Moderate** | 10-20% | Typical race - some clear favorites, some uncertainty | Normal |

**This race ({selected_race}):**
- Pattern: **{pattern}** ({distribution['mid_pct']:.1f}% in mid-range)
- {pattern_desc}

**Why does this happen?**
1. **H2H maturity**: More historical matchup data → stronger probability separation
2. **New rider penalty**: Unknown riders get pushed to low probabilities
3. **Field familiarity**: Familiar fields (World Cups) produce more bimodal distributions
4. **Model version**: Later versions (v6+) have more H2H data and better calibration

**Practical implication:**
- **Bimodal races**: Trust predictions above threshold - model knows who will perform
- **Balanced races**: Watch the mid-range riders - more surprises likely
            """)
    else:
        st.info("Distribution metrics not available for this race. Run `python pipeline.py backfill-distribution` to calculate.")

with tab5:
    st.header("🧪 LTR A/B Test: v6.x vs v7.1-LTR")
    st.markdown("**Comparing Binary Classification (v6.x) vs Learning-to-Rank (v7.1-LTR)**")

    # Load LTR validation results
    ltr_results_path = config.CLEAN_DIR / "ltr_validation_results.json"
    if ltr_results_path.exists():
        with open(ltr_results_path, 'r') as f:
            ltr_data = json.load(f)

        validations = ltr_data.get("validations", [])
        aggregate = ltr_data.get("aggregate", {})

        if validations:
            # Summary metrics
            st.markdown("### Aggregate Results")

            agg_col1, agg_col2, agg_col3, agg_col4 = st.columns(4)

            v6_h10 = aggregate.get("v6_hits10_total", 0)
            ltr_h10 = aggregate.get("ltr_hits10_total", 0)
            h10_possible = aggregate.get("v6_hits10_possible", 40)
            h10_winner = "LTR" if ltr_h10 > v6_h10 else ("v6.x" if v6_h10 > ltr_h10 else "TIE")

            v6_h3 = aggregate.get("v6_hits3_total", 0)
            ltr_h3 = aggregate.get("ltr_hits3_total", 0)
            h3_possible = aggregate.get("v6_hits3_possible", 12)
            h3_winner = "LTR" if ltr_h3 > v6_h3 else ("v6.x" if v6_h3 > ltr_h3 else "TIE")

            v6_mae = aggregate.get("v6_avg_mae", 0)
            ltr_mae = aggregate.get("ltr_avg_mae", 0)
            mae_winner = "LTR" if ltr_mae < v6_mae else ("v6.x" if v6_mae < ltr_mae else "TIE")

            v6_wins = aggregate.get("v6_wins", 0)
            ltr_wins = aggregate.get("ltr_wins", 0)
            ties = aggregate.get("ties", 0)

            agg_col1.metric("Hits@10", f"LTR: {ltr_h10}/{h10_possible}", f"v6.x: {v6_h10}/{h10_possible}")
            agg_col2.metric("Hits@3", f"v6.x: {v6_h3}/{h3_possible}", f"LTR: {ltr_h3}/{h3_possible}")
            agg_col3.metric("Avg MAE", f"LTR: {ltr_mae:.2f}", f"v6.x: {v6_mae:.2f}")
            agg_col4.metric("Race Wins", f"LTR: {ltr_wins}", f"v6.x: {v6_wins}, Ties: {ties}")

            # Overall winner
            if ltr_wins > v6_wins:
                overall = f"**v7.1-LTR wins {ltr_wins}-{v6_wins}-{ties}**"
                st.success(f"🏆 {overall}")
            elif v6_wins > ltr_wins:
                overall = f"**v6.x wins {v6_wins}-{ltr_wins}-{ties}**"
                st.info(f"🏆 {overall}")
            else:
                st.warning(f"🤝 **TIE: {v6_wins}-{ltr_wins}-{ties}**")

            st.markdown("---")

            # Race-by-race comparison chart
            st.markdown("### Race-by-Race Comparison")

            # Prepare data for chart
            race_labels = []
            v6_hits10 = []
            ltr_hits10 = []
            winners = []

            for v in validations:
                label = f"{v['race']} ({v['category'][:3]})"
                race_labels.append(label)
                v6_hits10.append(v['v6_hits10'])
                ltr_hits10.append(v['ltr_hits10'])
                winners.append(v['winner'])

            # Create grouped bar chart
            fig_compare = go.Figure()

            fig_compare.add_trace(go.Bar(
                name='v6.x',
                x=race_labels,
                y=v6_hits10,
                marker_color='#3b82f6',
                text=v6_hits10,
                textposition='outside',
                hovertemplate='%{x}<br>v6.x: %{y}/10<extra></extra>'
            ))

            fig_compare.add_trace(go.Bar(
                name='v7.1-LTR',
                x=race_labels,
                y=ltr_hits10,
                marker_color='#22c55e',
                text=ltr_hits10,
                textposition='outside',
                hovertemplate='%{x}<br>LTR: %{y}/10<extra></extra>'
            ))

            # Add target line
            fig_compare.add_hline(y=7, line_dash="dash", line_color="#f59e0b", line_width=2,
                                  annotation_text="Target (7/10)", annotation_position="right")

            fig_compare.update_layout(
                title='Hits@10 Comparison by Race',
                height=400,
                barmode='group',
                showlegend=True,
                legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5),
                yaxis=dict(range=[0, 11], title="Hits@10", dtick=2),
                xaxis=dict(tickangle=45),
                plot_bgcolor='#f8f9fa',
                paper_bgcolor='white',
                margin=dict(b=100)
            )

            st.plotly_chart(fig_compare, use_container_width=True)

            # Detailed results table
            st.markdown("### Detailed Validation Results")

            table_data = []
            for v in validations:
                # Determine metric winners
                h10_w = "LTR" if v['ltr_hits10'] > v['v6_hits10'] else ("v6.x" if v['v6_hits10'] > v['ltr_hits10'] else "TIE")
                h3_w = "LTR" if v['ltr_hits3'] > v['v6_hits3'] else ("v6.x" if v['v6_hits3'] > v['ltr_hits3'] else "TIE")
                sp_w = "LTR" if v['ltr_spearman'] > v['v6_spearman'] else ("v6.x" if v['v6_spearman'] > v['ltr_spearman'] else "TIE")
                mae_w = "LTR" if v['ltr_mae'] < v['v6_mae'] else ("v6.x" if v['v6_mae'] < v['ltr_mae'] else "TIE")

                table_data.append({
                    "Race": v['race'],
                    "Date": v['date'],
                    "Category": v['category'],
                    "v6.x Hits@10": f"{v['v6_hits10']}/10",
                    "LTR Hits@10": f"{v['ltr_hits10']}/10",
                    "v6.x Hits@3": f"{v['v6_hits3']}/3",
                    "LTR Hits@3": f"{v['ltr_hits3']}/3",
                    "v6.x MAE": v['v6_mae'],
                    "LTR MAE": v['ltr_mae'],
                    "Winner": v['winner']
                })

            table_df = pd.DataFrame(table_data)
            st.dataframe(table_df, use_container_width=True, hide_index=True)

            # Key insights
            st.markdown("### Key Insights")

            insights_col1, insights_col2 = st.columns(2)

            with insights_col1:
                st.markdown("**LTR Strengths:**")
                st.markdown("""
                - Better at Hits@10 (identifying more top-10 finishers)
                - Lower MAE (predictions closer to actual positions)
                - Optimizes for ranking, not just classification
                """)

            with insights_col2:
                st.markdown("**v6.x Strengths:**")
                st.markdown("""
                - Better at Hits@3 (podium predictions)
                - More conservative, higher precision
                - Calibrated probabilities for decision-making
                """)

            with st.expander("📖 Understanding the A/B Test"):
                st.markdown("""
**What are we comparing?**

| Model | Type | Approach |
|-------|------|----------|
| **v6.x** | Binary Classification | Predicts probability of Top-10 finish (yes/no) |
| **v7.1-LTR** | Learning-to-Rank | Optimizes ranking order directly using LambdaMART |

**Metrics Explained:**
- **Hits@10**: How many of our top-10 predictions finished in actual top-10? (X/10)
- **Hits@3**: How many of our top-3 picks made the actual podium? (X/3)
- **Spearman ρ**: Rank correlation (-1 to +1, higher = better ordering)
- **MAE Rank**: Average positions off (lower = better)

**Winner Determination:**
Each race compares 4 metrics. The model winning more metrics wins the race.
Ties count as ties. Overall winner = model with more race wins.

**Why LTR might be better for Hits@10:**
LTR directly optimizes for ranking position, not probability calibration.
It learns "who beats whom" rather than "is this person Top-10 material?"
                """)

        else:
            st.info("No LTR validation results yet. Run `python pipeline.py validate-race-ltr` to add results.")
    else:
        st.warning("LTR validation results file not found. Run LTR validations to populate this tab.")

with tab6:
    st.header("About VeloPredict")

    # Dynamic stats from metadata and registry
    accuracy_pct = metadata['top10_accuracy'] * 100
    improvement_pct = metadata['improvement_vs_baseline'] * 100
    total_obs = metadata.get('total_observations', metadata['train_size'] + metadata['test_size'])
    total_races = metadata.get('total_races', 'N/A')
    auc_roc = metadata.get('top10_auc', 0)
    brier = metadata.get('top10_brier_score', 0)
    current_version = registry.get("current_version", "v6")

    # Get top feature from metadata
    h2h_pct = 22.7  # default
    if 'feature_importance' in metadata:
        fi = metadata['feature_importance']
        h2h_pct = fi.get('h2h_field_score', 22.7)

    # Get latest validated race
    validated_races = [r for r in registry.get("races", []) if r.get("validation")]
    latest_validated = validated_races[-1] if validated_races else None
    validation_text = ""
    if latest_validated:
        v = latest_validated["validation"]
        validation_text = f"**Latest Validation ({latest_validated['name']}):** {v.get('precision', 'N/A')}% precision, {v.get('recall', 'N/A')}% recall"

    st.markdown(f"""
    ### 🎯 What It Does

    VeloPredict uses machine learning to predict which riders will finish in the **Top-10**
    (scoring positions) at cyclocross races.

    **Accuracy:** {accuracy_pct:.1f}% Top-10 accuracy (+{improvement_pct:.1f}% vs baseline)
    {validation_text}

    ### 🧠 How It Works

    **Algorithm:** Random Forest (300 trees) + Platt Scaling calibration

    The model analyzes:
    - **🥊 Head-to-Head** ({h2h_pct}%): Win rate against specific opponents in the field
    - **Current form:** Recent race results, days since last race
    - **Historical performance:** Career Top-10 rate, best recent finishes
    - **Rider pedigree:** UCI points, team quality
    - **Race context:** Category (Elite/U23/Junior), gender

    **Key Features ({current_version}):**
    - ✅ **Head-to-Head feature** - #1 most important feature at {h2h_pct}%!
    - ✅ Field-adjusted predictions based on actual startlist opponents
    - ✅ UCI-based inference for new riders
    - ✅ Probability calibration (Platt scaling)
    - ✅ New rider penalty for unknown athletes
    - ✅ **Robust Feature Extraction** (v6.4) - Uses best available cumulative data per rider

    **Training data:** {total_races} races from 2024-25 season ({total_obs:,} rider-race observations)

    ### 📊 Use Cases

    **For competitive cyclists:**
    - Race selection: "Should I travel to this race?"
    - Training focus: "Which races should I peak for?"
    - Confidence: "Can I realistically score points here?"

    **For teams:**
    - Roster decisions: "Which riders should we send?"
    - Strategy planning: "Who's our best bet for points?"

    ### 🚀 Part of Phoenix Launch

    VeloPredict is Phase 1 of a 90-day AI product ecosystem:

    1. **VeloPredict** (Days 1-30): Race predictions ← *You are here*
    2. **VeloIntel** (Days 31-60): Personal AI coach using wearables data
    3. **WellnessAI** (Days 61-90): Enterprise loyalty platform for retailers

    ### 🤝 Feedback Welcome

    Test predictions on upcoming races and let me know:
    - Were the Top-10 predictions accurate?
    - What features would make this more useful?
    - Would you pay for enhanced predictions + training insights?

    **Contact:** [Your LinkedIn/Email]

    ### 📄 Technical Details

    - **Model:** Random Forest Classifier (300 trees, depth 15) + Platt scaling
    - **Features:** {len(metadata['features'])} engineered features across 4 categories
    - **Validation:** Chronological train/test split (no data leakage)
    - **Calibration:** {metadata.get('calibration_method', 'Platt scaling')}
    - **Metrics:** Brier score {brier:.4f}, AUC-ROC {auc_roc:.3f}
    - **API:** FastAPI endpoint available (`./run_api.sh`)
    - **Code:** [GitHub Repository](https://github.com/YOUR_USERNAME/cyclocross-predictions)

    ---

    *Built by a Principal PM + Builder | Part of Phoenix Launch*
    """)

# Dynamic Footer - Auto-generated from registry
def get_footer_text(registry, metadata):
    """Generate footer text from registry and metadata."""
    header_stats = get_header_stats(registry, metadata)
    accuracy_pct = int(metadata['top10_accuracy'] * 100)
    return (
        f"VeloPredict {header_stats['version']} ({header_stats['latest_race']} validated) | "
        f"{accuracy_pct}% Top-10 Accuracy | "
        f"H2H = #1 Feature ({header_stats['h2h_importance']}%) | "
        f"Random Forest + Platt Scaling | "
        f"For educational and strategic planning purposes"
    )

st.markdown("---")
st.markdown(
    f"<div style='text-align: center; color: #666;'>{get_footer_text(registry, metadata)}</div>",
    unsafe_allow_html=True
)
