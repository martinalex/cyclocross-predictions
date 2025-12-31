# Azencross-Loenhout Validation Results

**X2O Trofee** | 2025-12-29

*VeloPredict v6.10 Performance Analysis*

---

### Men Elite Results

| Metric         | Value | Target |
|---------------|:-----:|:------:|
| **Hits@10**    |  6/10 |   7+   |
| **Hits@3**     |  2/3  |   2+   |
| **Spearman ρ** |  0.64 |  >0.5  |
| **MAE Rank**   |  2.7  |   <3   |

#### Metrics Interpretation

- **Hits@10** (6/10): How many of our top-10 predictions finished in actual top-10? ❌ Below target
- **Hits@3** (2/3): How many of our podium picks made actual podium? ✅ Met target
- **Spearman ρ** (0.64): Rank correlation between predicted and actual order. Good rank correlation. ✅ Met target
- **MAE Rank** (2.7): On average, our predictions were 2.7 positions off from actual finish. ✅ Met target

#### Predicted Top-10 Breakdown

| Pred Rank | Rider                | Probability |  Actual | Result |
|:---------:|-----------------------|-----------:|:-------:|:------:|
|     1     | VAN DER POEL Mathieu   |       99.2% |    P1   |   ✅    |
|     2     | NIEUWENHUIS Joris      |       98.7% |    P3   |   ✅    |
|     3     | VAN AERT Wout          |       98.6% |   P10   |   ✅    |
|     4     | NYS Thibau             |       98.2% |   DNS   |   ❌    |
|     5     | SWEECK Laurens         |       97.7% |   DNF   |   ❌    |
|     6     | VANDEPUTTE Niels       |       93.0% |    P2   |   ✅    |
|     7     | AERTS Toon             |       91.1% |    P5   |   ✅    |
|     8     | VAN DER HAAR Lars      |       49.0% |   DNS   |   ❌    |
|     9     | JANSSEN Wout           |       19.0% |   P11   |   ❌    |
|     10    | FERDINANDE Anton       |       13.7% |    P7   |   ✅    |

#### Predicted Podium Breakdown

*Top 3 riders by Top-3 Probability*

| Pred Rank | Rider                | Podium Prob | Actual | Result |
|:---------:|---------------------|-----------:|:------:|:------:|
|     1     | VAN DER POEL Mathieu |       98.2% |   P1   |   ✅    |
|     2     | NYS Thibau           |       73.1% |  DNS   |   ❌    |
|     3     | VAN AERT Wout        |       16.9% |  P10   |   ❌    |

#### Next 10 Riders (Ranks 11-20)

*How did our near-miss predictions perform?*

| Pred Rank | Rider               | Probability |  Actual | Made Top-10? |
|:---------:|--------------------|-----------:|:-------:|:------------:|
|     11    | MEEUSSEN Witse      |       12.3% |   P15   |      No      |
|     12    | SOETE Daan          |       11.6% |   P12   |      No      |
|     13    | VANDEBOSCH Toon     |       10.8% |   P13   |      No      |
|     14    | KAMP Ryan           |        9.7% |    P4   |    ✅ Yes!    |
|     15    | MASON Cameron       |        6.9% |    P8   |    ✅ Yes!    |
|     16    | VAN DE PUTTE Victor |        6.1% |   N/A   |      No      |
|     17    | BERTOLINI Gioele    |        5.0% |    P6   |    ✅ Yes!    |
|     18    | HORNY Clement       |        2.7% |   P27   |      No      |
|     19    | KUYPERS Gerben      |        2.6% |   N/A   |      No      |
|     20    | MEEUSEN Tom         |        2.5% |   P15   |      No      |

**Surprises:** KAMP Ryan (predicted #14, finished P4), MASON Cameron (predicted #15, finished P8), BERTOLINI Gioele (predicted #17, finished P6)

#### Actual Top-20 Results

*How the race actually unfolded vs our predictions*

| Pos | Rider                  | Our Prob | Our Rank | Rank Error | Status     |
|:---:|-----------------------|--------:|:--------:|:----------:|-----------|
|  P1 | VAN DER POEL Mathieu   |    99.2% |    #1    |     0      | ✅ Hit      |
|  P2 | VANDEPUTTE Niels       |    93.0% |    #6    |     +4     | ✅ Hit      |
|  P3 | NIEUWENHUIS Joris      |    98.7% |    #2    |     -1     | ✅ Hit      |
|  P4 | KAMP Ryan              |     9.7% |   #14    |    +10     | 📈 Surprise |
|  P5 | AERTS Toon             |    91.1% |    #7    |     +2     | ✅ Hit      |
|  P6 | BERTOLINI Gioele       |     5.0% |   #17    |    +11     | 📈 Surprise |
|  P7 | FERDINANDE Anton       |    13.7% |   #10    |     +3     | ✅ Hit      |
|  P8 | MASON Cameron          |     6.9% |   #15    |     +7     | 📈 Surprise |
|  P9 | LAURYSSEN Yorben       |     2.2% |   #22    |    +13     | 📈 Surprise |
| P10 | VAN AERT Wout          |    98.6% |    #3    |     -7     | ✅ Hit      |
| P11 | JANSSEN Wout           |    19.0% |    #9    |     -2     | 📉 Miss     |
| P12 | SOETE Daan             |    11.6% |   #12    |     0      |            |
| P13 | VANDEBOSCH Toon        |    10.8% |   #13    |     0      |            |
| P14 | MEIN Thomas            |     2.3% |   #21    |     +7     |            |
| P15 | MEEUSEN Tom            |     2.5% |   #20    |     +5     |            |
| P16 | BETON Damien           |     0.2% |   #39    |    +23     |            |
| P17 | FERRI Tommaso          |     0.4% |   #24    |     +7     |            |
| P18 | AGOSTINACCHIO Filippo  |     0.3% |   #25    |     +7     |            |
| P19 | DE VET Sander          |     0.9% |   #23    |     +4     |            |
| P20 | ODA Hijiri             |     0.2% |   #41    |    +21     |            |

---

### Women Elite Results

| Metric         | Value | Target |
|---------------|:-----:|:------:|
| **Hits@10**    |  6/10 |   7+   |
| **Hits@3**     |  1/3  |   2+   |
| **Spearman ρ** |  0.47 |  >0.5  |
| **MAE Rank**   |  4.3  |   <3   |

#### Metrics Interpretation

- **Hits@10** (6/10): How many of our top-10 predictions finished in actual top-10? ❌ Below target
- **Hits@3** (1/3): How many of our podium picks made actual podium? ❌ Below target
- **Spearman ρ** (0.47): Rank correlation between predicted and actual order. Moderate rank correlation. ❌ Below target
- **MAE Rank** (4.3): On average, our predictions were 4.3 positions off from actual finish. ❌ Below target

#### Predicted Top-10 Breakdown

| Pred Rank | Rider                      | Probability | Actual | Result |
|:---------:|---------------------------|-----------:|:------:|:------:|
|     1     | BRAND Lucinda              |       99.2% |   P1   |   ✅    |
|     2     | ALVARADO Ceylin Del Carmen |       99.0% |  DNS   |   ❌    |
|     3     | KASTELIJN Yara             |       96.9% |  P11   |   ❌    |
|     4     | NORBERT RIBEROLLE Marion   |       96.5% |   P5   |   ✅    |
|     5     | ZEMANOVÁ Kristýna          |       92.6% |   P2   |   ✅    |
|     6     | BAKKER Manon               |       77.4% |   P3   |   ✅    |
|     7     | BROUWERS Julie             |       17.8% |   P8   |   ✅    |
|     8     | MOLENGRAAF Lauren          |       15.2% |  P12   |   ❌    |
|     9     | TRUYEN Marthe              |       10.5% |  P22   |   ❌    |
|     10    | BACKSTEDT Zoe              |       10.1% |   P4   |   ✅    |

#### Predicted Podium Breakdown

*Top 3 riders by Top-3 Probability*

| Pred Rank | Rider                      | Podium Prob | Actual | Result |
|:---------:|---------------------------|-----------:|:------:|:------:|
|     1     | BRAND Lucinda              |       98.0% |   P1   |   ✅    |
|     2     | ALVARADO Ceylin Del Carmen |       35.8% |  DNS   |   ❌    |
|     3     | NORBERT RIBEROLLE Marion   |        6.2% |   P5   |   ❌    |

#### Next 10 Riders (Ranks 11-20)

*How did our near-miss predictions perform?*

| Pred Rank | Rider              | Probability | Actual | Made Top-10? |
|:---------:|-------------------|-----------:|:------:|:------------:|
|     11    | SCHREIBER Marie    |        9.4% |   P9   |    ✅ Yes!    |
|     12    | HARTOG Larissa     |        8.7% |   P7   |    ✅ Yes!    |
|     13    | VERDONSCHOT Laura  |        7.5% |  P13   |      No      |
|     14    | VON BERSWORDT Sophie|       7.0% |  P24   |      No      |
|     15    | CHLADOŇOVÁ Viktória|        6.8% |  P19   |      No      |
|     16    | DE BEER Jamie      |        6.5% |   N/A  |      No      |
|     17    | KRAHL Judith       |        6.0% |   N/A  |      No      |
|     18    | BARTHELS Maïté     |        4.4% |   N/A  |      No      |
|     19    | DE SCHOESITTER Shanyl|      4.3% |   N/A  |      No      |
|     20    | BRAMATI Lucia      |        4.2% |  P14   |      No      |

**Surprises:** SCHREIBER Marie (predicted #11, finished P9), HARTOG Larissa (predicted #12, finished P7), WORST Annemarie (not in top-20, finished P6)

#### Actual Top-20 Results

*How the race actually unfolded vs our predictions*

| Pos | Rider                    | Our Prob | Our Rank | Rank Error | Status     |
|:---:|-------------------------|--------:|:--------:|:----------:|-----------|
|  P1 | BRAND Lucinda            |    99.2% |    #1    |     0      | ✅ Hit      |
|  P2 | ZEMANOVÁ Kristýna        |    92.6% |    #5    |     +3     | ✅ Hit      |
|  P3 | BAKKER Manon             |    77.4% |    #6    |     +3     | ✅ Hit      |
|  P4 | BACKSTEDT Zoe            |    10.1% |   #10    |     +6     | ✅ Hit      |
|  P5 | NORBERT RIBEROLLE Marion |    96.5% |    #4    |     -1     | ✅ Hit      |
|  P6 | WORST Annemarie          |     N/A  |   N/A    |    N/A     | 📈 Surprise |
|  P7 | HARTOG Larissa           |     8.7% |   #12    |     +5     | 📈 Surprise |
|  P8 | BROUWERS Julie           |    17.8% |    #7    |     -1     | ✅ Hit      |
|  P9 | SCHREIBER Marie          |     9.4% |   #11    |     +2     | 📈 Surprise |
| P10 | GARIBOLDI Rebecca        |     3.1% |   #23    |    +13     | 📈 Surprise |
| P11 | KASTELIJN Yara           |    96.9% |    #3    |     -8     | 📉 Miss     |
| P12 | MOLENGRAAF Lauren        |    15.2% |    #8    |     -4     | 📉 Miss     |
| P13 | VERDONSCHOT Laura        |     7.5% |   #13    |     0      |            |
| P14 | BRAMATI Lucia            |     4.2% |   #20    |     +6     |            |
| P15 | SONNEMANS Sara           |     1.9% |   #27    |    +12     |            |
| P16 | KALIS Bloeme             |     N/A  |   N/A    |    N/A     |            |
| P17 | MOS Anniek               |     2.2% |   #26    |     +9     |            |
| P18 | MOES Noï                 |     0.8% |   #35    |    +17     |            |
| P19 | CHLADOŇOVÁ Viktória      |     6.8% |   #15    |     -4     |            |
| P20 | LAURIJSSEN Sanne         |     3.8% |   #21    |     +1     |            |

---

### Key Takeaways

1. **DNS Impact:** 4 predicted riders did not start or finish
   - Men: NYS Thibau (#4), SWEECK Laurens (#5), VAN DER HAAR Lars (#8)
   - Women: ALVARADO Ceylin Del Carmen (#2)

2. **Underrated Performers:**
   - KAMP Ryan (P4, predicted #14)
   - BERTOLINI Gioele (P6, predicted #17)
   - BACKSTEDT Zoe (P4, predicted #10)
   - WORST Annemarie (P6, not in predictions)

3. **Overrated Performers:**
   - KASTELIJN Yara (P11, predicted #3)
   - VAN AERT Wout (P10, predicted #3)

4. **Model Confidence vs Reality:**
   - High-confidence predictions (>90%) performed well when riders started
   - Mid-range predictions (10-30%) had several surprise performances

---

*Generated by VeloPredict pipeline on 2025-12-29*
