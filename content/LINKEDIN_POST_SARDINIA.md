# LinkedIn Post: Sardinia UCI World Cup Predictions

**Tone:** Professional, insight-driven, shows technical depth while remaining accessible

---

## Post

**I built an AI that predicts cyclocross race results. Here's what I learned when it was wrong.**

Two weeks ago, my model predicted an unknown Italian rider named Folcarelli had an 84% chance of finishing Top-10 at Sardinia.

That felt wrong. He's UCI rank 115 with zero race history in my dataset. So I investigated.

**What I found:**
- New riders (no history) have only 8% Top-10 rate vs 23% for known riders
- Even strong new riders (UCI top-200) only achieve 38% Top-10 rate
- My model was predicting 80%+ because it inferred "reasonable" features from UCI ranking

**The fix wasn't more ML. It was domain knowledge.**

I added a 50% discount for new riders. Not arbitrary - it's data-backed:
- Expected rate from UCI: 69.7%
- Actual historical rate: 38%
- Ratio: 38/69.7 ≈ 0.55

Folcarelli dropped from 84.5% → 40.2%. That feels right.

**The lesson:** Pure ML isn't always enough. Sometimes the best feature is understanding why your predictions don't make sense.

---

**Sardinia Predictions (Dec 7):**

🚴 **Men Elite** - No dominant favorite (podium unpredictable)
- Nieuwenhuis: 98% Top-10 | 93% H2H vs field
- Vandeputte: 84% Top-10 | 87% H2H
- Sweeck: 73% Top-10 | 86% H2H

🚴 **Women Elite** - Brand dominates
- Brand: 99% Top-10, **95% podium** | 99% H2H
- Casasola: 80% Top-10 | Home race advantage
- Bentveld: 63% Top-10 | 83% H2H

Model: 77.6% accuracy, H2H is #1 feature (22.5%), built in 14 days.

I'll validate after the race. Follow for results.

#MachineLearning #Cycling #DataScience #ProductManagement #AI

---

## Image suggestions:
1. Screenshot of predictions table
2. Before/after showing Folcarelli 84% → 40%
3. Feature importance chart with H2H at top

## Hashtags:
#MachineLearning #Cycling #DataScience #ProductManagement #AI #Cyclocross #SportsPrediction

---

**Character count:** ~1,800 (LinkedIn allows 3,000)
