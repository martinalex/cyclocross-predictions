# VeloPredict: UCI WC Dendermonde Predictions

**Race Date:** December 28, 2025
**Location:** Dendermonde, Belgium
**Series:** UCI WC
**Model Version:** v6.9
**Prediction Date:** December 27, 2025

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

**Field Size:** 65 riders
**High Confidence (>70%):** 9 riders

### Predicted Top-10

| Pred Rank | Rider                  | Top-10 % | Podium % | H2H vs Field |
|---------:|-----------------------|--------:|--------:|------------:|
|         1 | VAN AERT Wout          |    99.1% |    76.3% |          97% |
|         2 | DEL GROSSO Tibor       |    99.0% |    48.7% |          92% |
|         3 | NIEUWENHUIS Joris      |    98.9% |     1.1% |          92% |
|         4 | NYS Thibau             |    98.3% |    70.3% |          92% |
|         5 | VAN DER HAAR Lars      |    97.8% |     1.1% |          90% |
|         6 | VERSTRYNGE Emiel       |    97.3% |     0.4% |          87% |
|         7 | AERTS Toon             |    96.5% |     0.2% |          83% |
|         8 | VANTHOURENHOUT Michael |    95.1% |     1.6% |          80% |
|         9 | ORTS LLORET Felipe     |    85.2% |     0.0% |          74% |
|        10 | SWEECK Laurens         |    68.7% |     0.4% |          87% |

### Predicted Podium

| Position | Rider            | Probability |
|--------:|-----------------|-----------:|
|        1 | VAN AERT Wout    |       76.3% |
|        2 | NYS Thibau       |       70.3% |
|        3 | DEL GROSSO Tibor |       48.7% |

### Borderline Riders (11-15)

| Pred Rank | Rider         | Top-10 % | H2H vs Field |
|---------:|--------------|--------:|------------:|
|        11 | WYSEURE Joran |    62.1% |          64% |
|        12 | MICHELS Jente |    55.2% |          87% |
|        13 | HENDRIKX Mees |    44.3% |          72% |
|        14 | KAMP Ryan     |    44.2% |          76% |
|        15 | MASON Cameron |    40.7% |          82% |

---

## Women Elite

**Field Size:** 98 riders
**High Confidence (>70%):** 13 riders

### Predicted Top-10

| Pred Rank | Rider                      | Top-10 % | Podium % | H2H vs Field |
|---------:|---------------------------|--------:|--------:|------------:|
|         1 | BRAND Lucinda              |    99.0% |    98.8% |          99% |
|         2 | PIETERSE Puck              |    98.9% |    96.8% |          98% |
|         3 | ALVARADO Ceylin del Carmen |    98.0% |     1.6% |          92% |
|         4 | VAN ALPHEN Aniek           |    97.6% |    22.0% |          92% |
|         5 | VAN DER HEIJDEN Inge       |    97.4% |    10.7% |          94% |
|         6 | FOUQUENET Amandine         |    96.4% |    19.7% |          87% |
|         7 | NORBERT RIBEROLLE Marion   |    96.1% |     1.2% |          87% |
|         8 | CASASOLA Sara              |    95.7% |     1.1% |          81% |
|         9 | VAN ANROOIJ Shirin         |    94.0% |     0.0% |          77% |
|        10 | ZEMANOVÁ Kristýna          |    91.0% |     0.2% |          84% |

### Predicted Podium

| Position | Rider            | Probability |
|--------:|-----------------|-----------:|
|        1 | BRAND Lucinda    |       98.8% |
|        2 | PIETERSE Puck    |       96.8% |
|        3 | VAN ALPHEN Aniek |       22.0% |

### Borderline Riders (11-15)

| Pred Rank | Rider            | Top-10 % | H2H vs Field |
|---------:|-----------------|--------:|------------:|
|        11 | GERY Célia       |    79.8% |          76% |
|        12 | CARRIER Rafaelle |    79.7% |          70% |
|        13 | BROUWERS Julie   |    72.9% |          80% |
|        14 | SCHREIBER Marie  |    53.5% |          87% |
|        15 | BENTVELD Leonie  |    30.1% |          91% |

---

## Probability Distribution Analysis

### Men Elite

| Metric           | Value | Interpretation        |
|-----------------|-----:|----------------------|
| Low (<30%)       | 73.8% | Non-contenders        |
| Mid (30-60%)     |  9.2% | Uncertain zone        |
| High (>60%)      | 16.9% | Likely contenders     |
| Mean Probability | 20.0% | Average across field  |
| Std Deviation    | 0.348 | Probability spread    |
| New Riders       |     2 | No prior race history |
| Field Size       |    65 | Total riders          |

**Pattern:** BIMODAL - Model is decisive

### Women Elite

| Metric           | Value | Interpretation        |
|-----------------|-----:|----------------------|
| Low (<30%)       | 84.7% | Non-contenders        |
| Mid (30-60%)     |  2.0% | Uncertain zone        |
| High (>60%)      | 13.3% | Likely contenders     |
| Mean Probability | 15.2% | Average across field  |
| Std Deviation    | 0.312 | Probability spread    |
| New Riders       |     1 | No prior race history |
| Field Size       |    98 | Total riders          |

**Pattern:** BIMODAL - Model is decisive

---

*Generated by VeloPredict v6.9 | 9,589 observations*