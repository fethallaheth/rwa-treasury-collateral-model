# Explanation of the Tokenized Treasury Collateral Simulation

## 1. Purpose of the Dashboard

This dashboard is an applied simulation for the thesis topic **RWA Tokenization and Its Impact on Financial Markets**. It uses Apple Inc. 2025 financial data as a real-company baseline to model a counterfactual scenario in which part of a large institutional treasury portfolio becomes usable as tokenized Treasury collateral.

The model does **not** claim that Apple currently uses RWA tokenization. Apple is used only as a realistic proxy for a large institutional treasury environment with significant liquid assets, marketable securities, debt, equity, and profitability.

The dashboard compares two infrastructures:

- **Legacy collateral infrastructure**
- **Tokenized RWA collateral infrastructure**

The main question is whether tokenized collateral could improve financial market efficiency through:

- Greater collateral mobility
- Lower liquidity buffer requirements
- Additional usable collateral
- Capital liberated from liquidity reserves
- Lower cost of debt
- Lower WACC
- Higher adjusted ROE under reinvestment assumptions

The results should be interpreted as **indicative, not predictive**.

## 2. Baseline Data

All financial data are entered in **USD billions**.

The dashboard uses the following Apple 2025 baseline variables:

- Cash and cash equivalents
- Current marketable securities
- Non-current marketable securities
- Total liquid assets
- Total marketable securities
- Commercial paper
- Current term debt
- Non-current term debt
- Total debt
- Net income
- Shareholders' equity
- Effective tax rate

Two baseline values are especially important:

```python
liquid_asset_base = total_liquid_assets
tokenizable_asset_pool = total_marketable_securities
```

The **liquid asset base** is used to estimate liquidity buffer requirements.

The **tokenizable asset pool** is used to estimate how much collateral could enter the tokenized scenario.

## 3. Tokenized Collateral Pool

The tokenized collateral pool measures the amount of marketable securities assumed to be tokenized.

```python
tokenized_pool = tokenizable_asset_pool * tokenized_share
```

Where:

- `tokenizable_asset_pool` is Apple’s total marketable securities.
- `tokenized_share` is the selected percentage of marketable securities assumed to be tokenized.

For example, if the tokenizable asset pool is `$96.486B` and the tokenized share is `25%`, then:

```text
tokenized_pool = 96.486 * 0.25 = 24.1215
```

So approximately `$24.12B` of securities are treated as the tokenized collateral pool.

## 4. Usable Collateral

Collateral is usually subject to a haircut. A haircut reduces the recognized value of collateral to account for price, liquidity, operational, and counterparty risks.

The model applies haircuts to the same tokenized pool under both legacy and tokenized infrastructure.

```python
legacy_usable_collateral = tokenized_pool * (1 - legacy_haircut)
tokenized_usable_collateral = tokenized_pool * (1 - tokenized_haircut)
usable_collateral_difference = tokenized_usable_collateral - legacy_usable_collateral
```

The key idea is that tokenized collateral may receive a lower haircut if it is more mobile, transparent, programmable, or operationally efficient. However, this is only an assumption within the model.

The output **Additional usable collateral** shows how much more collateral value becomes usable under the tokenized scenario.

## 5. Liquidity Buffer

Large institutions hold liquidity buffers to manage funding needs, settlement risk, market stress, and operational uncertainty.

The legacy liquidity buffer is calculated as:

```python
legacy_buffer = liquid_asset_base * legacy_buffer_ratio
```

Where:

- `liquid_asset_base` is total liquid assets.
- `legacy_buffer_ratio` is the percentage of liquid assets assumed to be held as a liquidity buffer.

## 6. Effective Tokenized Buffer Ratio

The model does not assume that tokenization immediately reduces liquidity buffers across the entire balance sheet.

Instead, the liquidity buffer improvement scales with the tokenized adoption share:

```python
effective_tokenized_buffer_ratio = legacy_buffer_ratio - (
    (legacy_buffer_ratio - tokenized_buffer_ratio) * tokenized_share
)
```

This is important because if only a small share of assets is tokenized, the liquidity benefit should also be small. If a larger share is tokenized, the liquidity benefit becomes larger.

This prevents the model from overstating the benefit of tokenization at low adoption levels.

## 7. Tokenized Liquidity Buffer

The tokenized liquidity buffer is:

```python
tokenized_buffer = liquid_asset_base * effective_tokenized_buffer_ratio
```

This represents the liquidity buffer after accounting for the assumed efficiency benefit of tokenized collateral.

## 8. Capital Liberated

Capital liberated measures the reduction in required liquidity buffer.

```python
capital_liberated = legacy_buffer - tokenized_buffer
```

This does not mean cash is automatically created. It means the model estimates that less capital may need to remain tied up in liquidity reserves under the tokenized infrastructure assumptions.

This is one of the central outputs of the dashboard because it links collateral mobility to capital efficiency.

## 9. Cost of Debt

The legacy cost of debt is user-adjustable, with a default value based on Apple’s short-term funding proxy:

```python
legacy_kd = 0.0419
```

The tokenized cost of debt is calculated as:

```python
raw_tokenized_kd = legacy_kd - collateral_efficiency_spread + technology_risk_premium
tokenized_kd = max(risk_free_rate, raw_tokenized_kd)
```

This formula has two opposing effects:

- `collateral_efficiency_spread` reduces the cost of debt because better collateral usability may improve funding terms.
- `technology_risk_premium` increases the cost of debt because tokenized infrastructure introduces technology, custody, operational, legal, and smart contract risks.

The `max()` condition prevents the tokenized cost of debt from falling below the risk-free rate.

## 10. Cost of Equity

The model calculates cost of equity using CAPM:

```python
cost_of_equity = risk_free_rate + beta * market_risk_premium
```

Where:

- `risk_free_rate` is the assumed risk-free rate.
- `beta` measures equity market risk exposure.
- `market_risk_premium` is the expected return above the risk-free rate required by equity investors.

This is a simplified academic valuation assumption.

## 11. WACC

WACC stands for **Weighted Average Cost of Capital**. It measures the average cost of financing the firm using debt and equity.

The model supports two WACC modes:

- **Book Values**
- **Market Values**

### Book-Value WACC

Book-value WACC uses accounting values from the financial statements:

```python
equity_value = shareholders_equity
debt_value = total_debt
```

### Market-Value WACC

Market-value WACC uses market capitalization as the equity value:

```python
equity_value = market_cap
debt_value = total_debt
```

The WACC formula is:

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

The model reports WACC change in **percentage points**.

If `wacc_change` is negative, the tokenized scenario has a lower WACC than the legacy scenario. This may suggest improved financing efficiency under the selected assumptions.

## 12. ROE

ROE stands for **Return on Equity**.

The legacy ROE is:

```python
legacy_roe = net_income / shareholders_equity
```

The dashboard uses book equity for ROE even when WACC is calculated using market-value equity.

This matters because Apple’s shareholders’ equity can be affected by share repurchases. A lower book equity value can make ROE appear structurally high. Therefore, ROE should be interpreted carefully.

## 13. Additional Income From Liberated Capital

The model assumes that liberated capital can be reinvested at an after-tax return:

```python
additional_income = capital_liberated * after_tax_reinvestment_return
```

This is not a prediction. It is a scenario assumption showing how released capital might affect profitability if it were redeployed productively.

## 14. Adjusted ROE

Adjusted ROE includes the additional income from reinvested liberated capital:

```python
adjusted_net_income = net_income + additional_income
adjusted_roe = adjusted_net_income / shareholders_equity
roe_change = adjusted_roe - legacy_roe
```

ROE change is displayed in **percentage points**.

## 15. Liquidity Efficiency Ratio

The liquidity efficiency ratio compares usable collateral to the liquidity buffer.

```python
legacy_liquidity_efficiency = legacy_usable_collateral / legacy_buffer
tokenized_liquidity_efficiency = tokenized_usable_collateral / tokenized_buffer
liquidity_efficiency_change = tokenized_liquidity_efficiency - legacy_liquidity_efficiency
```

A higher liquidity efficiency ratio means that more usable collateral is available relative to the liquidity buffer requirement.

The code avoids division by zero.

## 16. Core KPI Outputs

The dashboard displays the following core KPI cards:

- Tokenized collateral pool
- Legacy usable collateral
- Tokenized usable collateral
- Additional usable collateral
- Legacy liquidity buffer
- Tokenized liquidity buffer
- Capital liberated
- Legacy cost of debt
- Tokenized cost of debt
- Legacy WACC
- Tokenized WACC
- WACC change
- Legacy ROE
- Adjusted ROE
- ROE change

These KPIs summarize the financial effect of the selected assumptions.

## 17. Legacy vs Tokenized Comparison Table

The comparison table shows the same metric under legacy and tokenized conditions:

- Haircut
- Usable collateral
- Liquidity buffer
- Cost of debt
- WACC
- ROE
- Liquidity efficiency ratio

The difference column helps identify whether the tokenized scenario improves or worsens the result under the selected assumptions.

## 18. Adoption Scenario Analysis

The adoption scenario section compares three levels of tokenized marketable securities:

| Scenario | Tokenized Share | Interpretation |
|---|---:|---|
| Conservative | 10% | Limited adoption |
| Moderate | 25% | Partial treasury integration |
| Aggressive | 40% | Higher but still partial adoption |

For each scenario, the dashboard calculates:

- Tokenized pool
- Legacy usable collateral
- Tokenized usable collateral
- Capital liberated
- Tokenized cost of debt
- Legacy WACC
- Tokenized WACC
- WACC change
- Adjusted ROE
- ROE change

The charts show how capital liberated, WACC change, and ROE change vary as adoption increases.

## 19. Market Stress Scenario Analysis

The stress scenario section tests whether the results remain meaningful under less favorable market conditions.

The dashboard includes:

- Normal Market
- Moderate Stress
- Severe Stress
- 2008-Style Liquidity Shock

The 2008-style scenario is a stress-test reference only. It does **not** imply that tokenized collateral existed during the 2008 financial crisis.

Stress scenarios generally increase:

- Haircuts
- Liquidity buffer ratios
- Technology risk premium

They generally reduce:

- Collateral efficiency spread

For each stress scenario, the dashboard calculates:

- Capital liberated
- Tokenized cost of debt
- WACC change
- ROE change
- Usable collateral difference

## 20. Monte Carlo Robustness Testing

The Monte Carlo simulation runs 5,000 randomized scenarios.

It randomly samples key assumptions within plausible ranges:

- Tokenized share
- Legacy haircut
- Tokenized haircut
- Legacy buffer ratio
- Tokenized buffer ratio
- Collateral efficiency spread
- Technology risk premium
- After-tax reinvestment return

The simulation enforces these constraints:

```python
tokenized_haircut <= legacy_haircut
tokenized_buffer_ratio <= legacy_buffer_ratio
tokenized_kd >= risk_free_rate
```

The output includes:

- Summary statistics table
- Histogram of WACC change
- Histogram of capital liberated
- Histogram of ROE change

The purpose is to test whether the main conclusion remains stable when assumptions vary.

## 21. Sensitivity Analysis

Sensitivity analysis changes one variable at a time while holding the others constant.

The tested variables are:

- Tokenized share
- Tokenized haircut
- Technology risk premium
- Collateral efficiency spread
- Tokenized buffer ratio

The model measures each variable’s effect on:

- WACC change
- Capital liberated
- ROE change

The sensitivity table and tornado-style chart help identify which assumptions drive the model most strongly.

## 22. Institutional Risk Architecture

The model includes a risk architecture section because institutional adoption depends on more than settlement speed.

The dashboard compares:

- Legacy financial infrastructure
- Pooled tokenized liquidity architecture
- Institutional isolated risk architecture

The key idea is that institutions may require segregated collateral structures that reduce contagion risk and preserve counterparty isolation.

Pooled tokenization may improve liquidity, but it can introduce contagion risk. Isolated vault-style architecture may be more compatible with institutional risk management.

## 23. Interpretation of Results

The model suggests that tokenized collateral may improve financial market efficiency mainly through operational and balance-sheet channels:

- More mobile collateral
- More usable collateral
- Lower liquidity buffer requirements
- Potential funding cost compression
- Potential WACC reduction
- Potential ROE improvement if liberated capital is productively reinvested

The dashboard does not argue that tokenization automatically creates value. The benefits depend on the assumptions selected and on whether institutional-grade risk architecture exists.

## 24. Limitations

The model has several important limitations:

- It is a counterfactual simulation, not historical evidence.
- Apple is used as a proxy and is not assumed to use RWA tokenization.
- Assumptions are based on financial logic and scenario design.
- WACC can be sensitive to book-value vs market-value capital structure.
- Apple’s ROE should be interpreted carefully because share repurchases affect book equity.
- RWA tokenization markets remain emerging and fragmented.
- Technology, custody, oracle, legal, and regulatory risks are simplified.
- The results are indicative, not predictive.

## 25. How to Read the Dashboard Academically

The dashboard should be read as a structured financial simulation, not as a forecast or investment recommendation.

Useful academic language includes:

- “Under the model assumptions...”
- “The simulation indicates...”
- “The results suggest...”
- “Tokenized collateral may improve...”
- “The benefit is conditional on...”

Avoid promotional claims such as:

- “Tokenization will revolutionize finance.”
- “Blockchain eliminates risk.”
- “Apple will save billions.”
- “RWA guarantees liquidity.”

The strongest academic interpretation is that RWA tokenization may improve financial market efficiency when it increases collateral usability while preserving institutional risk controls.
