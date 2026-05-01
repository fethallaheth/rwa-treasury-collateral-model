I already have a Streamlit dashboard/codebase for my Master thesis applied chapter. I want you to modify and align the codebase with my final Chapter 3 methodology.

## Thesis Context

My thesis title is:

**RWA Tokenization and Its Impact on Financial Markets**

The applied chapter is titled:

**Chapter 3: Applied Simulation of Tokenized Treasury Collateral and Its Impact on Financial Market Efficiency**

The chapter uses:

**Real Company Case Study + Counterfactual Scenario Simulation + Deterministic Scenario Analysis + Monte Carlo Robustness Testing + Sensitivity Analysis**

The model uses **Apple Inc. 2025 financial data** as a real-company baseline. The simulation must NOT claim that Apple currently uses RWA tokenization. Apple is only used as a realistic institutional treasury proxy.

The model compares:

1. **Legacy collateral infrastructure**
2. **Tokenized RWA collateral infrastructure**

The main financial outputs are:

* Usable collateral
* Liquidity buffer
* Capital liberated
* Cost of debt
* WACC
* ROE

The dashboard should be minimal, academic, clean, and suitable for a Master thesis defense.

---

# Required Chapter 3 Alignment

The dashboard should follow this chapter structure conceptually:

```text
3.1 Introduction
3.2 Research Design and Case Selection
3.3 Data, Variables, and Model Assumptions
3.4 Methodology and Simulation Framework
3.5 Financial Model and Calculation Logic
3.6 Results and Discussion
3.7 Limitations of the Model
3.8 Conclusion of the Chapter
```

The app should not feel like a crypto dashboard. It should feel like an institutional finance simulation tool.

Use careful academic language:

* “may improve”
* “could reduce”
* “under model assumptions”
* “counterfactual scenario”
* “simulation indicates”
* “results should be interpreted as indicative, not predictive”

Avoid:

* “Tokenization will revolutionize finance”
* “Apple will save billions”
* “Blockchain eliminates risk”
* “RWA guarantees liquidity”

---

# Data to Use

Use Apple 2025 financial data in **USD billions**:

```python
cash_and_equivalents = 35.934
current_marketable_securities = 18.763
non_current_marketable_securities = 77.723
total_liquid_assets = 132.420
total_marketable_securities = 96.486
commercial_paper = 7.979
current_term_debt = 12.350
non_current_term_debt = 78.328
total_debt = 98.657
net_income = 112.010
shareholders_equity_book = 73.733
tax_rate = 0.156
```

Use:

```python
liquid_asset_base = total_liquid_assets
tokenizable_asset_pool = total_marketable_securities
```

Important:

* All financial values should be shown in **USD billions**.
* Percentages should be shown with two decimals.
* WACC change and ROE change should be shown in **percentage points**.

---

# Important WACC Improvement

My previous model used only book equity. I now want the dashboard to support two WACC modes:

## Mode 1: Book-value WACC

Use:

```python
equity_value = shareholders_equity_book
debt_value = total_debt
```

## Mode 2: Market-value WACC

Allow the user to input:

```python
market_cap
```

Default:

```python
market_cap = 3500.0  # USD billions, editable by user
```

Then:

```python
equity_value = market_cap
debt_value = total_debt
```

Add a selector in the sidebar:

```text
Capital Structure Basis:
- Book Values
- Market Values
```

Explain in the app:

“Book-value WACC uses accounting values from Apple’s financial statements. Market-value WACC uses Apple’s market capitalization as the equity value. Market-value WACC is often preferred in valuation, while book-value WACC is kept for accounting consistency.”

Also add a note:

“Apple’s book equity can be affected by share repurchases, which may inflate ROE and distort book-value capital structure weights.”

---

# Required Formulas

## 1. Tokenized Collateral Pool

```python
tokenized_pool = tokenizable_asset_pool * tokenized_share
```

---

## 2. Usable Collateral

Use the same tokenized pool for both legacy and tokenized scenarios.

```python
legacy_usable_collateral = tokenized_pool * (1 - legacy_haircut)
tokenized_usable_collateral = tokenized_pool * (1 - tokenized_haircut)
additional_usable_collateral = tokenized_usable_collateral - legacy_usable_collateral
```

---

## 3. Legacy Liquidity Buffer

```python
legacy_buffer = liquid_asset_base * legacy_buffer_ratio
```

---

## 4. Effective Tokenized Buffer Ratio

Do NOT apply the full tokenized buffer ratio to the entire liquid asset base unless 100% of assets are tokenized.

Use:

```python
effective_tokenized_buffer_ratio = legacy_buffer_ratio - (
    (legacy_buffer_ratio - tokenized_buffer_ratio) * tokenized_share
)
```

This ensures that liquidity buffer improvement scales with tokenization adoption.

---

## 5. Tokenized Liquidity Buffer

```python
tokenized_buffer = liquid_asset_base * effective_tokenized_buffer_ratio
```

---

## 6. Capital Liberated

```python
capital_liberated = legacy_buffer - tokenized_buffer
```

---

## 7. Cost of Equity Using CAPM

```python
cost_of_equity = risk_free_rate + beta * market_risk_premium
```

Defaults:

```python
risk_free_rate = 0.04
beta = 1.20
market_risk_premium = 0.05
```

---

## 8. Legacy Cost of Debt

Default:

```python
legacy_kd = 0.0419
```

Allow user to adjust it.

---

## 9. Tokenized Cost of Debt

```python
raw_tokenized_kd = legacy_kd - collateral_efficiency_spread + technology_risk_premium
tokenized_kd = max(risk_free_rate, raw_tokenized_kd)
```

The cost of debt must not fall below the risk-free rate.

---

## 10. WACC

Use selected capital structure basis:

```python
V = debt_value + equity_value

legacy_wacc = (
    (equity_value / V) * cost_of_equity
    + (debt_value / V) * legacy_kd * (1 - tax_rate)
)

tokenized_wacc = (
    (equity_value / V) * cost_of_equity
    + (debt_value / V) * tokenized_kd * (1 - tax_rate)
)

wacc_change = tokenized_wacc - legacy_wacc
```

---

## 11. ROE

Book ROE:

```python
legacy_roe = net_income / shareholders_equity_book
```

Add an interpretive note:

“ROE is calculated using book equity. For Apple, this figure should be interpreted carefully because share repurchases reduce book equity and can make ROE appear unusually high.”

---

## 12. Additional Income from Liberated Capital

Treat reinvestment return as after-tax:

```python
additional_income = capital_liberated * after_tax_reinvestment_return
```

Default:

```python
after_tax_reinvestment_return = 0.05
```

---

## 13. Adjusted ROE

```python
adjusted_net_income = net_income + additional_income
adjusted_roe = adjusted_net_income / shareholders_equity_book
roe_change = adjusted_roe - legacy_roe
```

---

## 14. Liquidity Efficiency Ratio

```python
legacy_liquidity_efficiency = legacy_usable_collateral / legacy_buffer
tokenized_liquidity_efficiency = tokenized_usable_collateral / tokenized_buffer
liquidity_efficiency_change = tokenized_liquidity_efficiency - legacy_liquidity_efficiency
```

Avoid division by zero.

---

# Default Scenario Assumptions

## Legacy Scenario

```python
legacy_haircut = 0.05
legacy_buffer_ratio = 0.20
legacy_kd = 0.0419
```

## Tokenized RWA Scenario

```python
tokenized_haircut = 0.03
tokenized_buffer_ratio = 0.14
collateral_efficiency_spread = 0.007
technology_risk_premium = 0.002
after_tax_reinvestment_return = 0.05
```

---

# Adoption Scenarios

Use:

```python
adoption_scenarios = {
    "Conservative": 0.10,
    "Moderate": 0.25,
    "Aggressive": 0.40
}
```

Interpretation:

| Adoption Scenario | Tokenized Share | Interpretation                        |
| ----------------- | --------------: | ------------------------------------- |
| Conservative      |             10% | Limited institutional experimentation |
| Moderate          |             25% | Partial treasury integration          |
| Aggressive        |             40% | Advanced but still partial adoption   |

---

# Market Stress Scenarios

Use these scenarios:

```python
stress_scenarios = {
    "Normal Market": {
        "legacy_haircut": 0.05,
        "tokenized_haircut": 0.03,
        "legacy_buffer_ratio": 0.20,
        "tokenized_buffer_ratio": 0.14,
        "technology_risk_premium": 0.002,
        "collateral_efficiency_spread": 0.007
    },
    "Moderate Stress": {
        "legacy_haircut": 0.08,
        "tokenized_haircut": 0.05,
        "legacy_buffer_ratio": 0.24,
        "tokenized_buffer_ratio": 0.16,
        "technology_risk_premium": 0.0035,
        "collateral_efficiency_spread": 0.005
    },
    "Severe Stress": {
        "legacy_haircut": 0.12,
        "tokenized_haircut": 0.08,
        "legacy_buffer_ratio": 0.30,
        "tokenized_buffer_ratio": 0.18,
        "technology_risk_premium": 0.005,
        "collateral_efficiency_spread": 0.003
    },
    "2008-Style Liquidity Shock": {
        "legacy_haircut": 0.18,
        "tokenized_haircut": 0.12,
        "legacy_buffer_ratio": 0.35,
        "tokenized_buffer_ratio": 0.24,
        "technology_risk_premium": 0.007,
        "collateral_efficiency_spread": 0.002
    }
}
```

Important:
The 2008-style scenario is not saying tokenized RWAs existed in 2008. It is a stress-test inspired by extreme liquidity pressure, wider haircuts, and higher risk premia.

Add this note in the dashboard:

“The 2008-style liquidity shock is used as a stress-test reference. It does not imply that tokenized collateral existed during the 2008 crisis.”

---

# Institutional Risk Architecture Section

Add a section comparing:

| Feature                   | Pooled Tokenized Structure | Isolated Institutional Architecture |
| ------------------------- | -------------------------- | ----------------------------------- |
| Collateral exposure       | Shared across participants | Segregated by position or vault     |
| Contagion risk            | Higher                     | Lower                               |
| Institutional suitability | Limited                    | Stronger                            |
| Risk transparency         | Moderate                   | Higher                              |
| Operational logic         | Open liquidity pool        | Controlled collateral structure     |

Add explanatory text:

“The tokenized scenario assumes an isolated institutional architecture rather than a fully open pooled liquidity model. This reflects the idea that large corporations and regulated institutions are unlikely to use tokenized collateral systems that expose them to broad contagion risk.”

Mention examples carefully:

“Protocols and market designs such as Aave Horizon and isolated lending markets such as Morpho illustrate the broader movement toward permissioned or risk-segregated collateral structures. They are used here only as conceptual examples, not as direct case studies.”

Do not over-focus on any protocol.

---

# Dashboard Layout

Modify the app layout to follow this order:

## 1. Header

Title:

**Applied Simulation of Tokenized Treasury Collateral**

Subtitle:

**A counterfactual model using Apple Inc. 2025 financial data**

Add note:

“This dashboard does not claim that Apple currently uses RWA tokenization. Apple’s data are used as a real-company baseline to simulate how tokenized collateral infrastructure could affect liquidity and capital efficiency.”

---

## 2. Sidebar Controls

Add controls for:

### Capital Structure Basis

* Book Values
* Market Values

If Market Values selected, show editable market cap input.

Default:

```python
market_cap = 3500.0
```

### Adoption and Collateral Parameters

* Tokenized share: 10% to 40%, default 25%
* Legacy haircut: 4% to 18%, default 5%
* Tokenized haircut: 2% to 12%, default 3%

### Liquidity Parameters

* Legacy buffer ratio: 15% to 35%, default 20%
* Tokenized buffer ratio: 10% to 24%, default 14%

### Funding Parameters

* Legacy cost of debt: 3% to 8%, default 4.19%
* Collateral efficiency spread: 0.2% to 1.2%, default 0.7%
* Technology risk premium: 0.1% to 0.8%, default 0.2%

### WACC Parameters

* Risk-free rate: 2% to 6%, default 4%
* Beta: 0.8 to 1.6, default 1.2
* Market risk premium: 3% to 8%, default 5%

### ROE Parameters

* After-tax reinvestment return: 3% to 8%, default 5%

### Scenario Selector

* Custom
* Normal Market
* Moderate Stress
* Severe Stress
* 2008-Style Liquidity Shock

Use session state properly so selecting a preset updates the relevant assumptions.

---

## 3. Apple Baseline Data

Show a clean table with:

* Cash and cash equivalents
* Current marketable securities
* Non-current marketable securities
* Total liquid assets
* Total marketable securities
* Commercial paper
* Current term debt
* Non-current term debt
* Total debt
* Net income
* Book shareholders’ equity
* Effective tax rate

---

## 4. Core KPI Cards

Show:

* Tokenized collateral pool
* Legacy usable collateral
* Tokenized usable collateral
* Additional usable collateral
* Legacy liquidity buffer
* Tokenized liquidity buffer
* Capital liberated
* Legacy cost of debt
* Tokenized cost of debt
* Legacy WACC
* Tokenized WACC
* WACC change
* Legacy ROE
* Adjusted ROE
* ROE change

---

## 5. Legacy vs Tokenized Comparison

Create a table comparing:

| Metric                     | Legacy | Tokenized | Difference |
| -------------------------- | -----: | --------: | ---------: |
| Haircut                    |        |           |            |
| Usable collateral          |        |           |            |
| Liquidity buffer           |        |           |            |
| Cost of debt               |        |           |            |
| WACC                       |        |           |            |
| ROE                        |        |           |            |
| Liquidity efficiency ratio |        |           |            |

---

## 6. Adoption Scenario Analysis

Compare conservative, moderate, and aggressive adoption.

For each calculate:

* Tokenized pool
* Usable collateral
* Capital liberated
* Tokenized Kd
* WACC change
* ROE change

Show table and charts.

---

## 7. Stress Scenario Analysis

Compare:

* Normal Market
* Moderate Stress
* Severe Stress
* 2008-Style Liquidity Shock

For each calculate:

* Capital liberated
* Tokenized cost of debt
* WACC change
* ROE change
* Additional usable collateral

Show table and charts.

---

## 8. Monte Carlo Robustness Testing

Button:

**Run Monte Carlo Simulation**

Run 5,000 simulations.

Random variables:

```python
tokenized_share ~ Uniform(0.10, 0.40)
legacy_haircut ~ Uniform(0.04, 0.18)
tokenized_haircut ~ Uniform(0.02, min(0.12, legacy_haircut))
legacy_buffer_ratio ~ Uniform(0.15, 0.35)
tokenized_buffer_ratio ~ Uniform(0.10, min(0.24, legacy_buffer_ratio))
collateral_efficiency_spread ~ Uniform(0.002, 0.012)
technology_risk_premium ~ Uniform(0.001, 0.008)
after_tax_reinvestment_return ~ Uniform(0.03, 0.08)
```

Constraints:

```python
tokenized_haircut <= legacy_haircut
tokenized_buffer_ratio <= legacy_buffer_ratio
tokenized_kd >= risk_free_rate
```

Outputs:

* Capital liberated
* Additional usable collateral
* Tokenized WACC
* WACC change
* Adjusted ROE
* ROE change

Show:

* Summary statistics table
* Histogram of WACC change
* Histogram of capital liberated
* Histogram of ROE change

---

## 9. Sensitivity Analysis

Change one variable at a time while holding others at default/custom values.

Variables:

* Tokenized asset share
* Tokenized haircut
* Tokenized liquidity buffer ratio
* Collateral efficiency spread
* Technology risk premium

Measure effect on:

* WACC change
* Capital liberated
* ROE change

Show a clean table and a horizontal bar/tornado chart.

---

## 10. Interpretation Box

Add academic interpretation:

“The simulation evaluates tokenized collateral as a financial infrastructure mechanism. The expected benefit comes mainly from improved collateral mobility, reduced liquidity buffer requirements, and potential cost of debt compression. These effects may influence financial market efficiency by improving the usability of liquid assets in secured funding markets.”

Add caution:

“The results are conditional on the model assumptions. Tokenization benefits may be reduced if technology risk, custody risk, legal uncertainty, or weak institutional architecture offset the efficiency gains.”

---

## 11. Limitations Box

Include:

* The model is counterfactual and not a forecast.
* Apple is used as a proxy and is not assumed to use RWA tokenization.
* Some assumptions are scenario-based due to limited historical data.
* The WACC can be calculated using book or market values; each has limitations.
* Apple’s book equity is affected by share repurchases, so ROE should be interpreted carefully.
* The model focuses only on collateral mobility and treasury efficiency, not the entire financial market.
* Regulatory, legal, custody, and oracle risks are simplified.

---

# Styling Requirements

Use a minimal academic theme:

* White or very light gray background
* Dark gray text
* Muted navy/deep blue accent
* Clean cards
* Clean tables
* No neon colors
* No crypto-style gradients
* No hype language

The dashboard should look like:

```text
Master thesis defense dashboard
institutional finance model
academic research tool
```

not:

```text
DeFi app
crypto trading dashboard
marketing page
```

---

# Technical Requirements

Use:

```python
streamlit
pandas
numpy
plotly
```

Keep the code modular with functions:

```python
calculate_tokenized_pool()
calculate_usable_collateral()
calculate_effective_tokenized_buffer_ratio()
calculate_liquidity_buffers()
calculate_capital_liberated()
calculate_cost_of_equity()
calculate_cost_of_debt()
calculate_wacc()
calculate_roe()
run_single_case()
run_adoption_scenarios()
run_stress_scenarios()
run_monte_carlo()
run_sensitivity_analysis()
format_currency_b()
format_percent()
format_pp()
```

Make sure the app runs with:

```bash
streamlit run app.py
```

Before finishing, review the code for:

* formula consistency
* no division by zero
* correct percentage formatting
* constraints in Monte Carlo
* clean Streamlit state handling
* clear comments
* academic language
