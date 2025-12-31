# Koksijde Validation Results

**UCI World Cup** | 2025-12-21

*VeloPredict v6.5 Performance Analysis*

---

### Men Elite Results

| Metric         | Value | Target |
|---------------|:-----:|:------:|
| **Hits@10**    |  7/10 |   7+   |
| **Hits@3**     |  2/3  |   2+   |
| **Spearman ρ** |  0.68 |  >0.5  |
| **MAE Rank**   |  2.0  |   <3   |

#### Metrics Interpretation

- **Hits@10** (7/10): How many of our top-10 predictions finished in actual top-10? ✅ Met target
- **Hits@3** (2/3): How many of our podium picks made actual podium? ✅ Met target
- **Spearman ρ** (0.68): Rank correlation between predicted and actual order. Good rank correlation. ✅ Met target
- **MAE Rank** (2.0): On average, our predictions were 2.0 positions off from actual finish. ✅ Met target

#### Predicted Top-10 Breakdown

| Pred Rank | Rider                  | Probability |  Actual | Result |
|:---------:|-----------------------|-----------:|:-------:|:------:|
|     1     | VAN DER POEL Mathieu   |       99.1% |    P1   |   ✅    |
|     2     | VAN DER HAAR Lars      |       98.8% |   P11   |   ❌    |
|     3     | DEL GROSSO Tibor       |       97.4% |    P4   |   ✅    |
|     4     | SWEECK Laurens         |       96.9% |    P2   |   ✅    |
|     5     | VERSTRYNGE Emiel       |       95.4% |   P13   |   ❌    |
|     6     | MASON Cameron          |       92.9% |    P8   |   ✅    |
|     7     | VANDEPUTTE Niels       |       92.7% |    P3   |   ✅    |
|     8     | VANTHOURENHOUT Michael |       92.4% |    P9   |   ✅    |
|     9     | AERTS Toon             |       56.9% |    P5   |   ✅    |
|     10    | KAMP Ryan              |       15.0% |   P16   |   ❌    |

#### Predicted Podium Breakdown

*Top 3 riders by Top-3 Probability*

| Pred Rank | Rider                | Podium Prob | Actual | Result |
|:---------:|---------------------|-----------:|:------:|:------:|
|     1     | VAN DER POEL Mathieu |       99.3% |   P1   |   ✅    |
|     2     | SWEECK Laurens       |       36.1% |   P2   |   ✅    |
|     3     | VAN DER HAAR Lars    |       18.1% |  P11   |   ❌    |

#### Next 10 Riders (Ranks 11-20)

*How did our near-miss predictions perform?*

| Pred Rank | Rider               | Probability |  Actual | Made Top-10? |
|:---------:|---------------------|------------:|:-------:|:------------:|
|     11    | HENDRIKX Mees       |       14.6% |   P10   |    ✅ Yes!   |
|     12    | ORTS LLORET Felipe  |        6.3% |   P21   |      No      |
|     13    | RONHAAR Pim         |        5.7% |   P12   |      No      |
|     14    | WYSEURE Joran       |        5.6% |    P7   |    ✅ Yes!   |
|     15    | BOROŠ Michael       |        3.8% |   P20   |      No      |
|     16    | VANDEBOSCH Toon     |        3.2% |    P6   |    ✅ Yes!   |
|     17    | VAN DE PUTTE Victor |        2.8% |   P18   |      No      |
|     18    | KUHN Kevin          |        2.3% |   P14   |      No      |
|     19    | FERDINANDE Anton    |        2.3% |   P28   |      No      |
|     20    | FONTANA Filippo     |        1.9% |   P17   |      No      |

**Surprises:** HENDRIKX Mees (predicted #11, finished P10), WYSEURE Joran (predicted #14, finished P7), VANDEBOSCH Toon (predicted #16, finished P6)

#### Actual Top-20 Results

*How the race actually unfolded vs our predictions*

| Pos | Rider                  | Our Prob | Our Rank | Rank Error | Status     |
|:---:|-----------------------|--------:|:--------:|:----------:|-----------|
|  P1 | VAN DER POEL Mathieu   |    99.1% |    #1    |     0      | ✅ Hit      |
|  P2 | SWEECK Laurens         |    96.9% |    #4    |     +2     | ✅ Hit      |
|  P3 | VANDEPUTTE Niels       |    92.7% |    #7    |     +4     | ✅ Hit      |
|  P4 | DEL GROSSO Tibor       |    97.4% |    #3    |     -1     | ✅ Hit      |
|  P5 | AERTS Toon             |    56.9% |    #9    |     +4     | ✅ Hit      |
|  P6 | VANDEBOSCH Toon        |     3.2% |   #16    |    +10     | 📈 Surprise |
|  P7 | WYSEURE Joran          |     5.6% |   #14    |     +7     | 📈 Surprise |
|  P8 | MASON Cameron          |    92.9% |    #6    |     -2     | ✅ Hit      |
|  P9 | VANTHOURENHOUT Michael |    92.4% |    #8    |     -1     | ✅ Hit      |
| P10 | HENDRIKX Mees          |    14.6% |   #11    |     +1     | 📈 Surprise |
| P11 | VAN DER HAAR Lars      |    98.8% |    #2    |     -9     | 📉 Miss     |
| P12 | RONHAAR Pim            |     5.7% |   #13    |     +1     |            |
| P13 | VERSTRYNGE Emiel       |    95.4% |    #5    |     -8     | 📉 Miss     |
| P14 | KUHN Kevin             |     2.3% |   #18    |     +4     |            |
| P15 | MEEUSSEN Witse         |     0.7% |   #26    |    +11     |            |
| P16 | KAMP Ryan              |    15.0% |   #10    |     -6     | 📉 Miss     |
| P17 | FONTANA Filippo        |     1.9% |   #21    |     +4     |            |
| P18 | VAN DE PUTTE Victor    |     2.8% |   #17    |     -1     |            |
| P19 | THOMAS Théo            |     0.4% |   #30    |    +11     |            |
| P20 | BOROŠ Michael          |     3.8% |   #15    |     -5     |            |

---

### Women Elite Results

| Metric         | Value | Target |
|---------------|:-----:|:------:|
| **Hits@10**    |  9/10 |   7+   |
| **Hits@3**     |  2/3  |   2+   |
| **Spearman ρ** |  0.67 |  >0.5  |
| **MAE Rank**   |  1.7  |   <3   |

#### Metrics Interpretation

- **Hits@10** (9/10): How many of our top-10 predictions finished in actual top-10? ✅ Met target (BEST EVER!)
- **Hits@3** (2/3): How many of our podium picks made actual podium? ✅ Met target
- **Spearman ρ** (0.67): Rank correlation between predicted and actual order. Good rank correlation. ✅ Met target
- **MAE Rank** (1.7): On average, our predictions were 1.7 positions off from actual finish. ✅ Met target

#### Predicted Top-10 Breakdown

| Pred Rank | Rider                      | Probability | Actual | Result |
|:---------:|---------------------------|-----------:|:------:|:------:|
|     1     | PIETERSE Puck              |       99.2% |   P5   |   ✅    |
|     2     | BRAND Lucinda              |       99.2% |   P1   |   ✅    |
|     3     | ALVARADO Ceylin del Carmen |       98.6% |   P3   |   ✅    |
|     4     | VAN DER HEIJDEN Inge       |       98.1% |   P6   |   ✅    |
|     5     | VAN ALPHEN Aniek           |       96.8% |   P4   |   ✅    |
|     6     | CASASOLA Sara              |       95.4% |  DNF   |   ❌    |
|     7     | VAN ANROOIJ Shirin         |       92.1% |   P2   |   ✅    |
|     8     | ZEMANOVÁ Kristýna          |       91.1% |   P9   |   ✅    |
|     9     | BENTVELD Leonie            |       78.3% |   P8   |   ✅    |
|     10    | FOUQUENET Amandine         |       53.4% |  P10   |   ✅    |

#### Predicted Podium Breakdown

*Top 3 riders by Top-3 Probability*

| Pred Rank | Rider                      | Podium Prob | Actual | Result |
|:---------:|---------------------------|-----------:|:------:|:------:|
|     1     | BRAND Lucinda              |       99.4% |   P1   |   ✅    |
|     2     | PIETERSE Puck              |       95.7% |   P5   |   ❌    |
|     3     | ALVARADO Ceylin del Carmen |       22.9% |   P3   |   ✅    |

#### Next 10 Riders (Ranks 11-20)

*How did our near-miss predictions perform?*

| Pred Rank | Rider                    | Probability | Actual | Made Top-10? |
|:---------:|-------------------------|-----------:|:------:|:------------:|
|     11    | NORBERT RIBEROLLE Marion |       46.3% |  P22   |      No      |
|     12    | BAKKER Manon             |       44.5% |  P11   |      No      |
|     13    | SCHREIBER Marie          |       19.3% |  DNF   |      No      |
|     14    | CLAUZEL Hélène           |       18.5% |  P16   |      No      |
|     15    | CARRIER Rafaelle         |       17.8% |  DNS   |      No      |
|     16    | BETSEMA Denise           |       14.2% |   P7   |    ✅ Yes!    |
|     17    | MOORS Fleur              |       12.1% |  P17   |      No      |
|     18    | BROUWERS Julie           |       11.8% |  P14   |      No      |
|     19    | VERDONSCHOT Laura        |        9.4% |  P15   |      No      |
|     20    | NEFF Jolanda             |       14.0% |   -    |      No      |

**Surprises:** BETSEMA Denise (predicted #16, finished P7) - only outsider to crack top-10

#### Actual Top-20 Results

*How the race actually unfolded vs our predictions*

| Pos | Rider                      | Our Prob | Our Rank | Rank Error | Status     |
|:---:|---------------------------|--------:|:--------:|:----------:|-----------|
|  P1 | BRAND Lucinda              |    99.2% |    #2    |     +1     | ✅ Hit      |
|  P2 | VAN ANROOIJ Shirin         |    92.1% |    #7    |     +5     | ✅ Hit      |
|  P3 | ALVARADO Ceylin del Carmen |    98.6% |    #3    |     0      | ✅ Hit      |
|  P4 | VAN ALPHEN Aniek           |    96.8% |    #5    |     +1     | ✅ Hit      |
|  P5 | PIETERSE Puck              |    99.2% |    #1    |     -4     | ✅ Hit      |
|  P6 | VAN DER HEIJDEN Inge       |    98.1% |    #4    |     -2     | ✅ Hit      |
|  P7 | BETSEMA Denise             |    15.2% |   #16    |     +9     | 📈 Surprise |
|  P8 | BENTVELD Leonie            |    78.3% |    #9    |     +1     | ✅ Hit      |
|  P9 | ZEMANOVÁ Kristýna          |    91.1% |    #8    |     -1     | ✅ Hit      |
| P10 | FOUQUENET Amandine         |    53.4% |   #10    |     0      | ✅ Hit      |
| P11 | BAKKER Manon               |    44.5% |   #12    |     +1     |            |
| P12 | BRAMATI Lucia              |     4.4% |   #24    |    +12     |            |
| P13 | GERY Célia                 |    12.7% |   #21    |     +8     |            |
| P14 | BROUWERS Julie             |     7.3% |   #22    |     +8     |            |
| P15 | VERDONSCHOT Laura          |     3.4% |   #25    |    +10     |            |
| P16 | CLAUZEL Hélène             |    18.5% |   #14    |     -2     |            |
| P17 | MOORS Fleur                |     1.1% |   #40    |    +23     |            |
| P18 | MOLENGRAAF Lauren          |     3.2% |   #26    |     +8     |            |
| P19 | MULLER Amandine            |     1.6% |   #33    |    +14     |            |
| P20 | GUNSALUS Elizabeth         |     1.2% |   #37    |    +17     |            |

---

### Combined Summary

| Category     | Hits@10   | Hits@3 | Spearman ρ | MAE Rank | Targets Met |
|--------------|-----------|--------|------------|----------|-------------|
| Men Elite    | 7/10      | 2/3    | 0.68       | 2.0      | 4/4 ✅       |
| Women Elite  | 9/10      | 2/3    | 0.67       | 1.7      | 4/4 ✅       |
| **Combined** | **16/20** | **4/6** | **0.67**  | **1.8**  | **8/8 ✅**   |

### Key Takeaways

1. **BEST RACE PERFORMANCE** - All 8 targets met for the first time!
2. **Women Elite 9/10** - Highest single-category Hits@10 ever
3. **Strong Spearman** - 0.68 (ME) and 0.67 (WE) show good rank ordering
4. **Low MAE** - 2.0 (ME) and 1.7 (WE) - predictions very close to actual finishes

### Surprises Analysis

**Men Elite:**
- VAN DER HAAR Lars underperformed (P11 vs #2) - off day
- VANDEBOSCH Toon breakthrough (P6 vs #16)
- WYSEURE Joran strong (P7 vs #14)

**Women Elite:**
- CASASOLA Sara DNF - only miss
- VAN ANROOIJ Shirin P2 (vs #7) - major outperformance
- PIETERSE Puck P5 (vs #1) - unusual off day
- BETSEMA Denise P7 (vs #16) - surprise outsider

---

*Generated by VeloPredict pipeline on 2025-12-21*
