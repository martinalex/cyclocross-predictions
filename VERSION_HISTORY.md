# VeloPredict: Complete Version History

**Project Start:** November 2025
**Current Version:** v6.13
**Total Iterations:** 1 migration + 6 major versions + multiple refinements

---

## 🔄 Step Zero: The Migration (Nov 16-20, 2025)

### Context: Jupyter Notebooks → Production Code

**Starting Point:** 5 notebooks, 9 races scraped, broken predictions

**The Brutal Assessment:**
- **Critical flaw:** Model predicted identical finish (10.78) for every rider
- **Broken parser:** 02_extract_startlists.ipynb failed on all 8 PDFs
- **Amateur signals:** Hardcoded paths, no config, no tests, no README
- **Verdict:** "Would not pass McKinsey screen" - 3/10

### What Was Wrong

**The Model Problem:**
```python
# All riders had NaN features (no race history)
# Filled NaN with median (25)
# RandomForest learned: "everyone is median"
# Result: Predicted 10.78 for every single rider
MAE: 0.072  # Looked good but meaningless - no variance!
```

**The Code Quality Issues:**
1. **300+ lines of unused code** - Complex circuit detection that never worked
2. **No error handling** - Crashes on bad PDFs
3. **Hardcoded everything** - `Path("data")` instead of config
4. **Duplicate logic** - Same parse functions copy-pasted across notebooks
5. **No validation** - Never checked if predictions made sense

**The Data Problem:**
- Only 9 races scraped (need 30-50 minimum)
- No startlist data (parser completely broken)
- Can't calculate accuracy (no way to validate)

### The 2-Week Sprint Fix (Nov 20 - Dec 4)

**Week 1: Fix the Foundation**
- ✅ **Days 1-2:** Scraped 36 more races (9 → 45 total)
- ✅ **Days 3-4:** Fixed model with real features:
  - Added UCI rank as primary signal
  - Team tier (top teams vs others)
  - Form features (avg last 3, best last 5)
  - Result: Different predictions per rider!
- ✅ **Days 5-7:** Built validation framework
  - Chronological train/test split
  - Top-10 accuracy metric (not MAE)
  - Beat UCI baseline test

**Week 2: Production Refactor**
- ✅ **Days 8-10:** Created clean architecture
  ```
  OLD: 5 notebooks, all logic duplicated
  NEW:
    /src/data/ - scrapers, cleaners, features
    /src/models/ - training, prediction
    config.py - all paths and hyperparameters
    requirements.txt - reproducible environment
  ```
- ✅ **Days 11-14:** Professional polish
  - README with problem statement + results
  - Validation scripts (not notebooks)
  - Clean git history
  - Documentation

### Migration Results

| Metric | Before Migration | After Migration | Change |
|--------|-----------------|-----------------|--------|
| **Races** | 9 | 45 | +400% |
| **Observations** | 1,460 | 7,724 | +429% |
| **Model Predictions** | 1 (everyone 10.78) | Variable | ✅ Fixed |
| **Top-10 Accuracy** | 0% (not calculated) | 80.2% | ✅ Working |
| **Code Structure** | 5 notebooks | Modular /src | ✅ Production |
| **Portfolio Ready** | 3/10 | 7/10 | ✅ Interview-worthy |

### Key Lessons from Migration

**1. Jupyter is for Exploration, Not Production**
- Notebooks good for: EDA, experiments, visualizations
- Notebooks bad for: Reproducible pipelines, testing, deployment
- **Takeaway:** Build in notebooks, ship as modules

**2. "Working" ≠ Producing Output**
- Model had 0.072 MAE (looked good)
- But predicted same value for everyone (broken)
- **Takeaway:** Always validate predictions make sense

**3. Amateur Signals Kill Credibility**
- Hardcoded paths → "Not production-ready"
- No README → "Doesn't understand communication"
- No tests → "Doesn't value quality"
- **Takeaway:** Professional presentation matters

**4. Feature Engineering > Model Complexity**
- Initial model: RandomForest with NaN features = useless
- Fixed model: Same RandomForest + UCI rank = 80% accuracy
- **Takeaway:** Better features beat fancier algorithms

**5. Validation Framework is Non-Negotiable**
- Can't improve what you don't measure
- Need chronological split (not random)
- Need business metrics (Top-10, not MAE)
- **Takeaway:** Build validation before optimizing

### What Got Cut (Deferred to Future)

**Abandoned Features:**
- ❌ PDF startlist parser (too brittle, manual CSVs work)
- ❌ Weather data (complex, low signal)
- ❌ Course profiles (hard to get)
- ❌ Exact placement prediction (focused on Top-10 instead)

**Why This Was Right:**
- Ship working demo in 14 days
- Validate user interest before overengineering
- 80% Top-10 accuracy > 20% exact placement

### The Portfolio Impact

**Before Migration (Nov 16):**
> "I have some Jupyter notebooks that scrape race data"
> Interviewer: "Can you show me the code?"
> You: 😬 (broken, messy, no structure)

**After Migration (Nov 20):**
> "I built a cyclocross prediction system - 80% Top-10 accuracy on 45 races"
> Interviewer: "How does it work?"
> You: ✅ (clean repo, documented, working demo)

### Files from Migration Period

**Created:**
- `config.py` - Centralized configuration
- `requirements.txt` - Python 3.12, pandas, sklearn
- `README.md` - Professional documentation
- `/src` modules - Production code structure
- `train_model_v2.py` - Reproducible training
- `predict_race.py` - Inference script

**Deleted:**
- 02_extract_startlists.ipynb (300+ lines of broken code)
- Duplicate parsing functions (consolidated to /src/data)
- Hardcoded magic numbers (moved to config)

### Why This Matters for Content

**The Story Arc:**
1. **Honest starting point:** "My model predicted the same rank for everyone"
2. **Root cause analysis:** "All features were NaN → learned median"
3. **Systematic fix:** "Added UCI rank, rebuilt validation"
4. **Professional delivery:** "Refactored to production code"

**LinkedIn Post Angle:**
> "I spent 2 weeks migrating my cyclocross AI from Jupyter notebooks to production code. Here's what broke, what I learned, and why feature engineering > model complexity..."

**Interview Story:**
> "When I first built this in notebooks, the model looked like it worked (low MAE) but actually predicted the same value for everyone. I had to rebuild the feature engineering, add proper validation, and refactor to production modules. That migration taught me more about ML engineering than any tutorial."

---

## 📈 Evolution Overview

| Version | Date | Key Innovation | Training Accuracy | Live Validation | Status |
|---------|------|----------------|-------------------|-----------------|--------|
| **v1** | Nov 23 | Baseline Random Forest | 80.2% | 90% (Tabor) | Superseded |
| **v2** | Nov 25 | Confidence threshold + DNS filter | 80.2% | 80% (Flamanville) | Superseded |
| **v3** | Nov 30 | Higher default threshold (50) | 79.0% | Not tested | Superseded |
| **v4** | Dec 1 | UCI-based inference | 78.8% | Not tested | Superseded |
| **v5** | Dec 2 | **Head-to-Head (H2H) feature** | 76.9% | r=0.773/0.867 (Flamanville) | Superseded |
| **v6** | Dec 3 | **New Rider Penalty** | 77.6% | 100% recall (Sardinia) | Superseded |
| **v6.1** | Dec 7 | Aligned tables + metrics explanation | 83.5% | Sardinia validated | Superseded |
| **v6.2** | Dec 13 | **No DNS Exclusion** | 83.4% | 87.5% precision (Kortrijk) | Superseded |
| **v6.3** | Dec 14 | **+Namur Results** | 82.6% | 75% precision (Namur) | Superseded |
| **v6.4** | Dec 17 | **Robust Feature Extraction** | 82.6% | 75% precision (Antwerpen) | Superseded |
| **v6.5** | Dec 21 | **+Antwerpen Results** | 82.0% | Koksijde validated | Superseded |
| **v6.6** | Dec 21 | **+Koksijde Results** | 81.1% | Hofstade validated | Superseded |
| **v6.7** | Dec 22 | **+Hofstade Results** | 81.2% | Heusden-Zolder validated | Superseded |
| **v6.8** | Dec 26 | **+Heusden-Zolder Results** | 81.0% | Gavere validated | Superseded |
| **v6.9** | Dec 27 | **+Gavere Results** | 80.1% | Pending | Superseded |
| **v6.10** | Dec 28 | **+Dendermonde Results** | 80.5% | Pending | Superseded |
| **v6.11** | Dec 29 | **+Azencross-Loenhout Results** | 81.0% | Pending | Superseded |
| **v6.12** | Dec 29 | **+Azencross-Loenhout Results** | 79.2% | Pending | Superseded |
| **v6.13** | Dec 30 | **+Diegem Results** | 79.6% | Pending | **Current** |

---

## 🚀 Version 1: The Baseline (Nov 23, 2025)

### Context
First production model built in 2 days. Trained on 45 races (7,724 observations).

### Key Features
- Random Forest Classifier (300 trees, depth 15)
- 15 engineered features:
  - UCI points normalized
  - Recent form (avg last 3, best last 5)
  - Career success rates
  - Team tier, points tier
- Chronological train/test split (80/20)

### Model Configuration
```python
# Default values for new riders
MEDIAN_PLACE_DEFAULT = 25
confidence_threshold = 0.50  # 50% to predict Top-10
enable_dns_filter = False
```

### Training Performance
- Top-10 Accuracy: **80.2%**
- Top-3 Accuracy: **91.5%**
- Dataset: 7,724 observations, 45 races

### Live Validation: Tabor UCI World Cup (Nov 23)
| Category | Top-10 Accuracy | Precision | Podium | Predictions |
|----------|----------------|-----------|--------|-------------|
| Men Elite | 90.0% (9/10) | 47.4% (9/19) | 1/3 | 19 riders |
| Women Elite | 90.0% (9/10) | 37.5% (9/24) | 0/3 | 24 riders |
| **COMBINED** | **90.0% (18/20)** | **41.9% (18/43)** | **1/6** | **43 riders** |

### Key Insights
✅ **What worked:**
- Exceeded training accuracy (+9.8%)
- Correctly predicted all race favorites
- 90% Top-10 detection rate

❌ **What didn't work:**
- Low precision (too many predictions)
- Terrible podium accuracy (16.7%)
- Predicted 43 riders for 20 Top-10 spots

### Why v1 Failed
**Root cause:** Over-predicting. Model was too generous with Top-10 predictions.

**Example:** Predicted Ulík and Groenendaal for podium - both didn't start (DNS).

---

## 🎯 Version 2: Precision Improvements (Nov 25, 2025)

### Context
Post-Tabor analysis identified precision problem. Implemented 3 "quick wins."

### Changes from v1

**1. Confidence Threshold Increase**
```python
# v1: confidence_threshold = 0.50
# v2: confidence_threshold = 0.55  (+5%)
```
Expected: Reduce false positives from 25 → 15 per race

**2. DNS (Did Not Start) Filter**
```python
# Flag riders unlikely to start
if days_since_last_race > 21:
    dns_risk = True
elif races_so_far < 2:
    dns_risk = True
```
Expected: Prevent embarrassing DNS predictions

**3. Updated UCI Rankings**
- Would use Nov 17, 2025 UCI rankings (when provided)
- Expected +2-3% accuracy improvement

### Model Configuration
```python
MEDIAN_PLACE_DEFAULT = 25  # Unchanged from v1
confidence_threshold = 0.55  # Increased
enable_dns_filter = True     # NEW
```

### Training Performance
- Top-10 Accuracy: **80.2%** (same as v1)
- Model files unchanged (no retraining)
- Only prediction thresholds modified

### Live Validation: Flamanville UCI World Cup (Nov 30)
| Category | Top-10 Accuracy | Precision | Podium | Predictions |
|----------|----------------|-----------|--------|-------------|
| Men Elite | 70.0% (7/10) | 53.8% (7/13) | 1/3 | 13 riders |
| Women Elite | 90.0% (9/10) | 45.0% (9/20) | 1/3 | 20 riders |
| **COMBINED** | **80.0% (16/20)** | **48.5% (16/33)** | **2/6** | **33 riders** |

### Performance vs v1
| Metric | v1 (Tabor) | v2 (Flamanville) | Change |
|--------|-----------|-----------------|--------|
| Accuracy | 90% | 80% | **-10%** ❌ |
| Precision | 42% | 48% | **+6%** ✅ |
| Podium | 17% | 33% | **+16%** ✅ |
| Predictions | 43 | 33 | **-10** ✅ |

### Key Insights
✅ **What worked:**
- Precision improved (+6%)
- Fewer predictions (43 → 33)
- Podium accuracy doubled

❌ **What didn't work:**
- Accuracy dropped 10% (Men Elite catastrophic)
- DNS filter failed (still predicted 6 DNS riders)
- New riders got 86.3% Top-10 probability (way too high)

### Critical Bug Discovered
**New Rider Over-Confidence:**
```python
# 6 new riders at Flamanville (Women Elite)
features = {
    "avg_place_last3": 25,  # Default
    "uci_points_normalized": 0.1
}
# Result: 86.3% Top-10 probability → 6 false positives
```

**Catastrophic Miss:**
- Ronhaar: 70.7% confidence → finished P29
- Model missed race-day variance entirely

---

## 🔧 Version 3: Conservative Defaults (Nov 30, 2025)

### Context
Flamanville validation revealed new rider default (25) was too optimistic. Emergency fix.

### Changes from v2

**1. Higher Default Place Value**
```python
# v2: MEDIAN_PLACE_DEFAULT = 25 (median)
# v3: MEDIAN_PLACE_DEFAULT = 50 (75th percentile)

# Impact on new riders:
# v2: 86.3% Top-10 probability
# v3: ~50% Top-10 probability (more conservative)
```

**2. Expanded Training Data**
- Added Flamanville Men + Women results
- **7,724 → 7,793 observations** (+69)
- **45 → 47 races** (+2)

### Model Configuration
```python
MEDIAN_PLACE_DEFAULT = 50    # Increased from 25
confidence_threshold = 0.55  # Unchanged
enable_dns_filter = True     # Unchanged (still buggy)
```

### Training Performance
- Top-10 Accuracy: **79.0%** (-1.2% from v2)
- Top-3 Accuracy: **91.5%** (unchanged)
- AUC-ROC: **0.818** (new metric tracked)

### Expected Live Performance
| Metric | v2 Actual | v3 Expected |
|--------|----------|-------------|
| Accuracy | 80% | 75-80% |
| Precision | 48% | **55-60%** (+7-12%) |
| New Rider FP | 6 | **3-4** (-50%) |
| Predictions | 33 | **25-30** |

### Key Insights
✅ **What should work:**
- Lower new rider over-confidence
- Fewer false positives overall
- More selective predictions

❌ **What still won't work:**
- DNS filter bugs (unaddressed)
- Name matching issues (VANPUTTE vs VANDEPUTTE)
- Podium ordering (no improvements)
- Race-day variance (crashes, weather)

### Problem with v3
**Generic percentile approach still flawed:**
- All new riders get same default (50) regardless of UCI ranking
- Elite rider with no history? Default 50.
- Weak rider with no history? Also default 50.
- **Missing opportunity to use UCI ranking signal!**

---

## 🎯 Version 4: UCI-Based Inference (Dec 1, 2025) ⭐ CURRENT

### Context
User insight: "What if we weight defaults by UCI ranking instead of using generic percentiles?"

This became the **flagship improvement** - using regression to align features.

### The Core Innovation

**Discovery:**
```python
# Analyzed 3,906 Elite race observations
# Found strong correlation between UCI points and place

Linear Regression: place = 9.31 + 51.36 × uci_normalized
R² = 0.158 (15.8% variance explained)
P-value < 0.001 (highly significant)
Correlation = 0.398 (moderate positive)
```

**Key insight about UCI points:**
- "Carried Points" are INVERTED (lower = better, like golf)
- Strong riders: Low carried points (125) → low normalized (0.17)
- Weak riders: High carried points (450) → high normalized (0.60)

### Changes from v3

**1. UCI-Based Place Inference**
```python
# v3: All new riders get default = 50
# v4: Infer from UCI ranking

if uci_normalized > 0:
    inferred_place = 9.31 + 51.36 × uci_normalized
    inferred_place = clip(inferred_place, 5, 70)
else:
    inferred_place = 50  # Only if truly unknown

# Examples:
# Strong rider (UCI=0.17) → place=18.0 → 69.7% Top-10 chance
# Weak rider (UCI=0.60) → place=40.1 → 6.1% Top-10 chance
```

**2. Feature Alignment**
```python
# OLD (v3): Features contradict each other
features = {
    "uci_normalized": 0.60,  # Weak rider
    "avg_place_last3": 50,   # Generic average
}
# Model confused: "Weak UCI but okay form?"

# NEW (v4): Features align
features = {
    "uci_normalized": 0.60,  # Weak rider
    "avg_place_last3": 40.1, # Inferred weak form
}
# Model clear: "Weak UCI + weak form → Top-10 unlikely"
```

### Model Configuration
```python
UCI_PLACE_INTERCEPT = 9.3082  # NEW
UCI_PLACE_SLOPE = 51.3604      # NEW
MEDIAN_PLACE_DEFAULT = 50      # Fallback only
confidence_threshold = 0.55
enable_dns_filter = True
```

### Training Performance
- Top-10 Accuracy: **78.8%** (-0.2% from v3)
- Top-3 Accuracy: **91.1%** (-0.4% from v3)
- AUC-ROC: **0.820** (+0.002 from v3) ✅
- Recall: **67%** (+1% from v3) ✅
- **1,411 observations** now use UCI-inferred defaults

### Expected Live Performance
| Metric | v3 Expected | v4 Expected | Improvement |
|--------|------------|-------------|-------------|
| Accuracy | 75-80% | 75-80% | Maintain |
| Precision | 55-60% | **60-65%** | **+5-10%** |
| New Rider FP | 3-4 | **1-2** | **-50%** |
| Predictions | 25-30 | **20-25** | More selective |

### Feature Importance Changes
| Feature | v3 | v4 | Change |
|---------|----|----|--------|
| avg_place_last3 | 14.9% | **17.6%** | +2.7% ✅ |
| best_place_last5 | 16.8% | **17.7%** | +0.9% ✅ |
| last_place | 8.0% | **9.7%** | +1.7% ✅ |
| uci_points_normalized | 12.1% | **8.1%** | -4.0% ✅ |

**Why this is good:**
- Place features absorbed UCI information (via inference)
- Model relies more on form features (now UCI-aligned)
- Features "talk to each other" instead of contradicting

### Why v4 is Superior

**1. Smarter Defaults**
- v1-v3: Generic percentile (25 or 50) for ALL new riders
- v4: Personalized based on UCI ranking

**2. Feature Consistency**
- v1-v3: UCI says "weak" but form says "average" → confusion
- v4: UCI says "weak" AND form says "weak" → clarity

**3. Data-Driven**
- v1-v3: Arbitrary threshold choices
- v4: Linear regression on 3,906 observations

**4. Handles Both Extremes**
- Strong unknown rider (ALVARADO): Gets appropriate confidence boost
- Weak unknown rider: Gets filtered out

### Files Modified
```
config.py              - Added UCI regression coefficients
predict_race.py        - UCI-based inference for new riders
train_model_v2.py      - UCI-based NaN filling during training
models/*.joblib        - Retrained with UCI inference
```

### Documentation Created
```
V4_UCI_INFERENCE_RESULTS.md    - Technical writeup
UCI_POINTS_EXPLAINED.md        - Conceptual explanation
DOCUMENTATION_FIXES_SUMMARY.md - Clarification notes
analyze_uci_place_relationship.py - Regression analysis
```

---

## 🥊 Version 5: Head-to-Head Feature (Dec 2, 2025)

### Context
User insight: "Who a rider beats matters more than just their average finish. Let's add head-to-head history."

This became the **most predictive single feature** - historical win rates between specific rider pairs.

### The Core Innovation

**Discovery:**
```python
# Built pairwise H2H matrix from 47 races
# For each race, compared every pair of riders in same category
# Tracked: wins, total races together

# Example: Eli Iserbyt vs Laurens Sweeck
# Result: 67% win rate over 15 races → strong signal
```

**Why H2H is Powerful:**
- UCI ranking is static (updates weekly)
- H2H is specific to opponent matchups
- Captures style matchups (mud specialists, sprinters)
- Accounts for psychological edge

### The Head-to-Head Module

**New file:** `head_to_head.py`
```python
class HeadToHeadMatrix:
    """Builds and queries head-to-head records between riders."""

    def build_from_results(self, results_df, category_filter="Elite"):
        """Build pairwise win records from historical results."""
        # For each race, compare all rider pairs
        # Track wins/total for each matchup

    def get_win_rate(self, rider1, rider2) -> float:
        """Get rider1's win rate against rider2."""

    def get_field_h2h_score(self, rider, field) -> dict:
        """Calculate rider's avg win rate vs specific field."""
        # Returns: h2h_score, known_opponents, confidence
```

**Field-Adjusted Score:**
```python
# For a rider vs 10 opponents in field:
# - 6 have H2H data (known_opponents=6)
# - Average win rate vs those 6 = 0.72
# - Confidence = 6/10 = 60%
# - h2h_field_score = 0.72

# High H2H + high confidence = strong prediction
# Low H2H + high confidence = strong anti-prediction
# Any H2H + low confidence = uncertain
```

### Changes from v4

**1. New Feature: h2h_field_score**
```python
# Added to config.py NUMERIC_FEATURES
NUMERIC_FEATURES = [
    ...
    "h2h_field_score",  # Head-to-head win rate against race field
]

# Added to FILL_VALUES
FILL_VALUES = {
    ...
    "h2h_field_score": 0.5,  # Neutral H2H for unknown matchups
}
```

**2. Feature Engineering Pipeline**
```python
# update_results.py now calculates H2H features
# For each rider-race:
# 1. Get field of opponents from same race
# 2. Calculate avg H2H score vs field
# 3. Store h2h_field_score (0-1)
```

**3. Prediction Pipeline**
```python
# predict_race.py now uses H2H
# For each rider in startlist:
# 1. Load H2H matrix singleton
# 2. Calculate vs-field score against actual opponents
# 3. Include in feature vector for prediction
```

### Model Configuration
```python
NUMERIC_FEATURES = [
    ...
    "h2h_field_score",  # NEW: win rate vs field
]
FILL_VALUES = {
    ...
    "h2h_field_score": 0.5,  # Neutral default
}
```

### Training Performance
- Top-10 Accuracy: **76.9%** (-1.9% from v4)
- AUC-ROC: **0.830** (+0.010 from v4) ✅
- Dataset: **8,188 observations, 49 races**
- **H2H = #1 Feature at 21.4% importance!**

### Feature Importance (v5)
| Rank | Feature | Importance | Change from v4 |
|------|---------|------------|----------------|
| 1 | **h2h_field_score** | **21.4%** | NEW |
| 2 | avg_place_last3 | 13.0% | -4.6% |
| 3 | top10_rate_career | 12.9% | +3.2% |
| 4 | best_place_last5 | 12.7% | -5.0% |
| 5 | last_place | 9.4% | -0.3% |

**Why accuracy dropped but AUC improved:**
- H2H shifts probability distributions
- Model less "confident" but better calibrated
- AUC measures ranking ability (up!)
- Accuracy measures threshold (more conservative)

### Live Validation: Flamanville Retro-Analysis

Applied v5 H2H predictions to Flamanville results:

**Men Elite:**
```
H2H Correlation with actual finish: r = 0.773
Strong signal! H2H score correlates with placement
```

**Women Elite:**
```
H2H Correlation with actual finish: r = 0.867
Even stronger! H2H highly predictive for women
```

### Key Insights

✅ **What worked:**
- H2H became #1 feature (21.4% importance)
- Strong correlation with actual results (r=0.77-0.87)
- Field-adjusted predictions (knows the actual opponents)
- Captures matchup-specific dynamics

❌ **What still didn't work:**
- New riders still get inflated predictions (no H2H data)
- H2H confidence often low for less-raced riders
- Accuracy technically decreased (but ranking improved)

### Files Created/Modified
```
NEW: head_to_head.py           - H2H matrix class and functions
MOD: config.py                 - Added h2h_field_score to features
MOD: update_results.py         - Calculate H2H during feature engineering
MOD: predict_race.py           - Use H2H in prediction pipeline
MOD: train_model_v2.py         - Include H2H in training
MOD: app/demo.py               - Display H2H scores in Streamlit
```

### The Breakthrough Insight

**Before v5:**
> "This rider averages 8th place, so ~60% Top-10 chance"

**After v5:**
> "This rider averages 8th place, AND beats 72% of this specific field → 75% Top-10 chance"

The model now knows WHO is racing, not just how good the rider is in general.

---

## 🆕 Version 6: New Rider Penalty (Dec 3, 2025) ⭐ CURRENT

### Context
User identified critical bug: New riders (FOLCARELLI at 84.5%, PERUTA at 70.8%) getting inflated predictions despite being UCI rank 115 and 173 respectively.

**The Problem:**
```python
# FOLCARELLI Antonio - Men Elite
# - UCI rank: 115 (uci_normalized ≈ 0.15)
# - No race history in dataset
# - No H2H data (new rider)
# - v5 prediction: 84.5% Top-10 ← WAY TOO HIGH!

# PERUTA Sara - Women Elite
# - UCI rank: 173 (uci_normalized ≈ 0.25)
# - No race history in dataset
# - No H2H data (new rider)
# - v5 prediction: 70.8% Top-10 ← WAY TOO HIGH!
```

### The Data Analysis

**Investigated new rider performance:**
```python
# Training data analysis (8,188 observations):

Known riders (have history):
  - Top-10 rate: 23%
  - Count: 7,518 observations

New riders (no history):
  - Top-10 rate: 8%
  - Count: 670 observations

# New riders are 3x LESS likely to finish Top-10!
```

**Even strong new riders underperform:**
```python
# New riders with UCI norm ≤ 0.2 (top ~200 ranking):
  - Expected: 69.7% Top-10 (based on UCI-place regression)
  - Actual: 38% Top-10
  - Gap: 31.7 percentage points!

# UCI ranking alone doesn't capture:
# - Unfamiliarity with CX conditions
# - Lack of race fitness
# - Unknown opponents
# - Mental pressure
```

### The Solution: Hybrid Approach

**Three options were considered:**

1. **New Rider Discount (hardcoded)** - Quick fix, 40% reduction
2. **is_new_rider Feature (model-based)** - Let model learn penalty ← CHOSEN
3. **Pessimistic Defaults** - Lower inferred values for new riders

**Implemented Option 2 + Hybrid:**

**Step 1: Add is_new_rider feature**
```python
# update_results.py
combined["is_new_rider"] = (combined["races_so_far"] == 0).astype(int)
# Result: 8.0% of observations are new riders

# config.py - Added to features
NUMERIC_FEATURES = [
    ...
    "is_new_rider"  # Flag for riders with no history
]

FILL_VALUES = {
    ...
    "is_new_rider": 0  # Default to known rider
}
```

**Step 2: Retrain model**
```python
# Result: is_new_rider got only 0.23% importance
# The model didn't learn a strong penalty
# Because: inferred features looked "reasonable" for new riders
```

**Step 3: Add explicit discount (hybrid)**
```python
# predict_race.py lines 392-398
# v6: Apply new rider discount
# Data shows: new riders with UCI norm ≤0.2 have 38% top-10 rate, not 80%+
if status == "new_rider":
    NEW_RIDER_DISCOUNT = 0.5  # Reduce predictions by 50%
    top10_prob = top10_prob * NEW_RIDER_DISCOUNT
    top3_prob = top3_prob * NEW_RIDER_DISCOUNT
```

### Why Hybrid Approach?

**Pure model-based failed because:**
1. is_new_rider only got 0.23% feature importance
2. Model relies on inferred features (avg_place, best_place, etc.)
3. UCI-based inference makes new riders "look reasonable"
4. Model can't learn: "even if features look good, new = uncertain"

**Hybrid works because:**
1. Model feature captures some signal (0.23%)
2. Explicit discount addresses the 38% vs 69.7% gap
3. 50% discount is data-backed: 38% / 69.7% ≈ 0.55
4. Applied only to genuinely new riders (status = "new_rider")

### Changes from v5

**1. New Feature: is_new_rider**
```python
# config.py
NUMERIC_FEATURES = [
    ...
    "is_new_rider"  # 1 if first race in dataset, 0 otherwise
]

# update_results.py
combined["is_new_rider"] = (combined["races_so_far"] == 0).astype(int)
```

**2. Prediction Discount**
```python
# predict_race.py
# After model prediction:
if status == "new_rider":
    NEW_RIDER_DISCOUNT = 0.5
    top10_prob = top10_prob * NEW_RIDER_DISCOUNT
    top3_prob = top3_prob * NEW_RIDER_DISCOUNT
```

**3. Rider Status Tracking**
```python
# predict_race.py now tracks three statuses:
# - "found": Rider in dataset with history
# - "new_rider": New rider, features inferred from UCI
# - "not_found": Name not matched (fuzzy match failed)
```

### Model Configuration
```python
NUMERIC_FEATURES = [
    ...
    "h2h_field_score",  # v5
    "is_new_rider"      # v6 NEW
]

FILL_VALUES = {
    ...
    "h2h_field_score": 0.5,
    "is_new_rider": 0
}

# Prediction-time discount
NEW_RIDER_DISCOUNT = 0.5  # 50% reduction for new riders
```

### Training Performance
- Top-10 Accuracy: **77.6%** (+0.7% from v5) ✅
- AUC-ROC: **0.835** (+0.005 from v5) ✅
- Dataset: **8,357 observations, 50 races**
- is_new_rider importance: 0.23%
- H2H still #1 at **22.5%**

### Feature Importance (v6)
| Rank | Feature | Importance | Change from v5 |
|------|---------|------------|----------------|
| 1 | h2h_field_score | **22.5%** | +1.1% |
| 2 | avg_place_last3 | 12.8% | -0.2% |
| 3 | top10_rate_career | 12.5% | -0.4% |
| 4 | best_place_last5 | 12.3% | -0.4% |
| 5 | last_place | 9.2% | -0.2% |
| ... | is_new_rider | 0.23% | NEW |

### Results: Before vs After

**FOLCARELLI Antonio (Men Elite, UCI rank 115):**
| Metric | v5 | v6 | Change |
|--------|-----|-----|--------|
| Top-10 Prob | 84.5% | **40.2%** | **-44.3%** |
| Top-3 Prob | 37.2% | **18.6%** | **-18.6%** |

**PERUTA Sara (Women Elite, UCI rank 173):**
| Metric | v5 | v6 | Change |
|--------|-----|-----|--------|
| Top-10 Prob | 70.8% | **37.9%** | **-32.9%** |
| Top-3 Prob | 24.1% | **12.1%** | **-12.0%** |

### Why This Matters

**The Data Behind 50% Discount:**
```python
# Strong new riders (UCI norm ≤ 0.2):
# - UCI-inferred expectation: 69.7% Top-10
# - Actual historical rate: 38% Top-10
# - Ratio: 38% / 69.7% = 0.55 ≈ 50% discount

# The discount is NOT arbitrary - it's data-driven!
```

**v6 Now Correctly Predicts:**
- Strong new riders: ~40% Top-10 (not 80%+)
- Weak new riders: ~15% Top-10 (not 50%+)
- Known riders: Unchanged (no discount)

### Files Modified
```
MOD: config.py          - Added is_new_rider to features
MOD: update_results.py  - Calculate is_new_rider flag
MOD: train_model_v2.py  - Include is_new_rider in training
MOD: predict_race.py    - Add status tracking + 50% discount
MOD: app/demo.py        - Updated version to v6
```

### Key Insights

✅ **What worked:**
- New riders now get realistic predictions
- Discount is data-backed (38% vs 69.7% gap)
- Hybrid approach captures what model couldn't learn
- Accuracy improved (+0.7%) with more conservative predictions

⚠️ **Trade-offs:**
- Hardcoded discount (could be learned with more data)
- May under-predict exceptional debutants
- 50% discount is approximate (could be tuned)

### The Learning

**Pure ML isn't always enough:**
- Sometimes domain knowledge + data analysis beats model tuning
- "New rider uncertainty" is hard for RandomForest to learn
- Explicit rules can complement model predictions
- Always validate: does the prediction make sense?

---

## 📊 Version Comparison Summary

### Understanding the Metrics

Before diving into the numbers, here's what each metric actually tells you:

| Metric | Question It Answers | Why It Matters |
|--------|---------------------|----------------|
| **Accuracy** | "Of ALL riders, what % did we classify correctly?" | Overall model quality. Includes easy wins (correctly saying non-contenders won't podium). Can be misleading due to class imbalance—80% of riders don't finish Top-10, so a "predict nobody" model would still get 80% accuracy. |
| **Precision** | "When we predict Top-10, how often are we right?" | **Trust metric.** This is what users care about most. If precision is 75%, then 3 out of 4 predictions are correct. Low precision = too many false positives. |
| **Recall** | "Of actual Top-10 finishers, how many did we catch?" | **Coverage metric.** High recall = we didn't miss many winners. Low recall = we're too conservative or missing underdogs. |
| **AUC-ROC** | "How well does the model rank riders by probability?" | Measures if higher-probability riders actually perform better. 0.5 = random, 1.0 = perfect ranking. Good for comparing models. |

**Key Insight:** Training precision (~58%) is the baseline. Live validation precision (75-100%) beating this baseline means the model performs better on real UCI World Cup races than on average training data.

### Training Metrics

| Version | Accuracy   | Precision | AUC-ROC   | Observations | Innovation           |
|---------|------------|-----------|-----------|--------------|----------------------|
| v1      | 80.2%      | ~59%      | N/A       | 7,724        | Baseline             |
| v2      | 80.2%      | ~59%      | N/A       | 7,724        | Threshold only       |
| v3      | 79.0%      | ~59%      | 0.818     | 7,793        | Higher default       |
| v4      | 78.8%      | ~58%      | 0.820     | 7,793        | UCI inference        |
| v5      | 76.9%      | ~57%      | 0.830     | 8,188        | **H2H feature**      |
| v6      | 77.6%      | ~58%      | 0.835     | 8,357        | New rider penalty    |
| v6.2    | 83.4%      | ~60%      | 0.850     | 8,849        | No DNS exclusion     |
| v6.3    | 82.6%      | ~58%      | 0.833     | 8,950        | +Namur Results       |
| v6.5    | 82.0%      | ~58%      | 0.817     | 9,114        | +Antwerpen Results   |
| v6.6    | 81.1%      | ~58%      | 0.813     | 9,235        | +Koksijde Results        |
| v6.7    | 81.2%      | ~58%      | 0.812     | 9,355        | +Hofstade Results        |
| v6.8    | 81.0%      | ~58%      | 0.790     | 9,465        | +Heusden-Zolder Results  |
| v6.9    | 80.1%      | ~58%      | 0.783     | 9,589        | +Gavere Results          |
| v6.10   | **80.5%**  | ~58%      | **0.772** | **9,729**    | **+Dendermonde Results** |

### Live Validation

**UCI World Cup Races (Strong Fields):**

| Race        | Date   | Predicted With | Recall | Precision | Hits@10 | Notes                          |
|-------------|--------|----------------|--------|-----------|---------|--------------------------------|
| Tabor       | Nov 23 | v1             | 90%    | 42%       | 7/20    | First test - over-predicted    |
| Flamanville | Nov 30 | v2             | 80%    | 48%       | 13/20   | New rider false positives      |
| Sardinia    | Dec 7  | v6             | 100%   | 100%      | 13/20   | High-conf only, H2H active     |
| Namur       | Dec 14 | v6.1           | 60%    | 75%       | 12/20   | Belgian depth, NEFF surprise   |
| Antwerpen   | Dec 20 | v6.4           | 90%    | 75%       | 13/20   | NYS P23, VDH DNS, WE strong    |

**B-Tier Races (Weaker Fields):**

| Race        | Date   | Predicted With | Recall | Precision | Hits@10 | Notes                          |
|-------------|--------|----------------|--------|-----------|---------|--------------------------------|
| Kortrijk    | Dec 13 | v6.2           | 35%    | 87.5%     | 13/20   | DNS flags hurt recall          |

**Key Insight:** Model excels at World Cup races with strong, predictable fields. B-tier races have more variance (DNS surprises, underdog breakthroughs). High-confidence predictions (>55%) are most reliable. Women Elite consistently outperforms Men Elite in rank correlation.

---

## 🎓 Key Lessons Learned

### 1. Feature Engineering > Model Complexity
- v1→v2: Changed threshold → minor improvement
- v3→v4: Aligned features → significant improvement expected
- **Takeaway:** Fix feature contradictions before tuning hyperparameters

### 2. New Rider Handling is Critical
- 6 false positives at Flamanville (all new riders)
- Generic defaults don't work
- **Takeaway:** Use all available signal (UCI ranking)

### 3. Precision vs Accuracy Trade-off
- v1: High accuracy (90%) but terrible precision (42%)
- Better to be selective and correct than generous and wrong
- **Takeaway:** Optimize for precision in production

### 4. DNS (Did Not Start) is a Real Problem
- v2 DNS filter failed (still predicted 6 DNS riders)
- Need better logic: <3 races OR >14 days
- **Takeaway:** Domain knowledge matters

### 5. Regression Analysis Reveals Insights
- UCI points correlation analysis led to v4 breakthrough
- Data exploration > intuition
- **Takeaway:** Always analyze feature relationships

### 6. Documentation Matters
- UCI "Carried Points" inversion caused confusion
- Clear docs prevent misunderstanding
- **Takeaway:** Explain counterintuitive systems

### 7. Never Exclude Data, Just Annotate It (v6.2)
- Kortrijk: DNS-flagged riders Kamp (P3) and Wyseure (P7) were hidden from predictions
- Lost 2 Top-10 finishers because we excluded them entirely
- **Takeaway:** Show all data with flags, let users decide - exclusion hurts recall

---

## 🚀 Future Improvements (Backlog)

### Completed in v5-v6
- ✅ **Head-to-Head Feature** (v5) - Now #1 feature at 22.5%
- ✅ **Probability Calibration** (v5) - Platt scaling implemented
- ✅ **New Rider Penalty** (v6) - 50% discount for new riders

### High Priority (v7 candidates)
1. **Fix DNS Filter Logic**
   - Current: >21 days OR <2 races
   - Proposed: >14 days OR <3 races (stricter)
   - Expected: Eliminate DNS false positives

2. **Fuzzy Name Matching**
   - Current: Exact match fails for "VANPUTTE" vs "VANDEPUTTE"
   - Proposed: Levenshtein distance ≤2
   - Expected: +1-2% accuracy

3. **Separate Podium Model**
   - Current: Top-3 model trained same as Top-10
   - Proposed: Dedicated podium classifier with race-specific features
   - Expected: 17% → 50%+ podium accuracy

### Medium Priority
4. **Home Advantage Feature**
   - Riders from host country boost
   - Would have helped with Zemanová (Czech in Czech race)

5. **Course-Specific Features**
   - Technical vs power courses
   - Mud/sand conditions
   - Elevation profile

6. **Dynamic New Rider Discount**
   - Current: Fixed 50% discount
   - Could learn discount based on UCI ranking tier
   - E.g., UCI top-50 new rider gets 30% discount, top-200 gets 50%

### Low Priority
7. **Race-Day Variance Modeling**
   - Weather impact
   - Crash probability
   - Mechanical issues
   - (Likely impossible to predict)

8. **Ensemble Models**
   - Combine Random Forest + Gradient Boosting
   - May overfit on small dataset

---

## 💼 For Portfolio / Content

### LinkedIn Post Angles

**v1 Post (Tabor):**
> "Built a cyclocross AI in 2 days. 90% Top-10 accuracy on first test!"

**v2 Post (Flamanville):**
> "Iterated after validation. Precision improved but accuracy dropped. Here's why..."

**v4 Post (Next race):**
> "Fixed the 'new rider problem' using linear regression. Features now align instead of contradict."

### GitHub README
- Show version progression
- Link to validation results
- Demonstrate iterative ML development

### Interview Talking Points
1. **Problem-solving:** Identified precision issue, iterated rapidly
2. **Feature engineering:** UCI-based inference breakthrough
3. **Domain knowledge:** Understanding DNS, UCI points system
4. **Honest evaluation:** Documented failures (16.7% podium)
5. **Production mindset:** Validated on live races, not just backtesting

---

## 📁 File Structure

```
cyclocross-predictions/
├── VERSION_HISTORY.md              ← This file
├── TABOR_VALIDATION_RESULTS.md     ← v1 live test
├── FLAMANVILLE_VALIDATION_RESULTS.md ← v2 live test
├── IMPROVEMENTS_V2.md              ← v2 changes
├── V3_MODEL_COMPARISON.md          ← v3 analysis
├── V4_UCI_INFERENCE_RESULTS.md     ← v4 technical doc
├── UCI_POINTS_EXPLAINED.md         ← Conceptual guide
├── SARDINIA_PREDICTIONS_2025-12-07.md ← v6 predictions
├── head_to_head.py                 ← v5 H2H module (NEW)
├── config.py                       ← Centralized configuration
├── predict_race.py                 ← Prediction pipeline
├── train_model_v2.py               ← Model training script
├── update_results.py               ← Feature engineering
├── app/
│   └── demo.py                     ← Streamlit demo (v6)
├── models/
│   ├── top10_classifier.joblib     ← Current v6 model
│   ├── top3_classifier.joblib
│   └── model_metadata.json
└── data/
    ├── clean/
    │   ├── results_with_features.csv (8,357 obs, 50 races)
    │   └── predictions_*.csv
    └── results/
        └── *.csv (race results)
```

---

## 🔓 Version 6.2: No DNS Exclusion (Dec 13, 2025) ⭐ CURRENT

### Context
Kortrijk validation exposed critical flaw: DNS-flagged riders (Kamp, Wyseure) were excluded from predictions but actually raced and finished P3 and P7. The DNS filter was hurting recall.

**The Problem:**
```python
# Kortrijk Men Elite - Dec 13, 2025
# Ryan Kamp: Flagged as DNS risk → HIDDEN from predictions
# Actual result: P3 (podium!)

# Joran Wyseure: Flagged as DNS risk → HIDDEN from predictions
# Actual result: P7 (Top-10!)

# We missed 2 Top-10 finishers because we excluded them entirely
```

### The Fix

**Before (v6.1):**
- DNS-flagged riders excluded from Top-10/Borderline/Rest of Field tables
- Shown only in separate "DNS Risks" section with no probabilities
- Lost recall because genuine contenders were hidden

**After (v6.2):**
- ALL riders included in predictions with full probabilities
- DNS flag shown as ⚠️ emoji next to rider name (informational only)
- Legend explains: "⚠️ = DNS risk flagged (limited recent races - may still start)"
- No filtering, no exclusion, just a visual indicator

### Changes from v6.1

**Report Generation (`_generate_category_section`):**
```python
# v6.1: Excluded DNS-flagged riders
active_riders = predictions_df[predictions_df["DNS Risk"] == False].copy()

# v6.2: Include ALL riders
all_riders = predictions_df.copy()

# DNS flag shown visually, not used for filtering
if row.get('DNS Risk', False):
    rider_display = f"{row['Rider']} ⚠️"
```

### Kortrijk Validation (What Would Have Changed)

**With v6.2 approach:**
| Rider | v6.1 Display | v6.2 Display | Actual |
|-------|--------------|--------------|--------|
| Ryan Kamp | Hidden in DNS Risks | Shown with ⚠️ + full prob | **P3** |
| Joran Wyseure | Hidden in DNS Risks | Shown with ⚠️ + full prob | **P7** |

**Impact on metrics:**
- Recall would improve: 30% → ~50% (Men Elite)
- Precision unchanged (already included correct predictions)
- No more hidden contenders

### Model Configuration

```python
# DNS flag is now INFORMATIONAL ONLY
# No exclusion in report generation
# Rider probabilities calculated for everyone equally

# Visual indicator in reports:
# "Rider Name ⚠️" = DNS risk flagged but still included
# Legend: "*⚠️ = DNS risk flagged (limited recent races - may still start)*"
```

### Key Insights

✅ **What this fixes:**
- No more missed predictions due to DNS filtering
- Readers see all probabilities, make own judgment
- Higher recall without sacrificing precision

⚠️ **Trade-off:**
- More riders in predictions (potentially noisy)
- User must interpret ⚠️ flag themselves

### The Learning

**DNS prediction is unreliable:**
- Riders flagged as DNS often race (especially in B-tier events)
- Excluding them hurts recall more than it helps precision
- Better to show all data and let user decide

**Lesson from Kortrijk:**
> "We correctly predicted Kamp at 11.8% and Wyseure at 12.8% - but then hid them because of DNS flags. They finished P3 and P7. Never exclude data, just annotate it."

---

## 🏔️ Version 6.3: Namur Validation (Dec 14, 2025) ⭐ CURRENT

### Context
Namur UCI World Cup - technical course in Belgium. Added Kortrijk and Namur results to training data.

### Namur Validation Results

**Combined Summary:**

| Category     | Recall | Precision | High Conf | Podium |
|--------------|--------|-----------|-----------|--------|
| Men Elite    | 60%    | 75%       | 75%       | 2/3    |
| Women Elite  | 60%    | 75%       | 86%       | 1/3    |
| **Combined** | **60%**| **75%**   | **80%**   | **3/6**|

### Men Elite Breakdown

**Correct Predictions (6/10):**
- P1 VAN DER POEL Mathieu (99%)
- P2 NYS Thibau (96%)
- P3 VANTHOURENHOUT Michael (73%)
- P4 VAN DER HAAR Lars (98%)
- P5 VERSTRYNGE Emiel (74%)
- P6 VANDEPUTTE Niels (98%)

**Missed Top-10 (4):**
- P7 RONHAAR Pim (4%)
- P8 NIEUWENHUIS Joris (13%)
- P9 MEEUSSEN Witse (4%)
- P10 VANDEBOSCH Toon (8%)

**False Positives (3):**
- P11 MICHELS Jente (83%)
- P14 DEL GROSSO Tibor (99%)
- DNF MASON Cameron (90%) - crashed out

### Women Elite Breakdown

**Correct Predictions (6/10):**
- P1 BRAND Lucinda (99%)
- P2 VAN ALPHEN Aniek (95%)
- P3 FOUQUENET Amandine (85%)
- P4 PIETERSE Puck (99%)
- P6 VAN DER HEIJDEN Inge (98%)
- P8 BENTVELD Leonie (91%)

**Missed Top-10 (4):**
- P5 NEFF Jolanda (0%) - MTB legend, new to CX
- P7 ZEMANOVA Kristyna (23%)
- P9 MULLER Amandine (3%)
- P10 GERY Celia (8%)

**False Positives (2):**
- P11 CLAUZEL Helene (64%)
- P13 NORBERT RIBEROLLE Marion (79%)

### Key Insights from Namur

1. **Belgian home depth**: 4 missed riders (P7-P10 Men) all Belgian - model underestimates home crowd advantage
2. **New rider penalty working**: NEFF (0%) correctly flagged as unknown despite being MTB world champion
3. **Mason DNF impact**: Would have been true positive if he finished
4. **High confidence reliable**: 80% accuracy on >70% predictions

### Training Performance (v6.3)
- Top-10 Accuracy: **82.6%** (-0.8% from v6.2)
- AUC-ROC: **0.833** (-0.017 from v6.2)
- Dataset: **8,950 observations, 54 races**
- H2H still #1 at **22.7%** importance

### Files Modified
```
MOD: data/clean/results_with_features.csv  - Added Namur Men + Women
MOD: data/clean/race_registry.json         - Updated version, added results
MOD: models/*.joblib                       - Retrained with Namur data
MOD: app/demo.py                           - Updated header, sidebar, footer
NEW: NAMUR_VALIDATION_RESULTS.md           - Full validation report
```

---

## 🔧 Version 6.4: Robust Feature Extraction (Dec 17, 2025) ⭐ CURRENT

### Context
User discovered VAN DER POEL and other elite riders getting absurdly low predictions (6%) despite having 100% H2H vs field. Investigation revealed two issues:

1. **DNS filter incorrectly penalizing elite riders** who race infrequently in CX
2. **Data entry inconsistencies** causing latest race record to have NaN form features

**The Root Cause (VAN DER POEL example):**
```python
# VAN DER POEL has 9 races in dataset, but...
# - Namur (Dec 14): Entered as "Van Der Poel Mathieu" → rider_name_norm = "van der poel mathieu"
# - Earlier races: Entered as "Mathieu Van der poel" → rider_name_norm = "mathieu van der poel"

# When sorted by date, Namur record is latest but has:
# - races_so_far: 0 (not linked to history!)
# - avg_place_last3: NaN
# - top10_rate_career: NaN

# Model received garbage features despite rider having 7+ races of history
```

### The Fix: Robust Feature Source Selection (SOP)

**Before v6.4:**
```python
# Always use latest record by date
latest = rider_history.iloc[0]
features = {
    "avg_place_last3": latest["avg_place_last3"],  # Could be NaN!
    "top10_rate_career": latest["top10_rate_career"],  # Could be NaN!
}
```

**After v6.4:**
```python
# Find record with most complete cumulative data
form_source = latest
if len(rider_history) > 1:
    max_races_idx = rider_history["races_so_far"].fillna(0).idxmax()
    best_record = rider_history.loc[max_races_idx]
    if best_record["races_so_far"] > (latest["races_so_far"] or 0):
        form_source = best_record

# Use best record for CUMULATIVE features
"avg_place_last3": form_source["avg_place_last3"],
"top10_rate_career": form_source["top10_rate_career"],

# Use latest record for POINT-IN-TIME features
"last_place": latest["Place"],  # Actual latest race result
"last_carried_points": latest["Carried Points"],
```

### Changes from v6.3

**1. DNS Filter Disabled by Default**
```python
# predict_race.py
enable_dns_filter=False  # Was True - incorrectly flagged elite riders

# src/api/schemas.py
enable_dns_filter: bool = Field(False, ...)  # DEPRECATED
```

**2. Robust Feature Source Selection**
```python
# src/features/builder.py - _extract_known_rider_features()
# NEW SOP: Always use record with highest races_so_far for cumulative features
# This handles data entry inconsistencies automatically
```

### Results: Before vs After

**VAN DER POEL Mathieu:**
| Metric | v6.3 | v6.4 | Fix |
|--------|------|------|-----|
| Top-10 Prob | 6.0% | **98.9%** | ✅ |
| Podium Prob | 0.7% | **98.4%** | ✅ |
| races_so_far | 1.0 | **8.0** | ✅ |
| avg_place_last3 | NaN | **1.0** | ✅ |

**Other riders fixed:**
| Rider | v6.3 | v6.4 |
|-------|------|------|
| VAN DER HAAR Lars | 5.7% | **98.7%** |
| NYS Thibau | 6.1% | **98.4%** |
| DEL GROSSO Tibor | 5.6% | **84.8%** |
| VERSTRYNGE Emiel | 5.6% | **95.7%** |
| MICHELS Jente | 4.9% | **73.7%** |

### Why This is SOP (Not Just a Bug Fix)

The v6.4 approach is **always correct**, not just when there's a NaN:

1. **If latest record has complete data:** `races_so_far` will be highest → uses latest anyway
2. **If latest record is broken:** Automatically falls back to best available
3. **No NaN detection needed:** Works on `races_so_far` which is always present
4. **Resilient to future data issues:** Any inconsistent data entry is handled

### Key Insight

**The lesson:** Don't trust "latest by date" blindly. Cumulative features should come from the record with the most accumulated history, while point-in-time features should come from the actual latest event.

### Files Modified
```
MOD: predict_race.py           - DNS filter default False
MOD: src/api/schemas.py        - DNS filter default False
MOD: src/features/builder.py   - Robust feature source selection
NEW: ANTWERPEN_PREDICTIONS_2025-12-20.md - First predictions with v6.4
```

---

## 🎯 Current Status (Dec 27, 2025)

**Version:** v6.9
**Training Complete:** ✅ Yes (retrained with Gavere results)
**Live Validation:** ✅ Gavere validated (10 races total)
**Model Files:** ✅ Saved and ready
**Documentation:** ✅ Complete

### v6.9 Training Summary (Dec 27, 2025)

Added Gavere Men Elite + Women Elite results to training data.

| Metric | v6.8 | v6.9 | Change |
|--------|------|------|--------|
| Observations | 9,465 | 9,589 | +124 |
| Races | 62 | 64 | +2 |
| Riders | ~1,911 | ~1,932 | +21 |
| Top-10 Accuracy | 81.0% | 80.1% | -0.9% |
| AUC-ROC | 0.790 | 0.783 | -0.007 |
| H2H Pairs | 62,469 | 63,911 | +1,442 |

**v6.8 Gavere Validation Results:**

| Category     | Hits@10 | Hits@3 | Spearman ρ | MAE Rank | Targets Met |
|--------------|---------|--------|------------|----------|-------------|
| Men Elite    | 6/10    | 2/3    | 0.33       | 5.7      | 2/4         |
| Women Elite  | 7/10    | 2/3    | 0.61       | 4.5      | 3/4         |
| **Combined** | **13/20** | **4/6** | **0.47** | **5.1**  | **5/8**     |

**Men Elite Key Results:**
- VAN DER POEL P1 ✅, NYS P2 (surprise!), DEL GROSSO P3 ✅
- NIEUWENHUIS DNF, MICHELS DNF (DNS pattern continues)
- NYS redemption: #10 prediction → P2 (was P14 at Heusden-Zolder)
- Surprises: VERSTRYNGE (#17→P5), WYSEURE (#14→P7)
- False positives: SWEECK (#4→P11), VANDEPUTTE (#7→P18), ORTS (#8→P29)

**Women Elite Results:**
- BRAND P1 ✅, FOUQUENET P2 (surprise!), PIETERSE P3 ✅
- VAS Blanka P4 - big surprise (#15→P4)
- Strong predictions: VAN ALPHEN (#5→P5), VAN ANROOIJ (#10→P7)
- NEFF struggled: #9→P24 (continuing poor form)

**Season Totals (10 races validated):**
| Race        | Model | Hits@10 ME | Hits@10 WE | Notes |
|-------------|-------|------------|------------|-------|
| Tabor       | v1    | 4/10       | 3/10       | Over-predicted |
| Flamanville | v2    | 8/10       | 5/10       | New rider FPs |
| Sardinia    | v6    | 7/10       | 6/10       | High-conf only |
| Kortrijk    | v6.2  | 6/10       | 7/10       | B-tier race |
| Namur       | v6.1  | 6/10       | 6/10       | Belgian depth |
| Antwerpen   | v6.4  | 6/10       | 7/10       | First v6.4 live |
| Koksijde    | v6.5  | 7/10       | 9/10       | Best WE performance |
| Hofstade    | v6.6  | 8/10       | 7/10       | Best ME performance |
| Heusden-Zolder | v6.7 | 5/10   | 6/10       | 3 DNS, NYS P14 |
| Gavere      | v6.8  | 6/10       | 7/10       | NYS P2, VAS P4 surprises |
| Dendermonde | v6.9  | 8/10       | 7/10       | VAN AERT P6, NYS P1 |
| Diegem      | v6.12 | 6/10       | -          |  |

**Season Averages:** Hits@10: 6.5/10 (ME) / 6.4/10 (WE) | Hits@3: 1.8/3

**Key Learnings from Dendermonde:**
- VAN AERT P6 (predicted P1) - still building race fitness
- NYS wins (predicted podium) - form improving
- VAN DER HAAR P17 (predicted top-5) - big miss
- NIEUWENHUIS DNS continues pattern
- FOUQUENET P3 podium - breakout continues
- BENTVELD P6 surprise (predicted #15)

**Next Steps:**
1. Monitor Diegem, Loenhout, Baal races
2. Track VAN AERT form development
3. VAN DER HAAR needs form feature update

---

## 🖥️ Dashboard & Demo Evolution

The VeloPredict dashboard (`app/demo.py`) is a Streamlit application that evolved alongside the model. This section documents the UI/UX layer, metrics displayed, and architectural decisions.

### Dashboard Architecture

**Design Philosophy:** Zero hardcoding. The dashboard reads all data from two JSON sources:

| Source | Purpose | What It Controls |
|--------|---------|------------------|
| `data/clean/race_registry.json` | Race & validation data | Header stats, sidebar validation, race-by-race charts |
| `models/model_metadata.json` | Model metrics & features | Accuracy, AUC, feature importance, training info |

**Benefits:**
- Retrain model → dashboard auto-updates accuracy, feature importance
- Add race results → dashboard auto-updates validation sidebar, charts
- No code changes needed for routine updates

### Tab Structure

The dashboard has 5 tabs, each serving a distinct purpose:

#### Tab 1: 🔮 Predict Race
**Purpose:** Make live predictions for upcoming races

| Component | Description |
|-----------|-------------|
| Category selector | Men Elite / Women Elite |
| Rider multiselect | Choose riders from historical database |
| Prediction table | Shows Top-10 probability, Top-3 probability, confidence tier |
| H2H breakdown | Win rate vs selected field (expandable) |

**Key features:**
- Deduplicates rider names using `standardize_name()` function
- Shows "new rider" status for unknown riders
- Confidence tiers: High (>70%), Medium (55-70%), Low (<55%)

#### Tab 2: 📊 Model Performance
**Purpose:** Detailed metrics with explanations for technical audiences

| Section | Metrics Displayed | Source |
|---------|-------------------|--------|
| Primary Metrics | Accuracy, Top-3 Accuracy, vs Baseline, AUC-ROC | metadata.json |
| Live Validation | Avg Precision, Avg Recall, Races Validated | registry.json |
| Calibration | Brier Score, Log Loss, Calibration Method | metadata.json |
| Training Details | Train/Test size, Total observations, Races | metadata.json |
| Race-by-Race Table | Per-race precision, recall, notes | registry.json |

**Metric Explanations (in expandable sections):**

| Metric | Question It Answers | Range | Good Value |
|--------|---------------------|-------|------------|
| **Accuracy** | "Of ALL predictions, what % correct?" | 0-100% | >80% |
| **Precision** | "When we predict Top-10, how often right?" | 0-100% | >70% |
| **Recall** | "Of actual Top-10, how many did we catch?" | 0-100% | >60% |
| **AUC-ROC** | "How well does model rank riders?" | 0.5-1.0 | >0.80 |
| **Brier Score** | "How calibrated are probabilities?" | 0-1 | <0.25 |
| **Log Loss** | "Penalty for confident wrong predictions" | 0-∞ | <0.7 |

#### Tab 3: 📈 Model Insights
**Purpose:** Understanding what drives predictions

| Section | Content |
|---------|---------|
| Feature Importance | Top 5 features with % importance (dynamic from metadata) |
| Performance by Category | Top-10 rate breakdown by Men/Women Elite |
| Probability Distribution Patterns | Table of all races with distribution metrics |

**Distribution Patterns (new in v6.3):**

| Pattern | Mid-Range % | Meaning | Trust Level |
|---------|-------------|---------|-------------|
| **BIMODAL** | <10% | Model decisive - clear favorites vs non-contenders | Higher |
| **BALANCED** | >20% | Model uncertain - many "coin flip" riders | Lower |
| **MODERATE** | 10-20% | Typical race - some favorites, some uncertainty | Normal |

#### Tab 4: 📊 Season Tracker
**Purpose:** Visual performance over time with interactive charts

**Charts (6 panels):**
1. Live Race Performance (Recall, Precision, Podium by race)
2. Prediction Volume & Accuracy (predictions made vs correct)
3. Training Accuracy by Version (bar chart)
4. Model Quality AUC-ROC (line chart v3-v6)
5. Feature Importance Evolution (multi-line)
6. Dataset Growth (observations over versions)

**Race-by-Race Analysis:**
- Scatter plot: X = predicted probability, Y = actual position
- Green zone = Top-10, blue line = threshold
- Color coding: 🟢 True Positive, 🔴 False Positive, ⚫ Below threshold
- Distribution metrics panel below charts (new in v6.3)

#### Tab 5: 📚 About
**Purpose:** Project overview and methodology

| Section | Content |
|---------|---------|
| Project description | What VeloPredict does |
| How it works | Feature engineering, training process |
| Features used | List of all model features with descriptions |
| Limitations | What the model can't predict (crashes, tactics) |

### Dynamic Components

**Header (auto-updated):**
```
VeloPredict {version} | {accuracy}% accuracy | {observations} observations | {precision}% live precision
```

**Sidebar (auto-updated):**
- Last 3 validated races with precision/recall
- Quick links to tabs

**Footer (auto-updated):**
```
VeloPredict {version} | {accuracy}% Top-10 Accuracy | H2H #{importance}% | Random Forest + Platt Scaling
```

### Key Dashboard Improvements by Version

| Version | Dashboard Change |
|---------|------------------|
| v1-v5 | Static hardcoded values |
| v6.1 | Metrics explanation expanders added |
| v6.2 | Dynamic header/sidebar/footer from registry |
| v6.3 | Distribution metrics in Tab 3 + Tab 4 Race-by-Race |

### Distribution Metrics Deep Dive

**What it measures:**

| Metric | Description | Why It Matters |
|--------|-------------|----------------|
| `low_pct` | % riders with <30% probability | Non-contenders - model confident they won't Top-10 |
| `mid_pct` | % riders with 30-60% probability | "Uncertain zone" - coin flip riders |
| `high_pct` | % riders with >60% probability | Likely contenders - model confident they will Top-10 |
| `mean_prob` | Average probability across field | Higher = more top-heavy field |
| `std_prob` | Standard deviation of probabilities | Higher = more spread, lower = clustered |
| `new_rider_count` | Riders with no history | Unknown factors in field |
| `field_size` | Total riders | Context for percentages |

**How to interpret:**
- **BIMODAL (mid <10%):** Model knows this field well. Trust predictions above threshold.
- **BALANCED (mid >20%):** Model uncertain. More surprises likely. Watch mid-range riders.
- **MODERATE (mid 10-20%):** Typical race. Normal confidence in predictions.

**Observed patterns:**
- Earlier versions (v1, v2): More MODERATE distributions
- Later versions (v6+): More BIMODAL as H2H matures
- New rider penalty pushes unknowns to low bucket → more bimodal

### Files & Architecture

```
app/
├── demo.py              # Main Streamlit dashboard (1400+ lines)
└── (uses config.py for paths)

data/clean/
├── race_registry.json   # Source of truth for races, validation
└── results_with_features.csv  # Historical data for predictions

models/
├── model_metadata.json  # Training metrics, feature importance
├── top10_classifier.joblib
└── top3_classifier.joblib
```

### Pipeline Integration

The dashboard auto-updates when you run pipeline commands:

| Command | Dashboard Effect |
|---------|------------------|
| `python pipeline.py retrain` | Updates accuracy, AUC, feature importance |
| `python pipeline.py add-results` | Adds race to registry (shows in sidebar after validation) |
| `python pipeline.py backfill-distribution` | Adds distribution data to Tab 3 & Tab 4 |

No manual `demo.py` edits required for routine operations!

---

**Total Development Time:** ~30 days
**Iterations:** 14 versions (v1-v6.10)
**Races Validated:** 0 (including Diegem)
**Dataset Size:** 0 observations, 0 races
**Key Breakthroughs:**
- UCI-based inference (v4)
- Head-to-Head feature (v5) - #1 at 22.8%
- New Rider Penalty (v6) - validated at Sardinia & Namur
- No DNS Exclusion (v6.2) - show all data with flags
- Dynamic Dashboard (v6.2) - zero hardcoding architecture
- Distribution Metrics (v6.3) - model confidence analysis
- Robust Feature Extraction (v6.4) - first live validation at Antwerpen
- Antwerpen Results Added (v6.5) - 57,289 H2H pairs
- Koksijde Validation (v6.5) - **BEST WE: 9/10 Hits@10**
- Koksijde Results Added (v6.6) - 58,072 H2H pairs
- Hofstade Validation (v6.6) - **BEST ME: 8/10 Hits@10**
- Hofstade Results Added (v6.7) - 60,011 H2H pairs
- Heusden-Zolder Validation (v6.7) - DEL GROSSO breakout correctly predicted
- Heusden-Zolder Results Added (v6.8) - 62,469 H2H pairs
- Gavere Validation (v6.8) - NYS P2 redemption, VAS P4 surprise
- Gavere Results Added (v6.9) - 63,911 H2H pairs
**Portfolio Ready:** ✅ Yes - with 10 live validations!

**Season Performance (Original Predictions):**
- Average Hits@10: 6.3/10 (ME) / 6.3/10 (WE)
- Average Hits@3: 1.6/3
- Women Elite: Best at Koksijde (9/10)
- Men Elite: Best at Hofstade (8/10)

**Retraining Policy:**
- Retrain after each race validation to capture latest results
- H2H matrix grows with each race (~800-2,500 new pairs per race)
- Next retrain: After next race validation
