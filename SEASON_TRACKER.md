# VeloPredict Season 2025-26 Metrics Tracker

**Last Updated:** December 17, 2025
**Current Model Version:** v6.4

---

## Section 1: v6.4+ Live Predictions

Predictions made with v6.4 or later, evaluated with new metrics.

### New Metrics Explanation

| Metric         | Description                                                    | Target |
|----------------|----------------------------------------------------------------|--------|
| **Hits@10**    | How many of our 10 predictions finished in actual top-10?      | 7+/10  |
| **Hits@3**     | How many of our 3 podium picks made actual podium?             | 2+/3   |
| **Spearman ρ** | Rank correlation between predicted and actual order (-1 to +1) | >0.5   |
| **MAE Rank**   | Average positions off for our predicted top-10                 | <3     |

### Live Predictions (v6.4+)

| Date       | Race      | Series | Cat | Hits@10 | Hits@3 | Spearman ρ | MAE Rank | Notes     |
|------------|-----------|--------|-----|---------|--------|------------|----------|-----------|
| 2025-12-20 | Antwerpen | UCI WC | ME  | -       | -      | -          | -        | *Pending* |
| 2025-12-20 | Antwerpen | UCI WC | WE  | -       | -      | -          | -        | *Pending* |

---

## Section 2: Historical Legacy (Retroactive v6.4 Comparison)

Original predictions made with various model versions, plus retroactive v6.4 predictions for comparison.

### Tabor (Nov 23, 2025)

**Original Model:** v1 | **Threshold:** 0.5

| Category        | Metric       | Original (v1) | v6.4 Retro | Delta    |
|-----------------|--------------|---------------|------------|----------|
| **Men Elite**   | Precision    | 47.4%         | N/A        |          |
|                 | Recall       | 90%           | N/A        |          |
|                 | Hits@10      | 4/10          | **9/10**   | **+5**   |
|                 | Hits@3       | 1/3           | **2/3**    | **+1**   |
|                 | Spearman ρ   | -             | **0.30**   |          |
|                 | MAE Rank     | -             | **3.7**    |          |
| **Women Elite** | Precision    | 37.5%         | N/A        |          |
|                 | Recall       | 90%           | N/A        |          |
|                 | Hits@10      | 3/10          | **9/10**   | **+6**   |
|                 | Hits@3       | 0/3           | **2/3**    | **+2**   |
|                 | Spearman ρ   | -             | **0.80**   |          |
|                 | MAE Rank     | -             | **2.0**    |          |

**Notes:** First test - over-predicted with low threshold

---

### Flamanville (Nov 30, 2025)

**Original Model:** v2 | **Threshold:** 0.5

| Category        | Metric       | Original (v2) | v6.4 Retro | Delta    |
|-----------------|--------------|---------------|------------|----------|
| **Men Elite**   | Precision    | 53.8%         | N/A        |          |
|                 | Recall       | 70%           | N/A        |          |
|                 | Hits@10      | 8/10          | **9/10**   | **+1**   |
|                 | Hits@3       | 1/3           | **2/3**    | **+1**   |
|                 | Spearman ρ   | -             | **0.33**   |          |
|                 | MAE Rank     | -             | **2.4**    |          |
| **Women Elite** | Precision    | 45.0%         | N/A        |          |
|                 | Recall       | 90%           | N/A        |          |
|                 | Hits@10      | 5/10          | **9/10**   | **+4**   |
|                 | Hits@3       | 1/3           | **1/3**    | 0        |
|                 | Spearman ρ   | -             | **0.83**   |          |
|                 | MAE Rank     | -             | **1.3**    |          |

**Notes:** New rider false positives

---

### Sardinia (Dec 7, 2025)

**Original Model:** v6 | **Threshold:** 0.55

| Category        | Metric        | Original (v6) | v6.4 Retro | Delta    |
|-----------------|---------------|---------------|------------|----------|
| **Men Elite**   | Precision     | 40%           | N/A        |          |
|                 | Recall        | 100%          | N/A        |          |
|                 | High Conf Acc | 100%          | N/A        |          |
|                 | Hits@10       | 7/10          | **7/10**   | 0        |
|                 | Hits@3        | 1/3           | **2/3**    | **+1**   |
|                 | Spearman ρ    | -             | **0.64**   |          |
|                 | MAE Rank      | -             | **2.3**    |          |
| **Women Elite** | Precision     | 30%           | N/A        |          |
|                 | Recall        | 100%          | N/A        |          |
|                 | High Conf Acc | 100%          | N/A        |          |
|                 | Hits@10       | 6/10          | **7/10**   | **+1**   |
|                 | Hits@3        | 2/3           | **1/3**    | -1       |
|                 | Spearman ρ    | -             | **0.64**   |          |
|                 | MAE Rank      | -             | **1.9**    |          |

**Notes:** Smaller field (69 riders), 7/7 high-conf correct in original

---

### Kortrijk (Dec 13, 2025)

**Original Model:** v6.2 | **Threshold:** 0.55 | **Series:** Exact Cross (B-tier)

| Category        | Metric       | Original (v6.2) | v6.4 Retro | Delta    |
|-----------------|--------------|-----------------|------------|----------|
| **Men Elite**   | Precision    | 75%             | N/A        |          |
|                 | Recall       | 30%             | N/A        |          |
|                 | Hits@10      | 6/10            | **7/10**   | **+1**   |
|                 | Hits@3       | 1/3             | **0/3**    | -1       |
|                 | Spearman ρ   | -               | **0.39**   |          |
|                 | MAE Rank     | -               | **5.3**    |          |
| **Women Elite** | Precision    | 100%            | N/A        |          |
|                 | Recall       | 40%             | N/A        |          |
|                 | Hits@10      | 7/10            | **8/10**   | **+1**   |
|                 | Hits@3       | 2/3             | **2/3**    | 0        |
|                 | Spearman ρ   | -               | **0.81**   |          |
|                 | MAE Rank     | -               | **1.4**    |          |

**Notes:** B-tier race (Exact Cross) - model calibrated for UCI World Cup

---

### Namur (Dec 14, 2025)

**Original Model:** v6.1 | **Threshold:** 0.55

| Category        | Metric        | Original (v6.1) | v6.4 Retro | Delta    |
|-----------------|---------------|-----------------|------------|----------|
| **Men Elite**   | Precision     | 75%             | N/A        |          |
|                 | Recall        | 60%             | N/A        |          |
|                 | High Conf Acc | 75%             | N/A        |          |
|                 | Hits@10       | 6/10            | **7/10**   | **+1**   |
|                 | Hits@3        | 2/3             | **3/3**    | **+1**   |
|                 | Spearman ρ    | -               | **0.64**   |          |
|                 | MAE Rank      | -               | **2.0**    |          |
| **Women Elite** | Precision     | 75%             | N/A        |          |
|                 | Recall        | 60%             | N/A        |          |
|                 | High Conf Acc | 86%             | N/A        |          |
|                 | Hits@10       | 6/10            | **7/10**   | **+1**   |
|                 | Hits@3        | 1/3             | **1/3**    | 0        |
|                 | Spearman ρ    | -               | **0.46**   |          |
|                 | MAE Rank      | -               | **2.7**    |          |

**Notes:** Belgian depth, NEFF surprise (new rider finished P5 in Women)

---

## Section 3: v6.4 Aggregate Performance

### Overall Performance (Retroactive Predictions)

| Metric             | Men Elite | Women Elite | Combined     |
|--------------------|-----------|-------------|--------------|
| **Races**          | 5         | 5           | 10           |
| **Avg Hits@10**    | 7.8/10    | 8.0/10      | **7.9/10**   |
| **Avg Hits@3**     | 1.8/3     | 1.4/3       | **1.6/3**    |
| **Avg Spearman ρ** | 0.46      | 0.71        | **0.59**     |
| **Avg MAE Rank**   | 3.1       | 1.9         | **2.5**      |

### By Race Series

| Series        | Races | Avg Hits@10 | Avg Hits@3 | Avg Spearman | Avg MAE |
|---------------|-------|-------------|------------|--------------|---------|
| UCI World Cup | 8     | 8.0/10      | 1.8/3      | 0.58         | 2.2     |
| Exact Cross   | 2     | 7.5/10      | 1.0/3      | 0.60         | 3.4     |

### By Category

| Category    | Races | Avg Hits@10 | Avg Hits@3 | Avg Spearman | Avg MAE |
|-------------|-------|-------------|------------|--------------|---------|
| Men Elite   | 5     | 7.8/10      | 1.8/3      | 0.46         | 3.1     |
| Women Elite | 5     | 8.0/10      | 1.4/3      | 0.71         | 1.9     |

### Key Insights

1. **Hits@10 is strong**: 79% of predictions land in actual top-10
2. **Podium prediction harder**: Only 53% podium hit rate - more variance in top-3
3. **Women predictions more accurate**: Higher Spearman (0.71 vs 0.46) and lower MAE (1.9 vs 3.1)
4. **Ranking order needs work**: Spearman 0.59 means we get ~60% of ordering right
5. **B-tier race performance**: Kortrijk Men had worst MAE (5.3) - model optimized for UCI fields

---

## Model Version History

| Version    | Innovation                 | Test Accuracy | AUC   | Observations | Notes                              |
|------------|----------------------------|---------------|-------|--------------|------------------------------------|
| v1         | Baseline RF                | 80.2%         | -     | 7,724        | First deployment                   |
| v2         | +Threshold                 | 80.2%         | -     | 7,724        | Confidence filtering               |
| v3         | +Defaults                  | 79.0%         | 0.818 | 7,793        | Better NaN handling                |
| v4         | +UCI Inference             | 78.8%         | 0.820 | 7,793        | New rider prediction               |
| v5         | +H2H                       | 76.9%         | 0.830 | 8,188        | Head-to-head feature               |
| v6         | +New Rider                 | 77.6%         | 0.835 | 8,357        | New rider penalty                  |
| v6.2       | No DNS Exclusion           | 83.4%         | 0.850 | 8,849        | Stopped filtering elite racers     |
| v6.3       | +Namur Results             | 82.6%         | 0.833 | 8,950        | Training data update               |
| **v6.4**   | Robust Feature Extraction  | 82.6%         | 0.833 | 8,950        | **SOP: Always use best cumulative**|

---

## Retraining Policy

### When to Retrain

| Trigger                          | Action                     | Priority |
|----------------------------------|----------------------------|----------|
| Major feature engineering change | Retrain immediately        | HIGH     |
| 5+ UCI World Cup races completed | Scheduled retrain          | MEDIUM   |
| Accuracy drops >5% vs baseline   | Investigate + retrain      | HIGH     |
| New season starts                | Full retrain with new data | HIGH     |

### Why Not Retrain After Every Race?

1. **Marginal gains**: Each race adds ~1-2% to dataset (~100-200 obs out of ~9,000)
2. **H2H updates automatically**: Our #1 feature (22.7% importance) recalculates from historical data at prediction time
3. **Form features are dynamic**: avg_place_last3, best_place_last5 come from data lookup, not model weights
4. **Stability > freshness**: Frequent retraining risks overfitting to recent noise

### What Updates Without Retraining

| Component              | Updates Automatically? | Notes                                    |
|------------------------|------------------------|------------------------------------------|
| H2H matrix             | Yes                    | Rebuilt from results_with_features.csv   |
| Form features          | Yes                    | Looked up at prediction time             |
| UCI rankings           | Yes                    | Loaded from uci_rankings_*.csv           |
| Model weights          | No                     | Requires retraining                      |
| Feature importance     | No                     | Requires retraining                      |
| Probability calibration| No                     | Requires retraining                      |

### Current Retraining Schedule

- **Last retrain**: v6.3 (Dec 14, 2025) - Added Namur results
- **Next scheduled**: After Hulst (Jan 2026) or 5 more UCI WC races
- **Observations at last retrain**: 8,950

---

## Original vs v6.4 Retroactive Comparison

| Race        | Category    | Orig Hits@10 | v6.4 Hits@10 | Δ   | Orig Hits@3 | v6.4 Hits@3 | Δ   |
|-------------|-------------|--------------|--------------|-----|-------------|-------------|-----|
| Tabor       | Men Elite   | 4/10         | 9/10         | +5  | 1/3         | 2/3         | +1  |
| Tabor       | Women Elite | 3/10         | 9/10         | +6  | 0/3         | 2/3         | +2  |
| Flamanville | Men Elite   | 8/10         | 9/10         | +1  | 1/3         | 2/3         | +1  |
| Flamanville | Women Elite | 5/10         | 9/10         | +4  | 1/3         | 1/3         | 0   |
| Sardinia    | Men Elite   | 7/10         | 7/10         | 0   | 1/3         | 2/3         | +1  |
| Sardinia    | Women Elite | 6/10         | 7/10         | +1  | 2/3         | 1/3         | -1  |
| Kortrijk    | Men Elite   | 6/10         | 7/10         | +1  | 1/3         | 0/3         | -1  |
| Kortrijk    | Women Elite | 7/10         | 8/10         | +1  | 2/3         | 2/3         | 0   |
| Namur       | Men Elite   | 6/10         | 7/10         | +1  | 2/3         | 3/3         | +1  |
| Namur       | Women Elite | 6/10         | 7/10         | +1  | 1/3         | 1/3         | 0   |

**Totals:**
- **Original Avg Hits@10**: 5.8/10
- **v6.4 Retro Avg Hits@10**: 7.9/10 (+2.1 improvement)
- **Original Avg Hits@3**: 1.3/3
- **v6.4 Retro Avg Hits@3**: 1.6/3 (+0.3 improvement)

---

## Probability Distribution Analysis

Understanding how model confidence varies across races - key for policy decisions (auto-approve vs A/B test vs manual review).

### Distribution by Race

| Race        | Low (<30%) | Mid (30-60%) | High (>60%) | Pattern   | Field | New Riders |
|-------------|------------|--------------|-------------|-----------|-------|------------|
| Tabor       | 46.5%      | 19.3%        | 34.2%       | MODERATE  | 114   | 13         |
| Flamanville | 50.5%      | 17.2%        | 32.3%       | MODERATE  | 93    | 6          |
| Sardinia    | 75.4%      | 13.0%        | 11.6%       | MODERATE  | 69    | 8          |
| Kortrijk    | 88.2%      | 2.4%         | 9.4%        | BIMODAL   | 85    | 4          |
| Namur       | 84.3%      | 0.8%         | 14.9%       | BIMODAL   | 121   | 5          |
| Antwerpen*  | 82.6%      | 3.3%         | 14.1%       | BIMODAL   | 184   | 11         |

*\*Pending race - predictions only*

### Pattern Interpretation

| Pattern     | Mid-Range % | Model Confidence | Trust Level | Retail Analog           |
|-------------|-------------|------------------|-------------|-------------------------|
| **BIMODAL** | <10%        | Decisive         | Higher      | Auto-approve/suppress   |
| **MODERATE**| 10-20%      | Typical          | Normal      | Standard process        |
| **BALANCED**| >20%        | Uncertain        | Lower       | Requires A/B testing    |

### Distribution vs Accuracy Correlation

| Race        | Pattern   | Mid % | Hits@10 (v6.4) | Precision | Notes                    |
|-------------|-----------|-------|----------------|-----------|--------------------------|
| Tabor       | MODERATE  | 19.3% | 9/10           | 47%       | Early model, loose threshold |
| Flamanville | MODERATE  | 17.2% | 9/10           | 49%       | Many mid-range riders    |
| Sardinia    | MODERATE  | 13.0% | 7/10           | 35%       | Smaller field            |
| Kortrijk    | BIMODAL   | 2.4%  | 7.5/10         | 88%       | Decisive = high precision |
| Namur       | BIMODAL   | 0.8%  | 7/10           | 75%       | Very decisive            |

### Key Insights

1. **BIMODAL → Higher Precision**: Kortrijk (88%) and Namur (75%) had highest precision with lowest mid-range %
2. **Model maturity**: Early races (Tabor, Flamanville) had more MODERATE distributions; later races trend BIMODAL as H2H matures
3. **Field familiarity**: UCI World Cups with familiar riders produce more decisive distributions
4. **Policy implication**: When mid_pct < 10%, predictions are highly trustworthy for automation

### Confidence Tier Breakdown

| Tier           | Definition | Policy Action       | Season Avg % |
|----------------|------------|---------------------|--------------|
| **High**       | >60%       | Auto-approve        | 19.4%        |
| **Mid**        | 30-60%     | A/B test / review   | 9.3%         |
| **Low**        | <30%       | Auto-suppress       | 71.3%        |

### Season Trend

**🔵 Low Range (<30%) - Non-contenders**
```
Tabor (v1)       ██████████████████████████████████████████████▌ 46.5%
Flamanville (v2) ██████████████████████████████████████████████████▌ 50.5%
Sardinia (v6)    ███████████████████████████████████████████████████████████████████████████▍ 75.4%
Kortrijk (v6.2)  ████████████████████████████████████████████████████████████████████████████████████████▏ 88.2%
Namur (v6.1)     ████████████████████████████████████████████████████████████████████████████████████▎ 84.3%
Antwerpen (v6.4) ██████████████████████████████████████████████████████████████████████████████████▋ 82.6%
```

**🟡 Mid Range (30-60%) - Uncertain zone**
```
Tabor (v1)       ███████████████████▎ 19.3%
Flamanville (v2) █████████████████▏   17.2%
Sardinia (v6)    █████████████        13.0%
Kortrijk (v6.2)  ██▍                   2.4%
Namur (v6.1)     ▊                     0.8%
Antwerpen (v6.4) ███▎                  3.3%
```

**🟢 High Range (>60%) - Likely contenders**
```
Tabor (v1)       ██████████████████████████████████▏ 34.2%
Flamanville (v2) ████████████████████████████████▎   32.3%
Sardinia (v6)    ███████████▋                        11.6%
Kortrijk (v6.2)  █████████▍                           9.4%
Namur (v6.1)     ██████████████▉                     14.9%
Antwerpen (v6.4) ██████████████▏                     14.1%
```

**Trends**:
- 🔵 **Low range increasing**: More riders clearly identified as non-contenders (46% → 83%)
- 🟡 **Mid range decreasing**: Fewer "coin flip" predictions (19% → 3%)
- 🟢 **High range stabilizing**: Consistent ~10-15% of field identified as contenders

---

*Generated by VeloPredict v6.4 | Tracking season 2025-26*
