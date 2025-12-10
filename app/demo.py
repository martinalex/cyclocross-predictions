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
@st.cache_resource
def load_models():
    """Load trained models and metadata"""
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
    model_top10, model_top3, metadata = load_models()
    historical_data = load_data()
    model_loaded = True
except Exception as e:
    model_loaded = False
    error_msg = str(e)

# Header
st.title("🚴 VeloPredict: Cyclocross Race Predictions")
st.markdown("**AI-powered predictions with H2H analysis - 84% Top-10 accuracy**")
st.caption("Version: v6.1 (Sardinia validated) | 50 races, 8,800+ observations | H2H = #1 Feature (22.9%) | Live: 100% recall at Sardinia")

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

    st.markdown("---")
    st.markdown("### 🎯 Live Validation")
    st.markdown("**Sardinia (Dec 7):**")
    st.markdown("- ✅ 100% recall (7/7 high-conf)")
    st.markdown("- ✅ All podium predictions correct")
    st.markdown("")
    st.markdown("**Flamanville (Nov 30):**")
    st.markdown("- ✅ 80% Top-10 (16/20)")
    st.markdown("")
    st.markdown("**Tabor (Nov 23):**")
    st.markdown("- ✅ 90% Top-10 (18/20)")

# Main content
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔮 Predict Race", "🤖 AI Analysis", "📈 Model Insights", "📊 Season Tracker", "📚 About"])

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
    st.header("AI Race Analysis")
    st.markdown("**Generate LLM-powered narrative analysis of predictions**")

    # Check for API key
    import os
    api_key_set = bool(os.environ.get("ANTHROPIC_API_KEY"))

    if not api_key_set:
        st.warning("⚠️ ANTHROPIC_API_KEY not set. Set it to enable AI narratives.")
        st.code("export ANTHROPIC_API_KEY='your-key-here'")
    else:
        st.success("✅ Anthropic API key configured")

    # Category and rider selection for AI analysis
    ai_category = st.selectbox(
        "Category for AI Analysis",
        options=["Men Elite", "Women Elite"],
        key="ai_category"
    )

    # Get recent riders for this category
    ai_recent_data = historical_data[
        (historical_data["race_date"] > "2024-11-01") &
        (historical_data["Category Name"] == ai_category)
    ].copy()

    ai_recent_data["rider_name_std"] = ai_recent_data["rider_name"].apply(standardize_name)

    ai_riders = (
        ai_recent_data
        .groupby("rider_name_std")
        .agg({
            "rider_name": "last",
            "Carried Points": "last",
        })
        .sort_values("Carried Points", ascending=True)
        .head(40)
    )
    ai_riders.index = ai_riders["rider_name"]

    ai_selected = st.multiselect(
        f"Select riders for {ai_category} analysis",
        options=ai_riders.index.tolist(),
        default=ai_riders.index.tolist()[:15] if len(ai_riders) >= 15 else ai_riders.index.tolist(),
        key="ai_riders"
    )

    race_name = st.text_input("Race Name", value="UCI World Cup", key="ai_race_name")

    if st.button("🤖 Generate AI Analysis", disabled=not api_key_set or len(ai_selected) < 3):
        if len(ai_selected) < 3:
            st.error("Select at least 3 riders")
        else:
            with st.spinner("Generating predictions and AI analysis..."):
                # Build predictions for selected riders
                field_names_norm = [standardize_name(r) for r in ai_selected if standardize_name(r)]

                ai_predictions = []
                for rider in ai_selected:
                    rider_std = standardize_name(rider)
                    rider_history = historical_data[
                        (historical_data["rider_name_std"] == rider_std) &
                        (historical_data["Category Name"] == ai_category)
                    ]

                    if len(rider_history) == 0:
                        continue

                    rider_data = rider_history.iloc[-1]

                    # Calculate H2H
                    h2h_features = calculate_h2h_features(rider_std, field_names_norm)

                    # Prepare features
                    feature_cols = [f for f in config.NUMERIC_FEATURES if f != 'h2h_field_score'] + config.CATEGORICAL_FEATURES
                    X = pd.DataFrame([rider_data[feature_cols]])
                    X['h2h_field_score'] = h2h_features['h2h_field_score']
                    X = pd.get_dummies(X, columns=config.CATEGORICAL_FEATURES, drop_first=True)

                    for feat in metadata['features']:
                        if feat not in X.columns:
                            X[feat] = 0
                    X = X[metadata['features']]
                    X = X.fillna(config.FILL_VALUES)

                    top10_prob = model_top10.predict_proba(X)[0][1]
                    top3_prob = model_top3.predict_proba(X)[0][1]

                    ai_predictions.append({
                        "Rider": rider,
                        "Top-10 Probability": top10_prob,
                        "Top-3 Probability": top3_prob,
                        "H2H Field Score": h2h_features['h2h_field_score'],
                        "H2H Confidence": h2h_features['h2h_confidence'],
                        "Recent Form": rider_data["avg_place_last3"],
                        "Career Top-10 Rate": rider_data["top10_rate_career"],
                        "Status": "found"
                    })

                if ai_predictions:
                    df_ai = pd.DataFrame(ai_predictions).sort_values("Top-10 Probability", ascending=False)

                    try:
                        from src.llm.narratives import explain_predictions
                        narratives = explain_predictions(df_ai, race_name)

                        st.markdown("---")
                        st.markdown("### 📝 Race Preview")
                        st.markdown(narratives["race_preview"])

                        st.markdown("---")
                        st.markdown("### 🏆 Podium Prediction")
                        st.markdown(narratives["podium_prediction"])

                        st.markdown("---")
                        st.markdown("### 🔍 Top Rider Insights")
                        for item in narratives["top_insights"]:
                            st.markdown(f"**{item['rider']}**")
                            st.markdown(f"> {item['insight']}")
                            st.markdown("")

                    except Exception as e:
                        st.error(f"Error generating narrative: {e}")
                else:
                    st.error("No predictions could be generated for selected riders")

with tab3:
    st.header("Model Insights")

    st.markdown("### 🎯 Feature Importance")
    st.markdown("What the model considers most important:")

    st.markdown("""
    **Top 5 Most Important Features (v5 with H2H):**
    1. **🥊 H2H Field Score** (21.4%) - Historical win rate vs specific opponents
    2. **Average Place (Last 3)** (13.0%) - Current form trajectory
    3. **Top-10 Career Rate** (12.9%) - Historical success in scoring positions
    4. **Best Place (Last 5)** (12.7%) - Recent peak performance
    5. **Last Place** (9.4%) - Momentum from most recent race
    """)

    st.info("💡 **H2H is now the #1 feature!** The model weighs head-to-head history against the actual race field more than any other factor.")

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
                }
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

    # Summary stats
    total_predictions = sum(r["predictions"] for r in RACES)
    total_correct = sum(r["correct"] for r in RACES)
    season_precision = (total_correct / total_predictions * 100) if total_predictions > 0 else 0

    st.caption(f"{len(RACES)} Races | {len(VERSIONS)} Versions | {total_predictions} Predictions | {total_correct} Correct | Season Precision: {season_precision:.0f}% | Current: v6")

    # Create interactive 6-panel dashboard with Plotly
    fig = make_subplots(
        rows=3, cols=2,
        subplot_titles=(
            'Live Race Performance', 'Prediction Volume & Accuracy',
            'Training Accuracy by Version', 'Model Quality (AUC-ROC) v3-v6',
            'Feature Importance Evolution', 'Training Dataset Growth'
        ),
        vertical_spacing=0.12,
        horizontal_spacing=0.08
    )

    # ============================================================
    # Panel 1: Live Race Performance (top left)
    # ============================================================
    race_labels = [f"{r['name']} ({r['version']})" for r in RACES]

    fig.add_trace(go.Bar(
        name='Recall (%)', x=race_labels, y=[r["accuracy"] for r in RACES],
        marker_color='#22c55e', text=[f"{r['accuracy']}%" for r in RACES],
        textposition='outside', hovertemplate='%{x}<br>Recall: %{y}%<extra></extra>'
    ), row=1, col=1)

    fig.add_trace(go.Bar(
        name='Precision (%)', x=race_labels, y=[r["precision"] for r in RACES],
        marker_color='#3b82f6', text=[f"{r['precision']}%" for r in RACES],
        textposition='outside', hovertemplate='%{x}<br>Precision: %{y}%<extra></extra>'
    ), row=1, col=1)

    fig.add_trace(go.Bar(
        name='Podium (%)', x=race_labels, y=[r["podium"] for r in RACES],
        marker_color='#f59e0b', text=[f"{r['podium']}%" for r in RACES],
        textposition='outside', hovertemplate='%{x}<br>Podium: %{y}%<extra></extra>'
    ), row=1, col=1)

    # ============================================================
    # Panel 2: Predictions Made vs Correct (top right)
    # ============================================================
    race_date_labels = [f"{r['name']} ({r['date']})" for r in RACES]

    fig.add_trace(go.Bar(
        name='Predictions Made', x=race_date_labels, y=[r["predictions"] for r in RACES],
        marker_color='#94a3b8', text=[str(r['predictions']) for r in RACES],
        textposition='outside', hovertemplate='%{x}<br>Predictions: %{y}<extra></extra>',
        showlegend=True
    ), row=1, col=2)

    fig.add_trace(go.Bar(
        name='Correct (Top-10)', x=race_date_labels, y=[r["correct"] for r in RACES],
        marker_color='#22c55e', text=[str(r['correct']) for r in RACES],
        textposition='outside', hovertemplate='%{x}<br>Correct: %{y}<extra></extra>',
        showlegend=True
    ), row=1, col=2)

    # ============================================================
    # Panel 3: Training Accuracy - All Versions (middle left)
    # ============================================================
    v_all = [v["version"] for v in VERSIONS]
    accuracies = [v["accuracy"] for v in VERSIONS]
    innovations = [v["innovation"] for v in VERSIONS]

    fig.add_trace(go.Bar(
        name='Training Accuracy', x=v_all, y=accuracies,
        marker_color='#22c55e', text=[f"{a}%" for a in accuracies],
        textposition='outside', showlegend=False,
        hovertemplate='%{x}<br>Accuracy: %{y}%<br>%{customdata}<extra></extra>',
        customdata=innovations
    ), row=2, col=1)

    # ============================================================
    # Panel 4: Model Quality - AUC-ROC (middle right)
    # ============================================================
    versions_with_auc = [v for v in VERSIONS if v["auc"] is not None]
    v_names = [v["version"] for v in versions_with_auc]
    aucs = [v["auc"] for v in versions_with_auc]
    auc_innovations = [v["innovation"] for v in versions_with_auc]

    fig.add_trace(go.Scatter(
        name='AUC-ROC', x=v_names, y=aucs, mode='lines+markers+text',
        line=dict(color='#8b5cf6', width=3),
        marker=dict(size=12, color='white', line=dict(color='#8b5cf6', width=2)),
        text=[f"{a:.3f}" for a in aucs], textposition='top center',
        hovertemplate='%{x}<br>AUC: %{y:.3f}<br>%{customdata}<extra></extra>',
        customdata=auc_innovations, showlegend=False
    ), row=2, col=2)

    # ============================================================
    # Panel 5: Feature Importance Evolution (bottom left)
    # ============================================================
    features = ["h2h_field_score", "avg_place_last3", "best_place_last5", "top10_rate_career", "uci_points_normalized"]
    feature_labels = ["H2H Score", "Avg Place (L3)", "Best Place (L5)", "Top-10 Rate", "UCI Points"]
    feature_colors = ["#ef4444", "#22c55e", "#3b82f6", "#f59e0b", "#8b5cf6"]
    versions_fi = list(FEATURE_IMPORTANCE.keys())

    for feat, label, color in zip(features, feature_labels, feature_colors):
        values = [FEATURE_IMPORTANCE[v].get(feat, 0) for v in versions_fi]
        fig.add_trace(go.Scatter(
            name=label, x=versions_fi, y=values, mode='lines+markers',
            line=dict(color=color, width=2),
            marker=dict(size=8, color=color),
            hovertemplate=f'{label}<br>%{{x}}: %{{y:.1f}}%<extra></extra>'
        ), row=3, col=1)

    # Add annotation for H2H breakthrough
    fig.add_annotation(
        x='v5', y=21.4, text='H2H becomes #1', showarrow=True,
        arrowhead=2, arrowcolor='#ef4444', font=dict(color='#ef4444', size=10),
        ax=-40, ay=-30, row=3, col=1
    )

    # ============================================================
    # Panel 6: Dataset Growth (bottom right)
    # ============================================================
    obs = [v["observations"] for v in VERSIONS]

    fig.add_trace(go.Scatter(
        name='Observations', x=v_all, y=obs, mode='lines+markers+text',
        fill='tozeroy', fillcolor='rgba(6, 182, 212, 0.2)',
        line=dict(color='#06b6d4', width=3),
        marker=dict(size=10, color='white', line=dict(color='#06b6d4', width=2)),
        text=[f"{o:,}" for o in obs], textposition='top center',
        hovertemplate='%{x}<br>Observations: %{y:,}<extra></extra>',
        showlegend=False
    ), row=3, col=2)

    # Update layout
    fig.update_layout(
        height=900,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        barmode='group',
        hovermode='x unified',
        plot_bgcolor='#f8f9fa',
        paper_bgcolor='white'
    )

    # Update axes
    fig.update_yaxes(range=[0, 115], row=1, col=1, title_text="Percentage")
    fig.update_yaxes(range=[0, 55], row=1, col=2, title_text="Count")
    fig.update_yaxes(range=[74, 82], row=2, col=1, title_text="Accuracy (%)")
    fig.update_yaxes(range=[0.810, 0.845], row=2, col=2, title_text="AUC-ROC")
    fig.update_yaxes(range=[0, 28], row=3, col=1, title_text="Importance (%)")
    fig.update_yaxes(range=[7500, 8600], row=3, col=2, title_text="Observations")

    # Add gridlines
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
    fig.update_xaxes(showgrid=False)

    st.plotly_chart(fig, use_container_width=True)

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

    # Prepare data for plotting
    scatter_fig = go.Figure()

    # Separate by category (true positive, false positive, below threshold)
    for rider, prob, position, gender in predictions:
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

        symbol = 'square' if gender == 'W' else 'circle'
        gender_label = 'Women Elite' if gender == 'W' else 'Men Elite'

        scatter_fig.add_trace(go.Scatter(
            x=[prob * 100],
            y=[position],
            mode='markers+text',
            marker=dict(size=14, color=color, symbol=symbol, line=dict(color='white', width=2)),
            text=[rider],
            textposition='middle right',
            textfont=dict(size=10),
            name=f'{rider} ({gender_label})',
            hovertemplate=f'<b>{rider}</b><br>Probability: {prob*100:.0f}%<br>Position: {position}<br>{gender_label}<br>{category}<extra></extra>',
            showlegend=False
        ))

    # Add threshold line
    scatter_fig.add_vline(
        x=threshold * 100, line_dash="dash", line_color="#3b82f6", line_width=2,
        annotation_text=f"Threshold ({int(threshold*100)}%)",
        annotation_position="top"
    )

    # Add Top-10 zone
    scatter_fig.add_hrect(y0=0, y1=10.5, fillcolor="#22c55e", opacity=0.1, line_width=0)
    scatter_fig.add_hline(y=10.5, line_color="#22c55e", line_width=1, opacity=0.5)

    # Calculate stats
    above_thresh = [(r, p, pos, g) for r, p, pos, g in predictions if p >= threshold]
    true_pos = sum(1 for _, _, pos, _ in above_thresh if pos <= 10)
    false_pos = len(above_thresh) - true_pos
    total_top10 = sum(1 for _, _, pos, _ in predictions if pos <= 10)
    precision = true_pos / len(above_thresh) * 100 if above_thresh else 0
    recall = true_pos / total_top10 * 100 if total_top10 > 0 else 0

    max_position = max(p[2] for p in predictions)

    scatter_fig.update_layout(
        title=dict(
            text=f"VeloPredict {version} | {selected_race}<br><sub>Predicted Probability vs Actual Result</sub>",
            x=0.5,
            font=dict(size=16)
        ),
        xaxis_title="Predicted Top-10 Probability (%)",
        yaxis_title="Actual Finish Position",
        xaxis=dict(range=[0, 105], showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
        yaxis=dict(range=[max_position + 3, 0], showgrid=True, gridcolor='rgba(0,0,0,0.1)'),  # Inverted
        height=500,
        plot_bgcolor='#f8f9fa',
        paper_bgcolor='white',
        hovermode='closest',
        annotations=[
            dict(
                x=5, y=5, text="TOP 10 ZONE", showarrow=False,
                font=dict(color='#22c55e', size=12, weight='bold'), opacity=0.7
            )
        ]
    )

    st.plotly_chart(scatter_fig, use_container_width=True)

    # Stats row
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
    stat_col1.metric("Predictions", len(above_thresh))
    stat_col2.metric("True Positives", true_pos)
    stat_col3.metric("Precision", f"{precision:.0f}%")
    stat_col4.metric("Recall", f"{recall:.0f}%")

    # Legend
    st.markdown("""
    **Legend:** 🟢 True Positive (predicted + Top-10) | 🔴 False Positive (predicted + missed) | ⚫ Below threshold | ⬤ Men | ◼ Women
    """)

with tab5:
    st.header("About VeloPredict")

    st.markdown("""
    ### 🎯 What It Does

    VeloPredict uses machine learning to predict which riders will finish in the **Top-10**
    (scoring positions) at cyclocross races.

    **Accuracy:** 76.9% Top-10 accuracy (+29.4% vs baseline)
    **Validation:** Flamanville H2H correlation r=0.773 (men), r=0.867 (women)

    ### 🧠 How It Works

    **Algorithm:** Random Forest (300 trees) + Platt Scaling calibration

    The model analyzes:
    - **🥊 Head-to-Head** (21.4%): Win rate against specific opponents in the field
    - **Current form:** Recent race results, days since last race
    - **Historical performance:** Career Top-10 rate, best recent finishes
    - **Rider pedigree:** UCI points, team quality
    - **Race context:** Category (Elite/U23/Junior), gender

    **Key Improvements (v5 - H2H):**
    - ✅ **Head-to-Head feature** - #1 most important feature!
    - ✅ Field-adjusted predictions based on actual startlist opponents
    - ✅ UCI-based inference for new riders
    - ✅ Probability calibration (Platt scaling)
    - ✅ DNS risk filtering

    **Training data:** 49 races from 2024-25 season (8,188 rider-race observations)

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
    - **Features:** 15 engineered features across 4 categories
    - **Validation:** Chronological train/test split (no data leakage)
    - **Calibration:** Sigmoid (Platt scaling) for probability calibration
    - **Metrics:** Brier score <0.2, AUC-ROC 0.85+
    - **API:** FastAPI endpoint available (`./run_api.sh`)
    - **Code:** [GitHub Repository](https://github.com/YOUR_USERNAME/cyclocross-predictions)

    ---

    *Built by a Principal PM + Builder | Part of Phoenix Launch*
    """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "VeloPredict v6 (H2H + New Rider Penalty) | 78% Top-10 Accuracy | "
    "H2H = #1 Feature (22.5%) | "
    "Random Forest + Platt Scaling | "
    "For educational and strategic planning purposes"
    "</div>",
    unsafe_allow_html=True
)
