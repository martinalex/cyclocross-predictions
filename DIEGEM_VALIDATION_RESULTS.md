# Diegem Validation Results

**Superprestige** | 2025-12-30

*VeloPredict v6 Performance Analysis*

---

### Men Elite Results

| Metric         | Value | Target |
|---------------|:-----:|:------:|
| **Hits@10**    |  6/10 |   7+   |
| **Hits@3**     |  2/3  |   2+   |
| **Spearman ρ** |  0.90 |  >0.5  |
| **MAE Rank**   |  2.9  |   <3   |

#### Metrics Interpretation

- **Hits@10** (6/10): How many of our top-10 predictions finished in actual top-10? ❌ Below target
- **Hits@3** (2/3): How many of our podium picks made actual podium? ✅ Met target
- **Spearman ρ** (0.90): Rank correlation between predicted and actual order. Strong rank correlation. ✅ Met target
- **MAE Rank** (2.9): On average, our predictions were 2.9 positions off from actual finish. ✅ Met target

#### Predicted Top-10 Breakdown

| Pred Rank | Rider                  | Probability |  Actual | Result |
|:---------:|-----------------------|-----------:|:-------:|:------:|
|     1     | NIEUWENHUIS Joris      |       99.2% | DNF/DNS |   ❌    |
|     2     | DEL GROSSO Tibor       |       99.1% |    P1   |   ✅    |
|     3     | SWEECK Laurens         |       98.5% | DNF/DNS |   ❌    |
|     4     | NYS Thibau             |       98.4% |    P3   |   ✅    |
|     5     | VANTHOURENHOUT Michael |       96.1% |    P6   |   ✅    |
|     6     | VANDEPUTTE Niels       |       94.7% |    P5   |   ✅    |
|     7     | ORTS LLORET Felipe     |       91.0% |    P8   |   ✅    |
|     8     | MASON Cameron          |       72.4% |   P22   |   ❌    |
|     9     | MICHELS Jente          |       64.1% |   P10   |   ✅    |
|     10    | LOOCKX Lander          |       45.6% |   P13   |   ❌    |

#### Predicted Podium Breakdown

*Top 3 riders by Top-3 Probability*

| Pred Rank | Rider             | Podium Prob |  Actual | Result |
|:---------:|------------------|-----------:|:-------:|:------:|
|     1     | DEL GROSSO Tibor  |       77.1% |    P1   |   ✅    |
|     2     | NYS Thibau        |       76.8% |    P3   |   ✅    |
|     3     | NIEUWENHUIS Joris |       61.7% | DNF/DNS |   ❌    |

#### Next 10 Riders (Ranks 11-20)

*How did our near-miss predictions perform?*

| Pred Rank | Rider                | Probability |  Actual | Made Top-10? |
|:---------:|---------------------|-----------:|:-------:|:------------:|
|     11    | AGOSTINACCHIO Mattia |       32.1% | DNF/DNS |      No      |
|     12    | FERDINANDE Anton     |       17.7% |   P14   |      No      |
|     13    | VANDEBOSCH Toon      |       15.0% | DNF/DNS |      No      |
|     14    | FONTANA Filippo      |       13.1% |    P9   |    ✅ Yes!    |
|     15    | HENDRIKX Mees        |       13.0% |    P4   |    ✅ Yes!    |
|     16    | WYSEURE Joran        |       12.8% |    P2   |    ✅ Yes!    |
|     17    | JAMIN Antoine        |       12.7% |   P23   |      No      |
|     18    | JANSSEN Wout         |       12.5% | DNF/DNS |      No      |
|     19    | KUHN Kevin           |       11.4% |   P12   |      No      |
|     20    | MEEUSSEN Witse       |       10.2% | DNF/DNS |      No      |

**Surprises:** FONTANA Filippo (predicted #14, finished P9), HENDRIKX Mees (predicted #15, finished P4), WYSEURE Joran (predicted #16, finished P2)

#### Legacy Metrics (Threshold-based)

*Using 55% confidence threshold*

| Metric             | Value | Calculation                               |
|-------------------|:-----:|------------------------------------------|
| Recall             | 60.0% | 6 correct / 10 actual top-10              |
| Precision          | 85.7% | 6 correct / 7 predictions above threshold |
| High Conf Accuracy | 83.3% | 5 correct / 6 predictions >70%            |

#### Actual Top-20 Results

*How the race actually unfolded vs our predictions*

| Pos | Rider                  | Our Prob | Our Rank | Rank Error | Status     |
|:---:|-----------------------|--------:|:--------:|:----------:|-----------|
|  P1 | DEL GROSSO Tibor       |    99.1% |    #2    |     +1     | ✅ Hit      |
|  P2 | WYSEURE Joran          |    12.8% |   #16    |    +14     | 📈 Surprise |
|  P3 | NYS Thibau             |    98.4% |    #4    |     +1     | ✅ Hit      |
|  P4 | HENDRIKX Mees          |    13.0% |   #15    |    +11     | 📈 Surprise |
|  P5 | VANDEPUTTE Niels       |    94.7% |    #6    |     +1     | ✅ Hit      |
|  P6 | VANTHOURENHOUT Michael |    96.1% |    #5    |     -1     | ✅ Hit      |
|  P7 | KUYPERS Gerben         |     2.3% |   #32    |    +25     | 📈 Surprise |
|  P8 | ORTS LLORET Felipe     |    91.0% |    #7    |     -1     | ✅ Hit      |
|  P9 | FONTANA Filippo        |    13.1% |   #14    |     +5     | 📈 Surprise |
| P10 | MICHELS Jente          |    64.1% |    #9    |     -1     | ✅ Hit      |
| P11 | CORSUS Yordi           |     8.0% |   #22    |    +11     |            |
| P12 | KUHN Kevin             |    11.4% |   #19    |     +7     |            |
| P13 | LOOCKX Lander          |    45.6% |   #10    |     -3     | 📉 Miss     |
| P14 | FERDINANDE Anton       |    17.7% |   #12    |     -2     |            |
| P15 | BERTOLINI Gioele       |     6.5% |   #23    |     +8     |            |
| P16 | LAURYSSEN Yorben       |     4.4% |   #25    |     +9     |            |
| P17 | AGOSTINACCHIO Filippo  |     0.4% |   #47    |    +30     |            |
| P18 | HORNY Clement          |     2.1% |   #33    |    +15     |            |
| P19 | BOROŠ Michael          |     4.0% |   #26    |     +7     |            |
| P20 | REMIJN Senna           |     3.2% |   #29    |     +9     |            |

---

### Women Elite Results

| Metric         | Value | Target |
|---------------|:-----:|:------:|
| **Hits@10**    |  5/10 |   7+   |
| **Hits@3**     |  2/3  |   2+   |
| **Spearman ρ** |  0.37 |  >0.5  |
| **MAE Rank**   |  3.5  |   <3   |

#### Metrics Interpretation

- **Hits@10** (5/10): How many of our top-10 predictions finished in actual top-10? ❌ Below target
- **Hits@3** (2/3): How many of our podium picks made actual podium? ✅ Met target
- **Spearman ρ** (0.37): Rank correlation between predicted and actual order. Weak rank correlation. ❌ Below target
- **MAE Rank** (3.5): On average, our predictions were 3.5 positions off from actual finish. ❌ Below target

#### Predicted Top-10 Breakdown

| Pred Rank | Rider                      | Probability |  Actual | Result |
|:---------:|---------------------------|-----------:|:-------:|:------:|
|     1     | PIETERSE Puck              |       99.2% |    P1   |   ✅    |
|     2     | ALVARADO Ceylin Del Carmen |       99.0% |    P3   |   ✅    |
|     3     | NORBERT RIBEROLLE Marion   |       97.5% | DNF/DNS |   ❌    |
|     4     | VAN ALPHEN Aniek           |       97.4% |    P7   |   ✅    |
|     5     | CASASOLA Sara              |       96.3% | DNF/DNS |   ❌    |
|     6     | VAS Kata Blanka            |       94.6% |    P4   |   ✅    |
|     7     | VAN DER HEIJDEN Inge       |       77.3% | DNF/DNS |   ❌    |
|     8     | VAN ANROOIJ Shirin         |       58.3% | DNF/DNS |   ❌    |
|     9     | CARRIER Rafaelle           |       56.7% |   P16   |   ❌    |
|     10    | SCHREIBER Marie            |       47.7% |    P2   |   ✅    |

#### Predicted Podium Breakdown

*Top 3 riders by Top-3 Probability*

| Pred Rank | Rider                      | Podium Prob | Actual | Result |
|:---------:|---------------------------|-----------:|:------:|:------:|
|     1     | PIETERSE Puck              |       96.4% |   P1   |   ✅    |
|     2     | VAS Kata Blanka            |       27.2% |   P4   |   ❌    |
|     3     | ALVARADO Ceylin Del Carmen |        6.6% |   P3   |   ✅    |

#### Next 10 Riders (Ranks 11-20)

*How did our near-miss predictions perform?*

| Pred Rank | Rider              | Probability |  Actual | Made Top-10? |
|:---------:|-------------------|-----------:|:-------:|:------------:|
|     11    | HARTOG Larissa     |       43.0% |   P10   |    ✅ Yes!    |
|     12    | CLAUZEL Hélène     |       25.0% |   P11   |      No      |
|     13    | WORST Annemarie    |       24.9% | DNF/DNS |      No      |
|     14    | MOORE Elly         |       23.4% |   P33   |      No      |
|     15    | HAVILAND Alexa     |       22.5% |   P44   |      No      |
|     16    | BURQUIER Line      |       14.0% |    P8   |    ✅ Yes!    |
|     17    | VERDONSCHOT Laura  |        9.8% | DNF/DNS |      No      |
|     18    | GARIBOLDI Rebecca  |        8.4% |    P6   |    ✅ Yes!    |
|     19    | TRUYEN Marthe      |        8.4% | DNF/DNS |      No      |
|     20    | PELLIZOTTI Giorgia |        8.0% | DNF/DNS |      No      |

**Surprises:** HARTOG Larissa (predicted #11, finished P10), BURQUIER Line (predicted #16, finished P8), GARIBOLDI Rebecca (predicted #18, finished P6)

#### Legacy Metrics (Threshold-based)

*Using 55% confidence threshold*

| Metric             | Value  | Calculation                               |
|-------------------|:------:|------------------------------------------|
| Recall             | 40.0%  | 4 correct / 10 actual top-10              |
| Precision          | 80.0%  | 4 correct / 5 predictions above threshold |
| High Conf Accuracy | 100.0% | 4 correct / 4 predictions >70%            |

#### Actual Top-20 Results

*How the race actually unfolded vs our predictions*

| Pos | Rider                      | Our Prob | Our Rank | Rank Error | Status     |
|:---:|---------------------------|--------:|:--------:|:----------:|-----------|
|  P1 | PIETERSE Puck              |    99.2% |    #1    |     0      | ✅ Hit      |
|  P2 | SCHREIBER Marie            |    47.7% |   #10    |     +8     | ✅ Hit      |
|  P3 | ALVARADO Ceylin Del Carmen |    99.0% |    #2    |     -1     | ✅ Hit      |
|  P4 | VAS Kata Blanka            |    94.6% |    #6    |     +2     | ✅ Hit      |
|  P5 | NEFF Jolanda               |     4.6% |   #27    |    +22     | 📈 Surprise |
|  P6 | GARIBOLDI Rebecca          |     8.4% |   #18    |    +12     | 📈 Surprise |
|  P7 | VAN ALPHEN Aniek           |    97.4% |    #4    |     -3     | ✅ Hit      |
|  P8 | BURQUIER Line              |    14.0% |   #16    |     +8     | 📈 Surprise |
|  P9 | BORGHESI Letizia           |     1.4% |   #34    |    +25     | 📈 Surprise |
| P10 | HARTOG Larissa             |    43.0% |   #11    |     +1     | 📈 Surprise |
| P11 | CLAUZEL Hélène             |    25.0% |   #12    |     +1     |            |
| P12 | ASELTINE Mia               |     0.3% |   #70    |    +58     |            |
| P13 | SARKISOV Alyssa            |     4.0% |   #28    |    +15     |            |
| P14 | ESTERMANN Rebekka          |     1.2% |   #36    |    +22     |            |
| P15 | FERRI Elisa                |     0.9% |   #38    |    +23     |            |
| P16 | CARRIER Rafaelle           |    56.7% |    #9    |     -7     | 📉 Miss     |
| P17 | GUNSALUS Elizabeth         |     5.1% |   #26    |     +9     |            |
| P18 | KNOLL Nico                 |     0.6% |   #46    |    +28     |            |
| P19 | BORELLO Carlotta           |     5.9% |   #25    |     +6     |            |
| P20 | CABACA Mae                 |     6.1% |   #24    |     +4     |            |
---

*Generated by VeloPredict pipeline on 2025-12-30 20:22*