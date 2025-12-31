# Heusden-Zolder Validation Results

**Superprestige** | 2025-12-26

*VeloPredict v6 Performance Analysis*

---

### Men Elite Results

| Metric         | Value | Target |
|---------------|:-----:|:------:|
| **Hits@10**    |  5/10 |   7+   |
| **Hits@3**     |  2/3  |   2+   |
| **Spearman ρ** |  0.68 |  >0.5  |
| **MAE Rank**   |  4.9  |   <3   |

#### Metrics Interpretation

- **Hits@10** (5/10): How many of our top-10 predictions finished in actual top-10? ❌ Below target
- **Hits@3** (2/3): How many of our podium picks made actual podium? ✅ Met target
- **Spearman ρ** (0.68): Rank correlation between predicted and actual order. Moderate rank correlation. ✅ Met target
- **MAE Rank** (4.9): On average, our predictions were 4.9 positions off from actual finish. ❌ Below target

#### Predicted Top-10 Breakdown

| Pred Rank | Rider                  | Probability |  Actual | Result |
|:---------:|-----------------------|-----------:|:-------:|:------:|
|     1     | VAN AERT Wout          |       99.1% |    P2   |   ✅    |
|     2     | DEL GROSSO Tibor       |       98.8% |    P1   |   ✅    |
|     3     | NIEUWENHUIS Joris      |       98.6% | DNF/DNS |   ❌    |
|     4     | NYS Thibau             |       97.8% |   P14   |   ❌    |
|     5     | SWEECK Laurens         |       97.1% | DNF/DNS |   ❌    |
|     6     | VANTHOURENHOUT Michael |       94.4% |    P3   |   ✅    |
|     7     | VANDEPUTTE Niels       |       93.3% |    P4   |   ✅    |
|     8     | MASON Cameron          |       86.6% |   P19   |   ❌    |
|     9     | MICHELS Jente          |       63.1% | DNF/DNS |   ❌    |
|     10    | WYSEURE Joran          |       52.0% |    P5   |   ✅    |

#### Predicted Podium Breakdown

*Top 3 riders by Top-3 Probability*

| Pred Rank | Rider            | Podium Prob | Actual | Result |
|:---------:|-----------------|-----------:|:------:|:------:|
|     1     | VAN AERT Wout    |       98.1% |   P2   |   ✅    |
|     2     | DEL GROSSO Tibor |       70.3% |   P1   |   ✅    |
|     3     | NYS Thibau       |       60.2% |  P14   |   ❌    |

#### Next 10 Riders (Ranks 11-20)

*How did our near-miss predictions perform?*

| Pred Rank | Rider                | Probability |  Actual | Made Top-10? |
|:---------:|---------------------|-----------:|:-------:|:------------:|
|     11    | AGOSTINACCHIO Mattia |       44.5% |   P18   |      No      |
|     12    | KUHN Kevin           |       11.4% |    P7   |    ✅ Yes!    |
|     13    | HENDRIKX Mees        |       11.4% |    P8   |    ✅ Yes!    |
|     14    | DE CLERCQ Naud       |       10.8% |   P43   |      No      |
|     15    | JANSSEN Wout         |        9.5% |   P13   |      No      |
|     16    | BERTOLINI Gioele     |        6.7% |   P15   |      No      |
|     17    | SOETE Daan           |        6.5% |   P24   |      No      |
|     18    | DE BRUYCKERE Kay     |        5.9% | DNF/DNS |      No      |
|     19    | HORNY Clement        |        5.4% |   P27   |      No      |
|     20    | KUYPERS Gerben       |        3.6% |   P10   |    ✅ Yes!    |

**Surprises:** KUHN Kevin (predicted #12, finished P7), HENDRIKX Mees (predicted #13, finished P8), KUYPERS Gerben (predicted #20, finished P10)

#### Legacy Metrics (Threshold-based)

*Using 55% confidence threshold*

| Metric             | Value | Calculation                               |
|-------------------|:-----:|------------------------------------------|
| Recall             | 40.0% | 4 correct / 10 actual top-10              |
| Precision          | 66.7% | 4 correct / 6 predictions above threshold |
| High Conf Accuracy | 66.7% | 4 correct / 6 predictions >70%            |

#### Actual Top-20 Results

*How the race actually unfolded vs our predictions*

| Pos | Rider                  | Our Prob | Our Rank | Rank Error | Status     |
|:---:|-----------------------|--------:|:--------:|:----------:|-----------|
|  P1 | Tibor Del Grosso       |    98.8% |    #2    |     +1     | ✅ Hit      |
|  P2 | Wout van Aert          |    99.1% |    #1    |     -1     | ✅ Hit      |
|  P3 | Michael Vanthourenhout |    94.4% |    #6    |     +3     | ✅ Hit      |
|  P4 | Niels Vandeputte       |    93.3% |    #7    |     +3     | ✅ Hit      |
|  P5 | Joran Wyseure          |    52.0% |   #10    |     +5     | ✅ Hit      |
|  P6 | Felipe Orts Lloret     |     3.4% |   #21    |    +15     | 📈 Surprise |
|  P7 | Kevin Kuhn             |    11.4% |   #12    |     +5     | 📈 Surprise |
|  P8 | Mees Hendrikx          |    11.4% |   #13    |     +5     | 📈 Surprise |
|  P9 | Filippo Fontana        |     1.9% |   #30    |    +21     | 📈 Surprise |
| P10 | Gerben Kuypers         |     3.6% |   #20    |    +10     | 📈 Surprise |
| P11 | Aaron Dockx            |      N/A |   N/A    |    N/A     | ❓ Unknown  |
| P12 | Antoine Jamin          |     2.1% |   #28    |    +16     |            |
| P13 | Wout Janssen           |     9.5% |   #15    |     +2     |            |
| P14 | Thibau Nys             |    97.8% |    #4    |    -10     | 📉 Miss     |
| P15 | Gioele Bertolini       |     6.7% |   #16    |     +1     |            |
| P16 | Anton Ferdinande       |     1.9% |   #31    |    +15     |            |
| P17 | Léo Bisiaux            |     1.6% |   #32    |    +15     |            |
| P18 | Mattia Agostinacchio   |    44.5% |   #11    |     -7     |            |
| P19 | Cameron Mason          |    86.6% |    #8    |    -11     | 📉 Miss     |
| P20 | Thomas Mein            |     2.1% |   #27    |     +7     |            |

---

### Women Elite Results

| Metric         | Value | Target |
|---------------|:-----:|:------:|
| **Hits@10**    |  6/10 |   7+   |
| **Hits@3**     |  2/3  |   2+   |
| **Spearman ρ** |  0.69 |  >0.5  |
| **MAE Rank**   |  4.9  |   <3   |

#### Metrics Interpretation

- **Hits@10** (6/10): How many of our top-10 predictions finished in actual top-10? ❌ Below target
- **Hits@3** (2/3): How many of our podium picks made actual podium? ✅ Met target
- **Spearman ρ** (0.69): Rank correlation between predicted and actual order. Moderate rank correlation. ✅ Met target
- **MAE Rank** (4.9): On average, our predictions were 4.9 positions off from actual finish. ❌ Below target

#### Predicted Top-10 Breakdown

| Pred Rank | Rider                | Probability |  Actual | Result |
|:---------:|---------------------|-----------:|:-------:|:------:|
|     1     | VAN DER HEIJDEN Inge |       98.6% |    P4   |   ✅    |
|     2     | VAN ALPHEN Aniek     |       96.7% |    P3   |   ✅    |
|     3     | CASASOLA Sara        |       95.3% | DNF/DNS |   ❌    |
|     4     | VAS Kata Blanka      |       94.9% |    P2   |   ✅    |
|     5     | FOUQUENET Amandine   |       90.4% |    P1   |   ✅    |
|     6     | BROUWERS Julie       |       81.0% |    P9   |   ✅    |
|     7     | TRUYEN Marthe        |       73.0% |   P20   |   ❌    |
|     8     | CABACA Mae           |       55.3% |   P21   |   ❌    |
|     9     | CLAUZEL Hélène       |       26.4% | DNF/DNS |   ❌    |
|     10    | CARRIER Rafaelle     |       25.6% |   P10   |   ✅    |

#### Predicted Podium Breakdown

*Top 3 riders by Top-3 Probability*

| Pred Rank | Rider                | Podium Prob | Actual | Result |
|:---------:|---------------------|-----------:|:------:|:------:|
|     1     | VAS Kata Blanka      |       58.1% |   P2   |   ✅    |
|     2     | VAN DER HEIJDEN Inge |       14.5% |   P4   |   ❌    |
|     3     | VAN ALPHEN Aniek     |        1.2% |   P3   |   ✅    |

#### Next 10 Riders (Ranks 11-20)

*How did our near-miss predictions perform?*

| Pred Rank | Rider                    | Probability |  Actual | Made Top-10? |
|:---------:|-------------------------|-----------:|:-------:|:------------:|
|     11    | NORBERT RIBEROLLE Marion |       25.6% |    P5   |    ✅ Yes!    |
|     12    | NEFF Jolanda             |       13.7% |    P8   |    ✅ Yes!    |
|     13    | GARIBOLDI Rebecca        |       10.0% |   P19   |      No      |
|     14    | VAN SINAEY Xaydee        |        8.7% |   P39   |      No      |
|     15    | SCHREIBER Marie          |        7.5% |    P7   |    ✅ Yes!    |
|     16    | BORELLO Carlotta         |        7.0% |   P25   |      No      |
|     17    | DE BEER Jamie            |        6.4% | DNF/DNS |      No      |
|     18    | MOLENGRAAF Lauren        |        3.8% |   P24   |      No      |
|     19    | DURAFFOURG Lauriane      |        3.5% | DNF/DNS |      No      |
|     20    | BURQUIER Line            |        3.5% |   P11   |      No      |

**Surprises:** NORBERT RIBEROLLE Marion (predicted #11, finished P5), NEFF Jolanda (predicted #12, finished P8), SCHREIBER Marie (predicted #15, finished P7)

#### Legacy Metrics (Threshold-based)

*Using 55% confidence threshold*

| Metric             | Value | Calculation                               |
|-------------------|:-----:|------------------------------------------|
| Recall             | 50.0% | 5 correct / 10 actual top-10              |
| Precision          | 71.4% | 5 correct / 7 predictions above threshold |
| High Conf Accuracy | 83.3% | 5 correct / 6 predictions >70%            |

#### Actual Top-20 Results

*How the race actually unfolded vs our predictions*

| Pos | Rider                    | Our Prob | Our Rank | Rank Error | Status     |
|:---:|-------------------------|--------:|:--------:|:----------:|-----------|
|  P1 | Amandine Fouquenet       |    90.4% |    #5    |     +4     | ✅ Hit      |
|  P2 | Kata Blanka Vas          |    94.9% |    #4    |     +2     | ✅ Hit      |
|  P3 | Aniek van Alphen         |    96.7% |    #2    |     -1     | ✅ Hit      |
|  P4 | Inge van der Heijden     |    98.6% |    #1    |     -3     | ✅ Hit      |
|  P5 | Marion Norbert Riberolle |    25.6% |   #11    |     +6     | 📈 Surprise |
|  P6 | Fleur Moors              |     1.8% |   #26    |    +20     | 📈 Surprise |
|  P7 | Marie Schreiber          |     7.5% |   #15    |     +8     | 📈 Surprise |
|  P8 | Jolanda Neff             |    13.7% |   #12    |     +4     | 📈 Surprise |
|  P9 | Julie Brouwers           |    81.0% |    #6    |     -3     | ✅ Hit      |
| P10 | Rafaelle Carrier         |    25.6% |   #10    |     0      | ✅ Hit      |
| P11 | Line Burquier            |     3.5% |   #20    |     +9     |            |
| P12 | Bloeme Kalis             |     3.2% |   #22    |    +10     |            |
| P13 | Annemarie Worst          |      N/A |   N/A    |    N/A     | ❓ Unknown  |
| P14 | Jinse Peeters            |     3.1% |   #23    |     +9     |            |
| P15 | Elizabeth Gunsalus       |     1.6% |   #27    |    +12     |            |
| P16 | Rebekka Estermann        |     0.3% |   #70    |    +54     |            |
| P17 | Judith Krahl             |     1.9% |   #25    |     +8     |            |
| P18 | Letizia Borghesi         |     1.2% |   #30    |    +12     |            |
| P19 | Rebecca Gariboldi        |    10.0% |   #13    |     -6     |            |
| P20 | Marthe Truyen            |    73.0% |    #7    |    -13     | 📉 Miss     |
---

*Generated by VeloPredict pipeline on 2025-12-26 08:42*