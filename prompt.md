I want you to build a professional, academic, minimal Streamlit dashboard for my Master thesis simulation.

## Project Context

My thesis title is:

**RWA Tokenization and Its Impact on Financial Markets**

The applied chapter uses the following methodology:

**Real Company Case Study + Counterfactual Scenario Simulation + Deterministic Scenario Analysis + Monte Carlo Robustness Testing + Sensitivity Analysis**

The dashboard should model how tokenized Treasury collateral could affect institutional financial market efficiency through:

* collateral mobility
* liquidity buffer reduction
* capital liberated
* cost of debt compression
* WACC impact
* ROE impact
* institutional risk architecture

The case company is **Apple Inc.**, using its 2025 financial data as a real-company baseline. The simulation must NOT claim that Apple currently uses RWA tokenization. Apple is only used as a real-data proxy for a large institutional treasury environment.

## Main Objective

Build an interactive Streamlit dashboard that allows the user to compare:

1. **Legacy Financial Market Scenario**
2. **Tokenized RWA Collateral Scenario**
3. **Adoption Scenarios**
4. **Market Stress Scenarios**
5. **Monte Carlo Robustness Testing**
6. **Sensitivity Analysis**

The dashboard should be academically styled, clean, minimal, and well explained. It should look suitable for a Master thesis defense, not like a crypto trading app.

---

## Data to Use

Use Apple 2025 baseline data in USD billions:

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
shareholders_equity = 73.733
tax_rate = 0.156
```

Use:

```python
liquid_asset_base = total_liquid_assets
tokenizable_asset_pool = total_markable_securities
```

Important: if you notice the variable typo above, correct it in code as:

```python
tokenizable_asset_pool = total_marketable_securities
```

---

## Required Core Formulas

### 1. Tokenized Collateral Pool

```python
tokenized_pool = tokenizable_asset_pool * tokenized_share
```

Where:

```python
tokenized_share = percentage of marketable securities assumed to be tokenized
```

---

### 2. Usable Collateral

Use the same tokenized pool for legacy and tokenized comparison.

```python
legacy_usable_collateral = tokenized_pool * (1 - legacy_haircut)
tokenized_usable_collateral = tokenized_pool * (1 - tokenized_haircut)
usable_collateral_difference = tokenized_usable_collateral - legacy_usable_collateral
```

---

### 3. Legacy Liquidity Buffer

```python
legacy_buffer = liquid_asset_base * legacy_buffer_ratio
```

---

### 4. Effective Tokenized Buffer Ratio

The liquidity buffer benefit must scale with the tokenized share. Do NOT apply the full tokenized buffer ratio to the entire liquid asset base unless 100% of assets are tokenized.

Use this formula:

```python
effective_tokenized_buffer_ratio = legacy_buffer_ratio - (
    (legacy_buffer_ratio - tokenized_buffer_ratio) * tokenized_share
)
```

This means that if tokenized adoption is low, the liquidity buffer improvement is smaller. If tokenized adoption is higher, the liquidity buffer improvement is larger.

---

### 5. Tokenized Liquidity Buffer

```python
tokenized_buffer = liquid_asset_base * effective_tokenized_buffer_ratio
```

---

### 6. Capital Liberated

```python
capital_liberated = legacy_buffer - tokenized_buffer
```

---

### 7. Legacy Cost of Debt

Use a default value based on Apple’s short-term funding proxy:

```python
legacy_kd = 0.0419
```

Allow the user to adjust it from the sidebar.

---

### 8. Tokenized Cost of Debt

```python
raw_tokenized_kd = legacy_kd - collateral_efficiency_spread + technology_risk_premium
tokenized_kd = max(risk_free_rate, raw_tokenized_kd)
```

This prevents the tokenized cost of debt from falling below the risk-free rate.

---

### 9. Cost of Equity Using CAPM

```python
cost_of_equity = risk_free_rate + beta * market_risk_premium
```

Default values:

```python
risk_free_rate = 0.04
beta = 1.20
market_risk_premium = 0.05
```

---

### 10. WACC

Use book values for simplicity:

```python
V = total_debt + shareholders_equity

legacy_wacc = (
    (shareholders_equity / V) * cost_of_equity
    + (total_debt / V) * legacy_kd * (1 - tax_rate)
)

tokenized_wacc = (
    (shareholders_equity / V) * cost_of_equity
    + (total_debt / V) * tokenized_kd * (1 - tax_rate)
)

wacc_change = tokenized_wacc - legacy_wacc
```

Add a note in the dashboard:

“For simplicity, the model uses book values of debt and equity. A more advanced valuation model could use market values.”

---

### 11. ROE

```python
legacy_roe = net_income / shareholders_equity
```

Add a note:

“Apple’s ROE may appear structurally high because shareholders’ equity is affected by share repurchases; therefore, ROE should be interpreted carefully.”

---

### 12. Additional Income from Liberated Capital

Treat reinvestment return as an after-tax return.

```python
additional_income = capital_liberated * after_tax_reinvestment_return
```

---

### 13. Adjusted ROE

```python
adjusted_net_income = net_income + additional_income
adjusted_roe = adjusted_net_income / shareholders_equity
roe_change = adjusted_roe - legacy_roe
```

---

### 14. Liquidity Efficiency Ratio

Optional but useful:

```python
legacy_liquidity_efficiency = legacy_usable_collateral / legacy_buffer
tokenized_liquidity_efficiency = tokenized_usable_collateral / tokenized_buffer
liquidity_efficiency_change = tokenized_liquidity_efficiency - legacy_liquidity_efficiency
```

---

## Default Simulation Assumptions

### Legacy Scenario

```python
legacy_haircut = 0.05
legacy_buffer_ratio = 0.20
legacy_kd = 0.0419
```

### Tokenized RWA Scenario

```python
tokenized_haircut = 0.03
tokenized_buffer_ratio = 0.14
collateral_efficiency_spread = 0.007
technology_risk_premium = 0.002
after_tax_reinvestment_return = 0.05
```

### WACC Parameters

```python
risk_free_rate = 0.04
beta = 1.20
market_risk_premium = 0.05
```

### Adoption Scenarios

```python
conservative = 0.10
moderate = 0.25
aggressive = 0.40
```

### Market Stress Scenarios

Create three predefined scenarios:

```python
normal = {
    "legacy_haircut": 0.05,
    "tokenized_haircut": 0.03,
    "legacy_buffer_ratio": 0.20,
    "tokenized_buffer_ratio": 0.14,
    "technology_risk_premium": 0.002,
    "collateral_efficiency_spread": 0.007
}

moderate_stress = {
    "legacy_haircut": 0.08,
    "tokenized_haircut": 0.05,
    "legacy_buffer_ratio": 0.24,
    "tokenized_buffer_ratio": 0.16,
    "technology_risk_premium": 0.0035,
    "collateral_efficiency_spread": 0.005
}

severe_stress = {
    "legacy_haircut": 0.12,
    "tokenized_haircut": 0.08,
    "legacy_buffer_ratio": 0.30,
    "tokenized_buffer_ratio": 0.18,
    "technology_risk_premium": 0.005,
    "collateral_efficiency_spread": 0.003
}
```

---

## Institutional Risk Architecture

Include a section explaining that institutional adoption requires risk segregation.

The model should distinguish between:

1. Legacy financial infrastructure
2. Pooled tokenized liquidity architecture
3. Institutional isolated risk architecture

Use this comparison table:

| Parameter                   | Legacy System | Pooled Tokenization | Isolated Vault Architecture |
| --------------------------- | ------------: | ------------------: | --------------------------: |
| Settlement speed            |         Lower |              Higher |                      Higher |
| Collateral segregation      |        Strong |                Weak |                      Strong |
| Contagion risk              |           Low |                High |                         Low |
| Liquidity efficiency        |        Medium |                High |                 Medium-High |
| Institutional compatibility |          High |                 Low |                        High |
| Counterparty isolation      |        Strong |                Weak |                      Strong |
| Smart contract exposure     |          None |                High |                      Medium |
| Operational transparency    |        Medium |              Medium |                        High |

Add an explanation:

“Institutional adoption of tokenized collateral depends not only on settlement efficiency, but also on segregated risk architecture capable of limiting contagion exposure and preserving collateral integrity.”

Do not make the app about any specific protocol. Mention isolated vaults only as a general institutional-grade design principle.

---

## Dashboard Structure

Build the app with the following sections.

---

# 1. Header

Title:

**Applied Simulation of Tokenized Treasury Collateral**

Subtitle:

**A real-company counterfactual model using Apple Inc. 2025 financial data**

Add a short note:

“This dashboard does not claim that Apple currently uses RWA tokenization. Apple’s financial data are used as a real-company baseline to simulate how tokenized collateral infrastructure could affect institutional liquidity and capital efficiency.”

---

# 2. Sidebar Controls

Create a sidebar with adjustable sliders.

### Adoption and Collateral Parameters

* Tokenized share of marketable securities: 10% to 40%, default 25%
* Legacy haircut: 4% to 12%, default 5%
* Tokenized haircut: 2% to 8%, default 3%

### Liquidity Parameters

* Legacy liquidity buffer ratio: 15% to 30%, default 20%
* Tokenized liquidity buffer ratio: 10% to 20%, default 14%

### Funding Parameters

* Legacy cost of debt: 3% to 7%, default 4.19%
* Collateral efficiency spread: 0.3% to 1.2%, default 0.7%
* Technology risk premium: 0.1% to 0.5%, default 0.2%

### WACC Parameters

* Risk-free rate: 2% to 6%, default 4%
* Beta: 0.8 to 1.6, default 1.2
* Market risk premium: 3% to 8%, default 5%

### ROE Parameters

* After-tax reinvestment return: 3% to 8%, default 5%

### Scenario Selector

Dropdown:

* Custom
* Normal Market
* Moderate Stress
* Severe Stress

If the user selects a predefined scenario, automatically apply the relevant parameters.

Important: Streamlit sliders cannot easily update dynamically after creation without session state. Use `st.session_state` to manage scenario presets cleanly.

---

# 3. Baseline Company Data

Show a clean table with Apple 2025 data:

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
* Shareholders’ equity
* Effective tax rate

Add a short explanation:

“These variables form the real-company baseline used to calibrate the simulation.”

---

# 4. Key Simulation Outputs

Display KPI cards for:

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

Use clear formatting:

* USD values in billions
* Percentages with two decimals

For WACC change and ROE change, show percentage points, not only percentages.

Example:

```python
wacc_change_pp = wacc_change * 100
```

---

# 5. Legacy vs Tokenized Comparison Table

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

# 6. Adoption Scenario Analysis

Create a section comparing:

* Conservative adoption: 10%
* Moderate adoption: 25%
* Aggressive adoption: 40%

For each scenario, calculate using the same formulas:

* Tokenized pool
* Legacy usable collateral
* Tokenized usable collateral
* Capital liberated
* Tokenized cost of debt
* Legacy WACC
* Tokenized WACC
* WACC change
* Adjusted ROE
* ROE change

Show this as:

1. A table
2. A bar chart

Use Plotly for interactive charts.

---

# 7. Stress Scenario Analysis

Compare:

* Normal Market
* Moderate Stress
* Severe Stress

For each scenario, calculate:

* Capital liberated
* Tokenized cost of debt
* WACC change
* ROE change
* Usable collateral difference

Use charts and a table.

---

# 8. Monte Carlo Robustness Testing

Add a button:

**Run Monte Carlo Simulation**

When clicked, run 5,000 simulations.

Randomly sample:

```python
tokenized_share ~ Uniform(0.10, 0.40)
legacy_haircut ~ Uniform(0.04, 0.08)
tokenized_haircut ~ Uniform(0.02, legacy_haircut)
legacy_buffer_ratio ~ Uniform(0.15, 0.30)
tokenized_buffer_ratio ~ Uniform(0.10, legacy_buffer_ratio)
collateral_efficiency_spread ~ Uniform(0.003, 0.012)
technology_risk_premium ~ Uniform(0.001, 0.005)
after_tax_reinvestment_return ~ Uniform(0.03, 0.08)
```

Important constraints:

```python
tokenized_haircut <= legacy_haircut
tokenized_buffer_ratio <= legacy_buffer_ratio
tokenized_kd >= risk_free_rate
```

For each run calculate:

* Tokenized pool
* Legacy usable collateral
* Tokenized usable collateral
* Capital liberated
* Tokenized cost of debt
* Legacy WACC
* Tokenized WACC
* WACC change
* Adjusted ROE
* ROE change

Display:

* Summary statistics table: mean, median, std, min, max, 5th percentile, 95th percentile
* Histogram of WACC change
* Histogram of capital liberated
* Histogram of ROE change

Add interpretation text:

“The Monte Carlo simulation evaluates whether the model’s conclusions remain stable when key assumptions vary within plausible ranges.”

---

# 9. Sensitivity Analysis

Create a section that tests one variable at a time.

Variables:

* Tokenized share
* Tokenized haircut
* Technology risk premium
* Collateral efficiency spread
* Tokenized buffer ratio

For each variable, vary it across a plausible range while holding others at default values.

Measure the impact on:

* WACC change
* Capital liberated
* ROE change

Show which variable has the largest effect using:

* table
* horizontal bar chart or tornado-style chart

---

# 10. Academic Interpretation Section

Add a written explanation box:

“The simulation suggests that RWA tokenization affects financial market efficiency mainly through collateral mobility and liquidity buffer reduction. The value does not come primarily from speculative secondary trading, but from transforming liquid financial assets into programmable, segregated, and institutionally usable collateral.”

Also add:

“However, the benefits are conditional on institutional-grade risk architecture. Pooled liquidity models may introduce contagion risk, while isolated collateral structures may improve institutional compatibility by preserving risk segregation.”

---

# 11. Limitations Section

Add a collapsible expander titled:

**Model Limitations**

Include:

* This is a counterfactual simulation, not historical evidence.
* Apple is used as a proxy and is not assumed to use RWA tokenization.
* Assumptions are based on financial logic and scenario design.
* The model uses book values of debt and equity for simplicity.
* Apple’s ROE should be interpreted carefully because its book equity is affected by share repurchases.
* RWA tokenization markets remain emerging and fragmented.
* Technology, custody, oracle, and regulatory risks may reduce benefits.
* Results should be interpreted as indicative, not predictive.

---

## Styling Requirements

Use a minimal academic style.

Visual theme:

* Background: white or very light gray
* Text: dark gray / near black
* Accent color: muted navy or deep blue
* Avoid flashy crypto colors
* Avoid neon gradients
* Use clean section dividers
* Use consistent spacing
* Use cards for KPIs
* Tables should be clean and readable

The app should feel like:

```text
Master thesis defense dashboard
institutional finance model
academic research tool
```

Not like:

```text
crypto trading dashboard
DeFi gambling app
marketing website
```

---

## Technical Requirements

Use:

```python
streamlit
pandas
numpy
plotly
```

Optional:

```python
scipy
```

The app should be contained in one file:

```python
app.py
```

Code should be:

* clean
* commented
* modular
* easy to edit
* academically readable

Create helper functions for:

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
run_scenario()
run_adoption_scenarios()
run_stress_scenarios()
run_monte_carlo()
run_sensitivity_analysis()
format_currency_b()
format_percent()
```

---

## Important Academic Framing

Do not write language that sounds promotional.

Avoid:

* “Tokenization will revolutionize finance”
* “Blockchain eliminates risk”
* “Apple will save billions”
* “RWA guarantees liquidity”

Use cautious academic language:

* “may improve”
* “could reduce”
* “under the model assumptions”
* “the results suggest”
* “the simulation indicates”
* “counterfactual scenario”

---

## Final Output

Generate the full `app.py` code.

Also include:

1. A short explanation of how to run the app.
2. Required installation command:

```bash
pip install streamlit pandas numpy plotly
```

3. Run command:

```bash
streamlit run app.py
```

4. A short explanation of the dashboard sections.
