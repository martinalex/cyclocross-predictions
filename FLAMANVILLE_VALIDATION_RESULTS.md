# 🇫🇷 Flamanville Validation Results (Nov 30, 2025)

## Executive Summary

VeloPredict v2 showed **mixed results** at Flamanville:
- **Women Elite:** 90% accuracy (maintained from Tabor)
- **Men Elite:** 70% accuracy (dropped 20% from Tabor)
- **Overall precision:** Still needs improvement (45-54%)

**Key Finding:** v2 improvements (confidence threshold + DNS filter) improved precision but accuracy regressed for Men.

---

## 📊 Overall Performance

| Category | Top-10 Accuracy | Precision | Podium Accuracy | vs Tabor (v1) |
|----------|----------------|-----------|-----------------|---------------|
| **Men Elite** | 70.0% (7/10) | 53.8% (7/13) | 33.3% (1/3) | **-20.0%** ❌ |
| **Women Elite** | 90.0% (9/10) | 45.0% (9/20) | 33.3% (1/3) | **+0.0%** ✅ |
| **Combined** | 80.0% (16/20) | 48.5% (16/33) | 33.3% (2/6) | **-10.0%** |

### Comparison: v1 (Tabor) vs v2 (Flamanville)

| Metric | Tabor v1 | Flamanville v2 | Change | Goal |
|--------|----------|----------------|--------|------|
| **Predicted Top-10 count** | 19-24 | 13-20 | ✅ **Reduced** | 12-15 |
| **Precision** | 42-47% | 45-54% | ✅ **+3-7%** | 60% |
| **Top-10 Accuracy** | 90% | 70-90% | ⚠️ **Inconsistent** | 85-90% |
| **DNS in predictions** | 2 (podium) | 6 (Top-10) | ❌ **Worse** | 0 |

---

## 🚴 MEN ELITE DETAILED ANALYSIS

### ✅ Correct Predictions (7/10 = 70%)
1. NYS Thibau (P1) - ✓ Correctly called winner
2. VAN DER HAAR Lars (P2) - ✓ Correctly called podium
3. MASON Cameron (P3) - ✓ Correctly called podium
4. VANPUTTE Niels (P4) - ✓ **BUT name matching issue**
5. SWEECK Laurens (P5) - ✓
6. NIEUWENHUIS Joris (P6) - ✓ Predicted podium, finished 6th
7. MICHELS Jente (P8) - ✓
8. VERSTRYNGE Emiel (P9) - ✓

### ❌ Missed Predictions (3/10 = 30%)
1. **VANPUTTE Niels (P4)** - Name matching bug ("VANPUTTE" vs "VANDEPUTTE")
2. **VANHOURENHOUT Michael (P7)** - Model predicted DNS (only 1 race) but he started
3. **VAN DE PUTTE Victor (P10)** - Low confidence (38.8%), below 55% threshold

### ⚠️ False Positives (6/13 = 46%)
1. **MEEUSSEN Witse** - DNS (predicted 66.8%)
2. **VANTHOURENHOUT Michael** - DNS (predicted 69.0%, was flagged DNS risk but still included!)
3. **VANDEPUTTE Niels** - DNS (predicted 65.8%)
4. **AERTS Toon** - Finished P12 (predicted 57.7%)
5. **RONHAAR Pim** - Finished P29 (predicted 70.7% - **HUGE MISS**)
6. **WYSEURE Joran** - Finished P26 (predicted 57.4%)

### 🔍 Key Insights - Men Elite

**What Worked:**
- ✓ Correctly predicted winner (Nys) and Top-3
- ✓ 7 out of 13 predictions were correct (54% precision vs 47% at Tabor)

**What Failed:**
1. **DNS Filter Failure:** Flagged Vanthourenhout as DNS risk but still predicted him Top-10
2. **Name Matching Bug:** "VANPUTTE" vs "VANDEPUTTE" - missed obvious match
3. **Catastrophic Misses:** Ronhaar (70.7% → P29), Wyseure (57.4% → P26)
4. **3 DNS riders** in Top-10 predictions despite DNS filter

**Biggest Question:**
- **Why did Ronhaar finish P29?** 70.7% confidence suggests strong form, but massive underperformance
  - Possible: Mechanical? Crash? Illness?
  - Feature to add: "Race-day variance" or "reliability score"

---

## 🚴 WOMEN ELITE DETAILED ANALYSIS

### ✅ Correct Predictions (9/10 = 90%)
1. VAN ALPHEN Aniek (P1) - ✓ Correctly called winner
2. FOUQUENET Amandine (P2) - ✓
3. ALVARADO Ceylin del Carmen (P3) - ✓ **New rider with no history!**
4. VAN DER HEIJDEN Inge (P4) - ✓
5. BENTVELD Leonie (P5) - ✓
6. VAN ANROOIJ Shirin (P6) - ✓ **New rider with no history!**
7. NORBERT RIBEROLLE Marion (P7) - ✓
8. CLAUZEL Hélène (P8) - ✓
9. BAKKER Manon (P9) - ✓

### ❌ Missed Predictions (1/10 = 10%)
1. **MOORS Fleur (P10)** - Predicted 52.2% (below 55% threshold)

### ⚠️ False Positives (11/20 = 55%)
1. **EYEINGTON Joy Kacey** - DNS (new rider, predicted 86.3%)
2. **INGLIS Theodora Hope** - DNS (new rider, predicted 86.3% for podium!)
3. **SCHREIBER Marie** - DNS (predicted 60.9%)
4. **MOULIN Anaïs** - Finished P40 (new rider, predicted 86.3%)
5. **DRAKE Haf Ann Ffion** - Finished P18 (new rider, predicted 86.3%)
6. **BROUWERS Julie** - Finished P11 (predicted 83.3%)
7. **VERDONSCHOT Laura** - Finished P13 (predicted 78.5%)
8. **BETSEMA Denise** - Finished P12 (predicted 62.5%)
9. **CUSACK Lidia** - Finished P15 (predicted 78.4%)
10. **DESPREZ Lison** - Finished P25 (predicted 58.6%)
11. **WORST Annemarie** - DNF (predicted 78.3%)

### 🔍 Key Insights - Women Elite

**What Worked:**
- ✓ **90% accuracy maintained from Tabor**
- ✓ Correctly predicted winner (Van Alphen)
- ✓ **New riders performed well:** Alvarado (P3), Van Anrooij (P6) despite no history

**What Failed:**
1. **New Rider Default Problem:** 6 riders got 86.3% default probability
   - 2 performed well (Alvarado P3, Van Anrooij P6)
   - 4 were false positives (Inglis DNS, Moulin P40, Drake P18, Eyeington DNS)
2. **3 DNS riders** not flagged (Eyeington, Inglis, Schreiber)
3. **Precision still low:** 45% (9/20 correct) due to over-prediction

**Biggest Surprise:**
- **Alvarado & Van Anrooij** (no history) finished P3 and P6
  - Suggests: Need to incorporate "rider pedigree" beyond just race history
  - Could add: UCI ranking, team quality, age/experience proxies

---

## 🎯 ERROR ANALYSIS

### 1. Feature Failures

**What features failed to predict:**

| Issue | Failed Feature | Why It Failed | Potential Fix |
|-------|---------------|---------------|---------------|
| Ronhaar P29 | `top10_rate_career`, `recent_form` | Doesn't capture race-day events | Add "consistency" score, detect outlier risk |
| 6 DNS riders | `races_so_far`, `days_since_last_race` | Threshold too lenient (<2 races) | Stricter DNS filter: <3 races OR >14 days |
| New riders (6) | All features (no history) | Default probability too high (86.3%) | Lower default to 50%, require UCI ranking |
| Vanputte miss | Name matching | "VANPUTTE" vs "VANDEPUTTE" | Fuzzy string matching (Levenshtein distance) |

### 2. Unmodeled Factors

**What the model CAN'T predict:**

1. **Race-Day Events:**
   - Crashes (could explain Ronhaar?)
   - Mechanicals
   - Illness/injury on race day
   - Tactical decisions

2. **Course-Specific Factors:**
   - Course type (technical vs power)
   - Weather conditions (mud, cold)
   - Home advantage (missed at Tabor with Zemanová)

3. **Rider Motivation:**
   - Peaking for specific races
   - End-of-season fatigue
   - Training vs racing mode

### 3. Biggest Misses with Explanations

| Rider | Predicted | Actual | Confidence | Likely Reason |
|-------|-----------|--------|------------|---------------|
| **RONHAAR Pim** | Top-10 (70.7%) | P29 | HIGH | ⚠️ Crash/mechanical? Check race reports |
| **WYSEURE Joran** | Top-10 (57.4%) | P26 | MED | ⚠️ Bad day / strategic DNF? |
| **INGLIS Theodora** | Podium (80.9%) | DNS | HIGH | ❌ New rider default - no history |
| **MOULIN Anaïs** | Top-10 (86.3%) | P40 | HIGH | ❌ New rider default - wildly wrong |
| **DRAKE Haf Ann** | Top-10 (86.3%) | P18 | HIGH | ❌ New rider default - overpredicted |

**Action Items from Misses:**
1. Investigate Ronhaar race (crash? mechanical?)
2. Fix new rider defaults (86.3% → 50% or require UCI ranking)
3. Improve DNS detection (stricter thresholds)
4. Add fuzzy name matching for "VANPUTTE"/"VANDEPUTTE" cases

---

## 📈 Performance Metrics

### Brier Score Analysis

**Men Elite:**
- True positives: 7
- False positives: 6
- False negatives: 3
- Brier Score: ~0.28 (higher is worse)

**Women Elite:**
- True positives: 9
- False positives: 11
- False negatives: 1
- Brier Score: ~0.24

### Calibration Analysis

**Are probabilities calibrated?**

| Predicted Probability | Actual Success Rate | Calibrated? |
|----------------------|---------------------|-------------|
| 80-90% (new riders) | 33% (2/6) | ❌ **Overconfident** |
| 70-80% | 50% (4/8) | ⚠️ **Slightly over** |
| 60-70% | 64% (7/11) | ✅ **Good** |
| 55-60% | 50% (3/6) | ✅ **Reasonable** |

**Finding:** Model is overconfident for new riders (86.3% default) and high-confidence predictions (70%+).

**Fix:** Platt scaling or isotonic regression to calibrate probabilities.

---

## 🔧 v2 Improvements Assessment

### Did v2 Achieve Goals?

| Goal | Target | Actual | Result |
|------|--------|--------|--------|
| Reduce Top-10 count | 12-15 | 13-20 | ✅ **Partial** (men=13, women=20) |
| Improve precision | 60% | 45-54% | ❌ **Fell short** |
| Maintain accuracy | 85-90% | 70-90% | ⚠️ **Mixed** (men regressed) |
| Prevent DNS in podium | 0 | 1 (Inglis) | ❌ **Failed** |

### What Worked in v2:
1. ✅ Confidence threshold (55%) reduced false positives slightly
2. ✅ Prediction count more realistic (13-20 vs 19-24)
3. ✅ Women maintained 90% accuracy

### What Didn't Work in v2:
1. ❌ DNS filter still allowed 6 DNS riders through
2. ❌ Men accuracy dropped 20% (90% → 70%)
3. ❌ Precision only improved 3-7% (not 18% as hoped)
4. ❌ New rider defaults (86.3%) caused major false positives

---

## 🚀 NEXT STEPS (v3 Improvements)

### Priority 1: HIGH (Critical Fixes)

**1. Fix New Rider Defaults**
- **Current:** 86.3% Top-10 probability (way too high)
- **Fix:** Lower to 50% OR require UCI ranking data
- **Expected impact:** Reduce women false positives by ~5 riders

**2. Improve DNS Detection**
- **Current:** Flags if <2 races OR >21 days inactive
- **Fix:** Change to <3 races OR >14 days inactive
- **Expected impact:** Flag 3-6 more DNS risks per race

**3. Add Fuzzy Name Matching**
- **Current:** Exact match only (missed "VANPUTTE"/"VANDEPUTTE")
- **Fix:** Levenshtein distance ≤2 for matching
- **Expected impact:** Prevent 1-2 missed predictions per race

### Priority 2: MEDIUM (Model Improvements)

**4. Calibrate Probabilities**
- **Tool:** Platt scaling or isotonic regression
- **Goal:** Make 70% actually mean 70% success rate
- **Expected impact:** Better confidence intervals

**5. Add Course Type Feature**
- **Data needed:** Manual categorization (technical/power/mixed)
- **Why:** Riders perform differently on different courses
- **Expected impact:** +2-3% accuracy

**6. Add Consistency/Reliability Score**
- **Metric:** Variance in recent placements
- **Why:** Catch "Ronhaar moments" (high skill, high variance)
- **Expected impact:** Reduce catastrophic misses

### Priority 3: LOW (Nice to Have)

**7. Incorporate UCI Rankings for New Riders**
- **Source:** Nov 17, 2025 rankings (already downloaded)
- **Why:** Better than default 86.3%
- **Expected impact:** +5% precision for women

**8. Add Weather/Conditions Data**
- **Source:** Weather API or manual entry
- **Why:** Mud specialists vs dry-course riders
- **Expected impact:** +1-2% accuracy in extreme conditions

---

## 📊 DATA UPDATE PLAN

**Files to Add:**
1. `Results__UCI-World-Cup__Flamanville__Men-Elite__2025-11-30__Flamanville-FRANCE.csv` (Done ✓)
2. `Results__UCI-World-Cup__Flamanville__Women-Elite__2025-11-30__Flamanville-FRANCE.csv` (Done ✓)

**Pipeline Steps:**
1. Run `rebuild_data.py` to incorporate Flamanville results
2. Run `add_features.py` to update rolling features
3. Verify data quality (no NaN spikes, feature variance >0.01)
4. Check race count: 45 → 47 races (2 new from Flamanville)

**Expected Dataset Growth:**
- Current: 7,724 observations from 45 races
- After Flamanville: ~7,850 observations from 47 races (+126 observations)

---

## 🎯 MODEL RETRAIN CHECKLIST

**Before Retraining:**
- [ ] Add Flamanville results to data/results/
- [ ] Rebuild features with updated dataset
- [ ] Implement Priority 1 fixes (new rider defaults, DNS threshold)
- [ ] Add fuzzy name matching to validation

**Retraining Steps:**
1. Run `rebuild_data.py` (add 2 races)
2. Run `add_features.py` (update rolling features)
3. Modify `train_model_v2.py` → `train_model_v3.py` with fixes
4. Train v3 model with expanded dataset
5. Compare v3 vs v2 on holdout set

**Success Criteria for v3:**
- Top-10 accuracy: ≥85% (both genders)
- Precision: ≥60%
- DNS false positives: ≤2 per race
- No regressions vs v2

---

## 💼 LinkedIn Content Summary

**Honest Take for LinkedIn:**

> "My cyclocross prediction model just got a reality check. After 90% accuracy at Tabor, Flamanville showed mixed results:
>
> ✅ Women: 90% accuracy (maintained)
> ❌ Men: 70% accuracy (dropped 20%)
> ⚠️ Precision: 48% overall (still needs work)
>
> **Key learnings:**
> 1. New riders without history broke the model (86% default was too high)
> 2. DNS detection still needs work (6 riders didn't start)
> 3. Catastrophic misses (Ronhaar 70% confidence → P29) reveal unmodeled variance
>
> **Next iteration (v3):**
> - Lower new rider defaults
> - Stricter DNS filters
> - Add consistency/reliability scores
>
> This is what real ML looks like: iterate, fail, learn, improve.
>
> Full analysis: [link]"

**Engagement Hook:** "What would YOU add to predict race-day variance?"

---

## 📁 Files Referenced

**Predictions:**
- `data/clean/predictions_flamanville_men_elite.csv`
- `data/clean/predictions_flamanville_women_elite.csv`

**Results:**
- `data/results/Results__UCI-World-Cup__Flamanville__Men-Elite__2025-11-30__Flamanville-FRANCE.csv`
- `data/results/Results__UCI-World-Cup__Flamanville__Women-Elite__2025-11-30__Flamanville-FRANCE.csv`

**Validation:**
- This file: `FLAMANVILLE_VALIDATION_RESULTS.md`

---

**Bottom Line:** v2 showed improvement in precision (+6%) but accuracy regressed for Men (-20%). Root causes: new rider defaults too high, DNS filter too lenient, name matching bugs, and unmodeled race-day variance. v3 must address these before next race.

**Confidence Level:** Medium for Top-10, Low for podium, Critical need for new rider handling.

**Portfolio Status:** ✅ Shows iterative improvement and honest evaluation - valuable for consulting interviews.
