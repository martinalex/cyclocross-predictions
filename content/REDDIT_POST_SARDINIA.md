# Reddit Post: Sardinia UCI World Cup Predictions

**Subreddit:** r/cyclocross (or r/MachineLearning for technical angle)

**Tone:** Casual, community-focused, invites discussion, honest about limitations

---

## Title Options:

**For r/cyclocross:**
> [OC] I built an ML model to predict CX races. Here are my Sardinia picks + why I had to nerf new riders.

**For r/MachineLearning:**
> Built a sports prediction model, learned why domain knowledge beats more features

---

## Post (r/cyclocross version)

Hey all,

I've been building a machine learning model to predict Top-10 finishes in CX races. It's been a fun side project and I wanted to share my Sardinia predictions + some lessons learned.

**Quick background:**
- Random Forest model trained on 50 races, 8,357 observations
- Head-to-head history is the #1 feature (22.5% importance)
- 77.6% accuracy on test set, validated live at Tabor (90%) and Flamanville (80%)

---

### SARDINIA PREDICTIONS (Dec 7)

**Men Elite - Predicted Top-10:**

| Rider | Top-10 % | H2H vs Field | Notes |
|-------|----------|--------------|-------|
| Nieuwenhuis | 98.3% | 93% | Consistent Top-5 |
| Vandeputte | 84.4% | 87% | 4th Flamanville |
| Sweeck | 72.7% | 86% | 2nd Tabor |
| Vanthourenhout | 55.9% | 78% | Borderline |

**Podium:** Too competitive to call. Best riders all <10% podium probability. Anyone's race.

---

**Women Elite - Predicted Top-10:**

| Rider | Top-10 % | H2H vs Field | Notes |
|-------|----------|--------------|-------|
| Brand | 98.8% | 99% | **95% podium** - dominant |
| Casasola | 79.8% | 76% | Home race, 2nd Tabor |
| Bentveld | 63.4% | 83% | Strong H2H |

**Podium:** Only Brand meets 30% threshold. She's on another level right now.

---

### WHAT I LEARNED THIS WEEK

My model was predicting 84% Top-10 for Folcarelli (Italian, UCI rank 115, no race history in my data). That seemed insane.

Dug into the data:
- New riders overall: 8% Top-10 rate
- Known riders: 23% Top-10 rate
- Even strong new riders (UCI top-200): only 38% actual vs 70% expected

**The model was fooled** because I infer features from UCI ranking for unknown riders. Those features "look good" but new riders underperform for reasons the model can't see:
- Unfamiliar with CX chaos
- Unknown to opponents
- First-race nerves

**Fix:** Added 50% discount for new riders. Folcarelli now at 40% which feels right.

---

### WHY PODIUM IS HARD TO PREDICT

Someone asked why I don't show podium predictions for men. Here's the math:

Even Nieuwenhuis (best men's H2H at 93%) only has 46% career podium rate. When you have 5-6 riders who could all podium, the model correctly distributes probability - giving each ~7-10%.

Brand is different. 82% career podium rate, 99% H2H vs this field. Model gives her 95% podium. That's not a bug, that's dominance.

---

### WANT TO HELP VALIDATE?

I'll compare predictions to actual results after Sunday. If you watch the races, let me know if the model got it right!

**Model limitations I'm honest about:**
- Can't predict crashes/mechanicals
- DNS filter is imperfect
- New rider discount is a bit crude (could be tiered by UCI rank)

Code is on GitHub if anyone wants to poke at it.

Cheers and enjoy Sardinia! 🇮🇹

---

## Comments to seed discussion:

1. "Curious what you all think about the men's podium - is it really that unpredictable or am I missing something?"

2. "For the ML folks: H2H ended up being 22.5% of feature importance, which I didn't expect. Anyone seen similar results in other sports prediction models?"

3. "Hot take: Casasola podiums on home soil. Model says 0.2% but home crowd energy is real."

---

**Flair:** OC / Analysis
