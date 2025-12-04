"""
Head-to-Head Feature Module

Calculates historical win rates between pairs of riders and provides
field-adjusted head-to-head scores for race predictions.
"""
import pandas as pd
import numpy as np
from collections import defaultdict
from pathlib import Path

import config


class HeadToHeadMatrix:
    """Builds and queries head-to-head records between riders."""

    def __init__(self):
        self.h2h = defaultdict(lambda: defaultdict(lambda: [0, 0]))  # [wins, total]
        self._built = False

    def build_from_results(self, results_df: pd.DataFrame, category_filter: str = "Elite"):
        """
        Build head-to-head matrix from historical race results.

        Args:
            results_df: DataFrame with columns: race_id, rider_name_norm, Place, Category Name
            category_filter: Only include races matching this category (e.g., "Elite")
        """
        # Filter to relevant categories
        if category_filter:
            df = results_df[results_df['Category Name'].str.contains(category_filter, na=False, case=False)]
        else:
            df = results_df.copy()

        # Group by race and build pairwise records
        for race_id, race_df in df.groupby('race_id'):
            race_df = race_df.dropna(subset=['Place', 'rider_name_norm'])

            # Get riders with their places and categories
            riders = race_df[['rider_name_norm', 'Place', 'Category Name']].values

            for i in range(len(riders)):
                for j in range(i+1, len(riders)):
                    r1_name, r1_place, r1_cat = riders[i]
                    r2_name, r2_place, r2_cat = riders[j]

                    # Only compare within same category
                    if r1_cat != r2_cat:
                        continue

                    # Record the head-to-head result
                    self.h2h[r1_name][r2_name][1] += 1  # total races together
                    self.h2h[r2_name][r1_name][1] += 1

                    if r1_place < r2_place:
                        self.h2h[r1_name][r2_name][0] += 1  # r1 won (better place)
                    elif r2_place < r1_place:
                        self.h2h[r2_name][r1_name][0] += 1  # r2 won
                    # If tied, neither gets a win

        self._built = True

        # Count stats
        total_pairs = sum(len(v) for v in self.h2h.values()) // 2
        total_riders = len(self.h2h)
        print(f"H2H matrix built: {total_riders} riders, {total_pairs} unique pairs")

    def get_win_rate(self, rider1: str, rider2: str) -> float | None:
        """
        Get rider1's historical win rate against rider2.

        Returns:
            Win rate (0.0 to 1.0) or None if never raced together
        """
        if not self._built:
            raise ValueError("Matrix not built. Call build_from_results first.")

        if rider2 not in self.h2h[rider1]:
            return None

        wins, total = self.h2h[rider1][rider2]
        if total == 0:
            return None

        return wins / total

    def get_races_together(self, rider1: str, rider2: str) -> int:
        """Get number of races rider1 and rider2 have competed in together."""
        if rider2 not in self.h2h[rider1]:
            return 0
        return self.h2h[rider1][rider2][1]

    def get_field_h2h_score(self, rider: str, field: list[str], min_races: int = 1) -> dict:
        """
        Calculate rider's head-to-head score against a specific field of opponents.

        Args:
            rider: The rider to evaluate
            field: List of opponent rider names (normalized)
            min_races: Minimum races together to include opponent in calculation

        Returns:
            dict with:
                - h2h_score: Average win rate against known opponents (0-1)
                - known_opponents: Number of opponents with H2H data
                - total_opponents: Total opponents in field
                - confidence: known_opponents / total_opponents
        """
        opponents = [r for r in field if r != rider]

        if not opponents:
            return {
                'h2h_score': 0.5,  # Neutral if no opponents
                'known_opponents': 0,
                'total_opponents': 0,
                'confidence': 0.0
            }

        win_rates = []
        for opp in opponents:
            races = self.get_races_together(rider, opp)
            if races >= min_races:
                wr = self.get_win_rate(rider, opp)
                if wr is not None:
                    win_rates.append(wr)

        known = len(win_rates)
        total = len(opponents)

        if known == 0:
            # No H2H data - return neutral score with 0 confidence
            return {
                'h2h_score': 0.5,
                'known_opponents': 0,
                'total_opponents': total,
                'confidence': 0.0
            }

        return {
            'h2h_score': np.mean(win_rates),
            'known_opponents': known,
            'total_opponents': total,
            'confidence': known / total
        }


# Module-level singleton for caching
_h2h_matrix = None


def get_h2h_matrix() -> HeadToHeadMatrix:
    """Get or create the head-to-head matrix singleton."""
    global _h2h_matrix

    if _h2h_matrix is None:
        _h2h_matrix = HeadToHeadMatrix()

        # Load results and build matrix
        results_path = config.CLEAN_DIR / "results_with_features.csv"
        if results_path.exists():
            results_df = pd.read_csv(results_path)
            _h2h_matrix.build_from_results(results_df, category_filter="Elite")
        else:
            print(f"Warning: Results file not found at {results_path}")

    return _h2h_matrix


def calculate_h2h_features(rider_name_norm: str, field_names_norm: list[str]) -> dict:
    """
    Calculate head-to-head features for a rider against a specific field.

    Args:
        rider_name_norm: Normalized rider name
        field_names_norm: List of normalized names of all riders in the field

    Returns:
        dict with h2h features ready to add to model features
    """
    h2h = get_h2h_matrix()
    result = h2h.get_field_h2h_score(rider_name_norm, field_names_norm)

    return {
        'h2h_field_score': result['h2h_score'],
        'h2h_confidence': result['confidence'],
        'h2h_known_opponents': result['known_opponents']
    }


if __name__ == "__main__":
    # Test the module
    print("Testing Head-to-Head Module")
    print("=" * 50)

    h2h = get_h2h_matrix()

    # Test some known matchups
    test_pairs = [
        ('joris nieuwenhuis', 'eli iserbyt'),
        ('lucinda brand', 'ceylin alvarado'),
        ('toon aerts', 'laurens sweeck'),
    ]

    print("\nSample head-to-head records:")
    for r1, r2 in test_pairs:
        wr = h2h.get_win_rate(r1, r2)
        races = h2h.get_races_together(r1, r2)
        if wr is not None:
            print(f"  {r1} vs {r2}: {wr*100:.0f}% ({races} races)")
        else:
            print(f"  {r1} vs {r2}: no data")

    # Test field-adjusted score
    print("\nField-adjusted scores for sample startlist:")
    test_field = [
        'joris nieuwenhuis', 'eli iserbyt', 'laurens sweeck',
        'toon aerts', 'yordi corsus', 'niels vandeputte'
    ]

    for rider in test_field:
        features = calculate_h2h_features(rider, test_field)
        print(f"  {rider}: {features['h2h_field_score']*100:.1f}% "
              f"(conf: {features['h2h_confidence']*100:.0f}%, "
              f"{features['h2h_known_opponents']} known)")
