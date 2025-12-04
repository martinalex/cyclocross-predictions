# UCI World Cup Sardinia Predictions (Dec 7, 2025)

**Model:** VeloPredict v5 (H2H Feature + UCI Rank inference)
**Race:** Terralba - Sardinia, Italy
**Date:** December 7, 2025

---

## What's New in v5

- **Head-to-Head Feature** - Now the #1 most important feature (21.4% importance)
- **Field-adjusted predictions** - Each rider's H2H win rate vs actual startlist opponents
- **Model accuracy:** 76.9% Top-10 accuracy, +29.4% over baseline
- **Total observations:** 8,188 race results

---

## MEN ELITE PREDICTIONS

### Predicted Podium
1. **FOLCARELLI Antonio** (12.5% podium) - New rider, UCI rank 115
2. **NIEUWENHUIS Joris** (1.6% podium) - H2H: 93% vs field
3. **AERTS Toon** (1.0% podium) - H2H: 85% vs field

### Predicted Top-10 (5 riders above 55% threshold)

| Rank | Rider | Top-10 Prob | H2H vs Field | Notes |
|------|-------|-------------|--------------|-------|
| 1 | NIEUWENHUIS Joris | 98.2% | 93% | 3rd Tabor, 6th Flamanville |
| 2 | FOLCARELLI Antonio | 84.5% | N/A | New rider, UCI rank 115 |
| 3 | VANDEPUTTE Niels | 80.4% | 87% | 10th Tabor, 4th Flamanville |
| 4 | SWEECK Laurens | 78.2% | 83% | 2nd Tabor, 5th Flamanville |
| 5 | VANTHOURENHOUT Michael | 65.5% | 80% | 17th Tabor, 7th Flamanville |

### Borderline Predictions (40-55%)

| Rider | Top-10 Prob | H2H vs Field | Recent Form |
|-------|-------------|--------------|-------------|
| WYSEURE Joran | 46.8% | 81% | 22nd Tabor, 26th Flamanville |
| AERTS Toon | 45.6% | 85% | 8th Tabor, 12th Flamanville |

### Key Changes from v4
- **SWEECK Laurens** jumped from 23.7% to **78.2%** due to strong H2H (83%)
- **CORSUS Yordi** dropped from 69.4% to 10.8% (H2H only 43%)
- H2H properly weights historical head-to-head performance against this specific field

### Top H2H Performers (Men)
1. NIEUWENHUIS Joris - 93%
2. VANDEPUTTE Niels - 87%
3. AERTS Toon - 85%

---

## WOMEN ELITE PREDICTIONS

### Predicted Podium
1. **BRAND Lucinda** (97.9% podium) - H2H: 99% vs field - Dominant
2. **VAN ANROOIJ Shirin** (6.1% podium) - H2H: 57% vs field
3. **PERUTA Sara** (5.9% podium) - New rider, UCI rank 173

### Predicted Top-10 (7 riders above 55% threshold)

| Rank | Rider | Top-10 Prob | H2H vs Field | Notes |
|------|-------|-------------|--------------|-------|
| 1 | BRAND Lucinda | 98.9% | 99% | 1st Tabor, World Cup leader |
| 2 | VAN ANROOIJ Shirin | 77.2% | 57% | 16th Tabor, 6th Flamanville |
| 3 | CASASOLA Sara | 73.5% | 74% | 2nd Tabor, home race advantage |
| 4 | PERUTA Sara | 70.8% | N/A | New rider, UCI rank 173 |
| 5 | VAN ALPHEN Aniek | 59.8% | 76% | 5th Tabor, 1st Flamanville |
| 6 | NORBERT RIBEROLLE Marion | 56.6% | 75% | Consistent performer |
| 7 | BENTVELD Leonie | 56.3% | 81% | 4th Tabor |

### Borderline Predictions (40-55%)

| Rider | Top-10 Prob | H2H vs Field | Recent Form |
|-------|-------------|--------------|-------------|
| SCHREIBER Marie | 49.2% | 83% | DNF Tabor |
| ALVARADO Ceylin | 38.4% | N/A | 3rd Flamanville (limited H2H data) |

### Key Changes from v4
- **CASASOLA Sara** now correctly ranked ahead of PERUTA (73.5% vs 70.8%)
- **VERVLOET Sterre** dropped from 75.7% to 11.7% (H2H only 33%)
- **ALVARADO Ceylin** dropped to 38.4% (no H2H data in matrix)

### Top H2H Performers (Women)
1. BRAND Lucinda - 99%
2. SCHREIBER Marie - 83%
3. BENTVELD Leonie - 81%

### DNS Risk Flagged
- **AZZETTI Nicole** (Only 1 race this season)

---

## Head-to-Head Analysis

### How H2H Works
For each rider, we calculate their historical win rate against the specific opponents in this startlist:
- **H2H 90%+** = Historically beats almost everyone in the field
- **H2H 70-90%** = Strong record against this field
- **H2H 50-70%** = Competitive, mixed results
- **H2H <50%** = Usually loses to this field
- **H2H N/A** = New rider or insufficient head-to-head data

### H2H Coverage
- **Men Elite:** 31/37 riders have H2H data (84%)
- **Women Elite:** 26/32 riders have H2H data (81%)

### Feature Importance (v5 Model)
1. **h2h_field_score** - 21.4%
2. avg_place_last3 - 13.0%
3. top10_rate_career - 12.9%
4. best_place_last5 - 12.7%
5. last_place - 9.4%

---

## Race Context

### Startlist Summary
- **Men Elite:** 37 riders from 6 nations (BEL 11, ITA 13, NED 6, USA 4, FRA 2, GER 1)
- **Women Elite:** 32 riders from 8 nations (NED 9, ITA 12, BEL 6, others)

### Home Race Factor
Italian home race - expect strong crowd support for:
- **CASASOLA Sara** (Women) - 2nd at Tabor, H2H 74%
- **PERUTA Sara** (Women) - Italian talent, UCI rank 173
- **FOLCARELLI Antonio** (Men) - UCI rank 115

---

## Quick Reference

| Category | Predicted Top-10 | High Confidence (>70%) | DNS Risks |
|----------|------------------|------------------------|-----------|
| Men Elite | 5 riders | 4 (Nieuwenhuis, Folcarelli, Vandeputte, Sweeck) | 0 |
| Women Elite | 7 riders | 4 (Brand, Van Anrooij, Casasola, Peruta) | 1 |

**Race Date:** Sunday, December 7, 2025
- Women Elite: 13:40
- Men Elite: 15:10

---

*Predictions generated with VeloPredict v5 - Updated December 3, 2025*
*H2H feature enabled - 21.4% model importance*
