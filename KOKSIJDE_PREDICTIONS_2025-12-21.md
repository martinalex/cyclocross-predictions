# VeloPredict: UCI World Cup Koksijde Predictions

**Race Date:** December 21, 2025
**Location:** Koksijde, Belgium
**Model Version:** v6.5
**Prediction Date:** December 21, 2025

---

## Methodology (v6.4+)

### Fixed Top-10 Predictions

1. **Always predict exactly 10 riders** - No confidence threshold filtering
2. **Always predict exactly 3 podium picks** - Top 3 by podium probability

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

**Field Size:** 58 riders
**High Confidence (>70%):** 8 riders

### Predicted Top-10

| Pred Rank | Rider                  | Probability | H2H vs Field |
|-----------|------------------------|-------------|--------------|
| 1         | VAN DER POEL Mathieu   | 99.1%       | 100%         |
| 2         | VAN DER HAAR Lars      | 98.8%       | 93%          |
| 3         | DEL GROSSO Tibor       | 97.4%       | 89%          |
| 4         | SWEECK Laurens         | 96.9%       | 89%          |
| 5         | VERSTRYNGE Emiel       | 95.4%       | 91%          |
| 6         | MASON Cameron          | 92.9%       | 87%          |
| 7         | VANDEPUTTE Niels       | 92.7%       | 88%          |
| 8         | VANTHOURENHOUT Michael | 92.4%       | 83%          |
| 9         | AERTS Toon             | 56.9%       | 86%          |
| 10        | KAMP Ryan              | 15.0%       | 79%          |

### Predicted Podium

| Position | Rider                | Probability |
|----------|----------------------|-------------|
| 1        | VAN DER POEL Mathieu | 99.3%       |
| 2        | SWEECK Laurens       | 36.1%       |
| 3        | VAN DER HAAR Lars    | 18.1%       |

### Borderline Riders (11-15)

| Pred Rank | Rider              | Probability | H2H vs Field |
|-----------|--------------------|-------------|--------------|
| 11        | HENDRIKX Mees      | 14.6%       | 76%          |
| 12        | ORTS LLORET Felipe | 6.3%        | 77%          |
| 13        | RONHAAR Pim        | 5.7%        | 65%          |
| 14        | WYSEURE Joran      | 5.6%        | 63%          |
| 15        | BOROŠ Michael      | 3.8%        | 69%          |

### Key Observations

- **VAN AERT & NYS absent**: Neither on startlist - smaller elite field
- **VAN DER POEL clear favorite**: 99.3% podium probability, 100% H2H vs field
- **SWEECK rising**: After P2 at Antwerpen, now predicted podium
- **MASON Cameron** (GBR): Highest non-Belgian/Dutch at 92.9%
- **Gap at position 9**: Drop from 92.4% to 56.9% shows clear top-8

---

## Women Elite

**Field Size:** 87 riders
**High Confidence (>70%):** 10 riders

### Predicted Top-10

| Pred Rank | Rider                      | Probability | H2H vs Field |
|-----------|----------------------------|-------------|--------------|
| 1         | PIETERSE Puck              | 99.2%       | 98%          |
| 2         | BRAND Lucinda              | 99.2%       | 99%          |
| 3         | ALVARADO Ceylin del Carmen | 98.6%       | 92%          |
| 4         | VAN DER HEIJDEN Inge       | 98.1%       | 93%          |
| 5         | VAN ALPHEN Aniek           | 96.8%       | 89%          |
| 6         | CASASOLA Sara              | 95.4%       | 80%          |
| 7         | VAN ANROOIJ Shirin         | 92.1%       | 72%          |
| 8         | ZEMANOVÁ Kristýna          | 91.1%       | 83%          |
| 9         | BENTVELD Leonie            | 78.3%       | 89%          |
| 10        | FOUQUENET Amandine         | 53.4%       | 83%          |

### Predicted Podium

| Position | Rider                      | Probability |
|----------|----------------------------|-------------|
| 1        | BRAND Lucinda              | 99.4%       |
| 2        | PIETERSE Puck              | 95.7%       |
| 3        | ALVARADO Ceylin del Carmen | 22.9%       |

### Borderline Riders (11-15)

| Pred Rank | Rider                    | Probability | H2H vs Field |
|-----------|--------------------------|-------------|--------------|
| 11        | NORBERT RIBEROLLE Marion | 46.3%       | 82%          |
| 12        | BAKKER Manon             | 44.5%       | 81%          |
| 13        | SCHREIBER Marie          | 19.3%       | 86%          |
| 14        | CLAUZEL Hélène           | 18.5%       | 84%          |
| 15        | CARRIER Rafaelle         | 17.8%       | 60%          |

### Key Observations

- **BRAND vs PIETERSE**: Near-identical 99% - race could go either way
- **NEFF Jolanda** at 14.0% (#20): Could surprise again (P5 at Namur)
- **Strong Dutch contingent**: 6 of top-10 are NED
- **Clean separation**: Top-9 all above 78%, then drops to 53%

---

## Combined Summary

| Category    | Field | Top-10 >70% | Predicted Podium         |
|-------------|-------|-------------|--------------------------|
| Men Elite   | 58    | 8 riders    | VDP, SWEECK, VDH         |
| Women Elite | 87    | 10 riders   | BRAND, PIETERSE, ALVARADO|

---

## Probability Distribution Analysis

### Men Elite

| Metric           | Value  | Interpretation        |
|------------------|-------:|----------------------|
| Low (<30%)       | 84.5%  | Non-contenders        |
| Mid (30-60%)     |  1.7%  | Uncertain zone        |
| High (>60%)      | 13.8%  | Likely contenders     |
| Mean Probability | 15.5%  | Average across field  |
| Std Deviation    | 0.333  | Probability spread    |
| New Riders       |    0   | No prior race history |
| Field Size       |   58   | Total riders          |

**Pattern:** BIMODAL - Model is decisive

### Women Elite

| Metric           | Value  | Interpretation        |
|------------------|-------:|----------------------|
| Low (<30%)       | 85.1%  | Non-contenders        |
| Mid (30-60%)     |  3.4%  | Uncertain zone        |
| High (>60%)      | 11.5%  | Likely contenders     |
| Mean Probability | 14.6%  | Average across field  |
| Std Deviation    | 0.304  | Probability spread    |
| New Riders       |    2   | No prior race history |
| Field Size       |   87   | Total riders          |

**Pattern:** BIMODAL - Model is decisive

---

## Post-Race Validation Results

### Men Elite Results

| Metric             | Value   | Target | Result |
|--------------------|---------|--------|--------|
| Hits@10            | 7/10    | 7+     | PASS   |
| Hits@3             | 2/3     | 2+     | PASS   |
| Spearman ρ         | 0.68    | >0.5   | PASS   |
| MAE Rank           | 2.0     | <3     | PASS   |

**Prediction vs Actual:**

| Pred Rank | Rider                  | Actual | Hit? |
|-----------|------------------------|--------|------|
| 1         | VAN DER POEL Mathieu   | P1     | YES  |
| 2         | VAN DER HAAR Lars      | P11    | NO   |
| 3         | DEL GROSSO Tibor       | P4     | YES  |
| 4         | SWEECK Laurens         | P2     | YES  |
| 5         | VERSTRYNGE Emiel       | P13    | NO   |
| 6         | MASON Cameron          | P8     | YES  |
| 7         | VANDEPUTTE Niels       | P3     | YES  |
| 8         | VANTHOURENHOUT Michael | P9     | YES  |
| 9         | AERTS Toon             | P5     | YES  |
| 10        | KAMP Ryan              | P16    | NO   |

**Key observations:**
- VAN DER HAAR underperformed (P11 vs predicted P2)
- VANDEPUTTE podium surprise (P3 vs predicted P7)
- AERTS strong finish (P5 vs predicted P9)
- Borderline HENDRIKX made actual top-10 (P10)

### Women Elite Results

| Metric             | Value   | Target | Result |
|--------------------|---------|--------|--------|
| Hits@10            | 9/10    | 7+     | PASS   |
| Hits@3             | 2/3     | 2+     | PASS   |
| Spearman ρ         | 0.67    | >0.5   | PASS   |
| MAE Rank           | 1.7     | <3     | PASS   |

**Prediction vs Actual:**

| Pred Rank | Rider                      | Actual | Hit? |
|-----------|----------------------------|--------|------|
| 1         | PIETERSE Puck              | P5     | YES  |
| 2         | BRAND Lucinda              | P1     | YES  |
| 3         | ALVARADO Ceylin del Carmen | P3     | YES  |
| 4         | VAN DER HEIJDEN Inge       | P6     | YES  |
| 5         | VAN ALPHEN Aniek           | P4     | YES  |
| 6         | CASASOLA Sara              | DNF    | NO   |
| 7         | VAN ANROOIJ Shirin         | P2     | YES  |
| 8         | ZEMANOVÁ Kristýna          | P9     | YES  |
| 9         | BENTVELD Leonie            | P8     | YES  |
| 10        | FOUQUENET Amandine         | P10    | YES  |

**Key observations:**
- VAN ANROOIJ surprise P2 (predicted P7) - major outperformance
- PIETERSE off day (P5 vs predicted P1)
- CASASOLA DNF only miss
- BETSEMA P7 (not in our top-15) - surprise

### Combined Summary

| Category     | Hits@10 | Hits@3 | Spearman ρ | MAE Rank | Targets Met |
|--------------|---------|--------|------------|----------|-------------|
| Men Elite    | 7/10    | 2/3    | 0.68       | 2.0      | 4/4         |
| Women Elite  | 9/10    | 2/3    | 0.67       | 1.7      | 4/4         |
| **Combined** | **16/20** | **4/6** | **0.67** | **1.8**  | **8/8**     |

**BEST RACE PERFORMANCE** - All targets met for both categories!

---

*Generated by VeloPredict v6.5 | 9,114 observations, 57,289 H2H pairs*
