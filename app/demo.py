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

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
import config
from head_to_head import get_h2h_matrix, calculate_h2h_features
from predict_race import standardize_name

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

# Load historical data
@st.cache_data
def load_data():
    """Load historical race data"""
    df = pd.read_csv(config.RESULTS_WITH_FEATURES, parse_dates=["race_date"])
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
st.markdown("**AI-powered predictions with H2H analysis - 77% Top-10 accuracy**")
st.caption("Version: v5 (H2H) | Model: Random Forest + Platt Scaling | H2H = #1 Feature (21.4%)")

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
    st.markdown("**Tabor UCI World Cup:**")
    st.markdown("- ✅ 90% Top-10 accuracy (18/20)")
    st.markdown("- ✅ Men Elite: 9/10 correct")
    st.markdown("- ✅ Women Elite: 9/10 correct")

# Main content
tab1, tab2, tab3 = st.tabs(["🔮 Predict Race", "📈 Model Insights", "📚 About"])

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

    recent_riders = (
        historical_data[
            (historical_data["race_date"] > "2024-11-01") &
            (historical_data["Category Name"] == category)
        ]
        .groupby("rider_name")
        .agg({
            "Place": "mean",
            "Carried Points": "last",
            "team_tier": "last",
            "top10_rate_career": "last",
            "Team Name": get_last_non_empty
        })
        .sort_values("Carried Points", ascending=True)  # Lower points = better riders
        .head(50)
    )

    # Display rider selector
    selected_riders = st.multiselect(
        f"Choose riders from {category} (showing top 50 by UCI points)",
        options=recent_riders.index.tolist(),
        default=recent_riders.index.tolist()[:10] if len(recent_riders) >= 10 else recent_riders.index.tolist()
    )

    if selected_riders:
        # Build normalized field list for H2H calculations
        field_names_norm = [standardize_name(r) for r in selected_riders if standardize_name(r)]

        # Get latest features for selected riders in this category
        predictions = []

        for rider in selected_riders:
            rider_history = historical_data[
                (historical_data["rider_name"] == rider) &
                (historical_data["Category Name"] == category)
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

with tab3:
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
    "VeloPredict v5 (H2H) | 77% Top-10 Accuracy | "
    "H2H = #1 Feature (21.4%) | "
    "Random Forest + Platt Scaling | "
    "For educational and strategic planning purposes"
    "</div>",
    unsafe_allow_html=True
)
