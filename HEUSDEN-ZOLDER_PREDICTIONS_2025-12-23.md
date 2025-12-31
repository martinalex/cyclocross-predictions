# VeloPredict: SuperPrestige Heusden-Zolder Predictions

**Race Date:** December 23, 2025
**Location:** Heusden-Zolder, Belgium
**Series:** SuperPrestige
**Model Version:** v6.7
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

**Field Size:** 100 riders
**High Confidence (>70%):** 8 riders

### Predicted Top-10

| Pred Rank | Rider                  | Top-10 % | Podium % | H2H vs Field |
|---------:|-----------------------|--------:|--------:|------------:|
|         1 | VAN AERT Wout          |    99.1% |    98.1% |          99% |
|         2 | DEL GROSSO Tibor       |    98.8% |    70.3% |          94% |
|         3 | NIEUWENHUIS Joris      |    98.6% |     1.7% |          92% |
|         4 | NYS Thibau             |    97.8% |    60.2% |          95% |
|         5 | SWEECK Laurens         |    97.1% |     0.3% |          91% |
|         6 | VANTHOURENHOUT Michael |    94.4% |     0.3% |          83% |
|         7 | VANDEPUTTE Niels       |    93.3% |     0.4% |          91% |
|         8 | MASON Cameron          |    86.6% |     0.1% |          86% |
|         9 | MICHELS Jente          |    63.1% |     0.0% |          91% |
|        10 | WYSEURE Joran          |    52.0% |     0.0% |          78% |

### Predicted Podium

| Position | Rider            | Probability |
|--------:|-----------------|-----------:|
|        1 | VAN AERT Wout    |       98.1% |
|        2 | DEL GROSSO Tibor |       70.3% |
|        3 | NYS Thibau       |       60.2% |

### Borderline Riders (11-15)

| Pred Rank | Rider                | Top-10 % | H2H vs Field |
|---------:|---------------------|--------:|------------:|
|        11 | AGOSTINACCHIO Mattia |    44.5% |          N/A |
|        12 | KUHN Kevin           |    11.4% |          83% |
|        13 | HENDRIKX Mees        |    11.4% |          75% |
|        14 | DE CLERCQ Naud       |    10.8% |          N/A |
|        15 | JANSSEN Wout         |     9.5% |          65% |

---

## Women Elite

**Field Size:** 76 riders
**High Confidence (>70%):** 7 riders

### Predicted Top-10

| Pred Rank | Rider                | Top-10 % | Podium % | H2H vs Field |
|---------:|---------------------|--------:|--------:|------------:|
|         1 | VAN DER HEIJDEN Inge |    98.6% |    14.5% |          95% |
|         2 | VAN ALPHEN Aniek     |    96.7% |     1.2% |          92% |
|         3 | CASASOLA Sara        |    95.3% |     0.6% |          80% |
|         4 | VAS Kata Blanka      |    94.9% |    58.1% |          96% |
|         5 | FOUQUENET Amandine   |    90.4% |     0.1% |          85% |
|         6 | BROUWERS Julie       |    81.0% |     0.1% |          84% |
|         7 | TRUYEN Marthe        |    73.0% |     0.0% |          73% |
|         8 | CABACA Mae           |    55.3% |     0.0% |          58% |
|         9 | CLAUZEL Hélène       |    26.4% |     0.1% |          88% |
|        10 | CARRIER Rafaelle     |    25.6% |     0.8% |          76% |

### Predicted Podium

| Position | Rider                | Probability |
|--------:|---------------------|-----------:|
|        1 | VAS Kata Blanka      |       58.1% |
|        2 | VAN DER HEIJDEN Inge |       14.5% |
|        3 | VAN ALPHEN Aniek     |        1.2% |

### Borderline Riders (11-15)

| Pred Rank | Rider                    | Top-10 % | H2H vs Field |
|---------:|-------------------------|--------:|------------:|
|        11 | NORBERT RIBEROLLE Marion |    25.6% |          89% |
|        12 | NEFF Jolanda             |    13.7% |          N/A |
|        13 | GARIBOLDI Rebecca        |    10.0% |          81% |
|        14 | VAN SINAEY Xaydee        |     8.7% |          65% |
|        15 | SCHREIBER Marie          |     7.5% |          90% |

---

## Probability Distribution Analysis

### Men Elite

| Metric           | Value | Interpretation        |
|-----------------|-----:|----------------------|
| Low (<30%)       | 89.0% | Non-contenders        |
| Mid (30-60%)     |  2.0% | Uncertain zone        |
| High (>60%)      |  9.0% | Likely contenders     |
| Mean Probability | 10.4% | Average across field  |
| Std Deviation    | 0.270 | Probability spread    |
| New Riders       |     6 | No prior race history |
| Field Size       |   100 | Total riders          |

**Pattern:** BIMODAL - Model is decisive

### Women Elite

| Metric           | Value | Interpretation        |
|-----------------|-----:|----------------------|
| Low (<30%)       | 89.5% | Non-contenders        |
| Mid (30-60%)     |  1.3% | Uncertain zone        |
| High (>60%)      |  9.2% | Likely contenders     |
| Mean Probability | 11.5% | Average across field  |
| Std Deviation    | 0.266 | Probability spread    |
| New Riders       |     1 | No prior race history |
| Field Size       |    76 | Total riders          |

**Pattern:** BIMODAL - Model is decisive

---

*Generated by VeloPredict v6.7 | 9,333 observations*