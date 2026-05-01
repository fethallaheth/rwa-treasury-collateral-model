import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="Applied Simulation of Tokenized Treasury Collateral",
    layout="wide",
)


APPLE_DATA = {
    "cash_and_equivalents": 35.934,
    "current_marketable_securities": 18.763,
    "non_current_marketable_securities": 77.723,
    "total_liquid_assets": 132.420,
    "total_marketable_securities": 96.486,
    "commercial_paper": 7.979,
    "current_term_debt": 12.350,
    "non_current_term_debt": 78.328,
    "total_debt": 98.657,
    "net_income": 112.010,
    "shareholders_equity": 73.733,
    "tax_rate": 0.156,
}

DEFAULTS = {
    "tokenized_share": 0.25,
    "legacy_haircut": 0.05,
    "tokenized_haircut": 0.03,
    "legacy_buffer_ratio": 0.20,
    "tokenized_buffer_ratio": 0.14,
    "legacy_kd": 0.0419,
    "collateral_efficiency_spread": 0.007,
    "technology_risk_premium": 0.002,
    "risk_free_rate": 0.04,
    "beta": 1.20,
    "market_risk_premium": 0.05,
    "after_tax_reinvestment_return": 0.05,
    "market_cap": 3500.0,
}

ADOPTION_SCENARIOS = {
    "Conservative": 0.10,
    "Moderate": 0.25,
    "Aggressive": 0.40,
}

STRESS_SCENARIOS = {
    "Normal Market": {
        "legacy_haircut": 0.05,
        "tokenized_haircut": 0.03,
        "legacy_buffer_ratio": 0.20,
        "tokenized_buffer_ratio": 0.14,
        "technology_risk_premium": 0.002,
        "collateral_efficiency_spread": 0.007,
    },
    "Moderate Stress": {
        "legacy_haircut": 0.08,
        "tokenized_haircut": 0.05,
        "legacy_buffer_ratio": 0.24,
        "tokenized_buffer_ratio": 0.16,
        "technology_risk_premium": 0.0035,
        "collateral_efficiency_spread": 0.005,
    },
    "Severe Stress": {
        "legacy_haircut": 0.12,
        "tokenized_haircut": 0.08,
        "legacy_buffer_ratio": 0.30,
        "tokenized_buffer_ratio": 0.18,
        "technology_risk_premium": 0.005,
        "collateral_efficiency_spread": 0.003,
    },
    "2008-Style Liquidity Shock": {
        "legacy_haircut": 0.18,
        "tokenized_haircut": 0.12,
        "legacy_buffer_ratio": 0.35,
        "tokenized_buffer_ratio": 0.24,
        "technology_risk_premium": 0.007,
        "collateral_efficiency_spread": 0.002,
    },
}


def calculate_tokenized_pool(tokenizable_asset_pool, tokenized_share):
    return tokenizable_asset_pool * tokenized_share


def calculate_usable_collateral(tokenized_pool, legacy_haircut, tokenized_haircut):
    legacy_usable_collateral = tokenized_pool * (1 - legacy_haircut)
    tokenized_usable_collateral = tokenized_pool * (1 - tokenized_haircut)
    usable_collateral_difference = (
        tokenized_usable_collateral - legacy_usable_collateral
    )
    return (
        legacy_usable_collateral,
        tokenized_usable_collateral,
        usable_collateral_difference,
    )


def calculate_effective_tokenized_buffer_ratio(
    legacy_buffer_ratio, tokenized_buffer_ratio, tokenized_share
):
    return legacy_buffer_ratio - (
        (legacy_buffer_ratio - tokenized_buffer_ratio) * tokenized_share
    )


def calculate_liquidity_buffers(
    liquid_asset_base, legacy_buffer_ratio, tokenized_buffer_ratio, tokenized_share
):
    effective_tokenized_buffer_ratio = calculate_effective_tokenized_buffer_ratio(
        legacy_buffer_ratio, tokenized_buffer_ratio, tokenized_share
    )
    legacy_buffer = liquid_asset_base * legacy_buffer_ratio
    tokenized_buffer = liquid_asset_base * effective_tokenized_buffer_ratio
    return legacy_buffer, tokenized_buffer, effective_tokenized_buffer_ratio


def calculate_capital_liberated(legacy_buffer, tokenized_buffer):
    return legacy_buffer - tokenized_buffer


def calculate_cost_of_equity(risk_free_rate, beta, market_risk_premium):
    return risk_free_rate + beta * market_risk_premium


def calculate_cost_of_debt(
    legacy_kd, collateral_efficiency_spread, technology_risk_premium, risk_free_rate
):
    raw_tokenized_kd = (
        legacy_kd - collateral_efficiency_spread + technology_risk_premium
    )
    return max(risk_free_rate, raw_tokenized_kd)


def calculate_wacc(debt_value, equity_value, cost_of_equity, kd, tax_rate):
    value = debt_value + equity_value
    if value == 0:
        return np.nan
    return ((equity_value / value) * cost_of_equity) + (
        (debt_value / value) * kd * (1 - tax_rate)
    )


def calculate_roe(net_income, shareholders_equity):
    if shareholders_equity == 0:
        return np.nan
    return net_income / shareholders_equity


def safe_divide(numerator, denominator):
    if denominator == 0:
        return np.nan
    return numerator / denominator


def get_capital_structure_values(params):
    debt_value = APPLE_DATA["total_debt"]
    if params["capital_structure_basis"] == "Market Values":
        equity_value = params["market_cap"]
    else:
        equity_value = APPLE_DATA["shareholders_equity"]
    return debt_value, equity_value


def run_scenario(params):
    liquid_asset_base = APPLE_DATA["total_liquid_assets"]
    tokenizable_asset_pool = APPLE_DATA["total_marketable_securities"]
    debt_value, equity_value = get_capital_structure_values(params)

    tokenized_pool = calculate_tokenized_pool(
        tokenizable_asset_pool, params["tokenized_share"]
    )
    legacy_usable, tokenized_usable, usable_difference = calculate_usable_collateral(
        tokenized_pool, params["legacy_haircut"], params["tokenized_haircut"]
    )
    legacy_buffer, tokenized_buffer, effective_buffer_ratio = calculate_liquidity_buffers(
        liquid_asset_base,
        params["legacy_buffer_ratio"],
        params["tokenized_buffer_ratio"],
        params["tokenized_share"],
    )
    capital_liberated = calculate_capital_liberated(legacy_buffer, tokenized_buffer)

    cost_of_equity = calculate_cost_of_equity(
        params["risk_free_rate"], params["beta"], params["market_risk_premium"]
    )
    tokenized_kd = calculate_cost_of_debt(
        params["legacy_kd"],
        params["collateral_efficiency_spread"],
        params["technology_risk_premium"],
        params["risk_free_rate"],
    )

    legacy_wacc = calculate_wacc(
        debt_value,
        equity_value,
        cost_of_equity,
        params["legacy_kd"],
        APPLE_DATA["tax_rate"],
    )
    tokenized_wacc = calculate_wacc(
        debt_value,
        equity_value,
        cost_of_equity,
        tokenized_kd,
        APPLE_DATA["tax_rate"],
    )

    legacy_roe = calculate_roe(
        APPLE_DATA["net_income"], APPLE_DATA["shareholders_equity"]
    )
    additional_income = capital_liberated * params["after_tax_reinvestment_return"]
    adjusted_net_income = APPLE_DATA["net_income"] + additional_income
    adjusted_roe = calculate_roe(adjusted_net_income, APPLE_DATA["shareholders_equity"])

    legacy_liquidity_efficiency = safe_divide(legacy_usable, legacy_buffer)
    tokenized_liquidity_efficiency = safe_divide(tokenized_usable, tokenized_buffer)

    return {
        "tokenized_pool": tokenized_pool,
        "legacy_usable_collateral": legacy_usable,
        "tokenized_usable_collateral": tokenized_usable,
        "usable_collateral_difference": usable_difference,
        "legacy_buffer": legacy_buffer,
        "tokenized_buffer": tokenized_buffer,
        "effective_tokenized_buffer_ratio": effective_buffer_ratio,
        "capital_liberated": capital_liberated,
        "cost_of_equity": cost_of_equity,
        "debt_value": debt_value,
        "equity_value": equity_value,
        "capital_structure_basis": params["capital_structure_basis"],
        "legacy_kd": params["legacy_kd"],
        "tokenized_kd": tokenized_kd,
        "legacy_wacc": legacy_wacc,
        "tokenized_wacc": tokenized_wacc,
        "wacc_change": tokenized_wacc - legacy_wacc,
        "legacy_roe": legacy_roe,
        "additional_income": additional_income,
        "adjusted_net_income": adjusted_net_income,
        "adjusted_roe": adjusted_roe,
        "roe_change": adjusted_roe - legacy_roe,
        "legacy_liquidity_efficiency": legacy_liquidity_efficiency,
        "tokenized_liquidity_efficiency": tokenized_liquidity_efficiency,
        "liquidity_efficiency_change": (
            tokenized_liquidity_efficiency - legacy_liquidity_efficiency
        ),
    }


def run_adoption_scenarios(params):
    rows = []
    for scenario, share in ADOPTION_SCENARIOS.items():
        scenario_params = {**params, "tokenized_share": share}
        result = run_scenario(scenario_params)
        rows.append(
            {
                "Scenario": scenario,
                "Tokenized Share": share,
                "Tokenized Pool": result["tokenized_pool"],
                "Legacy Usable Collateral": result["legacy_usable_collateral"],
                "Tokenized Usable Collateral": result["tokenized_usable_collateral"],
                "Capital Liberated": result["capital_liberated"],
                "Tokenized Cost of Debt": result["tokenized_kd"],
                "Legacy WACC": result["legacy_wacc"],
                "Tokenized WACC": result["tokenized_wacc"],
                "WACC Change": result["wacc_change"],
                "Adjusted ROE": result["adjusted_roe"],
                "ROE Change": result["roe_change"],
            }
        )
    return pd.DataFrame(rows)


def run_stress_scenarios(params):
    rows = []
    for scenario, values in STRESS_SCENARIOS.items():
        scenario_params = {**params, **values}
        result = run_scenario(scenario_params)
        rows.append(
            {
                "Scenario": scenario,
                "Capital Liberated": result["capital_liberated"],
                "Tokenized Cost of Debt": result["tokenized_kd"],
                "WACC Change": result["wacc_change"],
                "ROE Change": result["roe_change"],
                "Usable Collateral Difference": result["usable_collateral_difference"],
            }
        )
    return pd.DataFrame(rows)


def run_monte_carlo(params, simulations=5000, seed=42):
    rng = np.random.default_rng(seed)
    rows = []

    tokenized_shares = rng.uniform(0.10, 0.40, simulations)
    legacy_haircuts = rng.uniform(0.04, 0.08, simulations)
    tokenized_haircuts = rng.uniform(0.02, legacy_haircuts)
    legacy_buffer_ratios = rng.uniform(0.15, 0.30, simulations)
    tokenized_buffer_ratios = rng.uniform(0.10, legacy_buffer_ratios)
    collateral_spreads = rng.uniform(0.003, 0.012, simulations)
    technology_premiums = rng.uniform(0.001, 0.005, simulations)
    reinvestment_returns = rng.uniform(0.03, 0.08, simulations)

    for index in range(simulations):
        run_params = {
            **params,
            "tokenized_share": tokenized_shares[index],
            "legacy_haircut": legacy_haircuts[index],
            "tokenized_haircut": tokenized_haircuts[index],
            "legacy_buffer_ratio": legacy_buffer_ratios[index],
            "tokenized_buffer_ratio": tokenized_buffer_ratios[index],
            "collateral_efficiency_spread": collateral_spreads[index],
            "technology_risk_premium": technology_premiums[index],
            "after_tax_reinvestment_return": reinvestment_returns[index],
        }
        result = run_scenario(run_params)
        rows.append(
            {
                "Tokenized Pool": result["tokenized_pool"],
                "Legacy Usable Collateral": result["legacy_usable_collateral"],
                "Tokenized Usable Collateral": result["tokenized_usable_collateral"],
                "Capital Liberated": result["capital_liberated"],
                "Tokenized Cost of Debt": result["tokenized_kd"],
                "Legacy WACC": result["legacy_wacc"],
                "Tokenized WACC": result["tokenized_wacc"],
                "WACC Change": result["wacc_change"],
                "Adjusted ROE": result["adjusted_roe"],
                "ROE Change": result["roe_change"],
            }
        )
    return pd.DataFrame(rows)


def run_sensitivity_analysis(params):
    variable_ranges = {
        "Tokenized share": ("tokenized_share", np.linspace(0.10, 0.40, 25)),
        "Tokenized haircut": ("tokenized_haircut", np.linspace(0.02, 0.08, 25)),
        "Technology risk premium": (
            "technology_risk_premium",
            np.linspace(0.001, 0.005, 25),
        ),
        "Collateral efficiency spread": (
            "collateral_efficiency_spread",
            np.linspace(0.003, 0.012, 25),
        ),
        "Tokenized buffer ratio": (
            "tokenized_buffer_ratio",
            np.linspace(0.10, 0.20, 25),
        ),
    }

    rows = []
    for variable, (key, values) in variable_ranges.items():
        results = []
        for value in values:
            scenario_params = {**params, key: value}
            if key == "tokenized_haircut":
                scenario_params[key] = min(value, params["legacy_haircut"])
            if key == "tokenized_buffer_ratio":
                scenario_params[key] = min(value, params["legacy_buffer_ratio"])
            result = run_scenario(scenario_params)
            results.append(result)

        rows.append(
            {
                "Variable": variable,
                "WACC Change Range": max(item["wacc_change"] for item in results)
                - min(item["wacc_change"] for item in results),
                "Capital Liberated Range": max(
                    item["capital_liberated"] for item in results
                )
                - min(item["capital_liberated"] for item in results),
                "ROE Change Range": max(item["roe_change"] for item in results)
                - min(item["roe_change"] for item in results),
            }
        )
    return pd.DataFrame(rows)


def format_currency_b(value):
    return f"${value:,.2f}B"


def format_percent(value):
    return f"{value * 100:.2f}%"


def format_pp(value):
    return f"{value * 100:.2f} pp"


def style_app():
    st.markdown(
        """
        <style>
        .stApp {
            background: #fafafa;
            color: #1f2933;
        }
        .block-container {
            max-width: 1240px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }
        h1, h2, h3 {
            color: #172033;
            letter-spacing: 0;
        }
        .note-box {
            border-left: 4px solid #173b63;
            background: #ffffff;
            border-radius: 6px;
            padding: 0.9rem 1rem;
            margin: 0.8rem 0 1.2rem 0;
            color: #344054;
            line-height: 1.5;
        }
        .kpi-card {
            background: #ffffff;
            border: 1px solid #d8dee7;
            border-radius: 8px;
            padding: 0.95rem 1rem;
            min-height: 108px;
        }
        .kpi-label {
            color: #5f6b7a;
            font-size: 0.84rem;
            margin-bottom: 0.35rem;
        }
        .kpi-value {
            color: #102a43;
            font-size: 1.42rem;
            font-weight: 700;
            line-height: 1.15;
        }
        .kpi-help {
            color: #687385;
            font-size: 0.78rem;
            margin-top: 0.35rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def initialize_state():
    for key, value in DEFAULTS.items():
        st.session_state.setdefault(key, value)
    st.session_state.setdefault("scenario_selector", "Custom")
    st.session_state.setdefault("capital_structure_basis", "Book Values")


def apply_scenario_preset():
    selected = st.session_state.scenario_selector
    if selected != "Custom":
        for key, value in STRESS_SCENARIOS[selected].items():
            st.session_state[key] = value


def sidebar_controls():
    st.sidebar.title("Simulation Controls")
    st.sidebar.selectbox(
        "Scenario Selector",
        [
            "Custom",
            "Normal Market",
            "Moderate Stress",
            "Severe Stress",
            "2008-Style Liquidity Shock",
        ],
        key="scenario_selector",
        on_change=apply_scenario_preset,
    )

    st.sidebar.subheader("Capital Structure Basis")
    st.sidebar.radio(
        "Capital Structure Basis",
        ["Book Values", "Market Values"],
        key="capital_structure_basis",
    )
    if st.session_state.capital_structure_basis == "Market Values":
        st.sidebar.number_input(
            "Market capitalization, USD billions",
            min_value=1.0,
            max_value=10000.0,
            step=50.0,
            key="market_cap",
        )

    st.sidebar.subheader("Adoption and Collateral Parameters")
    st.sidebar.slider(
        "Tokenized share of marketable securities",
        0.10,
        0.40,
        key="tokenized_share",
        step=0.01,
        format="%.2f",
    )
    st.sidebar.slider(
        "Legacy haircut",
        0.04,
        0.18,
        key="legacy_haircut",
        step=0.005,
        format="%.3f",
    )
    st.sidebar.slider(
        "Tokenized haircut",
        0.02,
        0.12,
        key="tokenized_haircut",
        step=0.005,
        format="%.3f",
    )

    st.sidebar.subheader("Liquidity Parameters")
    st.sidebar.slider(
        "Legacy liquidity buffer ratio",
        0.15,
        0.35,
        key="legacy_buffer_ratio",
        step=0.01,
        format="%.2f",
    )
    st.sidebar.slider(
        "Tokenized liquidity buffer ratio",
        0.10,
        0.24,
        key="tokenized_buffer_ratio",
        step=0.01,
        format="%.2f",
    )

    st.sidebar.subheader("Funding Parameters")
    st.sidebar.slider(
        "Legacy cost of debt",
        0.03,
        0.08,
        key="legacy_kd",
        step=0.001,
        format="%.3f",
    )
    st.sidebar.slider(
        "Collateral efficiency spread",
        0.002,
        0.012,
        key="collateral_efficiency_spread",
        step=0.001,
        format="%.3f",
    )
    st.sidebar.slider(
        "Technology risk premium",
        0.001,
        0.008,
        key="technology_risk_premium",
        step=0.0005,
        format="%.4f",
    )

    st.sidebar.subheader("WACC Parameters")
    st.sidebar.slider(
        "Risk-free rate",
        0.02,
        0.06,
        key="risk_free_rate",
        step=0.001,
        format="%.3f",
    )
    st.sidebar.slider("Beta", 0.8, 1.6, key="beta", step=0.05, format="%.2f")
    st.sidebar.slider(
        "Market risk premium",
        0.03,
        0.08,
        key="market_risk_premium",
        step=0.001,
        format="%.3f",
    )

    st.sidebar.subheader("ROE Parameters")
    st.sidebar.slider(
        "After-tax reinvestment return",
        0.03,
        0.08,
        key="after_tax_reinvestment_return",
        step=0.001,
        format="%.3f",
    )

    params = {key: st.session_state[key] for key in DEFAULTS}
    params["capital_structure_basis"] = st.session_state.capital_structure_basis
    return params


def note(text):
    st.markdown(f'<div class="note-box">{text}</div>', unsafe_allow_html=True)


def render_kpi(label, value, help_text=""):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-help">{help_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_header():
    st.title("Applied Simulation of Tokenized Treasury Collateral")
    st.caption("A real-company counterfactual model using Apple Inc. 2025 financial data")
    note(
        "This dashboard does not claim that Apple currently uses RWA tokenization. "
        "Apple's financial data are used as a real-company baseline to simulate how "
        "tokenized collateral infrastructure could affect institutional liquidity and "
        "capital efficiency."
    )


def render_baseline_data():
    st.header("Baseline Company Data")
    st.write("These variables form the real-company baseline used to calibrate the simulation.")
    labels = {
        "cash_and_equivalents": "Cash and cash equivalents",
        "current_marketable_securities": "Current marketable securities",
        "non_current_marketable_securities": "Non-current marketable securities",
        "total_liquid_assets": "Total liquid assets",
        "total_marketable_securities": "Total marketable securities",
        "commercial_paper": "Commercial paper",
        "current_term_debt": "Current term debt",
        "non_current_term_debt": "Non-current term debt",
        "total_debt": "Total debt",
        "net_income": "Net income",
        "shareholders_equity": "Shareholders' equity",
        "tax_rate": "Effective tax rate",
    }
    rows = [
        {
            "Variable": label,
            "Value": format_percent(APPLE_DATA[key])
            if key == "tax_rate"
            else format_currency_b(APPLE_DATA[key]),
        }
        for key, label in labels.items()
    ]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def render_core_kpis(result):
    st.header("Key Simulation Outputs")
    note(
        "The model estimates collateral usability, liquidity buffer reduction, capital "
        "liberation, funding cost compression, WACC impact, and ROE impact under the "
        "selected counterfactual assumptions."
    )
    kpis = [
        ("Tokenized collateral pool", format_currency_b(result["tokenized_pool"]), ""),
        (
            "Legacy usable collateral",
            format_currency_b(result["legacy_usable_collateral"]),
            "",
        ),
        (
            "Tokenized usable collateral",
            format_currency_b(result["tokenized_usable_collateral"]),
            "",
        ),
        (
            "Additional usable collateral",
            format_currency_b(result["usable_collateral_difference"]),
            "",
        ),
        ("Legacy liquidity buffer", format_currency_b(result["legacy_buffer"]), ""),
        ("Tokenized liquidity buffer", format_currency_b(result["tokenized_buffer"]), ""),
        ("Capital liberated", format_currency_b(result["capital_liberated"]), ""),
        ("Legacy cost of debt", format_percent(result["legacy_kd"]), ""),
        ("Tokenized cost of debt", format_percent(result["tokenized_kd"]), ""),
        ("Legacy WACC", format_percent(result["legacy_wacc"]), ""),
        ("Tokenized WACC", format_percent(result["tokenized_wacc"]), ""),
        ("WACC change", format_pp(result["wacc_change"]), "Percentage points"),
        ("Legacy ROE", format_percent(result["legacy_roe"]), ""),
        ("Adjusted ROE", format_percent(result["adjusted_roe"]), ""),
        ("ROE change", format_pp(result["roe_change"]), "Percentage points"),
    ]
    for start in range(0, len(kpis), 3):
        cols = st.columns(3)
        for col, (label, value, helper) in zip(cols, kpis[start : start + 3]):
            with col:
                render_kpi(label, value, helper)

    st.info(
        "Book-value WACC uses accounting values from Apple's financial statements. "
        "Market-value WACC uses Apple's market capitalization as the equity value. "
        "Market-value WACC is often preferred in valuation, while book-value WACC is "
        f"kept for accounting consistency. Current basis: {result['capital_structure_basis']}."
    )
    st.warning(
        "Apple's ROE may appear structurally high because shareholders' equity is "
        "affected by share repurchases; therefore, ROE should be interpreted carefully. "
        "ROE remains calculated using book equity even when WACC uses market-value equity."
    )


def render_comparison_table(result, params):
    st.header("Legacy vs Tokenized Comparison Table")
    rows = [
        {
            "Metric": "Haircut",
            "Legacy": format_percent(params["legacy_haircut"]),
            "Tokenized": format_percent(params["tokenized_haircut"]),
            "Difference": format_pp(params["tokenized_haircut"] - params["legacy_haircut"]),
        },
        {
            "Metric": "Usable collateral",
            "Legacy": format_currency_b(result["legacy_usable_collateral"]),
            "Tokenized": format_currency_b(result["tokenized_usable_collateral"]),
            "Difference": format_currency_b(result["usable_collateral_difference"]),
        },
        {
            "Metric": "Liquidity buffer",
            "Legacy": format_currency_b(result["legacy_buffer"]),
            "Tokenized": format_currency_b(result["tokenized_buffer"]),
            "Difference": format_currency_b(
                result["tokenized_buffer"] - result["legacy_buffer"]
            ),
        },
        {
            "Metric": "Cost of debt",
            "Legacy": format_percent(result["legacy_kd"]),
            "Tokenized": format_percent(result["tokenized_kd"]),
            "Difference": format_pp(result["tokenized_kd"] - result["legacy_kd"]),
        },
        {
            "Metric": "WACC",
            "Legacy": format_percent(result["legacy_wacc"]),
            "Tokenized": format_percent(result["tokenized_wacc"]),
            "Difference": format_pp(result["wacc_change"]),
        },
        {
            "Metric": "ROE",
            "Legacy": format_percent(result["legacy_roe"]),
            "Tokenized": format_percent(result["adjusted_roe"]),
            "Difference": format_pp(result["roe_change"]),
        },
        {
            "Metric": "Liquidity efficiency ratio",
            "Legacy": f"{result['legacy_liquidity_efficiency']:.2f}x",
            "Tokenized": f"{result['tokenized_liquidity_efficiency']:.2f}x",
            "Difference": f"{result['liquidity_efficiency_change']:.2f}x",
        },
    ]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def format_scenario_table(df):
    formatted = df.copy()
    currency_cols = [
        "Tokenized Pool",
        "Legacy Usable Collateral",
        "Tokenized Usable Collateral",
        "Capital Liberated",
        "Usable Collateral Difference",
    ]
    percent_cols = [
        "Tokenized Share",
        "Tokenized Cost of Debt",
        "Legacy WACC",
        "Tokenized WACC",
        "Adjusted ROE",
    ]
    pp_cols = ["WACC Change", "ROE Change"]
    for col in currency_cols:
        if col in formatted.columns:
            formatted[col] = formatted[col].map(format_currency_b)
    for col in percent_cols:
        if col in formatted.columns:
            formatted[col] = formatted[col].map(format_percent)
    for col in pp_cols:
        if col in formatted.columns:
            formatted[col] = formatted[col].map(format_pp)
    return formatted


def render_adoption_analysis(params):
    st.header("Adoption Scenario Analysis")
    note(
        "The adoption scenarios compare conservative, moderate, and aggressive levels "
        "of tokenized marketable securities while holding the other selected assumptions constant."
    )
    df = run_adoption_scenarios(params)
    st.dataframe(format_scenario_table(df), use_container_width=True, hide_index=True)

    capital_fig = px.bar(
        df,
        x="Scenario",
        y="Capital Liberated",
        color="Scenario",
        color_discrete_sequence=["#6c7f93", "#173b63", "#8aa6bf"],
        title="Capital liberated by adoption scenario",
    )
    capital_fig.update_layout(yaxis_title="USD billions", showlegend=False)
    st.plotly_chart(capital_fig, use_container_width=True)

    rate_df = df.copy()
    rate_df["WACC Change (pp)"] = rate_df["WACC Change"] * 100
    rate_df["ROE Change (pp)"] = rate_df["ROE Change"] * 100
    cols = st.columns(2)
    with cols[0]:
        wacc_fig = px.bar(
            rate_df,
            x="Scenario",
            y="WACC Change (pp)",
            color="Scenario",
            color_discrete_sequence=["#6c7f93", "#173b63", "#8aa6bf"],
            title="WACC change by adoption scenario",
        )
        wacc_fig.update_layout(yaxis_title="Percentage points", showlegend=False)
        st.plotly_chart(wacc_fig, use_container_width=True)
    with cols[1]:
        roe_fig = px.bar(
            rate_df,
            x="Scenario",
            y="ROE Change (pp)",
            color="Scenario",
            color_discrete_sequence=["#6c7f93", "#173b63", "#8aa6bf"],
            title="ROE change by adoption scenario",
        )
        roe_fig.update_layout(yaxis_title="Percentage points", showlegend=False)
        st.plotly_chart(roe_fig, use_container_width=True)


def render_stress_analysis(params):
    st.header("Market Stress Scenario Analysis")
    note(
        "Stress scenarios test whether the simulated benefits remain visible when "
        "haircuts, liquidity buffers, technology risk premia, and collateral efficiency "
        "spreads move against the tokenized scenario."
    )
    st.info(
        "The 2008-style liquidity shock is used as a stress-test reference. It does "
        "not imply that tokenized collateral existed during the 2008 crisis."
    )
    df = run_stress_scenarios(params)
    st.dataframe(format_scenario_table(df), use_container_width=True, hide_index=True)

    chart_df = df.melt(
        id_vars="Scenario",
        value_vars=["Capital Liberated", "Usable Collateral Difference"],
        var_name="Metric",
        value_name="USD Billions",
    )
    stress_fig = px.bar(
        chart_df,
        x="Scenario",
        y="USD Billions",
        color="Metric",
        barmode="group",
        color_discrete_sequence=["#173b63", "#7895b2"],
        title="Stress scenario collateral and liquidity effects",
    )
    st.plotly_chart(stress_fig, use_container_width=True)

    rate_df = df.copy()
    rate_df["WACC Change (pp)"] = rate_df["WACC Change"] * 100
    rate_df["ROE Change (pp)"] = rate_df["ROE Change"] * 100
    cols = st.columns(2)
    with cols[0]:
        wacc_fig = px.line(
            rate_df,
            x="Scenario",
            y="WACC Change (pp)",
            markers=True,
            title="WACC change under stress",
            color_discrete_sequence=["#173b63"],
        )
        wacc_fig.update_layout(yaxis_title="Percentage points")
        st.plotly_chart(wacc_fig, use_container_width=True)
    with cols[1]:
        roe_fig = px.line(
            rate_df,
            x="Scenario",
            y="ROE Change (pp)",
            markers=True,
            title="ROE change under stress",
            color_discrete_sequence=["#7895b2"],
        )
        roe_fig.update_layout(yaxis_title="Percentage points")
        st.plotly_chart(roe_fig, use_container_width=True)


def render_monte_carlo(params):
    st.header("Monte Carlo Robustness Testing")
    note(
        "The Monte Carlo simulation evaluates whether the model's conclusions remain "
        "stable when key assumptions vary within plausible ranges."
    )
    if st.button("Run Monte Carlo Simulation", type="primary"):
        mc_df = run_monte_carlo(params)
        summary_cols = ["Capital Liberated", "WACC Change", "ROE Change"]
        summary = mc_df[summary_cols].agg(["mean", "median", "std", "min", "max"])
        summary.loc["5th percentile"] = mc_df[summary_cols].quantile(0.05)
        summary.loc["95th percentile"] = mc_df[summary_cols].quantile(0.95)
        formatted_summary = summary.copy()
        formatted_summary["Capital Liberated"] = formatted_summary[
            "Capital Liberated"
        ].map(format_currency_b)
        formatted_summary["WACC Change"] = formatted_summary["WACC Change"].map(format_pp)
        formatted_summary["ROE Change"] = formatted_summary["ROE Change"].map(format_pp)
        st.dataframe(formatted_summary, use_container_width=True)

        cols = st.columns(3)
        charts = [
            ("WACC Change", "WACC change distribution"),
            ("Capital Liberated", "Capital liberated distribution"),
            ("ROE Change", "ROE change distribution"),
        ]
        for col, (metric, title) in zip(cols, charts):
            with col:
                plot_df = mc_df.copy()
                x_col = metric
                if metric in ["WACC Change", "ROE Change"]:
                    x_col = f"{metric} (pp)"
                    plot_df[x_col] = plot_df[metric] * 100
                fig = px.histogram(
                    plot_df,
                    x=x_col,
                    nbins=45,
                    title=title,
                    color_discrete_sequence=["#173b63"],
                )
                st.plotly_chart(fig, use_container_width=True)


def render_sensitivity(params):
    st.header("Sensitivity Analysis")
    note(
        "Sensitivity analysis varies one parameter at a time while holding other "
        "assumptions constant. This identifies which assumptions have the largest "
        "effect on WACC change, capital liberated, and ROE change."
    )
    df = run_sensitivity_analysis(params)
    formatted = df.copy()
    formatted["WACC Change Range"] = formatted["WACC Change Range"].map(format_pp)
    formatted["Capital Liberated Range"] = formatted["Capital Liberated Range"].map(
        format_currency_b
    )
    formatted["ROE Change Range"] = formatted["ROE Change Range"].map(format_pp)
    st.dataframe(formatted, use_container_width=True, hide_index=True)

    chart_df = df.sort_values("Capital Liberated Range", ascending=True)
    fig = px.bar(
        chart_df,
        x="Capital Liberated Range",
        y="Variable",
        orientation="h",
        title="Sensitivity by capital liberated range",
        color_discrete_sequence=["#173b63"],
    )
    fig.update_layout(xaxis_title="USD billions", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)


def render_risk_architecture():
    st.header("Institutional Risk Architecture")
    note(
        "Institutional adoption of tokenized collateral depends not only on settlement "
        "efficiency, but also on segregated risk architecture capable of limiting "
        "contagion exposure and preserving collateral integrity."
    )
    architecture = pd.DataFrame(
        [
            ["Settlement speed", "Lower", "Higher", "Higher"],
            ["Collateral segregation", "Strong", "Weak", "Strong"],
            ["Contagion risk", "Low", "High", "Low"],
            ["Liquidity efficiency", "Medium", "High", "Medium-High"],
            ["Institutional compatibility", "High", "Low", "High"],
            ["Counterparty isolation", "Strong", "Weak", "Strong"],
            ["Smart contract exposure", "None", "High", "Medium"],
            ["Operational transparency", "Medium", "Medium", "High"],
        ],
        columns=[
            "Parameter",
            "Legacy System",
            "Pooled Tokenization",
            "Isolated Vault Architecture",
        ],
    )
    st.dataframe(architecture, use_container_width=True, hide_index=True)


def render_interpretation_and_limitations():
    st.header("Academic Interpretation")
    note(
        "The simulation suggests that RWA tokenization affects financial market efficiency "
        "mainly through collateral mobility and liquidity buffer reduction. The value does "
        "not come primarily from speculative secondary trading, but from transforming "
        "liquid financial assets into programmable, segregated, and institutionally usable "
        "collateral.<br><br>"
        "However, the benefits are conditional on institutional-grade risk architecture. "
        "Pooled liquidity models may introduce contagion risk, while isolated collateral "
        "structures may improve institutional compatibility by preserving risk segregation."
    )

    with st.expander("Model Limitations", expanded=False):
        st.markdown(
            """
            - This is a counterfactual simulation, not historical evidence.
            - Apple is used as a proxy and is not assumed to use RWA tokenization.
            - Assumptions are based on financial logic and scenario design.
            - The model uses book values of debt and equity for simplicity.
            - Apple's ROE should be interpreted carefully because its book equity is affected by share repurchases.
            - RWA tokenization markets remain emerging and fragmented.
            - Technology, custody, oracle, and regulatory risks may reduce benefits.
            - Results should be interpreted as indicative, not predictive.
            """
        )


def main():
    style_app()
    initialize_state()
    params = sidebar_controls()
    result = run_scenario(params)

    render_header()
    render_baseline_data()
    st.divider()
    render_core_kpis(result)
    st.divider()
    render_comparison_table(result, params)
    st.divider()
    render_adoption_analysis(params)
    st.divider()
    render_stress_analysis(params)
    st.divider()
    render_monte_carlo(params)
    st.divider()
    render_sensitivity(params)
    st.divider()
    render_risk_architecture()
    st.divider()
    render_interpretation_and_limitations()


if __name__ == "__main__":
    main()
