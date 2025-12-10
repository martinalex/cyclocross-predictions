"""
LLM-powered narrative generation for race predictions.

Uses Claude to generate natural language explanations of predictions,
making the ML model's outputs more accessible and insightful.
"""
import os
from anthropic import Anthropic
import pandas as pd
from typing import Optional


# Initialize client (uses ANTHROPIC_API_KEY env var)
def get_client() -> Anthropic:
    """Get Anthropic client, raising helpful error if key missing."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY not set. "
            "Set it with: export ANTHROPIC_API_KEY='your-key-here'"
        )
    return Anthropic(api_key=api_key)


def generate_rider_insight(
    rider_name: str,
    top10_prob: float,
    top3_prob: float,
    h2h_score: float,
    h2h_confidence: float,
    recent_form: float,
    career_top10_rate: float,
    is_new_rider: bool,
    status: str,
    field_size: int = 30
) -> str:
    """
    Generate a 1-2 sentence insight about a rider's prediction.

    Args:
        rider_name: Display name of rider
        top10_prob: Probability of Top-10 finish (0-1)
        top3_prob: Probability of podium finish (0-1)
        h2h_score: Head-to-head win rate vs field (0-1)
        h2h_confidence: Confidence in H2H score (0-1)
        recent_form: Average place in last 3 races
        career_top10_rate: Career Top-10 finish rate (0-1)
        is_new_rider: True if no historical data
        status: 'found' or 'new_rider'
        field_size: Number of riders in field

    Returns:
        1-2 sentence narrative about the rider
    """
    client = get_client()

    # Build context for the LLM
    h2h_str = f"{h2h_score*100:.0f}%" if h2h_confidence > 0.3 else "unknown"

    prompt = f"""You are a cyclocross race analyst. Generate a single 1-2 sentence insight about this rider's chances.

RIDER: {rider_name}
PREDICTION DATA:
- Top-10 probability: {top10_prob*100:.1f}%
- Podium probability: {top3_prob*100:.1f}%
- H2H win rate vs this field: {h2h_str} (based on {int(h2h_confidence * field_size)} known opponents)
- Recent form (avg place last 3 races): {recent_form:.1f}
- Career Top-10 rate: {career_top10_rate*100:.0f}%
- Data status: {"New rider - limited historical data" if is_new_rider else "Known rider with history"}

Write ONE insight (1-2 sentences max) that explains WHY they have this probability. Focus on the most relevant factor. Be specific and analytical, not generic. Use cycling terminology naturally.

Examples of good insights:
- "Dominant H2H record (89%) against 12 of these riders suggests he'll be in the mix, though recent form has dipped."
- "Limited data makes this prediction uncertain, but UCI ranking suggests mid-pack potential."
- "Elite-level consistency (85% career Top-10 rate) combined with strong recent form points to another scoring finish."

Your insight:"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=150,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text.strip()


def generate_race_narrative(
    predictions_df: pd.DataFrame,
    race_name: str = "Race",
    category: str = "Men Elite",
    top_n: int = 5
) -> str:
    """
    Generate a race preview narrative from predictions.

    Args:
        predictions_df: DataFrame with prediction columns (Rider, Top-10 Probability, etc.)
        race_name: Name of the race
        category: Race category
        top_n: Number of top riders to highlight

    Returns:
        2-3 paragraph race preview narrative
    """
    client = get_client()

    # Get top predicted riders
    top_riders = predictions_df.nlargest(top_n, "Top-10 Probability")

    # Build rider summaries
    rider_summaries = []
    for _, row in top_riders.iterrows():
        h2h_str = f"{row['H2H Field Score']*100:.0f}%" if row.get('H2H Confidence', 0) > 0.3 else "N/A"
        summary = (
            f"- {row['Rider']}: {row['Top-10 Probability']*100:.0f}% Top-10, "
            f"{row['Top-3 Probability']*100:.0f}% podium, "
            f"H2H: {h2h_str}, "
            f"form: {row.get('Recent Form', 'N/A')}"
        )
        rider_summaries.append(summary)

    # Stats
    high_conf = len(predictions_df[predictions_df["Top-10 Probability"] > 0.7])
    new_riders = len(predictions_df[predictions_df["Status"] == "new_rider"])
    total = len(predictions_df)

    prompt = f"""You are a cyclocross race analyst writing a preview for {race_name} ({category}).

PREDICTION DATA:
Top {top_n} predicted finishers:
{chr(10).join(rider_summaries)}

Field stats:
- Total riders: {total}
- High confidence predictions (>70%): {high_conf}
- New riders (limited data): {new_riders}

Write a 2-3 paragraph race preview (150-200 words) that:
1. Opens with the headline story (who's favored and why)
2. Highlights 2-3 key matchups or storylines based on the H2H and form data
3. Mentions uncertainty factors (new riders, close probabilities)

Be specific about the data. Use natural cycling terminology. Sound like a knowledgeable analyst, not a generic sports writer.

Race preview:"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text.strip()


def generate_podium_prediction(
    predictions_df: pd.DataFrame,
    race_name: str = "Race"
) -> str:
    """
    Generate a podium prediction with reasoning.

    Args:
        predictions_df: DataFrame with prediction columns
        race_name: Name of the race

    Returns:
        Podium prediction with 1-sentence reasoning for each
    """
    client = get_client()

    # Get top 3 by podium probability
    top3 = predictions_df.nlargest(3, "Top-3 Probability")

    rider_data = []
    for i, (_, row) in enumerate(top3.iterrows()):
        h2h_str = f"{row['H2H Field Score']*100:.0f}%" if row.get('H2H Confidence', 0) > 0.3 else "N/A"
        rider_data.append({
            "position": i + 1,
            "name": row['Rider'],
            "podium_prob": row['Top-3 Probability'] * 100,
            "top10_prob": row['Top-10 Probability'] * 100,
            "h2h": h2h_str,
            "form": row.get('Recent Form', 'N/A'),
            "career_rate": row.get('Career Top-10 Rate', 0) * 100
        })

    prompt = f"""You are a cyclocross analyst making podium predictions for {race_name}.

PREDICTED PODIUM:
1. {rider_data[0]['name']} - {rider_data[0]['podium_prob']:.0f}% podium probability, H2H: {rider_data[0]['h2h']}, recent form: {rider_data[0]['form']}
2. {rider_data[1]['name']} - {rider_data[1]['podium_prob']:.0f}% podium probability, H2H: {rider_data[1]['h2h']}, recent form: {rider_data[1]['form']}
3. {rider_data[2]['name']} - {rider_data[2]['podium_prob']:.0f}% podium probability, H2H: {rider_data[2]['h2h']}, recent form: {rider_data[2]['form']}

Format your response EXACTLY like this:
🥇 [Name]: [One sentence explaining why they're predicted to win]
🥈 [Name]: [One sentence explaining second place prediction]
🥉 [Name]: [One sentence explaining third place prediction]

Be specific about the data driving each prediction. Keep each explanation to ONE sentence."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text.strip()


# Convenience function for CLI
def explain_predictions(predictions_df: pd.DataFrame, race_name: str = "Race") -> dict:
    """
    Generate all narratives for a set of predictions.

    Returns dict with:
        - race_preview: Full race narrative
        - podium_prediction: Podium picks with reasoning
        - top_insights: Individual insights for top 5 riders
    """
    result = {
        "race_preview": generate_race_narrative(predictions_df, race_name),
        "podium_prediction": generate_podium_prediction(predictions_df, race_name),
        "top_insights": []
    }

    # Generate individual insights for top 5
    top5 = predictions_df.nlargest(5, "Top-10 Probability")
    for _, row in top5.iterrows():
        insight = generate_rider_insight(
            rider_name=row['Rider'],
            top10_prob=row['Top-10 Probability'],
            top3_prob=row['Top-3 Probability'],
            h2h_score=row.get('H2H Field Score', 0.5),
            h2h_confidence=row.get('H2H Confidence', 0),
            recent_form=row.get('Recent Form', 25),
            career_top10_rate=row.get('Career Top-10 Rate', 0),
            is_new_rider=row.get('Status') == 'new_rider',
            status=row.get('Status', 'found'),
            field_size=len(predictions_df)
        )
        result["top_insights"].append({
            "rider": row['Rider'],
            "insight": insight
        })

    return result
