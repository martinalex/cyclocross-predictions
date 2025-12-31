# Hofstade Validation Results

**X2O-Trofee** | 2025-12-22

*VeloPredict v6 Performance Analysis*

---

### Men Elite Results

| Metric         | Value | Target |
|---------------|:-----:|:------:|
| **Hits@10**    |  8/10 |   7+   |
| **Hits@3**     |  2/3  |   2+   |
| **Spearman ρ** |  0.53 |  >0.5  |
| **MAE Rank**   |  2.6  |   <3   |

#### Metrics Interpretation

- **Hits@10** (8/10): How many of our top-10 predictions finished in actual top-10? ✅ Met target
- **Hits@3** (2/3): How many of our podium picks made actual podium? ✅ Met target
- **Spearman ρ** (0.53): Rank correlation between predicted and actual order. Moderate rank correlation. ✅ Met target
- **MAE Rank** (2.6): On average, our predictions were 2.6 positions off from actual finish. ✅ Met target

#### Predicted Top-10 Breakdown

| Pred Rank | Rider                  | Probability |  Actual | Result |
|:---------:|-----------------------|-----------:|:-------:|:------:|
|     1     | VAN DER POEL Mathieu   |       99.1% |    P1   |   ✅    |
|     2     | VAN AERT Wout          |       98.5% |    P2   |   ✅    |
|     3     | SWEECK Laurens         |       97.5% |    P5   |   ✅    |
|     4     | AERTS Toon             |       95.2% |    P7   |   ✅    |
|     5     | VANTHOURENHOUT Michael |       92.3% | DNF/DNS |   ❌    |
|     6     | VANDEPUTTE Niels       |       88.4% |    P3   |   ✅    |
|     7     | VAN DER HAAR Lars      |       76.3% |   P13   |   ❌    |
|     8     | MASON Cameron          |       69.9% |    P8   |   ✅    |
|     9     | NIEUWENHUIS Joris      |       66.3% |    P6   |   ✅    |
|     10    | NYS Thibau             |       44.4% |    P4   |   ✅    |

#### Predicted Podium Breakdown

*Top 3 riders by Top-3 Probability*

| Pred Rank | Rider                | Podium Prob | Actual | Result |
|:---------:|---------------------|-----------:|:------:|:------:|
|     1     | VAN DER POEL Mathieu |       98.9% |   P1   |   ✅    |
|     2     | VAN AERT Wout        |        7.4% |   P2   |   ✅    |
|     3     | SWEECK Laurens       |        4.1% |   P5   |   ❌    |

#### Next 10 Riders (Ranks 11-20)

*How did our near-miss predictions perform?*

| Pred Rank | Rider               | Probability |  Actual | Made Top-10? |
|:---------:|--------------------|-----------:|:-------:|:------------:|
|     11    | VANDEBOSCH Toon     |       15.2% |    P9   |    ✅ Yes!    |
|     12    | SOETE Daan          |        7.9% |   P18   |      No      |
|     13    | HORNY Clement       |        3.2% | DNF/DNS |      No      |
|     14    | VAN DE PUTTE Victor |        2.9% |   P15   |      No      |
|     15    | KAMP Ryan           |        2.8% |   P10   |    ✅ Yes!    |
|     16    | JANSSEN Wout        |        1.5% |   P16   |      No      |
|     17    | MEEUSSEN Witse      |        1.2% |   P11   |      No      |
|     18    | GASSNER Michael     |        0.5% |   P32   |      No      |
|     19    | KUYPERS Gerben      |        0.5% |   P12   |      No      |
|     20    | ROSENDAHL Karl-Erik |        0.4% |   P28   |      No      |

**Surprises:** VANDEBOSCH Toon (predicted #11, finished P9), KAMP Ryan (predicted #15, finished P10)

#### Legacy Metrics (Threshold-based)

*Using 55% confidence threshold*

| Metric             | Value | Calculation                               |
|-------------------|:-----:|------------------------------------------|
| Recall             | 70.0% | 7 correct / 10 actual top-10              |
| Precision          | 87.5% | 7 correct / 8 predictions above threshold |
| High Conf Accuracy | 83.3% | 5 correct / 6 predictions >70%            |

#### Actual Top-20 Results

*How the race actually unfolded vs our predictions*

| Pos | Rider                | Our Prob | Our Rank | Rank Error | Status     |
|:---:|---------------------|--------:|:--------:|:----------:|-----------|
|  P1 | VAN DER POEL Mathieu |    99.1% |    #1    |     0      | ✅ Hit      |
|  P2 | VAN AERT Wout        |    98.5% |    #2    |     0      | ✅ Hit      |
|  P3 | VANDEPUTTE Niels     |    88.4% |    #6    |     +3     | ✅ Hit      |
|  P4 | NYS Thibau           |    44.4% |   #10    |     +6     | ✅ Hit      |
|  P5 | SWEECK Laurens       |    97.5% |    #3    |     -2     | ✅ Hit      |
|  P6 | NIEUWENHUIS Joris    |    66.3% |    #9    |     +3     | ✅ Hit      |
|  P7 | AERTS Toon           |    95.2% |    #4    |     -3     | ✅ Hit      |
|  P8 | MASON Cameron        |    69.9% |    #8    |     0      | ✅ Hit      |
|  P9 | VANDEBOSCH Toon      |    15.2% |   #11    |     +2     | 📈 Surprise |
| P10 | KAMP Ryan            |     2.8% |   #15    |     +5     | 📈 Surprise |
| P11 | MEEUSSEN Witse       |     1.2% |   #17    |     +6     |            |
| P12 | KUYPERS Gerben       |     0.5% |   #19    |     +7     |            |
| P13 | VAN DER HAAR Lars    |    76.3% |    #7    |     -6     | 📉 Miss     |
| P14 | LAURYSSEN Yorben     |     0.3% |   #31    |    +17     |            |
| P15 | VAN DE PUTTE Victor  |     2.9% |   #14    |     -1     |            |
| P16 | JANSSEN Wout         |     1.5% |   #16    |     0      |            |
| P17 | MEEUSEN Tom          |     0.1% |   #35    |    +18     |            |
| P18 | SOETE Daan           |     7.9% |   #12    |     -6     |            |
| P19 | DE VET Sander        |     0.1% |   #36    |    +17     |            |
| P20 | BERTOLINI Gioele     |     0.2% |   #32    |    +12     |            |

---

### Women Elite Results

| Metric         | Value | Target |
|---------------|:-----:|:------:|
| **Hits@10**    |  7/10 |   7+   |
| **Hits@3**     |  1/3  |   2+   |
| **Spearman ρ** |  0.78 |  >0.5  |
| **MAE Rank**   |  2.8  |   <3   |

#### Metrics Interpretation

- **Hits@10** (7/10): How many of our top-10 predictions finished in actual top-10? ✅ Met target
- **Hits@3** (1/3): How many of our podium picks made actual podium? ❌ Below target
- **Spearman ρ** (0.78): Rank correlation between predicted and actual order. Strong rank correlation. ✅ Met target
- **MAE Rank** (2.8): On average, our predictions were 2.8 positions off from actual finish. ✅ Met target

#### Predicted Top-10 Breakdown

| Pred Rank | Rider                      | Probability |  Actual | Result |
|:---------:|---------------------------|-----------:|:-------:|:------:|
|     1     | BRAND Lucinda              |       99.0% |    P1   |   ✅    |
|     2     | ALVARADO Ceylin del Carmen |       98.8% | DNF/DNS |   ❌    |
|     3     | VAN ANROOIJ Shirin         |       95.0% |    P2   |   ✅    |
|     4     | LANGENBARG Puck            |       19.4% |   P10   |   ✅    |
|     5     | BROUWERS Julie             |       10.7% |    P5   |   ✅    |
|     6     | BAKKER Manon               |        9.6% |    P3   |   ✅    |
|     7     | VERDONSCHOT Laura          |        9.0% |    P4   |   ✅    |
|     8     | HLADÍKOVÁ Kateřina         |        9.0% |    P8   |   ✅    |
|     9     | CLAUZEL Perrine            |        7.2% |   P13   |   ❌    |
|     10    | SONNEMANS Sara             |        6.3% |   P18   |   ❌    |

#### Predicted Podium Breakdown

*Top 3 riders by Top-3 Probability*

| Pred Rank | Rider                      | Podium Prob |  Actual | Result |
|:---------:|---------------------------|-----------:|:-------:|:------:|
|     1     | BRAND Lucinda              |       99.1% |    P1   |   ✅    |
|     2     | ALVARADO Ceylin del Carmen |       77.0% | DNF/DNS |   ❌    |
|     3     | BROUWERS Julie             |        0.3% |    P5   |   ❌    |

#### Next 10 Riders (Ranks 11-20)

*How did our near-miss predictions perform?*

| Pred Rank | Rider                 | Probability |  Actual | Made Top-10? |
|:---------:|----------------------|-----------:|:-------:|:------------:|
|     11    | DE SCHOESITTER Shanyl |        5.7% | DNF/DNS |      No      |
|     12    | GARIBOLDI Rebecca     |        4.1% |    P6   |    ✅ Yes!    |
|     13    | BORELLO Carlotta      |        3.1% | DNF/DNS |      No      |
|     14    | HURTELOUP Adèle       |        2.8% |   P21   |      No      |
|     15    | LAURIJSSEN Sanne      |        2.5% |   P16   |      No      |
|     16    | VERVLOET Sterre       |        2.4% |   P15   |      No      |
|     17    | MOS Anniek            |        2.2% | DNF/DNS |      No      |
|     18    | NIEUWENHUIS Rianne    |        2.1% | DNF/DNS |      No      |
|     19    | CRABBÉ Kiona          |        1.8% | DNF/DNS |      No      |
|     20    | SCHAMPAERT Lien       |        1.4% |   P35   |      No      |

**Surprises:** GARIBOLDI Rebecca (predicted #12, finished P6)

#### Legacy Metrics (Threshold-based)

*Using 55% confidence threshold*

| Metric             | Value  | Calculation                               |
|-------------------|:------:|------------------------------------------|
| Recall             | 20.0%  | 2 correct / 10 actual top-10              |
| Precision          | 100.0% | 2 correct / 2 predictions above threshold |
| High Conf Accuracy | 100.0% | 2 correct / 2 predictions >70%            |

#### Actual Top-20 Results

*How the race actually unfolded vs our predictions*

| Pos | Rider                | Our Prob | Our Rank | Rank Error | Status     |
|:---:|---------------------|--------:|:--------:|:----------:|-----------|
|  P1 | BRAND Lucinda        |    99.0% |    #1    |     0      | ✅ Hit      |
|  P2 | VAN ANROOIJ Shirin   |    95.0% |    #3    |     +1     | ✅ Hit      |
|  P3 | BAKKER Manon         |     9.6% |    #6    |     +3     | ✅ Hit      |
|  P4 | VERDONSCHOT Laura    |     9.0% |    #7    |     +3     | ✅ Hit      |
|  P5 | BROUWERS Julie       |    10.7% |    #5    |     0      | ✅ Hit      |
|  P6 | GARIBOLDI Rebecca    |     4.1% |   #12    |     +6     | 📈 Surprise |
|  P7 | BURQUIER Line        |     0.1% |   #66    |    +59     | 📈 Surprise |
|  P8 | HLADÍKOVÁ Kateřina   |     9.0% |    #8    |     0      | ✅ Hit      |
|  P9 | DURAFFOURG Lauriane  |     0.1% |   #63    |    +54     | 📈 Surprise |
| P10 | LANGENBARG Puck      |    19.4% |    #4    |     -6     | ✅ Hit      |
| P11 | DESPREZ Lison        |     0.8% |   #26    |    +15     |            |
| P12 | SELS Loes            |     0.1% |   #52    |    +40     |            |
| P13 | CLAUZEL Perrine      |     7.2% |    #9    |     -4     | 📉 Miss     |
| P14 | KRAHL Judith         |     0.3% |   #48    |    +34     |            |
| P15 | VERVLOET Sterre      |     2.4% |   #16    |     +1     |            |
| P16 | LAURIJSSEN Sanne     |     2.5% |   #15    |     -1     |            |
| P17 | MOES Noï             |      N/A |   N/A    |    N/A     | ❓ Unknown  |
| P18 | SONNEMANS Sara       |     6.3% |   #10    |     -8     | 📉 Miss     |
| P19 | LENFERINK Femke      |     0.1% |   #61    |    +42     |            |
| P20 | DE RAEDEMAEKER Alexe |     0.9% |   #22    |     +2     |            |
---

*Generated by VeloPredict pipeline on 2025-12-22 14:50*