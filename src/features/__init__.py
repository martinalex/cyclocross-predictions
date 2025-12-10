"""
Feature building module for VeloPredict.
Provides unified feature extraction for CLI, API, and Streamlit.
"""

from src.features.builder import FeatureBuilder
from src.features.names import normalize_name, standardize_name, NAME_CORRECTIONS

__all__ = [
    'FeatureBuilder',
    'normalize_name',
    'standardize_name',
    'NAME_CORRECTIONS',
]
