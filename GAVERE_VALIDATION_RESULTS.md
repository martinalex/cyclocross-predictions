# Gavere Validation Results

**UCI WC** | 2025-12-26

*VeloPredict v6 Performance Analysis*

---

### Men Elite Results

| Metric         | Value | Target |
|---------------|:-----:|:------:|
| **Hits@10**    |  6/10 |   7+   |
| **Hits@3**     |  2/3  |   2+   |
| **Spearman ρ** |  0.33 |  >0.5  |
| **MAE Rank**   |  5.7  |   <3   |

#### Metrics Interpretation

- **Hits@10** (6/10): How many of our top-10 predictions finished in actual top-10? ❌ Below target
- **Hits@3** (2/3): How many of our podium picks made actual podium? ✅ Met target
- **Spearman ρ** (0.33): Rank correlation between predicted and actual order. Weak rank correlation. ❌ Below target
- **MAE Rank** (5.7): On average, our predictions were 5.7 positions off from actual finish. ❌ Below target

#### Predicted Top-10 Breakdown

| Pred Rank | Rider                  | Probability |  Actual | Result |
|:---------:|-----------------------|-----------:|:-------:|:------:|
|     1     | VAN DER POEL Mathieu   |       99.1% |    P1   |   ✅    |
|     2     | DEL GROSSO Tibor       |       98.9% |    P3   |   ✅    |
|     3     | NIEUWENHUIS Joris      |       98.8% | DNF/DNS |   ❌    |
|     4     | SWEECK Laurens         |       97.8% |   P11   |   ❌    |
|     5     | VANTHOURENHOUT Michael |       96.7% |    P6   |   ✅    |
|     6     | AERTS Toon             |       94.5% |    P4   |   ✅    |
|     7     | VANDEPUTTE Niels       |       92.2% |   P18   |   ❌    |
|     8     | ORTS LLORET Felipe     |       92.1% |   P29   |   ❌    |
|     9     | VAN DER HAAR Lars      |       73.7% |    P9   |   ✅    |
|     10    | NYS Thibau             |       65.9% |    P2   |   ✅    |

#### Predicted Podium Breakdown

*Top 3 riders by Top-3 Probability*

| Pred Rank | Rider                  | Podium Prob | Actual | Result |
|:---------:|-----------------------|-----------:|:------:|:------:|
|     1     | VAN DER POEL Mathieu   |       99.1% |   P1   |   ✅    |
|     2     | DEL GROSSO Tibor       |       81.9% |   P3   |   ✅    |
|     3     | VANTHOURENHOUT Michael |       41.0% |   P6   |   ❌    |

#### Next 10 Riders (Ranks 11-20)

*How did our near-miss predictions perform?*

| Pred Rank | Rider               | Probability |  Actual | Made Top-10? |
|:---------:|--------------------|-----------:|:-------:|:------------:|
|     11    | MICHELS Jente       |       61.1% | DNF/DNS |      No      |
|     12    | KUHN Kevin          |       58.1% | DNF/DNS |      No      |
|     13    | KAMP Ryan           |       56.5% | DNF/DNS |      No      |
|     14    | WYSEURE Joran       |       56.4% |    P7   |    ✅ Yes!    |
|     15    | VANDEBOSCH Toon     |       43.0% |   P14   |      No      |
|     16    | HENDRIKX Mees       |       39.9% |    P8   |    ✅ Yes!    |
|     17    | VERSTRYNGE Emiel    |       39.3% |    P5   |    ✅ Yes!    |
|     18    | FONTANA Filippo     |       19.4% |   P12   |      No      |
|     19    | MASON Cameron       |        8.7% |   P10   |    ✅ Yes!    |
|     20    | VAN DE PUTTE Victor |        8.6% | DNF/DNS |      No      |

**Surprises:** WYSEURE Joran (predicted #14, finished P7), HENDRIKX Mees (predicted #16, finished P8), VERSTRYNGE Emiel (predicted #17, finished P5), MASON Cameron (predicted #19, finished P10)

#### Legacy Metrics (Threshold-based)

*Using 55% confidence threshold*

| Metric             | Value | Calculation                                |
|-------------------|:-----:|-------------------------------------------|
| Recall             | 70.0% | 7 correct / 10 actual top-10               |
| Precision          | 70.0% | 7 correct / 10 predictions above threshold |
| High Conf Accuracy | 62.5% | 5 correct / 8 predictions >70%             |

#### Actual Top-20 Results

*How the race actually unfolded vs our predictions*

| Pos | Rider                  | Our Prob | Our Rank | Rank Error | Status     |
|:---:|-----------------------|--------:|:--------:|:----------:|-----------|
|  P1 | VAN DER POEL Mathieu   |    99.1% |    #1    |     0      | ✅ Hit      |
|  P2 | NYS Thibau             |    65.9% |   #10    |     +8     | ✅ Hit      |
|  P3 | DEL GROSSO Tibor       |    98.9% |    #2    |     -1     | ✅ Hit      |
|  P4 | AERTS Toon             |    94.5% |    #6    |     +2     | ✅ Hit      |
|  P5 | VERSTRYNGE Emiel       |    39.3% |   #17    |    +12     | 📈 Surprise |
|  P6 | VANTHOURENHOUT Michael |    96.7% |    #5    |     -1     | ✅ Hit      |
|  P7 | WYSEURE Joran          |    56.4% |   #14    |     +7     | 📈 Surprise |
|  P8 | HENDRIKX Mees          |    39.9% |   #16    |     +8     | 📈 Surprise |
|  P9 | VAN DER HAAR Lars      |    73.7% |    #9    |     0      | ✅ Hit      |
| P10 | MASON Cameron          |     8.7% |   #19    |     +9     | 📈 Surprise |
| P11 | SWEECK Laurens         |    97.8% |    #4    |     -7     | 📉 Miss     |
| P12 | FONTANA Filippo        |    19.4% |   #18    |     +6     |            |
| P13 | JANSSEN Wout           |     4.0% |   #24    |    +11     |            |
| P14 | VANDEBOSCH Toon        |    43.0% |   #15    |     +1     |            |
| P15 | LELANDAIS Rémi         |     0.2% |   #44    |    +29     |            |
| P16 | BOMMENEL Nathan        |     1.0% |   #28    |    +12     |            |
| P17 | BOROŠ Michael          |     4.6% |   #23    |     +6     |            |
| P18 | VANDEPUTTE Niels       |    92.2% |    #7    |    -11     | 📉 Miss     |
| P19 | MENUT David            |     0.2% |   #54    |    +35     |            |
| P20 | DE BRAUWERE Sil        |     1.5% |   #27    |     +7     |            |

---

### Women Elite Results

| Metric         | Value | Target |
|---------------|:-----:|:------:|
| **Hits@10**    |  7/10 |   7+   |
| **Hits@3**     |  2/3  |   2+   |
| **Spearman ρ** |  0.61 |  >0.5  |
| **MAE Rank**   |  4.5  |   <3   |

#### Metrics Interpretation

- **Hits@10** (7/10): How many of our top-10 predictions finished in actual top-10? ✅ Met target
- **Hits@3** (2/3): How many of our podium picks made actual podium? ✅ Met target
- **Spearman ρ** (0.61): Rank correlation between predicted and actual order. Moderate rank correlation. ✅ Met target
- **MAE Rank** (4.5): On average, our predictions were 4.5 positions off from actual finish. ❌ Below target

#### Predicted Top-10 Breakdown

| Pred Rank | Rider                    | Probability | Actual | Result |
|:---------:|-------------------------|-----------:|:------:|:------:|
|     1     | BRAND Lucinda            |       99.0% |   P1   |   ✅    |
|     2     | PIETERSE Puck            |       98.9% |   P3   |   ✅    |
|     3     | ALVARADO Ceylin          |       98.8% |   P8   |   ✅    |
|     4     | VAN DER HEIJDEN Inge     |       98.6% |   P9   |   ✅    |
|     5     | VAN ALPHEN Aniek         |       97.7% |   P5   |   ✅    |
|     6     | FOUQUENET Amandine       |       97.3% |   P2   |   ✅    |
|     7     | NORBERT RIBEROLLE Marion |       96.7% |  P12   |   ❌    |
|     8     | BENTVELD Leonie          |       96.1% |  P15   |   ❌    |
|     9     | NEFF Jolanda             |       95.0% |  P24   |   ❌    |
|     10    | VAN ANROOIJ Shirin       |       94.5% |   P7   |   ✅    |

#### Predicted Podium Breakdown

*Top 3 riders by Top-3 Probability*

| Pred Rank | Rider           | Podium Prob | Actual | Result |
|:---------:|----------------|-----------:|:------:|:------:|
|     1     | BRAND Lucinda   |       99.3% |   P1   |   ✅    |
|     2     | PIETERSE Puck   |       53.6% |   P3   |   ✅    |
|     3     | ALVARADO Ceylin |       28.1% |   P8   |   ❌    |

#### Next 10 Riders (Ranks 11-20)

*How did our near-miss predictions perform?*

| Pred Rank | Rider                   | Probability | Actual | Made Top-10? |
|:---------:|------------------------|-----------:|:------:|:------------:|
|     11    | BAKKER Manon            |       85.2% |  P22   |      No      |
|     12    | BETSEMA Denise          |       82.1% |  P17   |      No      |
|     13    | VERDONSCHOT Laura       |       66.7% |  P28   |      No      |
|     14    | BROUWERS Julie          |       63.0% |  P20   |      No      |
|     15    | VAS Blanka              |       34.7% |   P4   |    ✅ Yes!    |
|     16    | MOORS Fleur             |       27.5% |  P25   |      No      |
|     17    | CLAUZEL Hélène          |       21.0% |  P16   |      No      |
|     18    | GERY Célia              |       16.9% |   P6   |    ✅ Yes!    |
|     19    | CHLADONOVÁ Viktória     |       13.4% |  P10   |    ✅ Yes!    |
|     20    | LOPEZ DE SAN ROMAN Vida |        6.5% |  P13   |      No      |

**Surprises:** VAS Blanka (predicted #15, finished P4), GERY Célia (predicted #18, finished P6), CHLADONOVÁ Viktória (predicted #19, finished P10)

#### Legacy Metrics (Threshold-based)

*Using 55% confidence threshold*

| Metric             | Value | Calculation                                |
|-------------------|:-----:|-------------------------------------------|
| Recall             | 70.0% | 7 correct / 10 actual top-10               |
| Precision          | 50.0% | 7 correct / 14 predictions above threshold |
| High Conf Accuracy | 58.3% | 7 correct / 12 predictions >70%            |

#### Actual Top-20 Results

*How the race actually unfolded vs our predictions*

| Pos | Rider                    | Our Prob | Our Rank | Rank Error | Status     |
|:---:|-------------------------|--------:|:--------:|:----------:|-----------|
|  P1 | BRAND Lucinda            |    99.0% |    #1    |     0      | ✅ Hit      |
|  P2 | FOUQUENET Amandine       |    97.3% |    #6    |     +4     | ✅ Hit      |
|  P3 | PIETERSE Puck            |    98.9% |    #2    |     -1     | ✅ Hit      |
|  P4 | VAS Blanka               |    34.7% |   #15    |    +11     | 📈 Surprise |
|  P5 | VAN ALPHEN Aniek         |    97.7% |    #5    |     0      | ✅ Hit      |
|  P6 | GERY Célia               |    16.9% |   #18    |    +12     | 📈 Surprise |
|  P7 | VAN ANROOIJ Shirin       |    94.5% |   #10    |     +3     | ✅ Hit      |
|  P8 | ALVARADO Ceylin          |    98.8% |    #3    |     -5     | ✅ Hit      |
|  P9 | VAN DER HEIJDEN Inge     |    98.6% |    #4    |     -5     | ✅ Hit      |
| P10 | CHLADONOVÁ Viktória      |    13.4% |   #19    |     +9     | 📈 Surprise |
| P11 | MULLER Amandine          |     4.1% |   #24    |    +13     |            |
| P12 | NORBERT RIBEROLLE Marion |    96.7% |    #7    |     -5     | 📉 Miss     |
| P13 | LOPEZ DE SAN ROMAN Vida  |     6.5% |   #20    |     +7     |            |
| P14 | CRABBÉ Kiona             |     0.5% |   #42    |    +28     |            |
| P15 | BENTVELD Leonie          |    96.1% |    #8    |     -7     | 📉 Miss     |
| P16 | CLAUZEL Hélène           |    21.0% |   #17    |     +1     |            |
| P17 | BETSEMA Denise           |    82.1% |   #12    |     -5     |            |
| P18 | HARTOG Larissa           |     3.0% |   #26    |     +8     |            |
| P19 | CUSACK Lidia             |     4.2% |   #23    |     +4     |            |
| P20 | BROUWERS Julie           |    63.0% |   #14    |     -6     |            |
---

*Generated by VeloPredict pipeline on 2025-12-27 13:46*