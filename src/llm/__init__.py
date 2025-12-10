"""
LLM integration for VeloPredict.
Generates natural language narratives for race predictions.
"""

from src.llm.narratives import generate_race_narrative, generate_rider_insight

__all__ = [
    'generate_race_narrative',
    'generate_rider_insight',
]
