# UCI World Cup Sardinia Predictions (Dec 7, 2025)

**Model:** VeloPredict v6 (H2H + New Rider Penalty)
**Race:** Terralba - Sardinia, Italy
**Date:** December 7, 2025

---

## What's New in v6

- **New Rider Penalty** - 50% probability discount for riders with no race history in our dataset
- **Head-to-Head Feature** - #1 most important feature (22.5% importance)
- **Field-adjusted predictions** - Each rider's H2H win rate vs actual startlist opponents
- **Model accuracy:** 77.6% Top-10 accuracy, +29.8% over baseline
- **Total observations:** 8,357 race results

### Why the New Rider Penalty?
Data shows new riders (even with strong UCI rankings) have only 38% Top-10 rate, not 80%+. The model was over-predicting for unknown riders like Folcarelli and Peruta.

---

## MEN ELITE PREDICTIONS

### Predicted Podium
1. **NIEUWENHUIS Joris** (6.7% podium) - H2H: 93% vs field
2. **FOLCARELLI Antonio** (6.5% podium) - New rider, UCI rank 115 (discounted)
3. **SWEECK Laurens** (0.3% podium) - H2H: 86% vs field

### Predicted Top-10 (4 riders above 55% threshold)

| Rank | Rider | Top-10 Prob | H2H vs Field | Notes |
|------|-------|-------------|--------------|-------|
| 1 | NIEUWENHUIS Joris | 98.3% | 93% | 3rd Tabor, 6th Flamanville |
| 2 | VANDEPUTTE Niels | 84.4% | 87% | 10th Tabor, 4th Flamanville |
| 3 | SWEECK Laurens | 72.7% | 86% | 2nd Tabor, 5th Flamanville |
| 4 | VANTHOURENHOUT Michael | 55.9% | 78% | 17th Tabor, 7th Flamanville |

### Borderline Predictions (40-55%)

| Rider | Top-10 Prob | H2H vs Field | Notes |
|-------|-------------|--------------|-------|
| FOLCARELLI Antonio | 40.2% | N/A | New rider penalty applied (was 80%) |
| WYSEURE Joran | 35.3% | 78% | 22nd Tabor, 26th Flamanville |
| AERTS Toon | 30.5% | 85% | 8th Tabor, 12th Flamanville |

### Key Changes from v5
- **FOLCARELLI Antonio** dropped from 84.5% to **40.2%** (new rider penalty)
- New rider discount prevents over-prediction for unknown riders
- More realistic Top-10 predictions (4 vs 5 above threshold)

### Top H2H Performers (Men)
1. NIEUWENHUIS Joris - 93%
2. VANDEPUTTE Niels - 87%
3. SWEECK Laurens - 86%

---

## WOMEN ELITE PREDICTIONS

### Predicted Podium
1. **BRAND Lucinda** (95.1% podium) - H2H: 99% vs field - Dominant
2. **VAN ANROOIJ Shirin** (1.7% podium) - H2H: 56% vs field
3. **PERUTA Sara** (2.9% podium) - New rider, UCI rank 173 (discounted)

### Predicted Top-10 (4 riders above 55% threshold)

| Rank | Rider | Top-10 Prob | H2H vs Field | Notes |
|------|-------|-------------|--------------|-------|
| 1 | BRAND Lucinda | 98.8% | 99% | 1st Tabor, World Cup leader |
| 2 | CASASOLA Sara | 79.8% | 76% | 2nd Tabor, home race advantage |
| 3 | BENTVELD Leonie | 63.4% | 83% | 4th Tabor |
| 4 | VAN ANROOIJ Shirin | 53.9% | 56% | 16th Tabor, 6th Flamanville |

### Borderline Predictions (40-55%)

| Rider | Top-10 Prob | H2H vs Field | Notes |
|-------|-------------|--------------|-------|
| SCHREIBER Marie | 52.7% | 83% | DNF Tabor |
| VAN ALPHEN Aniek | 46.7% | 78% | 5th Tabor, 1st Flamanville |
| NORBERT RIBEROLLE Marion | 46.0% | 76% | Consistent performer |
| PERUTA Sara | 37.9% | N/A | New rider penalty applied (was 71%) |

### Key Changes from v5
- **PERUTA Sara** dropped from 70.8% to **37.9%** (new rider penalty)
- **CASASOLA Sara** remains correctly ranked (79.8%) - Italian with H2H data
- More realistic Top-10 predictions (4 vs 7 above threshold)

### Top H2H Performers (Women)
1. BRAND Lucinda - 99%
2. BENTVELD Leonie - 83%
3. SCHREIBER Marie - 83%

### DNS Risk Flagged
- **AZZETTI Nicole** (Only 1 race this season)

---

## New Rider Penalty Explained

### Why It Matters
- New riders have **8% overall Top-10 rate** vs 23% for known riders
- Even new riders with strong UCI rankings (top 200) only achieve **38% Top-10 rate**
- The model was predicting 80%+ for these riders based on inferred features

### How It Works
1. **is_new_rider feature** in model (learns from 1,400 new rider observations)
2. **50% probability discount** applied at prediction time
3. Results in predictions that match actual historical performance

### Affected Riders
| Rider | Category | Before | After | UCI Rank |
|-------|----------|--------|-------|----------|
| FOLCARELLI Antonio | Men | 84.5% | 40.2% | 115 |
| PERUTA Sara | Women | 70.8% | 37.9% | 173 |

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

### Feature Importance (v6 Model)
1. **h2h_field_score** - 22.5%
2. best_place_last5 - 13.7%
3. avg_place_last3 - 13.6%
4. top10_rate_career - 11.2%
5. last_place - 8.6%

---

## Race Context

### Startlist Summary
- **Men Elite:** 37 riders from 6 nations (BEL 11, ITA 13, NED 6, USA 4, FRA 2, GER 1)
- **Women Elite:** 32 riders from 8 nations (NED 9, ITA 12, BEL 6, others)

### Home Race Factor
Italian home race - expect strong crowd support for:
- **CASASOLA Sara** (Women) - 79.8%, H2H 76%, 2nd Tabor
- **PERUTA Sara** (Women) - 37.9% (new rider), UCI rank 173
- **FOLCARELLI Antonio** (Men) - 40.2% (new rider), UCI rank 115

---

## Quick Reference

| Category | Predicted Top-10 | High Confidence (>70%) | DNS Risks |
|----------|------------------|------------------------|-----------|
| Men Elite | 4 riders | 3 (Nieuwenhuis, Vandeputte, Sweeck) | 0 |
| Women Elite | 4 riders | 2 (Brand, Casasola) | 1 |

**Race Date:** Sunday, December 7, 2025
- Women Elite: 13:40
- Men Elite: 15:10

---

*Predictions generated with VeloPredict v6 - Updated December 3, 2025*
*H2H feature enabled (22.5%) + New rider penalty (50% discount)*
