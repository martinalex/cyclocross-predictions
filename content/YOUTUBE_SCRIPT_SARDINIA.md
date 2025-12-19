# YouTube Script: VeloPredict Sardinia Predictions + Model Evolution

**Video Title Options:**
1. "I Built an AI to Predict Bike Races - Here's What Went Wrong (and How I Fixed It)"
2. "ML Sports Prediction: When Your Model is Confidently Wrong"
3. "Sardinia CX Predictions + Why I Had to Nerf My Own AI"

**Length:** 8-12 minutes
**Tone:** Educational, conversational, shows the messy reality of ML development

---

## INTRO (0:00 - 1:00)

[HOOK - Show prediction screenshot]

**"My AI predicted an unknown Italian rider had an 84% chance of finishing Top-10 at Sardinia this weekend. That's higher than riders who've been winning races all season. Something was very wrong."**

Hey, I'm [Name]. I've been building a machine learning model to predict cyclocross race results. Today I want to share my predictions for this weekend's Sardinia UCI World Cup, but more importantly - I want to show you what happened when my model was confidently wrong, and what I learned fixing it.

This isn't a tutorial. It's a story about why pure machine learning isn't always enough.

---

## THE PREDICTIONS (1:00 - 3:00)

[SCREEN: Show prediction tables]

Let me give you the predictions first, then I'll explain the journey to get here.

### Women Elite

[Show Women's table]

This one's straightforward. Lucinda Brand is predicted at **98.8% Top-10** and **95% podium probability**. That's not a bug - she's genuinely dominant. 82% career podium rate, 99% head-to-head record against this field.

Behind her:
- Casasola at 80% - home race advantage, was 2nd at Tabor
- Bentveld at 63% - strong H2H score

Only Brand meets my 30% podium threshold. When you're that good, the model notices.

### Men Elite

[Show Men's table]

Men's is more interesting. Four riders above my 55% threshold:
- Nieuwenhuis at 98%
- Vandeputte at 84%
- Sweeck at 73%
- Vanthourenhout at 56%

But here's the thing - **no one meets my 30% podium threshold**. Even Nieuwenhuis, with a 93% head-to-head score against this field, only has 7% podium probability.

[PAUSE]

Why? Because podium prediction is fundamentally different from Top-10.

---

## WHY PODIUM IS HARD (3:00 - 4:30)

[Show math on screen]

Think about it:
- Top-10: 10 spots out of 35 riders = 29% base rate
- Podium: 3 spots out of 35 riders = 9% base rate

Even the best men's rider - Nieuwenhuis - only makes the podium 46% of the time historically. When you have 5-6 riders who could all win, the probability gets distributed. Each strong rider gets maybe 10-15% podium chance.

That's not the model being wrong. That's the model correctly capturing uncertainty.

Brand is different because she's genuinely in a tier of her own. When your H2H is 99% and your career podium rate is 82%, you get 95% probability.

---

## THE PROBLEM: FOLCARELLI (4:30 - 7:00)

[Show before/after screenshot]

Now let me tell you about this Italian rider named Folcarelli.

Last week, I ran predictions and he showed up at **84.5% Top-10 probability**. That's higher than Sweeck, who finished 2nd at Tabor. Higher than Vanthourenhout, who's been a consistent Top-10 finisher.

Folcarelli is UCI rank 115. Not bad - but he has zero race history in my dataset. No head-to-head data. No form data.

Something was wrong.

### The Investigation

[SCREEN: Code/data analysis]

I dug into my training data. Here's what I found:

**Known riders** (have history in my data):
- 23% Top-10 rate overall
- 7,518 observations

**New riders** (first appearance):
- 8% Top-10 rate overall
- 670 observations

New riders are **three times less likely** to finish Top-10. Even controlling for UCI ranking:

- New riders with UCI top-200: **38% actual Top-10 rate**
- But my model was predicting: **70-80%**

### Why Was The Model Fooled?

[SCREEN: Feature diagram]

My model uses UCI ranking to *infer* features for unknown riders. If you're rank 115, I estimate your expected finish around 18th place. That looks like a Top-10 contender.

But the model doesn't know:
- This rider has never raced in my dataset
- They might not be used to CX chaos
- They're unknown to opponents
- First-race nerves are real

The features looked "reasonable" but new riders underperform for reasons I can't capture.

### The Fix

[SCREEN: Code change]

I tried adding an `is_new_rider` feature and retraining. The model gave it 0.23% importance. It basically ignored it because the inferred features still looked fine.

So I added an explicit rule:

```python
if status == "new_rider":
    top10_prob = top10_prob * 0.5  # 50% discount
```

Why 50%? It's data-backed:
- Expected from UCI: 69.7% Top-10
- Actual historical: 38% Top-10
- Ratio: 38/69.7 = 0.55

Folcarelli went from 84.5% → 40.2%. That feels right for a strong-but-unknown rider.

---

## THE LESSON (7:00 - 8:30)

[Direct to camera]

Here's what I learned: **Pure ML isn't always enough.**

The model couldn't learn "new riders are risky" because I was giving it features that made new riders look safe. The signal was hidden by my own feature engineering.

Sometimes the best improvement isn't:
- More features
- Better hyperparameters
- Fancier algorithms

Sometimes it's stepping back and asking: "Does this prediction make sense?"

An 84% prediction for an unknown rider doesn't pass the smell test. That domain knowledge - that intuition from understanding the sport - led me to find and fix the bug.

---

## HEAD-TO-HEAD: THE BREAKTHROUGH (8:30 - 10:00)

[SCREEN: H2H diagram]

One more thing I want to share. The biggest improvement to my model wasn't the new rider fix. It was adding **head-to-head history**.

For each rider, I calculate: "What's your historical win rate against the specific opponents in this race?"

Nieuwenhuis has 93% H2H vs the Sardinia field. He historically beats almost everyone racing this weekend.

This became my **#1 feature at 22.5% importance**. More important than:
- UCI ranking
- Recent form
- Career Top-10 rate

Why? Because knowing WHO you're racing matters more than how good you are in general.

When I validated this on Flamanville retroactively:
- Men's H2H correlation with finish: r = 0.77
- Women's H2H correlation with finish: r = 0.87

That's a strong signal.

---

## WRAP UP (10:00 - 11:00)

[Show predictions one more time]

So those are my Sardinia predictions:

**Women:** Brand dominates, Casasola and Bentveld fight for Top-5

**Men:** Nieuwenhuis, Vandeputte, Sweeck are locks. Podium is anyone's race.

I'll post results after Sunday to see how the model did.

**Key lessons from this build:**
1. Domain knowledge catches what ML misses
2. Head-to-head history is underrated in sports prediction
3. When a prediction doesn't pass the smell test, investigate

If you want to follow along, I'm documenting the whole project. Link in description.

See you after the race.

---

## OUTRO / END SCREEN (11:00 - 11:30)

[End screen with subscribe prompt]

Thanks for watching. If you're into ML, cycling, or just seeing how messy real-world projects are - subscribe. I'll post the validation results next week.

Drop a comment: Who do you think takes the men's podium? Model says it's a coin flip.

---

## B-ROLL / VISUALS NEEDED:

1. Prediction tables (both categories)
2. Before/after Folcarelli screenshot (84% → 40%)
3. Training data stats (new vs known riders)
4. Code snippets (new rider discount)
5. Feature importance chart
6. H2H matrix visualization (optional)
7. Race footage from Tabor/Flamanville (for context, check licensing)

## CHAPTERS:
- 0:00 The Problem
- 1:00 Sardinia Predictions
- 3:00 Why Podium is Hard
- 4:30 The Folcarelli Bug
- 7:00 The Lesson
- 8:30 Head-to-Head Breakthrough
- 10:00 Summary

---

## THUMBNAIL OPTIONS:
1. "84% → 40%" with confused/enlightened face
2. "My AI Was Wrong" with prediction table
3. Brand at 95% podium vs "???" for men
