"""
Tests for name normalization and standardization.

These are critical functions that affect rider matching across the entire system.
"""
import pytest
from src.features.names import normalize_name, standardize_name, NAME_CORRECTIONS


class TestNormalizeName:
    """Tests for normalize_name function."""

    def test_basic_lowercase(self):
        assert normalize_name("John Smith") == "john smith"

    def test_handles_none(self):
        assert normalize_name(None) is None

    def test_handles_nan(self):
        import pandas as pd
        assert normalize_name(pd.NA) is None
        assert normalize_name(float('nan')) is None

    def test_strips_whitespace(self):
        assert normalize_name("  John Smith  ") == "john smith"

    def test_removes_common_diacritics(self):
        # French accents
        assert normalize_name("René Léger") == "rene leger"
        # German umlauts
        assert normalize_name("Müller Schröder") == "muller schroder"
        # Czech/Polish diacritics
        assert normalize_name("Řehák Žilková") == "rehak zilkova"
        assert normalize_name("Štefan Čech") == "stefan cech"

    def test_handles_mixed_diacritics(self):
        assert normalize_name("Émile Östberg") == "emile ostberg"

    def test_preserves_spaces(self):
        assert normalize_name("Van der Berg") == "van der berg"


class TestStandardizeName:
    """Tests for standardize_name function."""

    def test_lastname_firstname_format(self):
        """LASTNAME Firstname -> firstname lastname"""
        assert standardize_name("NYS Thibau") == "thibau nys"
        assert standardize_name("SWEECK Laurens") == "laurens sweeck"

    def test_multi_word_lastname(self):
        """VAN ALPHEN Aniek -> aniek van alphen"""
        assert standardize_name("VAN ALPHEN Aniek") == "aniek van alphen"
        assert standardize_name("VAN DER POEL Mathieu") == "mathieu van der poel"

    def test_already_standardized(self):
        """firstname lastname stays as firstname lastname"""
        assert standardize_name("thibau nys") == "thibau nys"
        assert standardize_name("Thibau Nys") == "thibau nys"

    def test_all_uppercase(self):
        """LASTNAME FIRSTNAME -> firstname lastname (assumes first word is last)"""
        assert standardize_name("NYS THIBAU") == "thibau nys"

    def test_handles_none(self):
        assert standardize_name(None) is None

    def test_single_name(self):
        """Single name should just be normalized"""
        assert standardize_name("Madonna") == "madonna"

    def test_known_corrections_applied(self):
        """Known typos should be corrected"""
        # These are in NAME_CORRECTIONS
        assert standardize_name("VANPUTTE Niels") == "niels vandeputte"
        assert standardize_name("HENDRIXX Mees") == "mees hendrikx"
        assert standardize_name("VANHOURENHOUT Michael") == "michael vanthourenhout"

    def test_removes_diacritics(self):
        """Diacritics should be removed during standardization"""
        assert standardize_name("MÜLLER François") == "francois muller"


class TestNameCorrections:
    """Tests that NAME_CORRECTIONS dictionary is valid."""

    def test_corrections_are_lowercase(self):
        """All corrections should be lowercase"""
        for key, value in NAME_CORRECTIONS.items():
            assert key == key.lower(), f"Key '{key}' should be lowercase"
            assert value == value.lower(), f"Value '{value}' should be lowercase"

    def test_corrections_are_standardized_format(self):
        """All corrections should be in 'firstname lastname' format"""
        for key, value in NAME_CORRECTIONS.items():
            parts = value.split()
            assert len(parts) >= 2, f"Value '{value}' should have at least 2 parts"


class TestEdgeCases:
    """Edge cases and regression tests."""

    def test_empty_string(self):
        assert normalize_name("") == ""
        assert standardize_name("") == ""

    def test_numeric_input(self):
        """Should handle numeric input gracefully"""
        assert normalize_name(123) == "123"
        assert standardize_name(123) == "123"

    def test_special_characters_preserved(self):
        """Hyphens and apostrophes should be preserved"""
        assert normalize_name("O'Brien") == "o'brien"
        assert normalize_name("Mary-Jane") == "mary-jane"

    def test_ceylin_alvarado_variations(self):
        """Test various formats of Ceylin del Carmen Alvarado"""
        # These should all normalize to a matchable form
        name1 = standardize_name("ALVARADO Ceylin")
        name2 = standardize_name("ceylin alvarado")
        # Note: middle name variations may differ, but first+last should match
        assert "ceylin" in name1 and "alvarado" in name1
        assert name2 == "ceylin alvarado"

    def test_iserbyt(self):
        """Test Eli Iserbyt - common name in data"""
        assert standardize_name("ISERBYT Eli") == "eli iserbyt"
        assert standardize_name("Eli Iserbyt") == "eli iserbyt"

    def test_van_der_poel(self):
        """Test Mathieu van der Poel - multi-word last name"""
        result = standardize_name("VAN DER POEL Mathieu")
        assert result == "mathieu van der poel"
