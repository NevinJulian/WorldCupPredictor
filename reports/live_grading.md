# WC 2026 — live forecast grading (A/B)

*Generated 2026-06-16; data as-of 2026-06-14. Running RPS (lower is better) of the **pre-match** prediction for every played WC-2026 match, for three variants on the same fixtures. As-of / leakage-free: each live prediction is built from data strictly before the match's matchday. Frozen = the immutable pre-tournament forecast (group fixtures only). The headline is the live **result-only vs xG-adjusted** A/B.*

## Running RPS

Headline A/B over all 12 graded matches: result-only **0.2022** vs xG-adjusted **0.2022** → tied so far.

| Variant | RPS (all matches) | RPS (group fixtures) | n |
|--|--:|--:|--:|
| Frozen pre-tournament | — | 0.2030 | 12 |
| Live result-only (xG off) | 0.2022 | 0.2022 | 12 |
| Live xG-adjusted (xG on) | 0.2022 | 0.2022 | 12 |

*The group-fixtures column is the clean three-way comparison on identical fixtures; the all-matches column adds knockout games (frozen has no knockout prediction).*

## Per-match

| Date | Stage | Match | Score | Result | Frozen | Result-only | xG-adj |
|--|--|--|:--:|:--:|--:|--:|--:|
| 2026-06-11 | group | Mexico v South Africa | 2-0 | H | 0.0419 | 0.0462 | 0.0462 |
| 2026-06-11 | group | South Korea v Czechia | 2-1 | H | 0.2080 | 0.1982 | 0.1982 |
| 2026-06-12 | group | Canada v Bosnia and Herzegovina | 1-1 | D | 0.2585 | 0.2526 | 0.2526 |
| 2026-06-12 | group | United States v Paraguay | 4-1 | H | 0.2483 | 0.2369 | 0.2369 |
| 2026-06-13 | group | Qatar v Switzerland | 1-1 | D | 0.2352 | 0.2611 | 0.2611 |
| 2026-06-13 | group | Brazil v Morocco | 1-1 | D | 0.1633 | 0.1359 | 0.1359 |
| 2026-06-13 | group | Haiti v Scotland | 0-1 | A | 0.1629 | 0.1348 | 0.1348 |
| 2026-06-13 | group | Australia v Türkiye | 2-0 | H | 0.2814 | 0.2965 | 0.2965 |
| 2026-06-14 | group | Germany v Curaçao | 7-1 | H | 0.0186 | 0.0244 | 0.0244 |
| 2026-06-14 | group | Ivory Coast v Ecuador | 1-0 | H | 0.4600 | 0.4796 | 0.4796 |
| 2026-06-14 | group | Netherlands v Japan | 2-2 | D | 0.1433 | 0.1316 | 0.1316 |
| 2026-06-14 | group | Sweden v Tunisia | 5-1 | H | 0.2149 | 0.2291 | 0.2291 |

*12 matches graded (12 group). Early on the sample is small and result-only ≈ xG-adjusted (few prior games to re-weight); the gap is meaningful only as games accumulate.*
