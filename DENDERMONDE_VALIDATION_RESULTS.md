# Dendermonde Validation Results

**UCI World Cup** | 2025-12-28

*VeloPredict v6 Performance Analysis*

---

### Women Elite Results

| Metric         | Value | Target |
|---------------|:-----:|:------:|
| **Hits@10**    |  7/10 |   7+   |
| **Hits@3**     |  2/3  |   2+   |
| **Spearman ρ** |  0.68 |  >0.5  |
| **MAE Rank**   |  2.3  |   <3   |

#### Metrics Interpretation

- **Hits@10** (7/10): How many of our top-10 predictions finished in actual top-10? ✅ Met target
- **Hits@3** (2/3): How many of our podium picks made actual podium? ✅ Met target
- **Spearman ρ** (0.68): Rank correlation between predicted and actual order. Moderate rank correlation. ✅ Met target
- **MAE Rank** (2.3): On average, our predictions were 2.3 positions off from actual finish. ✅ Met target

#### Predicted Top-10 Breakdown

| Pred Rank | Rider                      | Probability |  Actual | Result |
|:---------:|---------------------------|-----------:|:-------:|:------:|
|     1     | BRAND Lucinda              |       99.0% |    P1   |   ✅    |
|     2     | PIETERSE Puck              |       98.9% |    P2   |   ✅    |
|     3     | ALVARADO Ceylin del Carmen |       98.0% |    P4   |   ✅    |
|     4     | VAN ALPHEN Aniek           |       97.6% |    P7   |   ✅    |
|     5     | VAN DER HEIJDEN Inge       |       97.4% |   P13   |   ❌    |
|     6     | FOUQUENET Amandine         |       96.4% |    P3   |   ✅    |
|     7     | NORBERT RIBEROLLE Marion   |       96.1% |    P5   |   ✅    |
|     8     | CASASOLA Sara              |       95.7% | DNF/DNS |   ❌    |
|     9     | VAN ANROOIJ Shirin         |       94.0% |   P11   |   ❌    |
|     10    | ZEMANOVÁ Kristýna          |       91.0% |    P8   |   ✅    |

#### Predicted Podium Breakdown

*Top 3 riders by Top-3 Probability*

| Pred Rank | Rider            | Podium Prob | Actual | Result |
|:---------:|-----------------|-----------:|:------:|:------:|
|     1     | BRAND Lucinda    |       98.8% |   P1   |   ✅    |
|     2     | PIETERSE Puck    |       96.8% |   P2   |   ✅    |
|     3     | VAN ALPHEN Aniek |       22.0% |   P7   |   ❌    |

#### Next 10 Riders (Ranks 11-20)

*How did our near-miss predictions perform?*

| Pred Rank | Rider               | Probability | Actual | Made Top-10? |
|:---------:|--------------------|-----------:|:------:|:------------:|
|     11    | GERY Célia          |       79.8% |  P10   |    ✅ Yes!    |
|     12    | CARRIER Rafaelle    |       79.7% |  P14   |      No      |
|     13    | BROUWERS Julie      |       72.9% |  P21   |      No      |
|     14    | SCHREIBER Marie     |       53.5% |  P12   |      No      |
|     15    | BENTVELD Leonie     |       30.1% |   P6   |    ✅ Yes!    |
|     16    | BACKSTEDT Zoe       |       27.3% |  P27   |      No      |
|     17    | CLAUZEL Hélène      |       18.7% |  P23   |      No      |
|     18    | BRAMATI Lucia       |       13.6% |  P26   |      No      |
|     19    | BAKKER Manon        |       13.4% |   P9   |    ✅ Yes!    |
|     20    | CHLADONOVÁ Viktória |       12.3% |  P51   |      No      |

**Surprises:** GERY Célia (predicted #11, finished P10), BENTVELD Leonie (predicted #15, finished P6), BAKKER Manon (predicted #19, finished P9)

#### Legacy Metrics (Threshold-based)

*Using 55% confidence threshold*

| Metric             | Value | Calculation                                |
|-------------------|:-----:|-------------------------------------------|
| Recall             | 80.0% | 8 correct / 10 actual top-10               |
| Precision          | 66.7% | 8 correct / 12 predictions above threshold |
| High Conf Accuracy | 66.7% | 8 correct / 12 predictions >70%            |

#### Actual Top-20 Results

*How the race actually unfolded vs our predictions*

| Pos | Rider                    | Our Prob | Our Rank | Rank Error | Status     |
|:---:|-------------------------|--------:|:--------:|:----------:|-----------|
|  P1 | BRAND Lucinda            |    99.0% |    #1    |     0      | ✅ Hit      |
|  P2 | PIETERSE Puck            |    98.9% |    #2    |     0      | ✅ Hit      |
|  P3 | FOUQUENET Amandine       |    96.4% |    #6    |     +3     | ✅ Hit      |
|  P4 | ALVARADO Ceylin          |    98.0% |    #3    |     -1     | ✅ Hit      |
|  P5 | NORBERT RIBEROLLE Marion |    96.1% |    #7    |     +2     | ✅ Hit      |
|  P6 | BENTVELD Leonie          |    30.1% |   #15    |     +9     | 📈 Surprise |
|  P7 | VAN ALPHEN Aniek         |    97.6% |    #4    |     -3     | ✅ Hit      |
|  P8 | ZEMANOVÁ Kristýna        |    91.0% |   #10    |     +2     | ✅ Hit      |
|  P9 | BAKKER Manon             |    13.4% |   #19    |    +10     | 📈 Surprise |
| P10 | GERY Célia               |    79.8% |   #11    |     +1     | 📈 Surprise |
| P11 | VAN ANROOIJ Shirin       |    94.0% |    #9    |     -2     | 📉 Miss     |
| P12 | SCHREIBER Marie          |    53.5% |   #14    |     +2     |            |
| P13 | VAN DER HEIJDEN Inge     |    97.4% |    #5    |     -8     | 📉 Miss     |
| P14 | CARRIER Rafaelle         |    79.7% |   #12    |     -2     |            |
| P15 | NEFF Jolanda             |     5.2% |   #27    |    +12     |            |
| P16 | BETSEMA Denise           |     9.3% |   #22    |     +6     |            |
| P17 | WORST Annemarie          |     4.4% |   #31    |    +14     |            |
| P18 | GARIBOLDI Rebecca        |     1.5% |   #44    |    +26     |            |
| P19 | SARKISOV Alyssa          |     1.0% |   #48    |    +29     |            |
| P20 | GUNSALUS Elizabeth       |     1.9% |   #41    |    +21     |            |

---

### Men Elite Results

| Metric         | Value | Target |
|---------------|:-----:|:------:|
| **Hits@10**    |  8/10 |   7+   |
| **Hits@3**     |  2/3  |   2+   |
| **Spearman ρ** |  0.27 |  >0.5  |
| **MAE Rank**   |  3.8  |   <3   |

#### Metrics Interpretation

- **Hits@10** (8/10): How many of our top-10 predictions finished in actual top-10? ✅ Met target
- **Hits@3** (2/3): How many of our podium picks made actual podium? ✅ Met target
- **Spearman ρ** (0.27): Rank correlation between predicted and actual order. Poor rank correlation. ❌ Below target
- **MAE Rank** (3.8): On average, our predictions were 3.8 positions off from actual finish. ❌ Below target

#### Predicted Top-10 Breakdown

| Pred Rank | Rider                  | Probability |  Actual | Result |
|:---------:|-----------------------|-----------:|:-------:|:------:|
|     1     | VAN AERT Wout          |       99.1% |    P6   |   ✅    |
|     2     | DEL GROSSO Tibor       |       99.0% |    P2   |   ✅    |
|     3     | NIEUWENHUIS Joris      |       98.9% | DNF/DNS |   ❌    |
|     4     | NYS Thibau             |       98.3% |    P1   |   ✅    |
|     5     | VAN DER HAAR Lars      |       97.8% |   P17   |   ❌    |
|     6     | VERSTRYNGE Emiel       |       97.3% |    P4   |   ✅    |
|     7     | AERTS Toon             |       96.5% |   P10   |   ✅    |
|     8     | VANTHOURENHOUT Michael |       95.1% |    P7   |   ✅    |
|     9     | ORTS LLORET Felipe     |       85.2% |    P8   |   ✅    |
|     10    | SWEECK Laurens         |       68.7% |    P3   |   ✅    |

#### Predicted Podium Breakdown

*Top 3 riders by Top-3 Probability*

| Pred Rank | Rider            | Podium Prob | Actual | Result |
|:---------:|-----------------|-----------:|:------:|:------:|
|     1     | VAN AERT Wout    |       76.3% |   P6   |   ❌    |
|     2     | NYS Thibau       |       70.3% |   P1   |   ✅    |
|     3     | DEL GROSSO Tibor |       48.7% |   P2   |   ✅    |

#### Next 10 Riders (Ranks 11-20)

*How did our near-miss predictions perform?*

| Pred Rank | Rider            | Probability |  Actual | Made Top-10? |
|:---------:|-----------------|-----------:|:-------:|:------------:|
|     11    | WYSEURE Joran    |       62.1% |   P12   |      No      |
|     12    | MICHELS Jente    |       55.2% |   P11   |      No      |
|     13    | HENDRIKX Mees    |       44.3% |    P9   |    ✅ Yes!    |
|     14    | KAMP Ryan        |       44.2% |   P14   |      No      |
|     15    | MASON Cameron    |       40.7% |   P20   |      No      |
|     16    | KUHN Kevin       |       40.7% |   P13   |      No      |
|     17    | VANDEPUTTE Niels |       31.1% |    P5   |    ✅ Yes!    |
|     18    | VANDEBOSCH Toon  |        7.1% |   P22   |      No      |
|     19    | DOUBEY Fabien    |        6.8% | DNF/DNS |      No      |
|     20    | KUYPERS Gerben   |        6.0% |   P16   |      No      |

**Surprises:** HENDRIKX Mees (predicted #13, finished P9), VANDEPUTTE Niels (predicted #17, finished P5)

#### Legacy Metrics (Threshold-based)

*Using 55% confidence threshold*

| Metric             | Value | Calculation                                |
|-------------------|:-----:|-------------------------------------------|
| Recall             | 80.0% | 8 correct / 10 actual top-10               |
| Precision          | 72.7% | 8 correct / 11 predictions above threshold |
| High Conf Accuracy | 87.5% | 7 correct / 8 predictions >70%             |

#### Actual Top-20 Results

*How the race actually unfolded vs our predictions*

| Pos | Rider                  | Our Prob | Our Rank | Rank Error | Status     |
|:---:|-----------------------|--------:|:--------:|:----------:|-----------|
|  P1 | NYS Thibau             |    98.3% |    #4    |     +3     | ✅ Hit      |
|  P2 | DEL GROSSO Tibor       |    99.0% |    #2    |     0      | ✅ Hit      |
|  P3 | SWEECK Laurens         |    68.7% |   #10    |     +7     | ✅ Hit      |
|  P4 | VERSTRYNGE Emiel       |    97.3% |    #6    |     +2     | ✅ Hit      |
|  P5 | VANDEPUTTE Niels       |    31.1% |   #17    |    +12     | 📈 Surprise |
|  P6 | VAN AERT Wout          |    99.1% |    #1    |     -5     | ✅ Hit      |
|  P7 | VANTHOURENHOUT Michael |    95.1% |    #8    |     +1     | ✅ Hit      |
|  P8 | ORTS LLORET Felipe     |    85.2% |    #9    |     +1     | ✅ Hit      |
|  P9 | HENDRIKX Mees          |    44.3% |   #13    |     +4     | 📈 Surprise |
| P10 | AERTS Toon             |    96.5% |    #7    |     -3     | ✅ Hit      |
| P11 | MICHELS Jente          |    55.2% |   #12    |     +1     |            |
| P12 | WYSEURE Joran          |    62.1% |   #11    |     -1     |            |
| P13 | KUHN Kevin             |    40.7% |   #16    |     +3     |            |
| P14 | KAMP Ryan              |    44.2% |   #14    |     0      |            |
| P15 | GROSLAMBERT Martin     |     0.5% |   #31    |    +16     |            |
| P16 | KUYPERS Gerben         |     6.0% |   #20    |     +4     |            |
| P17 | VAN DER HAAR Lars      |    97.8% |    #5    |    -12     | 📉 Miss     |
| P18 | MENUT David            |     0.3% |   #33    |    +15     |            |
| P19 | LELANDAIS Rémi         |     1.0% |   #28    |     +9     |            |
| P20 | MASON Cameron          |    40.7% |   #15    |     -5     |            |
---

*Generated by VeloPredict pipeline on 2025-12-28 22:21*