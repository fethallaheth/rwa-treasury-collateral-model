For your dashboard/model, the results should be organized into **four levels**:

```text
1. Core output numbers
2. Comparison tables
3. Scenario results
4. Charts and robustness results
```

These are the outputs you need for **3.6 Results and Discussion**.

---

# 1. Core Output Numbers

These are the main numbers your dashboard should display as KPI cards.

## A. Collateral Outputs

| Output                       | Meaning                                                      |
| ---------------------------- | ------------------------------------------------------------ |
| Tokenized collateral pool    | Value of marketable securities assumed to be tokenized       |
| Legacy usable collateral     | Collateral value after legacy haircut                        |
| Tokenized usable collateral  | Collateral value after tokenized haircut                     |
| Additional usable collateral | Extra collateral capacity created by lower tokenized haircut |

These answer:

> Does tokenization make the same assets more usable as collateral?

---

## B. Liquidity Outputs

| Output                           | Meaning                                              |
| -------------------------------- | ---------------------------------------------------- |
| Legacy liquidity buffer          | Liquidity reserve required in the traditional system |
| Effective tokenized buffer ratio | Adjusted buffer ratio after partial tokenization     |
| Tokenized liquidity buffer       | Liquidity reserve required after tokenization        |
| Capital liberated                | Liquidity released because the required buffer falls |

These answer:

> Does tokenization reduce idle liquidity?

---

## C. Funding Cost Outputs

| Output                       | Meaning                                                   |
| ---------------------------- | --------------------------------------------------------- |
| Legacy cost of debt          | Baseline borrowing cost                                   |
| Collateral efficiency spread | Borrowing cost reduction from better collateral           |
| Technology risk premium      | Extra risk cost from tokenized infrastructure             |
| Tokenized cost of debt       | New borrowing cost after efficiency benefit and tech risk |
| Cost of debt change          | Difference between legacy and tokenized cost of debt      |

These answer:

> Does better collateral mobility reduce funding cost?

---

## D. Capital Efficiency Outputs

| Output         | Meaning                                 |
| -------------- | --------------------------------------- |
| Legacy WACC    | Cost of capital before tokenization     |
| Tokenized WACC | Cost of capital after tokenization      |
| WACC change    | Difference in percentage points         |
| Legacy ROE     | Return on equity before tokenization    |
| Adjusted ROE   | ROE after reinvesting liberated capital |
| ROE change     | Difference in percentage points         |

These answer:

> Does tokenization improve capital efficiency?

---

# 2. Main Dashboard KPI Cards

Your dashboard should show these cards at the top:

```text
Tokenized Collateral Pool
Legacy Usable Collateral
Tokenized Usable Collateral
Additional Usable Collateral
Legacy Liquidity Buffer
Tokenized Liquidity Buffer
Capital Liberated
Legacy Cost of Debt
Tokenized Cost of Debt
Legacy WACC
Tokenized WACC
WACC Change
Legacy ROE
Adjusted ROE
ROE Change
```

This gives the jury a quick view of the model’s main outputs.

---

# 3. Required Tables

## Table 1 — Apple Baseline Data

| Metric                            |     Value |
| --------------------------------- | --------: |
| Cash and cash equivalents         |  $35.934B |
| Current marketable securities     |  $18.763B |
| Non-current marketable securities |  $77.723B |
| Total liquid assets               | $132.420B |
| Total marketable securities       |  $96.486B |
| Total debt                        |  $98.657B |
| Net income                        | $112.010B |
| Shareholders’ equity              |  $73.733B |
| Effective tax rate                |     15.6% |

Purpose:

> Shows the real-company baseline.

---

## Table 2 — Baseline Simulation Assumptions

| Parameter                        | Value |
| -------------------------------- | ----: |
| Tokenized asset share            |   25% |
| Legacy haircut                   |    5% |
| Tokenized haircut                |    3% |
| Legacy liquidity buffer ratio    |   20% |
| Tokenized liquidity buffer ratio |   14% |
| Legacy cost of debt              | 4.19% |
| Collateral efficiency spread     | 0.70% |
| Technology risk premium          | 0.20% |
| After-tax reinvestment return    |    5% |

Purpose:

> Shows the assumptions behind the base simulation.

---

## Table 3 — Legacy vs Tokenized Results

| Metric                     | Legacy | Tokenized | Difference |
| -------------------------- | -----: | --------: | ---------: |
| Usable collateral          |      X |         X |          X |
| Liquidity buffer           |      X |         X |          X |
| Cost of debt               |      X |         X |          X |
| WACC                       |      X |         X |          X |
| ROE                        |      X |         X |          X |
| Liquidity efficiency ratio |      X |         X |          X |

Purpose:

> Your main comparison table.

---

## Table 4 — Adoption Scenario Results

| Scenario     | Tokenized Share | Tokenized Pool | Capital Liberated | WACC Change | ROE Change |
| ------------ | --------------: | -------------: | ----------------: | ----------: | ---------: |
| Conservative |             10% |              X |                 X |           X |          X |
| Moderate     |             25% |              X |                 X |           X |          X |
| Aggressive   |             40% |              X |                 X |           X |          X |

Purpose:

> Shows how impact changes as tokenization adoption increases.

---

## Table 5 — Stress Scenario Results

| Scenario                   | Capital Liberated | Tokenized Cost of Debt | WACC Change | ROE Change | Additional Usable Collateral |
| -------------------------- | ----------------: | ---------------------: | ----------: | ---------: | ---------------------------: |
| Normal Market              |                 X |                      X |           X |          X |                            X |
| Moderate Stress            |                 X |                      X |           X |          X |                            X |
| Severe Stress              |                 X |                      X |           X |          X |                            X |
| 2008-Style Liquidity Shock |                 X |                      X |           X |          X |                            X |

Purpose:

> Shows whether the model still works under market stress.

---

## Table 6 — Monte Carlo Summary Results

| Output                       | Mean | Median | Std. Dev. | Min | Max | 5th Percentile | 95th Percentile |
| ---------------------------- | ---: | -----: | --------: | --: | --: | -------------: | --------------: |
| Capital liberated            |    X |      X |         X |   X |   X |              X |               X |
| Additional usable collateral |    X |      X |         X |   X |   X |              X |               X |
| WACC change                  |    X |      X |         X |   X |   X |              X |               X |
| ROE change                   |    X |      X |         X |   X |   X |              X |               X |

Purpose:

> Shows robustness under uncertainty.

---

## Table 7 — Sensitivity Analysis Results

| Variable Tested                  | Impact on Capital Liberated | Impact on WACC Change | Impact on ROE Change | Sensitivity Level |
| -------------------------------- | --------------------------: | --------------------: | -------------------: | ----------------- |
| Tokenized asset share            |                           X |                     X |                    X | High/Medium/Low   |
| Tokenized haircut                |                           X |                     X |                    X | High/Medium/Low   |
| Tokenized liquidity buffer ratio |                           X |                     X |                    X | High/Medium/Low   |
| Collateral efficiency spread     |                           X |                     X |                    X | High/Medium/Low   |
| Technology risk premium          |                           X |                     X |                    X | High/Medium/Low   |

Purpose:

> Shows which variables drive the model most.

---

# 4. Required Charts

You do not need too many charts. Use **5–7 strong charts** maximum.

## Chart 1 — Legacy vs Tokenized Usable Collateral

Type:

```text
Bar chart
```

Shows:

```text
Legacy usable collateral vs Tokenized usable collateral
```

Purpose:

> Demonstrates collateral efficiency improvement.

---

## Chart 2 — Legacy vs Tokenized Liquidity Buffer

Type:

```text
Bar chart
```

Shows:

```text
Legacy buffer vs Tokenized buffer
```

Purpose:

> Shows liquidity buffer reduction.

---

## Chart 3 — Capital Liberated by Adoption Scenario

Type:

```text
Bar chart
```

Shows:

```text
Conservative vs Moderate vs Aggressive
```

Purpose:

> Shows that adoption intensity changes the size of the benefit.

---

## Chart 4 — WACC: Legacy vs Tokenized

Type:

```text
Bar chart or KPI delta
```

Shows:

```text
Legacy WACC vs Tokenized WACC
```

Purpose:

> Shows capital cost effect.

---

## Chart 5 — Stress Scenario Results

Type:

```text
Grouped bar chart
```

Shows:

```text
Normal, Moderate Stress, Severe Stress, 2008-Style Shock
```

Metrics:

```text
Capital liberated
WACC change
ROE change
```

Purpose:

> Shows whether benefits remain under stress.

---

## Chart 6 — Monte Carlo Distribution of WACC Change

Type:

```text
Histogram
```

Shows:

```text
Distribution of WACC change across 5,000 runs
```

Purpose:

> Shows robustness and uncertainty.

---

## Chart 7 — Sensitivity/Tornado Chart

Type:

```text
Horizontal bar chart
```

Shows:

```text
Which variable has the largest effect on WACC or capital liberated
```

Purpose:

> Shows which assumptions matter most.

---

# 5. Dashboard Sections

Your Streamlit dashboard should have these sections:

```text
1. Header and academic framing
2. Apple baseline data
3. Sidebar assumptions and scenario controls
4. Core KPI cards
5. Legacy vs tokenized comparison
6. Adoption scenario analysis
7. Stress scenario analysis
8. Monte Carlo robustness testing
9. Sensitivity analysis
10. Institutional risk architecture note
11. Interpretation and limitations
```

---

# 6. Exact Results You Need to Extract for Writing 3.6

When your dashboard is ready, copy these results:

## From Main Scenario

```text
Tokenized collateral pool
Legacy usable collateral
Tokenized usable collateral
Additional usable collateral
Legacy liquidity buffer
Tokenized liquidity buffer
Capital liberated
Legacy cost of debt
Tokenized cost of debt
Legacy WACC
Tokenized WACC
WACC change
Legacy ROE
Adjusted ROE
ROE change
```

## From Adoption Scenario

```text
Capital liberated at 10%
Capital liberated at 25%
Capital liberated at 40%
WACC change at 10%
WACC change at 25%
WACC change at 40%
ROE change at 10%
ROE change at 25%
ROE change at 40%
```

## From Stress Scenario

```text
Capital liberated under normal market
Capital liberated under moderate stress
Capital liberated under severe stress
Capital liberated under 2008-style shock

WACC change under normal market
WACC change under moderate stress
WACC change under severe stress
WACC change under 2008-style shock
```

## From Monte Carlo

```text
Mean capital liberated
Median capital liberated
5th percentile capital liberated
95th percentile capital liberated

Mean WACC change
Median WACC change
5th percentile WACC change
95th percentile WACC change

Mean ROE change
Median ROE change
5th percentile ROE change
95th percentile ROE change
```

## From Sensitivity

```text
Most important variable affecting capital liberated
Most important variable affecting WACC change
Most important variable affecting ROE change
Least important variable
Variables that can weaken the tokenization benefit
```

---

# 7. What Each Result Means

## If usable collateral increases

Interpretation:

> Tokenization improves collateral efficiency.

## If liquidity buffer falls

Interpretation:

> Tokenization reduces idle liquidity requirements.

## If capital liberated is positive

Interpretation:

> Tokenization allows part of precautionary liquidity to become deployable.

## If cost of debt decreases

Interpretation:

> Better collateral mobility may reduce funding spreads.

## If WACC decreases

Interpretation:

> Tokenization may improve capital cost efficiency.

## If ROE increases

Interpretation:

> ROE improves only if liberated capital is redeployed productively.

## If Monte Carlo results remain mostly positive

Interpretation:

> The model is robust under uncertainty.

## If sensitivity shows technology risk premium matters

Interpretation:

> Tokenization benefits depend heavily on risk control and institutional architecture.

---

# 8. Minimum Results for the Thesis

If you want to keep it clean, your thesis needs only:

```text
1 baseline data table
1 assumption table
1 legacy vs tokenized result table
1 adoption scenario table
1 stress scenario table
1 Monte Carlo summary table
1 sensitivity table

Charts:
1 WACC chart
1 capital liberated chart
1 stress scenario chart
1 Monte Carlo histogram
1 sensitivity/tornado chart
```

That is enough for a strong Chapter 3.

---

# Final Answer

Your full result package should include:

```text
Core KPIs
Legacy vs tokenized table
Adoption scenario table
Stress scenario table
Monte Carlo summary table
Sensitivity analysis table
WACC chart
ROE chart
Capital liberated chart
Stress scenario chart
Monte Carlo histogram
Tornado/sensitivity chart
Interpretation box
Limitations box
```

This gives you everything needed to write **3.6 Results and Discussion** in a clean finance Master thesis style.
