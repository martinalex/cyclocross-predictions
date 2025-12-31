# VeloPredict: X2O Trofee Azencross-Loenhout Predictions

**Race Date:** December 29, 2025
**Location:** Azencross-Loenhout, Belgium
**Series:** X2O Trofee
**Model Version:** v6.10
**Prediction Date:** December 28, 2025

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

**Field Size:** 72 riders
**High Confidence (>70%):** 7 riders

### Predicted Top-10

| Pred Rank | Rider                | Top-10 % | Podium % | H2H vs Field |
|---------:|---------------------|--------:|--------:|------------:|
|         1 | VAN DER POEL Mathieu |    99.2% |    98.2% |         100% |
|         2 | NIEUWENHUIS Joris    |    98.7% |     3.0% |          89% |
|         3 | VAN AERT Wout        |    98.6% |    16.9% |          96% |
|         4 | NYS Thibau           |    98.2% |    73.1% |          93% |
|         5 | SWEECK Laurens       |    97.7% |    12.4% |          88% |
|         6 | VANDEPUTTE Niels     |    93.0% |     0.2% |          88% |
|         7 | AERTS Toon           |    91.1% |     0.2% |          86% |
|         8 | VAN DER HAAR Lars    |    49.0% |     0.3% |          92% |
|         9 | JANSSEN Wout         |    19.0% |     0.0% |          64% |
|        10 | FERDINANDE Anton     |    13.7% |     0.0% |          66% |

### Predicted Podium

| Position | Rider                | Probability |
|--------:|---------------------|-----------:|
|        1 | VAN DER POEL Mathieu |       98.2% |
|        2 | NYS Thibau           |       73.1% |
|        3 | VAN AERT Wout        |       16.9% |

### Borderline Riders (11-15)

| Pred Rank | Rider           | Top-10 % | H2H vs Field |
|---------:|----------------|--------:|------------:|
|        11 | MEEUSSEN Witse  |    12.3% |          73% |
|        12 | SOETE Daan      |    11.6% |          73% |
|        13 | VANDEBOSCH Toon |    10.8% |          81% |
|        14 | KAMP Ryan       |     9.7% |          77% |
|        15 | MASON Cameron   |     6.9% |          84% |

---

## Women Elite

**Field Size:** 86 riders
**High Confidence (>70%):** 6 riders

### Predicted Top-10

| Pred Rank | Rider                      | Top-10 % | Podium % | H2H vs Field |
|---------:|---------------------------|--------:|--------:|------------:|
|         1 | BRAND Lucinda              |    99.2% |    98.0% |          99% |
|         2 | ALVARADO Ceylin Del Carmen |    99.0% |    35.8% |          96% |
|         3 | KASTELIJN Yara             |    96.9% |     1.5% |          84% |
|         4 | NORBERT RIBEROLLE Marion   |    96.5% |     6.2% |          94% |
|         5 | ZEMANOVÁ Kristýna          |    92.6% |     2.2% |          87% |
|         6 | BAKKER Manon               |    77.4% |     0.6% |          93% |
|         7 | BROUWERS Julie             |    17.8% |     0.1% |          90% |
|         8 | MOLENGRAAF Lauren          |    15.2% |     0.1% |          82% |
|         9 | TRUYEN Marthe              |    10.5% |     0.0% |          80% |
|        10 | BACKSTEDT Zoe              |    10.1% |     0.1% |          N/A |

### Predicted Podium

| Position | Rider                      | Probability |
|--------:|---------------------------|-----------:|
|        1 | BRAND Lucinda              |       98.0% |
|        2 | ALVARADO Ceylin Del Carmen |       35.8% |
|        3 | NORBERT RIBEROLLE Marion   |        6.2% |

### Borderline Riders (11-15)

| Pred Rank | Rider                | Top-10 % | H2H vs Field |
|---------:|---------------------|--------:|------------:|
|        11 | SCHREIBER Marie      |     9.4% |          91% |
|        12 | HARTOG Larissa       |     8.7% |          84% |
|        13 | VERDONSCHOT Laura    |     7.5% |          76% |
|        14 | VON BERSWORDT Sophie |     7.0% |          N/A |
|        15 | CHLADOŇOVÁ Viktória  |     6.8% |          77% |

---

## Probability Distribution Analysis

### Men Elite

| Metric           | Value | Interpretation        |
|-----------------|-----:|----------------------|
| Low (<30%)       | 88.9% | Non-contenders        |
| Mid (30-60%)     |  1.4% | Uncertain zone        |
| High (>60%)      |  9.7% | Likely contenders     |
| Mean Probability | 11.7% | Average across field  |
| Std Deviation    | 0.289 | Probability spread    |
| New Riders       |     9 | No prior race history |
| Field Size       |    72 | Total riders          |

**Pattern:** BIMODAL - Model is decisive

### Women Elite

| Metric           | Value | Interpretation        |
|-----------------|-----:|----------------------|
| Low (<30%)       | 93.0% | Non-contenders        |
| Mid (30-60%)     |  0.0% | Uncertain zone        |
| High (>60%)      |  7.0% | Likely contenders     |
| Mean Probability |  8.4% | Average across field  |
| Std Deviation    | 0.238 | Probability spread    |
| New Riders       |     3 | No prior race history |
| Field Size       |    86 | Total riders          |

**Pattern:** BIMODAL - Model is decisive

---

*Generated by VeloPredict v6.10 | 9,729 observations*