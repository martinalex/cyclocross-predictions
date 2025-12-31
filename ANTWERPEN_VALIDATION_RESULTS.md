# Antwerpen Validation Results

**UCI World Cup** | 2025-12-20

*VeloPredict v6 Performance Analysis*

---

### Men Elite Results

| Metric         | Value | Target |
|---------------|:-----:|:------:|
| **Hits@10**    |  6/10 |   7+   |
| **Hits@3**     |  1/3  |   2+   |
| **Spearman ρ** |  0.08 |  >0.5  |
| **MAE Rank**   |  6.0  |   <3   |

#### Metrics Interpretation

- **Hits@10** (6/10): How many of our top-10 predictions finished in actual top-10? ❌ Below target
- **Hits@3** (1/3): How many of our podium picks made actual podium? ❌ Below target
- **Spearman ρ** (0.08): Rank correlation between predicted and actual order. Poor rank correlation. ❌ Below target
- **MAE Rank** (6.0): On average, our predictions were 6.0 positions off from actual finish. ❌ Below target

#### Predicted Top-10 Breakdown

| Pred Rank | Rider                  | Probability |  Actual | Result |
|:---------:|-----------------------|-----------:|:-------:|:------:|
|     1     | VAN AERT Wout          |       99.1% |    P7   |   ✅    |
|     2     | VAN DER POEL Mathieu   |       99.0% |    P1   |   ✅    |
|     3     | VAN DER HAAR Lars      |       98.7% | DNF/DNS |   ❌    |
|     4     | VANTHOURENHOUT Michael |       98.4% |    P8   |   ✅    |
|     5     | NYS Thibau             |       98.0% |   P23   |   ❌    |
|     6     | VANDEPUTTE Niels       |       97.4% |    P5   |   ✅    |
|     7     | NIEUWENHUIS Joris      |       97.1% |   P16   |   ❌    |
|     8     | VERSTRYNGE Emiel       |       95.7% |    P3   |   ✅    |
|     9     | VANDEBOSCH Toon        |       86.4% |   P15   |   ❌    |
|     10    | DEL GROSSO Tibor       |       84.8% |    P6   |   ✅    |

#### Predicted Podium Breakdown

*Top 3 riders by Top-3 Probability*

| Pred Rank | Rider                | Podium Prob | Actual | Result |
|:---------:|---------------------|-----------:|:------:|:------:|
|     1     | VAN DER POEL Mathieu |       98.7% |   P1   |   ✅    |
|     2     | VAN AERT Wout        |       91.0% |   P7   |   ❌    |
|     3     | NYS Thibau           |       50.7% |  P23   |   ❌    |

#### Next 10 Riders (Ranks 11-20)

*How did our near-miss predictions perform?*

| Pred Rank | Rider               | Probability |  Actual | Made Top-10? |
|:---------:|--------------------|-----------:|:-------:|:------------:|
|     11    | SWEECK Laurens      |       83.6% |    P2   |    ✅ Yes!    |
|     12    | MICHELS Jente       |       73.7% | DNF/DNS |      No      |
|     13    | RONHAAR Pim         |       66.9% |    P4   |    ✅ Yes!    |
|     14    | KAMP Ryan           |       46.3% |   P13   |      No      |
|     15    | ORTS LLORET Felipe  |       43.8% |   P12   |      No      |
|     16    | VAN DE PUTTE Victor |       29.1% |   P18   |      No      |
|     17    | HENDRIKX Mees       |       22.4% |    P9   |    ✅ Yes!    |
|     18    | AERTS Toon          |       16.6% |   P11   |      No      |
|     19    | MEEUSSEN Witse      |       11.3% |   P14   |      No      |
|     20    | BOROŠ Michael       |        8.2% |   P20   |      No      |

**Surprises:** SWEECK Laurens (predicted #11, finished P2), RONHAAR Pim (predicted #13, finished P4), HENDRIKX Mees (predicted #17, finished P9)

#### Actual Top-20 Results

*How the race actually unfolded vs our predictions*

| Pos | Rider                  | Our Prob | Our Rank | Rank Error | Status     |
|:---:|-----------------------|--------:|:--------:|:----------:|-----------|
|  P1 | VAN DER POEL Mathieu   |    99.0% |    #2    |     +1     | ✅ Hit      |
|  P2 | SWEECK Laurens         |    83.6% |   #11    |     +9     | 📈 Surprise |
|  P3 | VERSTRYNGE Emiel       |    95.7% |    #8    |     +5     | ✅ Hit      |
|  P4 | RONHAAR Pim            |    66.9% |   #13    |     +9     | 📈 Surprise |
|  P5 | VANDEPUTTE Niels       |    97.4% |    #6    |     +1     | ✅ Hit      |
|  P6 | DEL GROSSO Tibor       |    84.8% |   #10    |     +4     | ✅ Hit      |
|  P7 | VAN AERT Wout          |    99.1% |    #1    |     -6     | ✅ Hit      |
|  P8 | VANTHOURENHOUT Michael |    98.4% |    #4    |     -4     | ✅ Hit      |
|  P9 | HENDRIKX Mees          |    22.4% |   #17    |     +8     | 📈 Surprise |
| P10 | WYSEURE Joran          |     6.6% |   #23    |    +13     | 📈 Surprise |
| P11 | AERTS Toon             |    16.6% |   #18    |     +7     |            |
| P12 | ORTS LLORET Felipe     |    43.8% |   #15    |     +3     |            |
| P13 | KAMP Ryan              |    46.3% |   #14    |     +1     |            |
| P14 | MEEUSSEN Witse         |    11.3% |   #19    |     +5     |            |
| P15 | VANDEBOSCH Toon        |    86.4% |    #9    |     -6     | 📉 Miss     |
| P16 | NIEUWENHUIS Joris      |    97.1% |    #7    |     -9     | 📉 Miss     |
| P17 | FONTANA Filippo        |     1.1% |   #32    |    +15     |            |
| P18 | VAN DE PUTTE Victor    |    29.1% |   #16    |     -2     |            |
| P19 | AGOSTINACCHIO Filippo  |     2.6% |   #28    |     +9     |            |
| P20 | BOROŠ Michael          |     8.2% |   #20    |     0      |            |

---

### Women Elite Results

| Metric         | Value | Target |
|---------------|:-----:|:------:|
| **Hits@10**    |  7/10 |   7+   |
| **Hits@3**     |  2/3  |   2+   |
| **Spearman ρ** |  0.78 |  >0.5  |
| **MAE Rank**   |  3.4  |   <3   |

#### Metrics Interpretation

- **Hits@10** (7/10): How many of our top-10 predictions finished in actual top-10? ✅ Met target
- **Hits@3** (2/3): How many of our podium picks made actual podium? ✅ Met target
- **Spearman ρ** (0.78): Rank correlation between predicted and actual order. Strong rank correlation. ✅ Met target
- **MAE Rank** (3.4): On average, our predictions were 3.4 positions off from actual finish. ❌ Below target

#### Predicted Top-10 Breakdown

| Pred Rank | Rider                      | Probability | Actual | Result |
|:---------:|---------------------------|-----------:|:------:|:------:|
|     1     | BRAND Lucinda              |       99.1% |   P1   |   ✅    |
|     2     | PIETERSE Puck              |       99.0% |   P4   |   ✅    |
|     3     | ALVARADO Ceylin del Carmen |       98.6% |   P2   |   ✅    |
|     4     | VAN DER HEIJDEN Inge       |       98.6% |   P8   |   ✅    |
|     5     | CASASOLA Sara              |       96.8% |   P7   |   ✅    |
|     6     | FOUQUENET Amandine         |       95.6% |  P13   |   ❌    |
|     7     | VAN ALPHEN Aniek           |       95.6% |   P3   |   ✅    |
|     8     | BENTVELD Leonie            |       94.9% |  P10   |   ✅    |
|     9     | NORBERT RIBEROLLE Marion   |       93.9% |  P12   |   ❌    |
|     10    | CLAUZEL Hélène             |       88.3% |  P19   |   ❌    |

#### Predicted Podium Breakdown

*Top 3 riders by Top-3 Probability*

| Pred Rank | Rider                      | Podium Prob | Actual | Result |
|:---------:|---------------------------|-----------:|:------:|:------:|
|     1     | PIETERSE Puck              |       97.7% |   P4   |   ❌    |
|     2     | BRAND Lucinda              |       97.4% |   P1   |   ✅    |
|     3     | ALVARADO Ceylin del Carmen |        9.0% |   P2   |   ✅    |

#### Next 10 Riders (Ranks 11-20)

*How did our near-miss predictions perform?*

| Pred Rank | Rider              | Probability | Actual | Made Top-10? |
|:---------:|-------------------|-----------:|:------:|:------------:|
|     11    | ZEMANOVÁ Kristýna  |       87.6% |   P5   |    ✅ Yes!    |
|     12    | VAN ANROOIJ Shirin |       76.9% |   P6   |    ✅ Yes!    |
|     13    | BAKKER Manon       |       66.0% |   P9   |    ✅ Yes!    |
|     14    | SCHREIBER Marie    |       53.4% |  P18   |      No      |
|     15    | CARRIER Rafaelle   |       43.3% |  P25   |      No      |
|     16    | BETSEMA Denise     |       35.4% |  P11   |      No      |
|     17    | MOORS Fleur        |       30.5% |  P14   |      No      |
|     18    | BROUWERS Julie     |       26.9% |  P16   |      No      |
|     19    | GERY Célia         |       17.2% |  P15   |      No      |
|     20    | GARIBOLDI Rebecca  |       17.0% |  P36   |      No      |

**Surprises:** ZEMANOVÁ Kristýna (predicted #11, finished P5), VAN ANROOIJ Shirin (predicted #12, finished P6), BAKKER Manon (predicted #13, finished P9)

#### Actual Top-20 Results

*How the race actually unfolded vs our predictions*

| Pos | Rider                    | Our Prob | Our Rank | Rank Error | Status     |
|:---:|-------------------------|--------:|:--------:|:----------:|-----------|
|  P1 | BRAND Lucinda            |    99.1% |    #1    |     0      | ✅ Hit      |
|  P2 | ALVARADO Ceylin          |    98.6% |    #3    |     +1     | ✅ Hit      |
|  P3 | VAN ALPHEN Aniek         |    95.6% |    #7    |     +4     | ✅ Hit      |
|  P4 | PIETERSE Puck            |    99.0% |    #2    |     -2     | ✅ Hit      |
|  P5 | ZEMANOVÁ Kristýna        |    87.6% |   #11    |     +6     | 📈 Surprise |
|  P6 | VAN ANROOIJ Shirin       |    76.9% |   #12    |     +6     | 📈 Surprise |
|  P7 | CASASOLA Sara            |    96.8% |    #5    |     -2     | ✅ Hit      |
|  P8 | VAN DER HEIJDEN Inge     |    98.6% |    #4    |     -4     | ✅ Hit      |
|  P9 | BAKKER Manon             |    66.0% |   #13    |     +4     | 📈 Surprise |
| P10 | BENTVELD Leonie          |    94.9% |    #8    |     -2     | ✅ Hit      |
| P11 | BETSEMA Denise           |    35.4% |   #16    |     +5     |            |
| P12 | NORBERT RIBEROLLE Marion |    93.9% |    #9    |     -3     | 📉 Miss     |
| P13 | FOUQUENET Amandine       |    95.6% |    #6    |     -7     | 📉 Miss     |
| P14 | MOORS Fleur              |    30.5% |   #17    |     +3     |            |
| P15 | GERY Célia               |    17.2% |   #19    |     +4     |            |
| P16 | BROUWERS Julie           |    26.9% |   #18    |     +2     |            |
| P17 | BRAMATI Lucia            |    12.4% |   #21    |     +4     |            |
| P18 | SCHREIBER Marie          |    53.4% |   #14    |     -4     |            |
| P19 | CLAUZEL Hélène           |    88.3% |   #10    |     -9     | 📉 Miss     |
| P20 | MULLER Amandine          |     8.4% |   #25    |     +5     |            |
---

*Generated by VeloPredict pipeline on 2025-12-21 08:38*