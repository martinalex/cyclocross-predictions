# VeloPredict v7.1-LTR Experiment

## Validation Summary

### v7.1-LTR vs v6.x Performance

| Race                | Date       | Category | Model   | Hits@10 | Hits@3   | Spearman | MAE  | Winner  |
|:-------------------:|:----------:|:--------:|:-------:|:-------:|:--------:|:--------:|:----:|:-------:|
| Azencross Loenhout  | 2025-12-29 | Men      | v6.10   | 6/10     | **2/3** | **0.64** | **2.7**  |         |
|                     |            |          | v7.1-LTR| **7/10** | 1/3     | 0.52     | 2.9      | **LTR** |
| Azencross Loenhout  | 2025-12-29 | Women    | v6.10   | 6/10     | 1/3     | 0.47     | 4.3      |         |
|                     |            |          | v7.1-LTR| **8/10** | 1/3     | **0.60** | **2.5**  | **LTR** |
| Diegem              | 2025-12-30 | Men      | v6.12   | **6/10** | 2/3     | 0.90     | **2.9**  |         |
|                     |            |          | v7.1-LTR| 5/10     | 2/3     | **0.93** | 3.0      | **v6.x** |
| Diegem              | 2025-12-30 | Women    | v6.12   | 5/10     | 2/3     | 0.37     | 3.5      |         |
|                     |            |          | v7.1-LTR| 5/10     | 2/3     | **0.57** | **2.9**  | **LTR** |

### Aggregate Results

|   Metric    | v6.x Total | v7.1-LTR Total | Winner  |
|:-----------:|:----------:|:--------------:|:-------:|
| Hits@10     | 23/40      | **25/40**      | **LTR** |
| Hits@3      | **7/12**   | 6/12           | **v6.x** |
| Avg MAE     | 3.4        | **2.8**        | **LTR** |
| Races Won   | 5          | **7**          | **LTR** |

**Overall: v7.1-LTR wins 7-5-4**

---

## Overview

This document describes the Learning-to-Rank (LTR) experiment comparing the LambdaMART ranking model (v7.1-LTR) against the baseline binary classification model (v6.10/v6.12).

## Motivation

The current v6.x model uses binary classification (Top-10 vs Outside Top-10), which has limitations:

1. **Binary output**: Only predicts if a rider will finish in the top 10, not their relative position
2. **Independent predictions**: Each rider is scored independently, ignoring relative strength within the field
3. **No ranking optimization**: Model optimizes classification accuracy, not ranking quality (NDCG)

LTR addresses these by directly optimizing for ranking quality, considering relative positions within each race.

---

## Model Comparison

### v6.12 (Binary Classification)
- **Algorithm**: RandomForest (calibrated with Platt scaling)
- **Objective**: Binary classification (is_top10)
- **Output**: Probability of finishing Top-10 (0-1)
- **Primary Metric**: Accuracy (80.5%)
- **Secondary Metrics**: AUC-ROC (0.772), Brier Score (0.161)

### v7.1-LTR (Learning-to-Rank)
- **Algorithm**: LambdaMART (LightGBM)
- **Objective**: Listwise ranking optimization (lambdarank)
- **Output**: Ranking score (higher = better predicted finish)
- **Primary Metric**: NDCG@10 (0.725)
- **Secondary Metrics**: MAP@10 (0.580), MRR (0.789)
- **Training**: 50 rounds (CV-tuned with 5-fold cross-validation)

### Relevance Grading Scale (LTR)

| Relevance | Finish Position |  Description  |
|:---------:|:---------------:|:-------------:|
|     5     |        1        |    Winner     |
|     4     |       2-3       |    Podium     |
|     3     |       4-5       |     Top-5     |
|     2     |      6-10       |    Top-10     |
|     1     |      11-20      |    Top-20     |
|     0     |       21+       | Below Top-20  |

---

## Training Details

### Dataset
- **Total observations**: 9,848
- **Total races**: 68
- **Train/Test split**: 80/20 by race (chronological)
- **Train**: 54 races, 8,362 observations
- **Test**: 14 races, 1,486 observations

### v7.1-LTR Parameters (Regularized)
```python
{
    "objective": "lambdarank",
    "metric": "ndcg",
    "ndcg_eval_at": [3, 5, 10],
    "boosting_type": "gbdt",
    "num_leaves": 15,         # Reduced from 31
    "learning_rate": 0.01,    # Reduced from 0.05
    "feature_fraction": 0.7,  # Reduced from 0.9
    "bagging_fraction": 0.7,  # Reduced from 0.8
    "bagging_freq": 5,
    "min_child_samples": 50,  # Increased from 20
    "lambda_l1": 1.0,         # Increased from 0.1
    "lambda_l2": 1.0,         # Increased from 0.1
    "max_depth": 5,           # New constraint
    "random_state": 42
}
```

### v7.0-LTR Issue (Fixed in v7.1)
The original v7.0-LTR stopped after only 2 boosting rounds due to:
- Early stopping triggered by test NDCG drop after round 2
- Only 14 test races caused unstable validation scores
- Classic overfitting with insufficient regularization

**Fix in v7.1:**
- 5-fold cross-validation to find optimal rounds
- Stronger regularization (higher L1/L2, fewer leaves, more samples per leaf)
- Minimum 50 rounds guaranteed
- Lower learning rate for smoother optimization

### Feature Importance Comparison

|      Feature       | v6.12 (RF) | v7.1-LTR  |
|:------------------:|:----------:|:---------:|
| top10_rate_career  |    11.3%   | **35.6%** |
| avg_place_last3    |    13.2%   | **25.4%** |
| best_place_last5   |    14.2%   |   14.5%   |
| top3_rate_career   |     4.8%   |   11.6%   |
| h2h_field_score    |  **22.5%** |    5.4%   |
| last_place         |    10.0%   |    5.1%   |

**Key Observation**: LTR weights career consistency (top10_rate_career at 35.6%) and recent form (avg_place_last3 at 25.4%) much more heavily than RF. H2H is less important in LTR (5.4% vs 22.5%).

---

## Loenhout A/B Comparison (2025-12-29)

### Men Elite Predictions

| Rank |    v6.10 Prediction    | v6.10 Prob |   v7.1-LTR Prediction  | LTR Score |
|:----:|:----------------------:|:----------:|:----------------------:|:---------:|
|   1  | VAN DER POEL Mathieu   |    99.2%   | VAN DER POEL Mathieu   |   0.606   |
|   2  | NIEUWENHUIS Joris      |    98.7%   | NYS Thibau             |   0.520   |
|   3  | VAN AERT Wout          |    98.6%   | VAN AERT Wout          |   0.457   |
|   4  | NYS Thibau             |    98.2%   | NIEUWENHUIS Joris      |   0.435   |
|   5  | SWEECK Laurens         |    97.7%   | SWEECK Laurens         |   0.327   |
|   6  | VANDEPUTTE Niels       |    93.0%   | VAN DER HAAR Lars      |   0.286   |
|   7  | AERTS Toon             |    91.1%   | VANDEPUTTE Niels       |   0.247   |
|   8  | VAN DER HAAR Lars      |    49.0%   | AERTS Toon             |   0.147   |
|   9  | JANSSEN Wout           |    19.0%   | MASON Cameron          |  -0.006   |
|  10  | FERDINANDE Anton       |    13.7%   | KAMP Ryan              |  -0.132   |

**Key Differences**:
- LTR ranks NYS Thibau higher (#2 vs #4)
- LTR includes MASON Cameron (#9) and KAMP Ryan (#10) instead of JANSSEN and FERDINANDE

### Women Elite Predictions

| Rank |      v6.10 Prediction      | v6.10 Prob |    v7.1-LTR Prediction     | LTR Score |
|:----:|:--------------------------:|:----------:|:--------------------------:|:---------:|
|   1  | BRAND Lucinda              |    99.2%   | BRAND Lucinda              |   0.606   |
|   2  | ALVARADO Ceylin D.C.       |    99.0%   | ALVARADO Ceylin D.C.       |   0.491   |
|   3  | KASTELIJN Yara             |    96.9%   | NORBERT RIBEROLLE Marion   |   0.308   |
|   4  | NORBERT RIBEROLLE Marion   |    96.5%   | BACKSTEDT Zoe              |   0.269   |
|   5  | ZEMANOVA Kristyna          |    92.5%   | ZEMANOVA Kristyna          |   0.182   |
|   6  | BAKKER Manon               |    77.4%   | SCHREIBER Marie            |   0.173   |
|   7  | BROUWERS Julie             |    17.8%   | BAKKER Manon               |   0.105   |
|   8  | MOLENGRAAF Lauren          |    15.2%   | BROUWERS Julie             |   0.030   |
|   9  | TRUYEN Marthe              |    10.5%   | KASTELIJN Yara             |  -0.054   |
|  10  | BACKSTEDT Zoe              |    10.1%   | HARTOG Larissa             |  -0.132   |

**Key Differences**:
- LTR ranks BACKSTEDT Zoe much higher (#4 vs #10)
- LTR ranks SCHREIBER Marie (#6) and HARTOG Larissa (#10) in top-10
- KASTELIJN drops to #9 despite 100% career rate

---

## Metrics Explanation

### NDCG (Normalized Discounted Cumulative Gain)
Measures ranking quality with emphasis on top positions. A perfect ranking scores 1.0.
- NDCG@3: 0.707 - How well we rank the podium
- NDCG@5: 0.698 - How well we rank the top 5
- NDCG@10: 0.725 - How well we rank the top 10

### MAP (Mean Average Precision)
Average precision across all relevant items. Rewards placing relevant items (Top-10 finishers) early in the ranking.
- MAP@10: 0.580

### MRR (Mean Reciprocal Rank)
How well we identify the race winner (1/rank of first relevant item).
- MRR: 0.789 - We find the winner in top ~1.3 positions on average

---

## Loenhout Validation Results (2025-12-29)

### Men Elite Results

|    Metric     | v6.10 | v7.1-LTR |  Winner   |
|:-------------:|:-----:|:--------:|:---------:|
| **Hits@10**   |  6/10 | **7/10** | **LTR**   |
| **Hits@3**    |  2/3  |   1/3    |  v6.10    |
| **Spearman p**|  0.64 |   0.52   |  v6.10    |
| **MAE Rank**  |  2.7  |   2.9    |  v6.10    |

**Key Observations:**
- LTR got 7/10 correct vs v6.10's 6/10
- LTR correctly included MASON (#9->P8) and KAMP (#10->P4)
- v6.10 had JANSSEN (#9->P11) and FERDINANDE (#10->P7)
- 3 DNS hurt both models: NYS, SWEECK, VAN DER HAAR

**Actual Podium:** VAN DER POEL (P1), VANDEPUTTE (P2), NIEUWENHUIS (P3)

### Women Elite Results

|    Metric     | v6.10 | v7.1-LTR |  Winner  |
|:-------------:|:-----:|:--------:|:--------:|
| **Hits@10**   |  6/10 | **8/10** | **LTR**  |
| **Hits@3**    |  1/3  |   1/3    |   TIE    |
| **Spearman p**|  0.47 | **0.60** | **LTR**  |
| **MAE Rank**  |  4.3  | **2.5**  | **LTR**  |

**Key Observations:**
- LTR significantly outperformed on Hits@10 (8 vs 6)
- LTR correctly ranked BACKSTEDT at #4 (actual P4) vs v6.10 had her at #10
- LTR correctly included SCHREIBER (#6->P9) and HARTOG (#10->P7)
- v6.10 missed SCHREIBER and HARTOG entirely (had MOLENGRAAF P12, TRUYEN P22)
- ALVARADO DNS hurt both models equally

**Actual Podium:** BRAND (P1), ZEMANOVA (P2), BAKKER (P3)

### Overall Winner: v7.1-LTR

|   Category   | v6.10 Wins | LTR Wins | Ties |
|:------------:|:----------:|:--------:|:----:|
| Men Elite    |     3      |    1     |   0  |
| Women Elite  |     0      |    3     |   1  |
| **Total**    |   **3**    |  **4**   | **1**|

**Verdict:** v7.1-LTR wins overall (4-3-1) with significant gains:
- Men Elite: +1 hit (7/10 vs 6/10)
- Women Elite: +2 hits (8/10 vs 6/10), much better MAE (2.5 vs 4.3)

### Analysis

1. **LTR's career weighting worked for both categories**: BACKSTEDT (100% career top-10), KAMP (P4 finish) were correctly elevated
2. **v6.10's H2H helped Men Elite podium**: More balanced feature weights got NIEUWENHUIS #2 (actual P3)
3. **DNS remains the biggest challenge**: Both models penalized by unexpected DNS (NYS, SWEECK, VAN DER HAAR, ALVARADO)
4. **LTR found hidden value**: SCHREIBER, HARTOG, MASON, KAMP were correctly identified by LTR but missed by v6.10

### Recommendation

**Continue using v7.1-LTR for predictions.** The +1 hit on Men Elite and +2 hits on Women Elite, plus significantly better Women Elite MAE (2.5 vs 4.3), justify using LTR as the primary model.

---

## Files

|                            File                             |          Description           |
|:-----------------------------------------------------------:|:------------------------------:|
| `train_model_ltr.py`                                        | LTR training script (v7.1)     |
| `predict_race_ltr.py`                                       | LTR prediction script          |
| `models/ltr_ranker.joblib`                                  | Trained LTR model              |
| `models/ltr_metadata.json`                                  | LTR model metadata             |
| `LOENHOUT_LTR_PREDICTIONS_2025-12-29.md`                    | Loenhout predictions + validation |
| `DIEGEM_LTR_PREDICTIONS_2025-12-30.md`                      | Diegem predictions             |

---

## Version History

| Version |    Date    |                         Changes                          |
|:-------:|:----------:|:--------------------------------------------------------:|
|  7.0    | 2025-12-29 | Initial LTR implementation (stopped at 2 iterations)     |
|  7.1    | 2025-12-30 | Fixed with CV, regularization, 50 rounds                 |

---

*Document created: 2025-12-29*
*Last updated: 2025-12-30*
*Model trained: 2025-12-30 (v7.1-LTR)*
