# 🇫🇷 Flamanville Predictions (Nov 30, 2025)

**Model:** VeloPredict v2 (Post-Tabor improvements)
**Race:** Flamanville, France
**Date:** November 30, 2025

---

## 🆕 What's New in v2

After Tabor validation (90% accuracy, 42% precision), we implemented:
- **Confidence threshold:** 50% → 55% (reduce false positives)
- **DNS filtering:** Flag riders unlikely to start
- **Expected:** Better precision (42% → 60%)

---

## 🚴 MEN ELITE PREDICTIONS

### Predicted Podium
1. 🥇 **JORIS NIEUWENHUIS** (63.0% podium chance)
2. 🥈 **THIBAU NYS** (41.4% podium chance)
3. 🥉 **JENTE MICHELS** (38.3% podium chance)

### Predicted Top-10 (13 riders)
1. NIEUWENHUIS Joris (83.8% Top-10 chance)
2. NYS Thibau (74.1%)
3. VERSTRYNGE Emiel (71.0%)
4. RONHAAR Pim (70.7%)
5. MICHELS Jente (69.7%)
6. SWEECK Laurens (69.3%)
7. VANTHOURENHOUT Michael (69.0%)
8. MEEUSSEN Witse (66.8%)
9. VANDEPUTTE Niels (65.8%)
10. VAN DER HAAR Lars (64.9%)
11. MASON Cameron (60.2%)
12. AERTS Toon (57.7%)
13. WYSEURE Joran (57.4%)

### ⚠️ DNS Risks Flagged (3 riders)
- NAVARRO Quentin (Only 1 race this season)
- JUNGE Frederick (Only 1 race this season)
- JOT Hugo (Only 1 race this season)

### Key Insights
- **Strong field:** 4 riders with >70% confidence
- **Competitive race:** 13 riders predicted Top-10 (realistic count)
- **Favorites:** Nieuwenhuis, Nys, Verstrynge all showing high confidence
- **DNS filter working:** 3 riders flagged as unlikely to start

---

## 🚴 WOMEN ELITE PREDICTIONS

### Predicted Podium
1. 🥇 **SHIRIN VAN ANROOIJ** (80.9% podium chance)
2. 🥈 **CEYLIN DEL CARMEN ALVARADO** (80.9% podium chance)
3. 🥉 **THEODORA HOPE INGLIS** (80.9% podium chance)

### Predicted Top-10 (20 riders)
1. VAN DER HEIJDEN Inge (91.8% Top-10 chance)
2. FOUQUENET Amandine (87.4%)
3. VAN ANROOIJ Shirin (86.3%)
4. ALVARADO Ceylin del Carmen (86.3%)
5. INGLIS Theodora Hope (86.3%)
6. MOULIN Anaïs (86.3%)
7. EYEINGTON Joy Kacey (86.3%)
8. DRAKE Haf Ann Ffion (86.3%)
9. BENTVELD Leonie (83.3%)
10. BROUWERS Julie (83.3%)
11. NORBERT RIBEROLLE Marion (82.8%)
12. VAN ALPHEN Aniek (81.9%)
13. CLAUZEL Hélène (81.6%)
14. VERDONSCHOT Laura (78.5%)
15. CUSACK Lidia (78.4%)
16. WORST Annemarie (78.3%)
17. BAKKER Manon (76.5%)
18. BETSEMA Denise (62.5%)
19. SCHREIBER Marie (60.9%)
20. DESPREZ Lison (58.6%)

### ⚠️ DNS Risks Flagged (1 rider)
- DETILLEUX Emeline (Only 1 race this season)

### Key Insights
- **⚠️ WARNING:** 6 riders have no history (new riders) - model assigned default 86.3% probability
  - Van Anrooij, Alvarado, Inglis, Moulin, Eyeington, Drake
  - These predictions are **less reliable** due to lack of historical data
- **High confidence field:** 17 riders with >70% confidence
- **More predictions:** 20 riders (vs 13 for men) due to new rider defaults

### 🚨 Women's Race Caveat
The model predicted **6 new riders** with identical 86.3% probability. This is a known limitation - the model doesn't have historical data for these riders and uses defaults. **Treat these predictions with caution.**

**New riders flagged:**
- Van Anrooij, Alvarado (likely strong - check UCI rankings!)
- Inglis, Moulin, Eyeington, Drake (unknown quality)

---

## 📊 v2 Improvements in Action

### Men Elite
- **Predicted:** 13 Top-10 (down from 19 at Tabor) ✅
- **High confidence:** 4 riders (>70%)
- **DNS flagged:** 3 riders
- **Expected precision:** ~60% (vs 47% at Tabor)

### Women Elite
- **Predicted:** 20 Top-10 (higher due to 6 new riders)
- **High confidence:** 17 riders
- **DNS flagged:** 1 rider
- **New rider issue:** 6 riders with no history skewing predictions

---

## 🎯 Validation Plan (Sunday Night)

After the race:
1. **Download results** from UCI or race website
2. **Run validation:**
   ```bash
   python validate_predictions.py \
     --predictions data/clean/predictions_flamanville_men_elite.csv \
     --results data/results/Results__Flamanville__Men-Elite__2025-11-30.csv \
     --category "Men Elite"
   ```
3. **Compare to Tabor:**
   - Did precision improve from 47% → 60%?
   - Did DNS filter prevent embarrassing predictions?
   - Did confidence threshold reduce false positives?

---

## 📈 Success Criteria

**v2 is successful if:**
- Precision improves by 10%+ (47% → 57%+)
- No DNS riders in predicted podium
- Predicted Top-10 count is realistic (12-15, not 19-24)
- Maintain 85%+ Top-10 accuracy

---

## 📁 Files Generated

**Prediction CSVs:**
- `data/clean/predictions_flamanville_men_elite.csv` (42 riders analyzed)
- `data/clean/predictions_flamanville_women_elite.csv` (51 riders analyzed)

**This Summary:**
- `FLAMANVILLE_PREDICTIONS_2025-11-30.md`

---

## 🤔 Post-Race: What to Watch For

### Men Elite
- **Nieuwenhuis vs Nys:** Both have high podium probability
- **DNS validation:** Did Navarro, Junge, Jot actually start?
- **Precision check:** How many of 13 predictions were correct?

### Women Elite
- **New rider performance:** How did Van Anrooij, Alvarado actually perform?
- **Model limitation:** Need to add "new rider detection" warning in future
- **Precision impact:** Did new riders skew overall precision?

---

**Good luck! Let's see if v2 improvements work!** 🚀

---

## 📌 Quick Reference

**Race:** Flamanville, France
**Date:** November 30, 2025
**Model:** VeloPredict v2 (improved precision)
**Men predicted Top-10:** 13 riders
**Women predicted Top-10:** 20 riders (6 new riders)
**DNS risks flagged:** 4 total (3 men, 1 women)
