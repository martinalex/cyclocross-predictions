# VeloPredict: X2O Trofee Hofstade Predictions

**Race Date:** December 22, 2025
**Location:** Hofstade, Belgium
**Series:** X2O Trofee
**Model Version:** v6.6
**Prediction Date:** December 22, 2025

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

**Field Size:** 47 riders
**High Confidence (>70%):** 7 riders

### Predicted Top-10

| Pred Rank | Rider                  | Top-10 % | Podium % | H2H vs Field |
|----------:|------------------------|---------:|---------:|-------------:|
|         1 | VAN DER POEL Mathieu   |    99.1% |    98.9% |         100% |
|         2 | VAN AERT Wout          |    98.5% |     7.4% |          94% |
|         3 | SWEECK Laurens         |    97.5% |     4.1% |          85% |
|         4 | AERTS Toon             |    95.2% |     0.1% |          80% |
|         5 | VANTHOURENHOUT Michael |    92.3% |     0.4% |          77% |
|         6 | VANDEPUTTE Niels       |    88.4% |     0.2% |          82% |
|         7 | VAN DER HAAR Lars      |    76.3% |     0.3% |          88% |
|         8 | MASON Cameron          |    69.9% |     0.1% |          74% |
|         9 | NIEUWENHUIS Joris      |    66.3% |     0.5% |          85% |
|        10 | NYS Thibau             |    44.4% |     1.1% |          93% |

### Predicted Podium

| Position | Rider                | Probability |
|---------:|----------------------|------------:|
|        1 | VAN DER POEL Mathieu |       98.9% |
|        2 | VAN AERT Wout        |        7.4% |
|        3 | SWEECK Laurens       |        4.1% |

### Borderline Riders (11-15)

| Pred Rank | Rider               | Top-10 % | H2H vs Field |
|----------:|---------------------|---------:|-------------:|
|        11 | VANDEBOSCH Toon     |    15.2% |          72% |
|        12 | SOETE Daan          |     7.9% |          65% |
|        13 | HORNY Clement       |     3.2% |          60% |
|        14 | VAN DE PUTTE Victor |     2.9% |          62% |
|        15 | KAMP Ryan           |     2.8% |          68% |

---

## Women Elite

**Field Size:** 71 riders
**High Confidence (>70%):** 3 riders

### Predicted Top-10

| Pred Rank | Rider                      | Top-10 % | Podium % | H2H vs Field |
|----------:|----------------------------|---------:|---------:|-------------:|
|         1 | BRAND Lucinda              |    99.0% |    99.1% |          99% |
|         2 | ALVARADO Ceylin del Carmen |    98.8% |    77.0% |          98% |
|         3 | VAN ANROOIJ Shirin         |    95.0% |     0.1% |          N/A |
|         4 | LANGENBARG Puck            |    19.4% |     0.0% |          76% |
|         5 | BROUWERS Julie             |    10.7% |     0.3% |          92% |
|         6 | BAKKER Manon               |     9.6% |     0.2% |          95% |
|         7 | VERDONSCHOT Laura          |     9.0% |     0.0% |          76% |
|         8 | HLADÍKOVÁ Kateřina         |     9.0% |     0.0% |          N/A |
|         9 | CLAUZEL Perrine            |     7.2% |     0.0% |          75% |
|        10 | SONNEMANS Sara             |     6.3% |     0.0% |          65% |

### Predicted Podium

| Position | Rider                      | Probability |
|--------:|---------------------------|-----------:|
|        1 | BRAND Lucinda              |       99.1% |
|        2 | ALVARADO Ceylin del Carmen |       77.0% |
|        3 | BROUWERS Julie             |        0.3% |

### Borderline Riders (11-15)

| Pred Rank | Rider                 | Top-10 % | H2H vs Field |
|---------:|----------------------|--------:|------------:|
|        11 | DE SCHOESITTER Shanyl |     5.7% |          69% |
|        12 | GARIBOLDI Rebecca     |     4.1% |          85% |
|        13 | BORELLO Carlotta      |     3.1% |          75% |
|        14 | HURTELOUP Adèle       |     2.8% |          61% |
|        15 | LAURIJSSEN Sanne      |     2.5% |          N/A |

---

## Probability Distribution Analysis

### Men Elite

| Metric           | Value | Interpretation        |
|-----------------|-----:|----------------------|
| Low (<30%)       | 78.7% | Non-contenders        |
| Mid (30-60%)     |  2.1% | Uncertain zone        |
| High (>60%)      | 19.1% | Likely contenders     |
| Mean Probability | 18.5% | Average across field  |
| Std Deviation    | 0.348 | Probability spread    |
| New Riders       |     4 | No prior race history |
| Field Size       |    47 | Total riders          |

**Pattern:** BIMODAL - Model is decisive

### Women Elite

| Metric           | Value | Interpretation        |
|-----------------|-----:|----------------------|
| Low (<30%)       | 95.8% | Non-contenders        |
| Mid (30-60%)     |  0.0% | Uncertain zone        |
| High (>60%)      |  4.2% | Likely contenders     |
| Mean Probability |  5.8% | Average across field  |
| Std Deviation    | 0.197 | Probability spread    |
| New Riders       |     7 | No prior race history |
| Field Size       |    71 | Total riders          |

**Pattern:** BIMODAL - Model is decisive

---

*Generated by VeloPredict v6.6 | 9,235 observations*