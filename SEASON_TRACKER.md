# VeloPredict Season 2025-26 Metrics Tracker

**Last Updated:** December 30, 2025
**Current Model Version:** v6.13

---

## Season Summary

Actual predictions as published (original model versions for historical, v6.4 live for Antwerpen+).

| Date       | Race        | Series    | Cat | Model | Hits@10 | Hits@3 | Spearman ρ | MAE Rank |
|------------|-------------|-----------|-----|-------|---------|--------|------------|----------|
| 2025-11-23 | Tabor       | UCI WC    | ME  | v1    | 4/10    | 1/3    | n/a        | n/a      |
| 2025-11-23 | Tabor       | UCI WC    | WE  | v1    | 3/10    | 0/3    | n/a        | n/a      |
| 2025-11-30 | Flamanville | UCI WC    | ME  | v2    | 8/10    | 1/3    | n/a        | n/a      |
| 2025-11-30 | Flamanville | UCI WC    | WE  | v2    | 5/10    | 1/3    | n/a        | n/a      |
| 2025-12-07 | Sardinia    | UCI WC    | ME  | v6    | 7/10    | 1/3    | n/a        | n/a      |
| 2025-12-07 | Sardinia    | UCI WC    | WE  | v6    | 6/10    | 2/3    | n/a        | n/a      |
| 2025-12-13 | Kortrijk    | Exact     | ME  | v6.2  | 6/10    | 1/3    | n/a        | n/a      |
| 2025-12-13 | Kortrijk    | Exact     | WE  | v6.2  | 7/10    | 2/3    | n/a        | n/a      |
| 2025-12-14 | Namur       | UCI WC    | ME  | v6.1  | 6/10    | 2/3    | n/a        | n/a      |
| 2025-12-14 | Namur       | UCI WC    | WE  | v6.1  | 6/10    | 1/3    | n/a        | n/a      |
| 2025-12-20 | Antwerpen   | UCI WC    | ME  | v6.4  | 6/10    | 1/3    | 0.08       | 6.0      |
| 2025-12-20 | Antwerpen   | UCI WC    | WE  | v6.4  | 7/10    | 2/3    | 0.78       | 3.4      |
| 2025-12-21 | Koksijde    | UCI WC    | ME  | v6.5  | 7/10    | 2/3    | 0.68       | 2.0      |
| 2025-12-21 | Koksijde    | UCI WC    | WE  | v6.5  | 9/10    | 2/3    | 0.67       | 1.7      |
| 2025-12-22 | Hofstade    | X2O-Trofee| ME  | v6.6  | 8/10    | 2/3    | 0.53       | 2.6      |
| 2025-12-22 | Hofstade    | X2O-Trofee| WE  | v6.6  | 7/10    | 1/3    | 0.78       | 2.8      |
| 2025-12-26 | Heusden-Zolder | Superp | ME  | v6.7  | 5/10    | 2/3    | 0.68       | 4.9      |
| 2025-12-26 | Heusden-Zolder | Superp | WE  | v6.7  | 6/10    | 2/3    | 0.69       | 4.9      |
| 2025-12-26 | Gavere      | UCI WC    | ME  | v6.8  | 6/10    | 2/3    | 0.33       | 5.7      |
| 2025-12-26 | Gavere      | UCI WC    | WE  | v6.8  | 7/10    | 2/3    | 0.61       | 4.5      |
| 2025-12-28 | Dendermonde | UCI WC    | ME  | v6.9  | 8/10    | 2/3    | 0.27       | 3.8      |
| 2025-12-28 | Dendermonde | UCI WC    | WE  | v6.9  | 7/10    | 2/3    | 0.68       | 2.3      |
| 2025-12-29 | Loenhout    | X2O-Trofee| ME  | v6.10 | 6/10    | 2/3    | 0.64       | 2.7      |
| 2025-12-29 | Loenhout    | X2O-Trofee| WE  | v6.10 | 6/10    | 1/3    | 0.47       | 4.3      |
| 2025-12-30 | Diegem      | Superp    | ME | v6.12 | 6/10    | 2/3    | 0.90       | 2.9      |
| 2025-12-30 | Diegem      | Superp    | WE | v6.12 | 5/10    | 2/3    | 0.37       | 3.5      |

### Season Averages

| Category    | Races | Avg Hits@10 | Avg Hits@3 |
|-------------|-------|-------------|------------|
| Men Elite   | 13    | 6.4/10      | 1.6/3      |
| Women Elite | 13    | 6.2/10      | 1.5/3      |
| **Overall** | 26    | **6.3/10**  | **1.6/3**  |

### Targets

| Metric | Target | Season Avg | Status |
|--------|--------|------------|--------|
| Hits@10 | 7+/10 | 6.3/10 | ❌ Below |
| Hits@3 | 2+/3 | 1.6/3 | ❌ Below |
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

| Date       | Race      | Series | Cat | Hits@10 | Hits@3 | Spearman ρ | MAE Rank | Notes            |
|------------|-----------|--------|-----|---------|--------|------------|----------|------------------|
| 2025-12-30 | Diegem    | Superp | WE  | 5/10    | 2/3    | 0.37       | 3.5      |           |
| 2025-12-30 | Diegem    | Superp | ME  | 6/10    | 2/3    | 0.90       | 2.9      |           |
| 2025-12-29 | Loenhout  | X2O-Tr | ME  | 6/10    | 2/3    | 0.64       | 2.7      | 3 DNS (NYS,SWEECK,VDH) |
| 2025-12-29 | Loenhout  | X2O-Tr | WE  | 6/10    | 1/3    | 0.47       | 4.3      | ALVARADO DNS     |
| 2025-12-28 | Dendermonde | UCI WC | ME  | 8/10    | 2/3    | 0.27       | 3.8      |           |
| 2025-12-28 | Dendermonde | UCI WC | WE  | 7/10    | 2/3    | 0.68       | 2.3      |           |
| 2025-12-26 | Gavere    | UCI WC | WE  | 7/10    | 2/3    | 0.61       | 4.5      |           |
| 2025-12-26 | Gavere    | UCI WC | ME  | 6/10    | 2/3    | 0.33       | 5.7      |           |
| 2025-12-26 | Heusden-Zolder | Superp | WE  | 6/10    | 2/3    | 0.69       | 4.9      |           |
| 2025-12-26 | Heusden-Zolder | Superp | ME  | 5/10    | 2/3    | 0.68       | 4.9      |           |
| 2025-12-22 | Hofstade  | X2O-Tr | WE  | 7/10    | 1/3    | 0.78       | 2.8      |           |
| 2025-12-22 | Hofstade  | X2O-Tr | ME  | 8/10    | 2/3    | 0.53       | 2.6      |           |
| 2025-12-20 | Antwerpen | UCI WC | ME  | 6/10    | 1/3    | 0.08       | 6.0      | NYS P23, VDH DNS |
| 2025-12-20 | Antwerpen | UCI WC | WE  | 7/10    | 2/3    | 0.78       | 3.4      |                  |
| 2025-12-21 | Koksijde  | UCI WC | ME  | 7/10    | 2/3    | 0.68       | 2.0      | VDH P11, 4/4 targets |
| 2025-12-21 | Koksijde  | UCI WC | WE  | 9/10    | 2/3    | 0.67       | 1.7      | VAN ANROOIJ P2, 4/4 targets |


#### Antwerpen 2025-12-20 Details

**ME:** 🔴 0/4 targets met
- Surprises: Laurens (#11→P2), Pim (#13→P4), Mees (#17→P9)
- Misses: Lars (DNS), Thibau (P23), Joris (P16)
- Podium: 1/3 | Spearman: 0.08

**WE:** 🟡 3/4 targets met
- Surprises: Kristýna (#11→P5), Shirin (#12→P6), Manon (#13→P9)
- Misses: Amandine (P13), Marion (P12), Hélène (P19)
- Podium: 2/3 | Spearman: 0.78

#### Koksijde 2025-12-21 Details

**ME:** 🟢 4/4 targets met
- Hits: VDP P1, SWEECK P2, VANDEPUTTE P3, DEL GROSSO P4, AERTS P5, MASON P8, VANTHOURENHOUT P9
- Misses: VAN DER HAAR (P11), VERSTRYNGE (P13), KAMP (P16)
- Surprise: HENDRIKX (#11→P10) made actual top-10
- Podium: 2/3 | Spearman: 0.68

**WE:** 🟢 4/4 targets met
- Hits: BRAND P1, VAN ANROOIJ P2, ALVARADO P3, VAN ALPHEN P4, PIETERSE P5, VAN DER HEIJDEN P6, BENTVELD P8, ZEMANOVÁ P9, FOUQUENET P10
- Misses: CASASOLA (DNF)
- Surprise: VAN ANROOIJ (#7→P2) major outperformance
- Podium: 2/3 | Spearman: 0.67

**BEST RACE PERFORMANCE** - All 8/8 targets met!


#### Hofstade 2025-12-22 Details

**ME:** 🟢 All targets met
- Surprises: Toon (#11→P9), Ryan (#15→P10)
- Misses: Michael (DNS), Lars (P13)
- Podium: 2/3 | Spearman: 0.53

**WE:** 🟡 3/4 targets met
- Surprises: Rebecca (#12→P6)
- Misses: Carmen (DNS), Perrine (P13), Sara (P18)
- Podium: 1/3 | Spearman: 0.78

#### Heusden-Zolder 2025-12-26 Details

**ME:** 🟡 2/4 targets met
- Surprises: Kevin (#12→P7), Mees (#13→P8), Gerben (#20→P10)
- Misses: Joris (DNS), Thibau (P14), Laurens (DNS)
- Podium: 2/3 | Spearman: 0.68

**WE:** 🟡 2/4 targets met
- Surprises: Marion (#11→P5), Jolanda (#12→P8), Marie (#15→P7)
- Misses: Sara (DNS), Marthe (P20), Mae (P21)
- Podium: 2/3 | Spearman: 0.69

#### Gavere 2025-12-26 Details

**ME:** 🔴 1/4 targets met
- Surprises: Joran (#14→P7), Mees (#16→P8), Emiel (#17→P5)
- Misses: Joris (DNS), Laurens (P11), Niels (P18)
- Podium: 2/3 | Spearman: 0.33

**WE:** 🟡 3/4 targets met
- Surprises: Blanka (#15→P4), Célia (#18→P6), Viktória (#19→P10)
- Misses: Marion (P12), Leonie (P15), Jolanda (P24)
- Podium: 2/3 | Spearman: 0.61


#### Dendermonde 2025-12-28 Details

**WE:** 🟢 All targets met
- Surprises: Célia (#11→P10), Leonie (#15→P6), Manon (#19→P9)
- Misses: Inge (P13), Sara (DNS), Shirin (P11)
- Podium: 2/3 | Spearman: 0.68

**ME:** 🟡 2/4 targets met
- Surprises: Mees (#13→P9), Niels (#17→P5)
- Misses: Joris (DNS), Lars (P17)
- Podium: 2/3 | Spearman: 0.27

#### Diegem 2025-12-30 Details

**ME:** 🟡 3/4 targets met
- Surprises: Filippo (#14→P9), Mees (#15→P4), Joran (#16→P2)
- Misses: Joris (DNS), Laurens (DNS), Cameron (P22)
- Podium: 2/3 | Spearman: 0.90

**WE:** 🔴 1/4 targets met
- Surprises: Larissa (#11→P10), Line (#16→P8), Rebecca (#18→P6)
- Misses: Marion (DNS), Sara (DNS), Inge (DNS)
- Podium: 2/3 | Spearman: 0.37
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
| v6.4       | Robust Feature Extraction  | 82.6%         | 0.833 | 8,950        | SOP: Always use best cumulative    |
| v6.5       | +Antwerpen Results         | 82.0%         | 0.817 | 9,114        | Post Antwerpen                     |
| v6.6       | +Koksijde Results          | 81.1%         | 0.813 | 9,235        | Post Koksijde                      |
| v6.7       | +Hofstade Results          | 81.2%         | 0.812 | 9,355        | Post Hofstade                    |
| v6.8       | +Heusden-Zolder Results    | 81.0%         | 0.790 | 9,465        | Post Heusden-Zolder              |
| v6.9       | +Gavere Results            | 80.1%         | 0.783 | 9,589        | Post Gavere        |
| v6.10  | +Dendermonde Results       | 80.5%         | 0.772 | 9,729        | Post Dendermonde |
| v6.11   | +Azencross-Loenhout Results | 81.0%         | 0.773 | 9,777        | Post Azencross-Loenhout |
| v6.12   | +Azencross-Loenhout Results | 79.2%         | 0.767 | 9,848        | Post Azencross-Loenhout |
| **v6.13**   | +Diegem Results            | 79.6%         | 0.735 | 9,994        | **Current - Post Diegem** |

---

## Retraining Policy

### Current Policy: Retrain After Each Race

Starting with v6.5, we retrain after each race validation to capture the latest H2H data.

| Step | Action                                    | Automated? |
|------|-------------------------------------------|------------|
| 1    | Add results to results_with_features.csv  | Yes        |
| 2    | Run `python pipeline.py retrain`          | Manual     |
| 3    | Bump version in race_registry.json        | Manual     |
| 4    | SEASON_TRACKER.md version updates         | Yes        |

### What Updates Without Retraining

| Component              | Updates Automatically? | Notes                                    |
|------------------------|------------------------|------------------------------------------|
| H2H matrix             | Yes                    | Rebuilt from results_with_features.csv   |
| Form features          | Yes                    | Looked up at prediction time             |
| UCI rankings           | Yes                    | Loaded from uci_rankings_*.csv           |
| Model weights          | No                     | Requires retraining                      |
| Feature importance     | No                     | Requires retraining                      |
| Probability calibration| No                     | Requires retraining                      |

### Retraining History

| Version | Date       | Trigger                 | Observations | Notes                |
|---------|------------|-------------------------|--------------|--------------------- |
| v6.3    | 2025-12-14 | +Namur Results          | 8,950        | Post-Namur           |
| v6.5    | 2025-12-21 | +Antwerpen Results      | 9,114        | Post-Antwerpen       |
| v6.6    | 2025-12-21 | +Koksijde Results       | 9,235        | Post-Koksijde        |
| v6.7    | 2025-12-22 | +Hofstade Results       | 9,355        | Post-Hofstade        |
| v6.8    | 2025-12-26 | +Heusden-Zolder Results | 9,465        | Post-Heusden-Zolder  |
| v6.9    | 2025-12-27 | +Gavere Results         | 9,589        | Post-Gavere          |
| v6.10    | 2025-12-28 | +Dendermonde Results    | 9,729        | Post-Dendermonde     |
| v6.11    | 2025-12-29 | +Azencross-Loenhout Results | 9,777        | Post-Azencross-Loenhout |
| v6.12    | 2025-12-29 | +Azencross-Loenhout Results | 9,848        | Post-Azencross-Loenhout |
| v6.13    | 2025-12-30 | +Diegem Results         | 9,994        | Post-Diegem          |

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
| Antwerpen   | 82.6%      | 3.3%         | 14.1%       | BIMODAL   | 184   | 11         |
| Koksijde ME | 84.5%      | 1.7%         | 13.8%       | BIMODAL   | 58    | 0          |
| Koksijde WE | 85.1%      | 3.4%         | 11.5%       | BIMODAL   | 87    | 2          |
| Hofstade ME | 78.7%  | 2.1%     | 19.1%   | BIMODAL   | 47    | 0          |
| Hofstade WE | 95.8%  | 0.0%     | 4.2%    | BIMODAL   | 71    | 0          |
| Heusden-Zolder ME | 89.0%  | 2.0%     | 9.0%    | BIMODAL   | 100   | 0          |
| Heusden-Zolder WE | 89.5%  | 1.3%     | 9.2%    | BIMODAL   | 76    | 0          |
| Gavere ME   | 75.7%  | 8.6%     | 15.7%   | BIMODAL   | 70    | 0          |
| Gavere WE   | 77.9%  | 1.5%     | 20.6%   | BIMODAL   | 68    | 0          |
| Dendermonde WE | 84.7%  | 2.0%     | 13.3%   | BIMODAL   | 98    | 0          |
| Dendermonde ME | 73.8%  | 9.2%     | 16.9%   | BIMODAL   | 65    | 0          |
| Diegem ME   | 89.0%  | 2.0%     | 9.0%    | BIMODAL   | 100   | 0          |
| Diegem WE   | 89.0%  | 4.0%     | 7.0%    | BIMODAL   | 100   | 0          |

### Pattern Interpretation

| Pattern     | Mid-Range % | Model Confidence | Trust Level | Retail Analog           |
|-------------|-------------|------------------|-------------|-------------------------|
| **BIMODAL** | <10%        | Decisive         | Higher      | Auto-approve/suppress   |
| **MODERATE**| 10-20%      | Typical          | Normal      | Standard process        |
| **BALANCED**| >20%        | Uncertain        | Lower       | Requires A/B testing    |

### Distribution vs Accuracy Correlation

| Race        | Pattern   | Mid % | Hits@10 (v6.4+) | Precision | Notes                    |
|-------------|-----------|-------|-----------------|-----------|--------------------------|
| Tabor       | MODERATE  | 19.3% | 9/10            | 47%       | Early model, loose threshold |
| Flamanville | MODERATE  | 17.2% | 9/10            | 49%       | Many mid-range riders    |
| Sardinia    | MODERATE  | 13.0% | 7/10            | 35%       | Smaller field            |
| Kortrijk    | BIMODAL   | 2.4%  | 7.5/10          | 88%       | Decisive = high precision |
| Namur       | BIMODAL   | 0.8%  | 7/10            | 75%       | Very decisive            |
| Antwerpen   | BIMODAL   | 3.3%  | 6.5/10          | 75%       | VDH DNS, NYS P23         |
| Koksijde    | BIMODAL   | 2.6%  | 8/10            | 80%       | Best performance, 8/8 targets |
| Hofstade    | BIMODAL   | 1.1%  | 7.5/10          | 85%       | VDP vs VAN AERT, X2O debut |
| Heusden-Zolder | BIMODAL | 1.7% | 5.5/10         | 72%       | 3 DNS, NYS P14           |
| Gavere      | BIMODAL   | 5.1%  | 6.5/10          | 76%       | Joran #14→P7, Emiel #17→P5 |

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
Koksijde (v6.5)  ████████████████████████████████████████████████████████████████████████████████████▌ 84.8%
Hofstade (v6.6)  ██████████████████████████████████████████████████████████████████████▊ 78.7%
Heusden-Zolder (v6.7) ████████████████████████████████████████████████████████████████████████████████ 89.0%
Gavere (v6.8)    ████████████████████████████████████████████████████████████████████ 75.7%
Dendermonde (v6.9) ████████████████████████████████████████████████████████████████████████████ 84.7%
Diegem (v6.12)   ████████████████████████████████████████████████████████████████████████████████ 89.0%
```

**🟡 Mid Range (30-60%) - Uncertain zone**
```
Tabor (v1)       ███████████████████▎ 19.3%
Flamanville (v2) █████████████████▏   17.2%
Sardinia (v6)    █████████████        13.0%
Kortrijk (v6.2)  ██▍                   2.4%
Namur (v6.1)     ▊                     0.8%
Antwerpen (v6.4) ███▎                  3.3%
Koksijde (v6.5)  ██▋                   2.6%
Hofstade (v6.6)  █▊                   2.1%
Heusden-Zolder (v6.7) █▊                   2.0%
Gavere (v6.8)    ███████▌             8.6%
Dendermonde (v6.9) █▊                   2.0%
Diegem (v6.12)   █▊                   2.0%
```

**🟢 High Range (>60%) - Likely contenders**
```
Tabor (v1)       ██████████████████████████████████▏ 34.2%
Flamanville (v2) ████████████████████████████████▎   32.3%
Sardinia (v6)    ███████████▋                        11.6%
Kortrijk (v6.2)  █████████▍                           9.4%
Namur (v6.1)     ██████████████▉                     14.9%
Antwerpen (v6.4) ██████████████▏                     14.1%
Koksijde (v6.5)  ████████████▋                       12.6%
Hofstade (v6.6)  █████████████████                   19.1%
Heusden-Zolder (v6.7) ████████                            9.0%
Gavere (v6.8)    ██████████████                      15.7%
Dendermonde (v6.9) ███████████▊                        13.3%
Diegem (v6.12)   ████████                            9.0%
```

**Trends**:
- 🔵 **Low range increasing**: More riders clearly identified as non-contenders (46% → 85%)
- 🟡 **Mid range decreasing**: Fewer "coin flip" predictions (19% → 3%)
- 🟢 **High range stabilizing**: Consistent ~10-15% of field identified as contenders

---

*Generated by VeloPredict v6.13 | Tracking season 2025-26*
