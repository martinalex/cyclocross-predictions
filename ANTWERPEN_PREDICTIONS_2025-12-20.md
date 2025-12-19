# VeloPredict: UCI World Cup Antwerpen Predictions

**Race Date:** December 20, 2025
**Location:** Antwerpen, Belgium
**Model Version:** v6.4
**Prediction Date:** December 17, 2025

---

## Methodology Update (v6.4)

### Changes from v6.3

1. **DNS filter removed** - Was incorrectly penalizing elite riders like VAN DER POEL who race infrequently
2. **NaN fallback fix** - When latest race record has missing form features (due to data entry inconsistencies), model now uses valid features from older records
3. **Fixed top-10 predictions** - Always predict exactly 10 riders (no confidence threshold filtering)

### Metrics We Track

| Metric | Description |
|--------|-------------|
| **Hits@10** | How many of our 10 predictions finished in actual top-10? (X/10) |
| **Hits@3** | How many of our 3 podium picks made the actual podium? (X/3) |
| **Spearman Rank Correlation** | Did we get the ordering right? (-1 to +1) |
| **MAE on Rank** | Average positions off for predicted riders |

*Note: With fixed N=10 predictions, precision@10 = recall@10 = Hits@10/10*

---

## Men Elite

**Field Size:** 97 riders
**High Confidence (>70%):** 12 riders

### Predicted Top-10

| Rank | Rider | Probability | H2H vs Field |
|------|-------|-------------|--------------|
| 1 | VAN DER POEL Mathieu | 99.0% | 100% |
| 2 | VAN AERT Wout | 99.1% | 97% |
| 3 | VAN DER HAAR Lars | 98.7% | 92% |
| 4 | VANTHOURENHOUT Michael | 98.4% | 83% |
| 5 | NYS Thibau | 98.0% | 94% |
| 6 | VANDEPUTTE Niels | 97.4% | 89% |
| 7 | NIEUWENHUIS Joris | 97.1% | 92% |
| 8 | VERSTRYNGE Emiel | 95.7% | 90% |
| 9 | VANDEBOSCH Toon | 86.4% | 81% |
| 10 | DEL GROSSO Tibor | 84.8% | 91% |

### Predicted Podium

| Position | Rider | Probability |
|----------|-------|-------------|
| 1 | VAN DER POEL Mathieu | 98.7% |
| 2 | VAN AERT Wout | 91.0% |
| 3 | NYS Thibau | 50.7% |

### Borderline Riders (11-15)

| Rank | Rider | Probability | H2H vs Field |
|------|-------|-------------|--------------|
| 11 | SWEECK Laurens | 83.6% | 90% |
| 12 | MICHELS Jente | 73.7% | 91% |
| 13 | RONHAAR Pim | 66.9% | 69% |
| 14 | KAMP Ryan | 46.3% | 82% |
| 15 | ORTS LLORET Felipe | 43.8% | 80% |

### Key Observations

- **Dutch-Belgian dominance**: Top 12 are all NED/BEL riders
- **VAN DER POEL** returns with perfect 100% H2H score vs field - has won all 7 CX races in dataset
- **Deep competition**: 12 riders above 70% probability creates tight race for positions 5-10
- **SWEECK at 83.6%** ranked 11th shows brutal competition - would be Top-5 lock in most fields

---

## Women Elite

**Field Size:** 87 riders
**High Confidence (>70%):** 12 riders

### Predicted Top-10

| Rank | Rider | Probability | H2H vs Field |
|------|-------|-------------|--------------|
| 1 | BRAND Lucinda | 99.1% | 99% |
| 2 | PIETERSE Puck | 99.0% | 98% |
| 3 | ALVARADO Ceylin del Carmen | 98.6% | 93% |
| 4 | VAN DER HEIJDEN Inge | 98.6% | 93% |
| 5 | CASASOLA Sara | 96.8% | 81% |
| 6 | FOUQUENET Amandine | 95.6% | 84% |
| 7 | VAN ALPHEN Aniek | 95.6% | 90% |
| 8 | BENTVELD Leonie | 94.9% | 90% |
| 9 | NORBERT RIBEROLLE Marion | 93.9% | 83% |
| 10 | CLAUZEL Helene | 88.3% | 85% |

### Predicted Podium

| Position | Rider | Probability |
|----------|-------|-------------|
| 1 | PIETERSE Puck | 97.7% |
| 2 | BRAND Lucinda | 97.4% |
| 3 | ALVARADO Ceylin del Carmen | 9.0% |

*Note: Only 2 riders above 30% podium threshold. Third spot is highly competitive.*

### Borderline Riders (11-15)

| Rank | Rider | Probability | H2H vs Field |
|------|-------|-------------|--------------|
| 11 | ZEMANOVA Kristyna | 87.6% | 83% |
| 12 | VAN ANROOIJ Shirin | 76.9% | 73% |
| 13 | BAKKER Manon | 66.0% | 83% |
| 14 | SCHREIBER Marie | 53.4% | 85% |
| 15 | CARRIER Rafaelle | 43.3% | 61% |

### Key Observations

- **BRAND vs PIETERSE**: Near-identical 99% Top-10 and 97%+ podium probabilities
- **Very strong field**: Riders ranked 11-15 all above 43% probability
- **NEFF Jolanda** (MTB champion) at 0.1% - correctly flagged as new rider with no CX history in our dataset. Finished P5 at Namur, could surprise again.

---

## Combined Summary

| Category | Field | Top-10 >70% | Predicted Podium |
|----------|-------|-------------|------------------|
| Men Elite | 97 | 12 | VDP, WVA, NYS |
| Women Elite | 87 | 12 | PIETERSE, BRAND, ALVARADO |

---

## Post-Race Validation Template

*To be completed after race:*

### Men Elite Results

| Metric | Value | Notes |
|--------|-------|-------|
| Hits@10 | /10 | |
| Hits@3 | /3 | |
| Spearman Correlation | | |
| MAE Rank | | |

### Women Elite Results

| Metric | Value | Notes |
|--------|-------|-------|
| Hits@10 | /10 | |
| Hits@3 | /3 | |
| Spearman Correlation | | |
| MAE Rank | | |

---

## Probability Distribution Analysis

| Metric           | Value | Interpretation        |
|-----------------|-----:|----------------------|
| Low (<30%)       | 82.6% | Non-contenders        |
| Mid (30-60%)     |  3.3% | Uncertain zone        |
| High (>60%)      | 14.1% | Likely contenders     |
| Mean Probability | 16.1% | Average across field  |
| Std Deviation    | 0.319 | Probability spread    |
| New Riders       |    11 | No prior race history |
| Field Size       |   184 | Total riders          |

**Pattern:** BIMODAL
- Model is decisive - clear separation between contenders and non-contenders

**What this means:**
- 83% of riders had <30% probability (clear non-contenders)
- 3% in the uncertain 30-60% range
- 14% were predicted >60% (likely Top-10)

---

*Generated by VeloPredict v6.4 | Model: 82.6% accuracy, 8,950 observations, 54 races*
