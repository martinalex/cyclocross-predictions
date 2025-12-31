# VeloPredict: UCI WC Gavere Predictions

**Race Date:** December 26, 2025
**Location:** Gavere, Belgium
**Series:** UCI WC
**Model Version:** v6.8
**Prediction Date:** December 26, 2025

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

**Field Size:** 70 riders
**High Confidence (>70%):** 9 riders

### Predicted Top-10

| Pred Rank | Rider                  | Top-10 % | Podium % | H2H vs Field |
|---------:|-----------------------|--------:|--------:|------------:|
|         1 | VAN DER POEL Mathieu   |    99.1% |    99.1% |         100% |
|         2 | DEL GROSSO Tibor       |    98.9% |    81.9% |          91% |
|         3 | NIEUWENHUIS Joris      |    98.8% |     4.5% |          89% |
|         4 | SWEECK Laurens         |    97.8% |     1.2% |          87% |
|         5 | VANTHOURENHOUT Michael |    96.7% |    41.0% |          81% |
|         6 | AERTS Toon             |    94.5% |     1.0% |          82% |
|         7 | VANDEPUTTE Niels       |    92.2% |     0.2% |          87% |
|         8 | ORTS LLORET Felipe     |    92.1% |     0.0% |          75% |
|         9 | VAN DER HAAR Lars      |    73.7% |     0.7% |          90% |
|        10 | NYS Thibau             |    65.9% |     2.0% |          93% |

### Predicted Podium

| Position | Rider                  | Probability |
|--------:|-----------------------|-----------:|
|        1 | VAN DER POEL Mathieu   |       99.1% |
|        2 | DEL GROSSO Tibor       |       81.9% |
|        3 | VANTHOURENHOUT Michael |       41.0% |

### Borderline Riders (11-15)

| Pred Rank | Rider           | Top-10 % | H2H vs Field |
|---------:|----------------|--------:|------------:|
|        11 | MICHELS Jente   |    61.1% |          86% |
|        12 | KUHN Kevin      |    58.1% |          77% |
|        13 | KAMP Ryan       |    56.5% |          76% |
|        14 | WYSEURE Joran   |    56.4% |          69% |
|        15 | VANDEBOSCH Toon |    43.0% |          75% |

---

## Women Elite

**Field Size:** 68 riders
**High Confidence (>70%):** 12 riders

### Predicted Top-10

| Pred Rank | Rider                    | Top-10 % | Podium % | H2H vs Field |
|---------:|-------------------------|--------:|--------:|------------:|
|         1 | BRAND Lucinda            |    99.0% |    99.3% |          99% |
|         2 | PIETERSE Puck            |    98.9% |    53.6% |          98% |
|         3 | ALVARADO Ceylin          |    98.8% |    28.1% |          91% |
|         4 | VAN DER HEIJDEN Inge     |    98.6% |    24.9% |          94% |
|         5 | VAN ALPHEN Aniek         |    97.7% |    14.5% |          91% |
|         6 | FOUQUENET Amandine       |    97.3% |    23.9% |          87% |
|         7 | NORBERT RIBEROLLE Marion |    96.7% |     2.4% |          86% |
|         8 | BENTVELD Leonie          |    96.1% |     0.2% |          91% |
|         9 | NEFF Jolanda             |    95.0% |     0.1% |          78% |
|        10 | VAN ANROOIJ Shirin       |    94.5% |     0.6% |          75% |

### Predicted Podium

| Position | Rider           | Probability |
|--------:|----------------|-----------:|
|        1 | BRAND Lucinda   |       99.3% |
|        2 | PIETERSE Puck   |       53.6% |
|        3 | ALVARADO Ceylin |       28.1% |

### Borderline Riders (11-15)

| Pred Rank | Rider             | Top-10 % | H2H vs Field |
|---------:|------------------|--------:|------------:|
|        11 | BAKKER Manon      |    85.2% |          83% |
|        12 | BETSEMA Denise    |    82.1% |          82% |
|        13 | VERDONSCHOT Laura |    66.7% |          60% |
|        14 | BROUWERS Julie    |    63.0% |          78% |
|        15 | VAS Blanka        |    34.7% |          N/A |

---

## Probability Distribution Analysis

### Men Elite

| Metric           | Value | Interpretation        |
|-----------------|-----:|----------------------|
| Low (<30%)       | 75.7% | Non-contenders        |
| Mid (30-60%)     |  8.6% | Uncertain zone        |
| High (>60%)      | 15.7% | Likely contenders     |
| Mean Probability | 19.1% | Average across field  |
| Std Deviation    | 0.335 | Probability spread    |
| New Riders       |     0 | No prior race history |
| Field Size       |    70 | Total riders          |

**Pattern:** BIMODAL - Model is decisive

### Women Elite

| Metric           | Value | Interpretation        |
|-----------------|-----:|----------------------|
| Low (<30%)       | 77.9% | Non-contenders        |
| Mid (30-60%)     |  1.5% | Uncertain zone        |
| High (>60%)      | 20.6% | Likely contenders     |
| Mean Probability | 21.2% | Average across field  |
| Std Deviation    | 0.366 | Probability spread    |
| New Riders       |     0 | No prior race history |
| Field Size       |    68 | Total riders          |

**Pattern:** BIMODAL - Model is decisive

---

*Generated by VeloPredict v6.8 | 9,465 observations*