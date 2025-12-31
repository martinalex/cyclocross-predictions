# VeloPredict: Superprestige Diegem Predictions

**Race Date:** December 30, 2025
**Location:** Diegem, Belgium
**Series:** Superprestige
**Model Version:** v6.12
**Prediction Date:** December 29, 2025

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

**Field Size:** 100 riders
**High Confidence (>70%):** 8 riders

### Predicted Top-10

| Pred Rank | Rider                  | Top-10 % | Podium % | H2H vs Field |
|---------:|-----------------------|--------:|--------:|------------:|
|         1 | NIEUWENHUIS Joris      |    99.2% |    61.7% |          94% |
|         2 | DEL GROSSO Tibor       |    99.1% |    77.1% |          97% |
|         3 | SWEECK Laurens         |    98.5% |     7.7% |          91% |
|         4 | NYS Thibau             |    98.4% |    76.8% |          95% |
|         5 | VANTHOURENHOUT Michael |    96.1% |     2.1% |          81% |
|         6 | VANDEPUTTE Niels       |    94.7% |     1.0% |          93% |
|         7 | ORTS LLORET Felipe     |    91.0% |     0.7% |          81% |
|         8 | MASON Cameron          |    72.4% |     0.2% |          86% |
|         9 | MICHELS Jente          |    64.1% |     0.2% |          91% |
|        10 | LOOCKX Lander          |    45.6% |     0.0% |          74% |

### Predicted Podium

| Position | Rider             | Probability |
|--------:|------------------|-----------:|
|        1 | DEL GROSSO Tibor  |       77.1% |
|        2 | NYS Thibau        |       76.8% |
|        3 | NIEUWENHUIS Joris |       61.7% |

### Borderline Riders (11-15)

| Pred Rank | Rider                | Top-10 % | H2H vs Field |
|---------:|---------------------|--------:|------------:|
|        11 | AGOSTINACCHIO Mattia |    32.1% |          67% |
|        12 | FERDINANDE Anton     |    17.7% |          73% |
|        13 | VANDEBOSCH Toon      |    15.0% |          84% |
|        14 | FONTANA Filippo      |    13.1% |          79% |
|        15 | HENDRIKX Mees        |    13.0% |          79% |

---

## Women Elite

**Field Size:** 100 riders
**High Confidence (>70%):** 7 riders

### Predicted Top-10

| Pred Rank | Rider                      | Top-10 % | Podium % | H2H vs Field |
|---------:|---------------------------|--------:|--------:|------------:|
|         1 | PIETERSE Puck              |    99.2% |    96.4% |          99% |
|         2 | ALVARADO Ceylin Del Carmen |    99.0% |     6.6% |          91% |
|         3 | NORBERT RIBEROLLE Marion   |    97.5% |     2.0% |          89% |
|         4 | VAN ALPHEN Aniek           |    97.4% |     2.8% |          92% |
|         5 | CASASOLA Sara              |    96.3% |     0.6% |          78% |
|         6 | VAS Kata Blanka            |    94.6% |    27.2% |          95% |
|         7 | VAN DER HEIJDEN Inge       |    77.3% |     3.9% |          94% |
|         8 | VAN ANROOIJ Shirin         |    58.3% |     0.2% |          81% |
|         9 | CARRIER Rafaelle           |    56.7% |     0.7% |          76% |
|        10 | SCHREIBER Marie            |    47.7% |     0.1% |          89% |

### Predicted Podium

| Position | Rider                      | Probability |
|--------:|---------------------------|-----------:|
|        1 | PIETERSE Puck              |       96.4% |
|        2 | VAS Kata Blanka            |       27.2% |
|        3 | ALVARADO Ceylin Del Carmen |        6.6% |

### Borderline Riders (11-15)

| Pred Rank | Rider           | Top-10 % | H2H vs Field |
|---------:|----------------|--------:|------------:|
|        11 | HARTOG Larissa  |    43.0% |          78% |
|        12 | CLAUZEL Hélène  |    25.0% |          86% |
|        13 | WORST Annemarie |    24.9% |          77% |
|        14 | MOORE Elly      |    23.4% |          N/A |
|        15 | HAVILAND Alexa  |    22.5% |          N/A |

---

## Probability Distribution Analysis

### Men Elite

| Metric           | Value | Interpretation        |
|-----------------|-----:|----------------------|
| Low (<30%)       | 89.0% | Non-contenders        |
| Mid (30-60%)     |  2.0% | Uncertain zone        |
| High (>60%)      |  9.0% | Likely contenders     |
| Mean Probability | 10.8% | Average across field  |
| Std Deviation    | 0.262 | Probability spread    |
| New Riders       |     7 | No prior race history |
| Field Size       |   100 | Total riders          |

**Pattern:** BIMODAL - Model is decisive

### Women Elite

| Metric           | Value | Interpretation        |
|-----------------|-----:|----------------------|
| Low (<30%)       | 89.0% | Non-contenders        |
| Mid (30-60%)     |  4.0% | Uncertain zone        |
| High (>60%)      |  7.0% | Likely contenders     |
| Mean Probability | 11.0% | Average across field  |
| Std Deviation    | 0.256 | Probability spread    |
| New Riders       |    11 | No prior race history |
| Field Size       |   100 | Total riders          |

**Pattern:** BIMODAL - Model is decisive

---

*Generated by VeloPredict v6.12 | 9,848 observations*