# Stage 2 test: diesel hedge ratio on out-of-sample data (preliminary)

- Windows: 97 (21-day windows stepped by 5 trading days; they overlap).
- First window: 2024-09-03 .. 2024-10-02
- Last window:  2026-07-31 .. 2026-08-31
- Cap level and fixed costs are constant within a window and cancel; not modelled.
- CVaR columns are CVaR of LOSS (MNT/L); positive = tail loss.
- Hedge ratios FIXED from the design period; none re-estimated on test data.

## alpha = 0
| hedge | h | mean | std | CVaR loss 0.90 | CVaR loss 0.95 | CVaR 0.90 change vs no hedge (%) |
|---|---:|---:|---:|---:|---:|---:|
| none | 0.0000 | -87.0985 | 372.7544 | 911.4976 | 1211.6252 | 0.00 |
| 100 | 1.0000 | -48.0454 | 225.8143 | 522.6251 | 709.8048 | -42.66 |
| minvar | 1.3870 | -32.9319 | 211.1070 | 453.6003 | 574.4707 | -50.24 |
| cvar90 | 1.7160 | -20.0835 | 226.3206 | 425.9226 | 527.1731 | -53.27 |
| cvar95 | 1.4843 | -29.1321 | 213.0131 | 444.8717 | 544.0226 | -51.19 |

## alpha = 0.25
| hedge | h | mean | std | CVaR loss 0.90 | CVaR loss 0.95 | CVaR 0.90 change vs no hedge (%) |
|---|---:|---:|---:|---:|---:|---:|
| none | 0.0000 | -65.3238 | 279.5658 | 683.6232 | 908.7189 | 0.00 |
| 100 | 1.0000 | -26.2708 | 158.2785 | 343.9287 | 443.4485 | -49.69 |
| minvar | 1.0402 | -24.6989 | 158.3302 | 340.2002 | 430.8530 | -50.24 |
| cvar90 | 1.2870 | -15.0626 | 169.7404 | 319.4420 | 395.3798 | -53.27 |
| cvar95 | 1.1132 | -21.8491 | 159.7598 | 333.6538 | 408.0169 | -51.19 |

## alpha = 0.5
| hedge | h | mean | std | CVaR loss 0.90 | CVaR loss 0.95 | CVaR 0.90 change vs no hedge (%) |
|---|---:|---:|---:|---:|---:|---:|
| none | 0.0000 | -43.5492 | 186.3772 | 455.7488 | 605.8126 | 0.00 |
| 100 | 1.0000 | -4.4962 | 128.3756 | 226.9828 | 293.5007 | -50.20 |
| minvar | 0.6935 | -16.4660 | 105.5535 | 226.8001 | 287.2354 | -50.24 |
| cvar90 | 0.8580 | -10.0417 | 113.1603 | 212.9613 | 263.5866 | -53.27 |
| cvar95 | 0.7421 | -14.5660 | 106.5066 | 222.4358 | 272.0113 | -51.19 |

## alpha = 0.75
| hedge | h | mean | std | CVaR loss 0.90 | CVaR loss 0.95 | CVaR 0.90 change vs no hedge (%) |
|---|---:|---:|---:|---:|---:|---:|
| none | 0.0000 | -21.7746 | 93.1886 | 227.8744 | 302.9063 | 0.00 |
| 100 | 1.0000 | 17.2784 | 158.9865 | 289.0199 | 382.1489 | 26.83 |
| minvar | 0.3468 | -8.2330 | 52.7767 | 113.4001 | 143.6177 | -50.24 |
| cvar90 | 0.4290 | -5.0209 | 56.5801 | 106.4807 | 131.7933 | -53.27 |
| cvar95 | 0.3711 | -7.2830 | 53.2533 | 111.2179 | 136.0056 | -51.19 |

## alpha = 1
| hedge | h | mean | std | CVaR loss 0.90 | CVaR loss 0.95 | CVaR 0.90 change vs no hedge (%) |
|---|---:|---:|---:|---:|---:|---:|
| none | 0.0000 | 0.0000 | 0.0000 | -0.0000 | -0.0000 | 0.00 |
| 100 | 1.0000 | 39.0530 | 226.8069 | 372.1968 | 516.2894 | 0.00 |
| minvar | 0.0000 | 0.0000 | 0.0000 | -0.0000 | -0.0000 | 0.00 |
| cvar90 | 0.0000 | 0.0000 | 0.0000 | -0.0000 | -0.0000 | 0.00 |
| cvar95 | 0.0000 | 0.0000 | 0.0000 | -0.0000 | -0.0000 | 0.00 |

## Checks (from tool output)

- no_overlap (first test window start >= 2024-09-01): PASS
- fixed_h (h values exactly the fixed set): PASS
- alpha1_zero (at alpha=1 none/minvar/cvar90 rows are zero): PASS