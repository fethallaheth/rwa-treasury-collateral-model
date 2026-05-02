I want you to restructure my existing Streamlit dashboard so it works as a **data tables and charts companion** for my Master thesis Chapter 3.

The website should NOT contain long academic writing. I will write the discussion in the thesis paper myself. The dashboard should mainly provide:

* clean result tables
* finance-style charts
* downloadable outputs if possible
* short labels and minimal interpretation notes only

## Project Context

Thesis title:

**RWA Tokenization and Its Impact on Financial Markets**

Applied chapter:

**Chapter 3: Applied Simulation of Tokenized Treasury Collateral and Its Impact on Financial Market Efficiency**

The model compares:

* Legacy collateral infrastructure
* Tokenized RWA collateral infrastructure

The model uses:

* Apple Inc. 2025 financial data
* Real-company baseline
* Counterfactual simulation
* Adoption scenarios
* Stress scenarios
* Monte Carlo robustness testing
* Sensitivity analysis

Important academic framing:

* Do NOT claim Apple uses tokenized collateral.
* Apple is only a real-company baseline.
* The model is counterfactual.
* The website is for tables and charts, not for long theoretical explanation.

---

# Main Goal

Restructure the Streamlit app around the final **3.6 Results and Discussion** structure:

```text
3.6 Results and Discussion

3.6.1 Baseline Scenario Results
3.6.2 Adoption Effect under Normal Market Conditions
3.6.3 Stress Effect under Moderate Adoption
3.6.4 Cross-Scenario Matrix Results
3.6.5 Monte Carlo Robustness Results
3.6.6 Sensitivity Analysis Results
3.6.7 Financial Interpretation of the Results
```

The dashboard should mirror this structure using sections, tables, and charts.

No long paragraphs. Use only short helper notes where needed.

---

# Dashboard Layout

Use this exact layout.

---

## 1. Header

Title:

**Tokenized Treasury Collateral Simulation**

Subtitle:

**Tables and charts for Chapter 3 results**

Short note:

**Counterfactual model using Apple Inc. 2025 financial data. Apple is used only as a real-company baseline and is not assumed to use RWA tokenization.**

Keep this short.

---

## 2. Sidebar Controls

The sidebar should allow the user to control:

### Capital Structure Basis

* Book Values
* Market Values

If Market Values is selected, allow editable market capitalization input.

### Base Scenario Settings

* Market scenario selector:

  * Normal Market
  * Moderate Stress
  * Severe Stress
  * 2008-Style Liquidity Shock

* Adoption level selector:

  * Conservative 10%
  * Moderate 25%
  * Aggressive 40%

### Model Parameters

Keep sliders for:

* tokenized share
* legacy haircut
* tokenized haircut
* legacy buffer ratio
* tokenized buffer ratio
* legacy cost of debt
* collateral efficiency spread
* technology risk premium
* risk-free rate
* beta
* market risk premium
* after-tax reinvestment return

But make the dashboard sections below use the fixed methodology:

* Baseline = Normal Market + 25% adoption
* Adoption analysis = Normal Market fixed, adoption changes 10%, 25%, 40%
* Stress analysis = 25% adoption fixed, market scenario changes
* Cross-scenario matrix = 4 market scenarios × 3 adoption levels

---

# Section 3.6.1 — Baseline Scenario Results

Purpose:

Show the base case:

```text
Normal Market + 25% adoption
```

Create:

## Table: Baseline Legacy vs Tokenized Results

Columns:

| Indicator | Legacy | Tokenized | Difference |
| --------- | -----: | --------: | ---------: |

Rows:

* Tokenized collateral pool
* Haircut
* Usable collateral
* Liquidity buffer
* Capital liberated
* Cost of debt
* WACC
* ROE
* Liquidity efficiency ratio

## Charts

Add:

### Chart 1: Liquidity Buffer Waterfall

Title:

**Liquidity Buffer Bridge: Legacy to Tokenized**

Shows:

* legacy liquidity buffer
* reduction / capital liberated
* tokenized liquidity buffer

Use Plotly waterfall.

### Chart 2: Cost of Debt Bridge

Title:

**Cost of Debt Bridge: Efficiency Gain vs Technology Risk**

Shows:

* legacy cost of debt
* collateral efficiency spread as negative
* technology risk premium as positive
* tokenized cost of debt

Use Plotly waterfall.

### Optional Chart 3: Legacy vs Tokenized Dumbbell

Title:

**Legacy vs Tokenized Baseline Comparison**

Use connected dot/dumbbell chart for:

* usable collateral
* liquidity buffer
* cost of debt
* WACC
* ROE

If units conflict, split into:

* Amount metrics
* Percentage metrics

Add only one short note:

**Baseline case: Normal Market with 25% tokenization adoption.**

---

# Section 3.6.2 — Adoption Effect under Normal Market Conditions

Purpose:

Show what happens when adoption changes while market condition stays fixed.

Use:

```text
Market condition = Normal Market
Adoption levels = 10%, 25%, 40%
```

Create:

## Table: Adoption Effect under Normal Market

Columns:

| Adoption Level | Tokenized Share | Tokenized Pool | Additional Usable Collateral | Capital Liberated | WACC Change | ROE Change |
| -------------- | --------------: | -------------: | ---------------------------: | ----------------: | ----------: | ---------: |

Rows:

* Conservative 10%
* Moderate 25%
* Aggressive 40%

## Charts

### Chart 1: Capital Liberated by Adoption Level

Grouped or simple bar chart.

### Chart 2: Additional Usable Collateral by Adoption Level

Bar chart.

### Chart 3: ROE Change by Adoption Level

Bar chart.

Short note:

**This section isolates the adoption effect by keeping market conditions fixed at Normal Market.**

---

# Section 3.6.3 — Stress Effect under Moderate Adoption

Purpose:

Show what happens when market stress changes while adoption remains fixed.

Use:

```text
Adoption = 25%
Market scenarios = Normal, Moderate Stress, Severe Stress, 2008-Style Liquidity Shock
```

Create:

## Table: Stress Effect under 25% Adoption

Columns:

| Market Scenario | Additional Usable Collateral | Capital Liberated | Tokenized Cost of Debt | WACC Change | ROE Change |
| --------------- | ---------------------------: | ----------------: | ---------------------: | ----------: | ---------: |

Rows:

* Normal Market
* Moderate Stress
* Severe Stress
* 2008-Style Liquidity Shock

## Charts

### Chart 1: Capital Liberated under Stress Scenarios

Bar chart.

### Chart 2: WACC Change under Stress Scenarios

Bar chart with a horizontal zero line.

### Chart 3: Tokenized Cost of Debt under Stress Scenarios

Line or bar chart.

Short note:

**This section isolates the stress effect by keeping adoption fixed at 25%.**

Add small warning under the 2008 scenario:

**The 2008-style scenario is a stress-test reference, not a historical tokenization case.**

---

# Section 3.6.4 — Cross-Scenario Matrix Results

Purpose:

Show the full scenario space:

```text
4 market scenarios × 3 adoption levels = 12 cases
```

Create matrix tables and heatmaps.

## Matrix Tables

Create four matrix tables:

### Table 1: Capital Liberated Matrix

Rows:

* Normal Market
* Moderate Stress
* Severe Stress
* 2008-Style Liquidity Shock

Columns:

* 10% Adoption
* 25% Adoption
* 40% Adoption

Values:

* capital liberated

### Table 2: Additional Usable Collateral Matrix

Same layout.

### Table 3: WACC Change Matrix

Same layout.

### Table 4: ROE Change Matrix

Same layout.

Use conditional formatting:

* Higher capital liberated = stronger positive shading
* Higher additional usable collateral = stronger positive shading
* Negative WACC change = favorable
* Positive WACC change = caution
* Positive ROE change = favorable

## Heatmaps

Create:

### Heatmap 1: Capital Liberated

Title:

**Capital Liberated Across Scenario Matrix**

### Heatmap 2: WACC Change

Title:

**WACC Change Across Scenario Matrix**

Use a diverging scale centered at zero.

### Heatmap 3: ROE Change

Title:

**ROE Change Across Scenario Matrix**

Short note:

**The matrix summarizes all 12 scenario outcomes generated by combining four market conditions with three adoption levels.**

---

# Section 3.6.5 — Monte Carlo Robustness Results

Purpose:

Show uncertainty and robustness.

Create:

## Table: Monte Carlo Summary Statistics

Columns:

| Output | Mean | Median | Std. Dev. | Min | Max | 5th Percentile | 95th Percentile |
| ------ | ---: | -----: | --------: | --: | --: | -------------: | --------------: |

Rows:

* Capital liberated
* Additional usable collateral
* Tokenized WACC
* WACC change
* Adjusted ROE
* ROE change

## Charts

### Chart 1: Monte Carlo Distribution of Capital Liberated

Histogram with mean and median vertical lines.

### Chart 2: Monte Carlo Distribution of WACC Change

Histogram with mean, median, and zero vertical lines.

### Chart 3: Monte Carlo Distribution of ROE Change

Histogram with mean and median vertical lines.

### Chart 4: Monte Carlo Box Plot

Create two box plots:

* USD outcomes: capital liberated, additional usable collateral
* Percentage-point outcomes: WACC change, ROE change

Use tabs if needed:

* “Distributions”
* “Box Plots”

Short note:

**Monte Carlo results show how the outputs behave when key assumptions vary within predefined ranges.**

Performance requirement:

Use `@st.cache_data` for Monte Carlo simulation.

---

# Section 3.6.6 — Sensitivity Analysis Results

Purpose:

Show which assumptions drive the model.

Create:

## Table: Sensitivity Analysis Results

Columns:

| Variable Tested | Impact on Capital Liberated | Impact on WACC Change | Impact on ROE Change | Main Interpretation |
| --------------- | --------------------------: | --------------------: | -------------------: | ------------------- |

Variables:

* Tokenized asset share
* Tokenized buffer ratio
* Tokenized haircut
* Collateral efficiency spread
* Technology risk premium

## Charts

### Chart 1: WACC Sensitivity Tornado Chart

Title:

**WACC Sensitivity to Key Assumptions**

Horizontal bar chart sorted by absolute impact.

### Chart 2: Capital Liberated Sensitivity Tornado Chart

Title:

**Capital Liberated Sensitivity to Key Assumptions**

Horizontal bar chart sorted by absolute impact.

### Chart 3: ROE Sensitivity Tornado Chart

Optional.

Short note:

**Sensitivity analysis changes one variable at a time to identify the strongest model drivers.**

---

# Section 3.6.7 — Financial Interpretation Summary

This section should be short. No long writing.

Create four compact cards:

1. **Collateral Channel**

   * Shows: additional usable collateral result
   * Short text: “Tokenization changes collateral usability through haircut assumptions.”

2. **Liquidity Channel**

   * Shows: capital liberated result
   * Short text: “Liquidity effects are driven mainly by adoption level and buffer assumptions.”

3. **Funding-Cost Channel**

   * Shows: WACC change result
   * Short text: “WACC effect depends on collateral efficiency spread versus technology risk premium.”

4. **Institutional Risk Channel**

   * Short text: “Benefits depend on isolated risk architecture, custody reliability, legal enforceability, and operational trust.”

Keep this section minimal.

---

# Downloadable Outputs

Add download buttons for:

* baseline results CSV
* adoption effect CSV
* stress effect CSV
* cross-scenario matrix CSV
* Monte Carlo summary CSV
* sensitivity analysis CSV

Use:

```python
st.download_button()
```

---

# Technical Requirements

Use:

```python
streamlit
pandas
numpy
plotly.express
plotly.graph_objects
```

Do not invent new values.

Use the existing model calculations and dataframes.

If required, create these helper functions:

```python
build_baseline_results()
build_adoption_results()
build_stress_results()
build_cross_scenario_matrix()
run_monte_carlo()
run_sensitivity_analysis()

plot_liquidity_waterfall()
plot_cost_of_debt_waterfall()
plot_adoption_bar()
plot_stress_bar()
plot_heatmap()
plot_histogram_with_markers()
plot_boxplot()
plot_tornado()
plot_dumbbell()
```

---

# Performance Rules

* Use `@st.cache_data` for Monte Carlo.
* Do not recompute the same scenario table multiple times.
* Build scenario result dataframes once, then pass them to tables and charts.
* Avoid animations.
* Avoid 3D charts.
* Avoid more than two charts per row.
* Use tabs or expanders for advanced charts if the page becomes too long.

---

# Visual Style

Use a clean academic finance style:

* white or light gray background
* dark text
* muted navy accent
* clear labels
* compact spacing
* no crypto/neon aesthetic
* no marketing language

---

# Final Deliverable

Modify the existing Streamlit codebase so the website becomes a clean **Chapter 3 results dashboard** organized exactly as:

```text
3.6.1 Baseline Scenario Results
3.6.2 Adoption Effect under Normal Market Conditions
3.6.3 Stress Effect under Moderate Adoption
3.6.4 Cross-Scenario Matrix Results
3.6.5 Monte Carlo Robustness Results
3.6.6 Sensitivity Analysis Results
3.6.7 Financial Interpretation Summary
```

Each subsection must contain:

* one or more clean tables
* relevant finance-style charts
* very short notes only
* downloadable CSV outputs where useful

Do not add long academic explanations.
