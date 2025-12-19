# Kortrijk Validation Results

**Exact Cross** | 2025-12-13

*VeloPredict v6.1 | Post-race validation*

---

## Summary

| Category     | Recall  | Precision | High Conf Accuracy | Podium Accuracy |
|--------------|--------:|----------:|-------------------:|----------------:|
| Men Elite    |   30.0% |     75.0% |              75.0% |             N/A |
| Women Elite  |   40.0% |    100.0% |             100.0% |           100.0% |
| **Combined** |   35.0% |     87.5% |              83.3% |           100.0% |

**Key takeaway:** High precision (87.5%) but lower recall (35%) - this was a B-tier race with a weaker field, and several riders we flagged as DNS risks (Kamp, Wyseure) actually raced and performed well.

---

## Men Elite

| Metric                    | Value                 |
|---------------------------|----------------------:|
| **Recall**                | 30.0% (3/10)          |
| **Precision**             | 75.0% (3/4)           |
| High Confidence Accuracy  | 75.0% (3/4)           |

### Correct Predictions

| Pred | Actual | Rider                | Prob  | Notes                    |
|-----:|-------:|----------------------|------:|--------------------------|
|    1 |      1 | **Niels Vandeputte** | 98.3% | Winner - nailed it       |
|    3 |      2 | **Cameron Mason**    | 92.9% | Strong form paid off     |
|    4 |      6 | Viktor Vandenberghe  | 91.3% | In Top-10 as predicted   |

### Missed Top-10 (False Negatives)

| Actual | Rider             | Prob  | Why Missed                              |
|-------:|-------------------|------:|-----------------------------------------|
|      3 | Ryan Kamp         | 11.8% | Flagged as DNS risk - raced and podiumed |
|      4 | Anton Ferdinande  | 11.9% | Limited H2H data, underestimated        |
|      5 | Yorben Lauryssen  |  4.3% | Low career rate, but rising star        |
|      7 | Joran Wyseure     | 12.8% | Flagged as DNS risk - raced P7          |
|      8 | Thomas Mein       |  3.4% | Strong in weaker field                  |
|      9 | Kenay De Moyer    | 23.0% | Just below threshold                    |
|     10 | Arne Baers        | 28.5% | Borderline - nearly predicted           |

### False Positives

| Pred | Actual | Rider                  | Prob  | Why Wrong                        |
|-----:|-------:|------------------------|------:|----------------------------------|
|    5 |     15 | Michael Vanthourenhout | 87.7% | Off day, came from Sardinia wins |

### Analysis

**What went right:**
- Top 2 correct (Vandeputte, Mason)
- All high-confidence predictions were Top-10 worthy riders

**What went wrong:**
- DNS risk flags were too aggressive - Kamp (P3) and Wyseure (P7) both raced
- Vanthourenhout had an off day after back-to-back Sardinia wins
- Underestimated several riders in a weaker field (Ferdinande, Lauryssen, Mein)

**Lessons:**
- DNS risk flagging needs refinement for B-tier races
- Recent form may not transfer between elite UCI World Cup and regional races
- Need to account for "load management" after intensive weekends

---

## Women Elite

| Metric                    | Value                 |
|---------------------------|----------------------:|
| **Recall**                | 40.0% (4/10)          |
| **Precision**             | 100.0% (4/4)          |
| High Confidence Accuracy  | 100.0% (2/2)          |
| Podium Accuracy           | 100.0% (1/1)          |

### Correct Predictions

| Pred | Actual | Rider                    | Prob  | Notes                    |
|-----:|-------:|--------------------------|------:|--------------------------|
|    1 |      1 | **Inge van der Heijden** | 98.6% | Winner as predicted      |
|    2 |      2 | **Marion Norbert Riberolle** | 84.0% | Perfect placement    |
|    3 |      4 | Hélène Clauzel           | 67.8% | Solid Top-5              |
|    4 |      8 | Mae Cabaca               | 57.6% | Just made Top-10         |

### Missed Top-10 (False Negatives)

| Actual | Rider          | Prob  | Why Missed                    |
|-------:|----------------|------:|-------------------------------|
|      3 | Julie Brouwers | 13.4% | Strong H2H (87%) but low prob |
|      5 | Jinse Peeters  |  4.3% | Local race boost?             |
|      6 | Xan Crees      |  2.7% | Improving rider               |
|      7 | Lotte Baele    |  0.4% | Youth breakthrough            |
|      9 | Sara Sonnemans |  0.4% | Weaker field opportunity      |
|     10 | Sara Cueto Vega|  0.2% | Just squeaked in              |

### False Positives

*None - 100% precision!*

### Analysis

**What went right:**
- Perfect precision - every prediction was correct
- Top 2 exactly right
- Podium prediction (VDH) was correct

**What went wrong:**
- Missed Julie Brouwers (P3) despite 87% H2H - her 13.4% prob was too low
- Several young riders broke through in the weaker field

**Lessons:**
- B-tier races are opportunities for borderline riders
- H2H alone isn't enough when probability is low
- Young rider emergence is hard to predict

---

## DNS Risk Analysis

| Rider         | Our Flag     | Actual     | Impact                           |
|---------------|--------------|------------|----------------------------------|
| Ryan Kamp     | DNS Risk     | **P3**     | Major miss - podiumed!           |
| Joran Wyseure | DNS Risk     | **P7**     | Significant miss                 |
| Nele De Vos   | DNS Risk     | P18        | Raced, low finish                |

**Conclusion:** DNS risk flagging cost us 2 Top-10 predictions in the men's race. Need to recalibrate for B-tier races where riders often participate.

---

## Model Performance Trend

| Race          | Date       | Recall | Precision | High Conf |
|---------------|------------|-------:|----------:|----------:|
| Tabor         | 2024-12-21 |  90.0% |     90.0% |    100.0% |
| Flamanville   | 2025-11-30 | 100.0% |     90.9% |    100.0% |
| Sardinia D1   | 2025-12-07 | 100.0% |    100.0% |    100.0% |
| Sardinia D2   | 2025-12-08 | 100.0% |    100.0% |    100.0% |
| **Kortrijk**  | 2025-12-13 |  35.0% |     87.5% |     83.3% |

**Note:** Kortrijk was a weaker field B-tier race. Performance drops on non-World Cup events where:
- DNS risk flags are less reliable
- Favorites may underperform (load management)
- Young/lower-ranked riders have more opportunities

---

## Probability Distribution Analysis

| Metric           | Value | Interpretation        |
|-----------------|-----:|----------------------|
| Low (<30%)       | 88.2% | Non-contenders        |
| Mid (30-60%)     |  2.4% | Uncertain zone        |
| High (>60%)      |  9.4% | Likely contenders     |
| Mean Probability | 11.8% | Average across field  |
| Std Deviation    | 0.268 | Probability spread    |
| New Riders       |     4 | No prior race history |
| Field Size       |    85 | Total riders          |

**Pattern:** BIMODAL
- Model is decisive - clear separation between contenders and non-contenders

**What this means:**
- 88% of riders had <30% probability (clear non-contenders)
- 2% in the uncertain 30-60% range
- 9% were predicted >60% (likely Top-10)
---

*Generated by VeloPredict pipeline on 2025-12-13*
