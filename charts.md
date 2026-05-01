I want you to modify my existing Streamlit dashboard by adding a professional finance-style chart package. Do not change the existing formulas, data values, or model logic unless required to connect the charts to existing outputs.

The dashboard already calculates the simulation results. Your task is to build charts from the existing result dataframes/outputs.

## Project Context

This dashboard supports a Master thesis applied chapter titled:

**Applied Simulation of Tokenized Treasury Collateral and Its Impact on Financial Market Efficiency**

The model compares:

* Legacy collateral infrastructure
* Tokenized RWA collateral infrastructure

Across:

* multiple market stress scenarios
* multiple tokenization adoption ratios
* Monte Carlo robustness testing
* sensitivity analysis

The dashboard should look like an institutional finance research tool, not a crypto trading app.

Use a minimal academic style:

* white or light gray background
* dark gray text
* muted navy/deep blue accent
* no neon colors
* no hype language
* clean titles and axis labels
* values formatted as USD billions, percentages, and percentage points where appropriate

Use Plotly and Streamlit:

```python
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
```

Use `st.plotly_chart(fig, use_container_width=True)` for all charts.

If the app already has dataframes such as scenario results, stress results, adoption results, Monte Carlo results, or sensitivity results, reuse them. Do not hardcode values. Build the charts dynamically from the existing model outputs.

---

# General Formatting Requirements

Create helper formatters if they do not already exist:

```python
def format_currency_b(x):
    return f"${x:,.2f}B"

def format_percent(x):
    return f"{x * 100:.2f}%"

def format_pp(x):
    return f"{x * 100:.2f} pp"
```

If some values are already stored as percentages rather than decimals, detect or handle consistently.

Chart titles should be academic and descriptive.

Good titles:

* “Capital Liberated Across Adoption and Market Scenarios”
* “WACC Change Under Market Stress Conditions”
* “Liquidity Buffer Bridge: Legacy to Tokenized Scenario”

Avoid titles:

* “Tokenization Wins”
* “Massive Capital Unlock”
* “RWA Revolution”

---

# Required Chart Package

Add the following charts to the dashboard.

---

## 1. KPI Cards with Delta

Create a top-level KPI section named:

**Executive Simulation Summary**

Show key metrics using `st.metric()` or custom cards:

* Tokenized collateral pool
* Additional usable collateral
* Capital liberated
* Legacy WACC
* Tokenized WACC
* WACC change
* Legacy ROE
* Adjusted ROE
* ROE change
* Tokenized cost of debt

Use deltas where useful:

* WACC change should show a negative delta as favorable.
* ROE change should show positive as favorable.
* Capital liberated should show positive as favorable.

Add a short note below:

“Positive capital liberated and additional usable collateral indicate improved liquidity and collateral efficiency. WACC improvement is conditional on the balance between collateral efficiency gains and technology risk premiums.”

---

## 2. Waterfall Chart — Liquidity Buffer Bridge

Build a waterfall chart showing how the legacy liquidity buffer moves to the tokenized liquidity buffer.

Chart title:

**Liquidity Buffer Bridge: From Legacy Reserve to Tokenized Reserve**

Structure:

* Start: Legacy liquidity buffer
* Change: Reduction due to tokenized collateral efficiency
* End: Tokenized liquidity buffer

Use Plotly `go.Waterfall`.

Expected inputs from model:

* legacy_buffer
* tokenized_buffer
* capital_liberated

Logic:

```python
reduction = tokenized_buffer - legacy_buffer
```

This reduction should appear negative.

Y-axis:

* USD billions

Hover labels:

* Legacy buffer
* Reduction / capital liberated
* Tokenized buffer

Interpretation text below chart:

“This chart shows how tokenized collateral may reduce precautionary liquidity reserves. The difference between the legacy and tokenized buffer represents capital liberated under the selected assumptions.”

---

## 3. Waterfall Chart — Cost of Debt Bridge

Build a second waterfall chart showing how the legacy cost of debt becomes the tokenized cost of debt.

Chart title:

**Cost of Debt Bridge: Efficiency Gain vs. Technology Risk**

Structure:

* Start: Legacy cost of debt
* Change: Collateral efficiency spread, negative
* Change: Technology risk premium, positive
* End: Tokenized cost of debt

Use Plotly `go.Waterfall`.

Expected inputs:

* legacy_kd
* collateral_efficiency_spread
* technology_risk_premium
* tokenized_kd

Y-axis:

* percentage

Interpretation text:

“The cost of debt bridge separates the expected funding benefit of improved collateral mobility from the additional risk premium introduced by tokenized infrastructure.”

---

## 4. Heatmap — Capital Liberated Matrix

Build a heatmap using all market scenarios and adoption ratios.

Chart title:

**Capital Liberated Across Adoption and Market Scenarios**

Rows:

* Market scenarios

Columns:

* Adoption ratios

Values:

* capital liberated

Use Plotly heatmap.

Expected dataframe format can be either wide or long. If long, use:

```python
pivot = df.pivot(index="scenario", columns="adoption", values="capital_liberated")
```

Y-axis:

* Market scenario

X-axis:

* Tokenized adoption ratio

Color:

* Capital liberated in USD billions

Hover:

* scenario
* adoption ratio
* capital liberated

Interpretation text:

“The heatmap shows how liquidity release changes jointly with market stress and tokenization adoption. Higher adoption levels should generally increase the capital liberated through lower liquidity buffer requirements.”

---

## 5. Heatmap — WACC Change Matrix

Build a second heatmap.

Chart title:

**WACC Change Across Adoption and Market Scenarios**

Rows:

* Market scenarios

Columns:

* Adoption ratios

Values:

* WACC change in percentage points

Use a diverging color scale centered around zero if possible.

Interpretation:

* negative WACC change = cost of capital reduction
* positive WACC change = cost of capital increase

Add a note:

“Negative values indicate a reduction in WACC, while positive values indicate that tokenization-related risk costs outweigh the collateral efficiency benefit.”

---

## 6. Heatmap — ROE Change Matrix

Build a third heatmap.

Chart title:

**ROE Change Across Adoption and Market Scenarios**

Rows:

* Market scenarios

Columns:

* Adoption ratios

Values:

* ROE change in percentage points

Interpretation:

“ROE change reflects the assumed redeployment of liberated capital at an after-tax reinvestment return. It should be interpreted as a conditional outcome rather than an automatic profitability gain.”

---

## 7. Grouped Bar Chart — Additional Usable Collateral

Build a grouped bar chart.

Chart title:

**Additional Usable Collateral by Scenario and Adoption Level**

X-axis:

* market scenario

Y-axis:

* additional usable collateral in USD billions

Color/group:

* adoption ratio

Interpretation:

“This chart captures the collateral-efficiency channel by showing how lower tokenized haircuts increase usable collateral relative to the legacy framework.”

---

## 8. Dumbbell / Connected Dot Plot — Legacy vs Tokenized Comparison

Build a dumbbell chart comparing legacy and tokenized values for selected metrics.

Chart title:

**Legacy vs. Tokenized Scenario Comparison**

Metrics:

* usable collateral
* liquidity buffer
* cost of debt
* WACC
* ROE

Because these metrics have different units, either:

1. create separate dumbbell charts for financial amounts and percentages, or
2. normalize/index them to 100 for visual comparison.

Preferred approach:

### Chart A: Amount Metrics

* usable collateral
* liquidity buffer

### Chart B: Percentage Metrics

* cost of debt
* WACC
* ROE

Use connected scatter traces in Plotly.

Interpretation:

“The connected-dot comparison highlights how the same asset base behaves under legacy and tokenized collateral infrastructure.”

---

## 9. Bar Chart — WACC Change Under Stress Scenarios

Build a clean bar chart.

Chart title:

**WACC Change Under Market Stress Conditions**

X-axis:

* market scenario

Y-axis:

* WACC change in percentage points

Use the selected/base adoption ratio or allow a selector for adoption ratio.

Add a horizontal zero line.

Interpretation:

“The zero line separates scenarios where tokenization reduces WACC from scenarios where higher risk premia offset the funding benefit.”

---

## 10. Monte Carlo Histogram — WACC Change

Build a histogram from Monte Carlo simulation results.

Chart title:

**Monte Carlo Distribution of WACC Change**

X-axis:

* WACC change in percentage points

Y-axis:

* frequency

Add vertical lines for:

* mean
* median
* zero

Use `go.Figure()` with histogram and line shapes.

Interpretation:

“The Monte Carlo distribution shows whether the WACC effect remains stable when key assumptions vary within predefined ranges.”

---

## 11. Monte Carlo Histogram — Capital Liberated

Build a second histogram.

Chart title:

**Monte Carlo Distribution of Capital Liberated**

X-axis:

* capital liberated in USD billions

Y-axis:

* frequency

Add vertical lines for:

* mean
* median

Interpretation:

“This distribution shows the range of possible liquidity release outcomes under uncertainty.”

---

## 12. Monte Carlo Box Plot

Build a box plot for main Monte Carlo outputs.

Chart title:

**Monte Carlo Output Dispersion**

Variables:

* capital liberated
* additional usable collateral
* WACC change
* ROE change

Because these have different units, either:

1. use separate box plots for USD outputs and percentage-point outputs, or
2. create two tabs:

   * USD outcomes
   * percentage-point outcomes

Preferred:

* Box plot A: capital liberated and additional usable collateral
* Box plot B: WACC change and ROE change

Interpretation:

“Box plots summarize the dispersion of model outcomes and help identify whether results are concentrated or highly sensitive to assumption changes.”

---

## 13. Tornado Chart — WACC Sensitivity

Build a tornado-style horizontal bar chart.

Chart title:

**Sensitivity of WACC Change to Key Assumptions**

Input:

* sensitivity results dataframe

Variables:

* collateral efficiency spread
* technology risk premium
* tokenized asset share
* tokenized haircut
* tokenized buffer ratio

Value:

* range or absolute impact on WACC change

Sort descending by absolute impact.

Interpretation:

“The WACC tornado chart identifies which assumptions have the greatest influence on the cost-of-capital result.”

---

## 14. Tornado Chart — Capital Liberated Sensitivity

Build a second tornado chart.

Chart title:

**Sensitivity of Capital Liberated to Key Assumptions**

Variables:

* tokenized asset share
* tokenized buffer ratio
* tokenized haircut
* collateral efficiency spread
* technology risk premium

Value:

* range or absolute impact on capital liberated

Sort descending by absolute impact.

Interpretation:

“The capital liberated tornado chart shows whether liquidity efficiency is mainly driven by adoption intensity or by buffer-ratio assumptions.”

---

## 15. Sankey Diagram — Model Mechanism Flow

Build one Sankey diagram explaining the financial mechanism of the model.

Chart title:

**Simulation Mechanism: From Liquid Assets to Capital Efficiency**

Suggested flow:

* Total liquid assets
* Marketable securities
* Tokenized collateral pool
* Usable collateral
* Liquidity buffer reduction
* Capital liberated
* Additional income
* Adjusted ROE

Use Plotly `go.Sankey`.

The Sankey does not need to show every accounting item perfectly. It should visually communicate the model mechanism.

Interpretation:

“The Sankey diagram summarizes the logic of the simulation: tokenization converts part of the marketable securities pool into programmable collateral, which may increase usable collateral, reduce liquidity buffers, liberate capital, and affect ROE through reinvestment.”

---

## 16. Scenario Matrix Table with Conditional Formatting

Create a styled table for the 4 × 3 scenario matrix.

Rows:

* market scenarios

Columns:

* adoption ratios

Create separate matrix tables for:

* Capital liberated
* Additional usable collateral
* WACC change
* ROE change

Use conditional formatting:

* higher capital liberated = stronger positive shading
* higher additional usable collateral = stronger positive shading
* negative WACC change = favorable
* positive WACC change = caution
* positive ROE change = favorable

In Streamlit, use `pandas Styler` or `st.dataframe`.

Interpretation:

“The matrix view provides a compact summary of the twelve scenario outcomes produced by the four market conditions and three adoption levels.”

---

# Dashboard Placement

Organize charts in this order:

## Section 1: Executive Overview

* KPI cards
* short interpretation box

## Section 2: Baseline Financial Bridges

* Liquidity buffer waterfall
* Cost of debt waterfall
* dumbbell comparison

## Section 3: Scenario Matrix Analysis

* capital liberated heatmap
* WACC change heatmap
* ROE change heatmap
* additional usable collateral grouped bar
* scenario matrix tables

## Section 4: Stress Scenario Analysis

* WACC change under stress scenarios
* liquidity buffer comparison if already available

## Section 5: Robustness and Sensitivity

* Monte Carlo WACC histogram
* Monte Carlo capital liberated histogram
* Monte Carlo box plots
* WACC tornado chart
* capital liberated tornado chart

## Section 6: Model Logic

* Sankey diagram
* interpretation note
* limitations note

---

# Performance Requirements

The dashboard must remain fast.

Use these performance rules:

1. Use `@st.cache_data` for Monte Carlo simulation outputs.
2. Do not recompute scenario matrices on every chart if already computed.
3. Build reusable functions:

   * `plot_liquidity_waterfall()`
   * `plot_cost_of_debt_waterfall()`
   * `plot_heatmap()`
   * `plot_grouped_bar()`
   * `plot_dumbbell()`
   * `plot_histogram_with_markers()`
   * `plot_boxplot()`
   * `plot_tornado()`
   * `plot_sankey()`
4. Keep Plotly templates minimal.
5. Avoid animation.
6. Avoid 3D charts.
7. Use no more than two charts per row.
8. Use tabs or expanders for advanced robustness charts if the page becomes too long.

---

# Quality Requirements

Before finishing, check:

* All charts use existing model outputs.
* No formulas were silently changed.
* USD values are shown in billions.
* WACC and ROE changes are shown in percentage points.
* Negative WACC change is interpreted as favorable.
* The dashboard does not imply that Apple actually uses tokenized collateral.
* The 2008-style shock is clearly labeled as a stress-test reference, not a historical tokenization case.
* The visual style remains academic and minimal.
* The charts help explain the thesis rather than decorate the dashboard.

---

# Final Deliverable

Modify the existing Streamlit codebase and return the updated Python code.

The final dashboard should include:

* KPI cards
* liquidity waterfall chart
* cost of debt waterfall chart
* scenario heatmaps
* additional usable collateral grouped bar chart
* legacy vs tokenized dumbbell charts
* WACC stress bar chart
* Monte Carlo histograms
* Monte Carlo box plots
* WACC sensitivity tornado chart
* capital liberated sensitivity tornado chart
* Sankey mechanism diagram
* scenario matrix tables with conditional formatting

Do not invent values. Use the values already calculated by the app.
