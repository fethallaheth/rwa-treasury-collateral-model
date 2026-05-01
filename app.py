import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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


ACCENT = "#0f2f56"
ACCENT_LIGHT = "#5d82a7"
ACCENT_PALE = "#d9e7f2"
TEXT = "#172033"
MUTED = "#667085"
POSITIVE = "#2f6f4e"
CAUTION = "#b42318"
GOLD = "#b68b2c"
GRID = "#d8dee7"
PLOTLY_TEMPLATE = "plotly_white"
SEQUENTIAL_SCALE = [
    [0.0, "#f7fbff"],
    [0.25, "#e4eff7"],
    [0.55, "#b8d1e5"],
    [0.80, "#82aacb"],
    [1.0, "#5d82a7"],
]
DIVERGING_SCALE = [
    [0.0, "#7eb28e"],
    [0.45, "#e4f0e7"],
    [0.50, "#f8fafc"],
    [0.55, "#f4dfdc"],
    [1.0, "#d88a80"],
]


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
                "Additional Usable Collateral": result["usable_collateral_difference"],
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
                "Tokenized Share": scenario_params["tokenized_share"],
                "Tokenized Pool": result["tokenized_pool"],
                "Legacy Usable Collateral": result["legacy_usable_collateral"],
                "Tokenized Usable Collateral": result["tokenized_usable_collateral"],
                "Additional Usable Collateral": result["usable_collateral_difference"],
                "Capital Liberated": result["capital_liberated"],
                "Tokenized Cost of Debt": result["tokenized_kd"],
                "Legacy WACC": result["legacy_wacc"],
                "Tokenized WACC": result["tokenized_wacc"],
                "WACC Change": result["wacc_change"],
                "Adjusted ROE": result["adjusted_roe"],
                "ROE Change": result["roe_change"],
                "Usable Collateral Difference": result["usable_collateral_difference"],
                "Legacy Liquidity Buffer": result["legacy_buffer"],
                "Tokenized Liquidity Buffer": result["tokenized_buffer"],
            }
        )
    return pd.DataFrame(rows)


def run_scenario_matrix(params):
    rows = []
    for market_scenario, stress_values in STRESS_SCENARIOS.items():
        for adoption_scenario, tokenized_share in ADOPTION_SCENARIOS.items():
            scenario_params = {
                **params,
                **stress_values,
                "tokenized_share": tokenized_share,
            }
            result = run_scenario(scenario_params)
            rows.append(
                {
                    "Scenario": market_scenario,
                    "Adoption Scenario": adoption_scenario,
                    "Adoption": tokenized_share,
                    "Adoption Label": format_percent(tokenized_share),
                    "Tokenized Pool": result["tokenized_pool"],
                    "Legacy Usable Collateral": result["legacy_usable_collateral"],
                    "Tokenized Usable Collateral": result[
                        "tokenized_usable_collateral"
                    ],
                    "Additional Usable Collateral": result[
                        "usable_collateral_difference"
                    ],
                    "Capital Liberated": result["capital_liberated"],
                    "Legacy WACC": result["legacy_wacc"],
                    "Tokenized WACC": result["tokenized_wacc"],
                    "WACC Change": result["wacc_change"],
                    "Adjusted ROE": result["adjusted_roe"],
                    "ROE Change": result["roe_change"],
                }
            )
    return pd.DataFrame(rows)


@st.cache_data(show_spinner=False)
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
                "Additional Usable Collateral": result["usable_collateral_difference"],
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
            border-left: 4px solid #0f2f56;
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
    st.header("Executive Simulation Summary")
    note(
        "Positive capital liberated and additional usable collateral indicate improved "
        "liquidity and collateral efficiency. WACC improvement is conditional on the "
        "balance between collateral efficiency gains and technology risk premiums."
    )

    rows = [
        [
            ("Tokenized collateral pool", format_currency_b(result["tokenized_pool"]), None, "normal"),
            (
                "Additional usable collateral",
                format_currency_b(result["usable_collateral_difference"]),
                format_currency_b(result["usable_collateral_difference"]),
                "normal",
            ),
            (
                "Capital liberated",
                format_currency_b(result["capital_liberated"]),
                format_currency_b(result["capital_liberated"]),
                "normal",
            ),
            ("Legacy WACC", format_percent(result["legacy_wacc"]), None, "normal"),
            (
                "Tokenized WACC",
                format_percent(result["tokenized_wacc"]),
                format_pp(result["wacc_change"]),
                "inverse",
            ),
        ],
        [
            (
                "WACC change",
                format_pp(result["wacc_change"]),
                format_pp(result["wacc_change"]),
                "inverse",
            ),
            ("Legacy ROE", format_percent(result["legacy_roe"]), None, "normal"),
            (
                "Adjusted ROE",
                format_percent(result["adjusted_roe"]),
                format_pp(result["roe_change"]),
                "normal",
            ),
            (
                "ROE change",
                format_pp(result["roe_change"]),
                format_pp(result["roe_change"]),
                "normal",
            ),
            ("Tokenized cost of debt", format_percent(result["tokenized_kd"]), None, "normal"),
        ],
    ]
    for metric_row in rows:
        cols = st.columns(5)
        for col, (label, value, delta, delta_color) in zip(cols, metric_row):
            with col:
                st.metric(label, value, delta=delta, delta_color=delta_color)

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
    st.header("Baseline Financial Bridges")
    cols = st.columns(2)
    with cols[0]:
        st.plotly_chart(plot_liquidity_waterfall(result), use_container_width=True)
        note(
            "This chart shows how tokenized collateral may reduce precautionary "
            "liquidity reserves. The difference between the legacy and tokenized "
            "buffer represents capital liberated under the selected assumptions."
        )
    with cols[1]:
        st.plotly_chart(plot_cost_of_debt_waterfall(result, params), use_container_width=True)
        note(
            "The cost of debt bridge separates the expected funding benefit of "
            "improved collateral mobility from the additional risk premium introduced "
            "by tokenized infrastructure."
        )

    cols = st.columns(2)
    with cols[0]:
        st.plotly_chart(
            plot_dumbbell(
                build_amount_dumbbell_data(result),
                "Legacy vs. Tokenized Scenario Comparison: Amount Metrics",
                "USD billions",
            ),
            use_container_width=True,
        )
    with cols[1]:
        st.plotly_chart(
            plot_dumbbell(
                build_rate_dumbbell_data(result),
                "Legacy vs. Tokenized Scenario Comparison: Percentage Metrics",
                "Percent",
            ),
            use_container_width=True,
        )
    note(
        "The connected-dot comparison highlights how the same asset base behaves "
        "under legacy and tokenized collateral infrastructure."
    )

    st.subheader("Legacy vs Tokenized Comparison Table")
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
        "Additional Usable Collateral",
        "Capital Liberated",
        "Usable Collateral Difference",
        "Legacy Liquidity Buffer",
        "Tokenized Liquidity Buffer",
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


def apply_chart_style(fig, title, x_title=None, y_title=None, height=430):
    fig.update_layout(
        title=title,
        template=PLOTLY_TEMPLATE,
        height=height,
        margin=dict(l=30, r=30, t=72, b=40),
        font=dict(color=TEXT, size=13),
        title_font=dict(size=18, color=TEXT),
        title_x=0.02,
        legend_title_text="",
        legend=dict(
            font=dict(color=TEXT, size=12),
            bgcolor="rgba(255,255,255,0.92)",
            bordercolor=GRID,
            borderwidth=1,
        ),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
    )
    fig.update_xaxes(
        title=x_title,
        title_font=dict(color=MUTED, size=13),
        tickfont=dict(color=TEXT, size=12),
        gridcolor="#e5e9f0",
        linecolor=GRID,
        zerolinecolor=GRID,
    )
    fig.update_yaxes(
        title=y_title,
        title_font=dict(color=MUTED, size=13),
        tickfont=dict(color=TEXT, size=12),
        gridcolor="#e5e9f0",
        linecolor=GRID,
        zerolinecolor=GRID,
    )
    return fig


def format_chart_label(value, unit):
    if unit == "currency":
        return f"${value:,.2f}B"
    if unit == "percent":
        return f"{value:.2f}%"
    if unit == "pp":
        return f"{value:.2f} pp"
    return f"{value:,.2f}"


def plot_liquidity_waterfall(result):
    reduction = result["tokenized_buffer"] - result["legacy_buffer"]
    values = [result["legacy_buffer"], reduction, result["tokenized_buffer"]]
    fig = go.Figure(
        go.Waterfall(
            measure=["absolute", "relative", "absolute"],
            x=[
                "Legacy liquidity buffer",
                "Reduction / capital liberated",
                "Tokenized liquidity buffer",
            ],
            y=values,
            text=[format_chart_label(value, "currency") for value in values],
            textposition="outside",
            connector={"line": {"color": GRID}},
            decreasing={"marker": {"color": POSITIVE}},
            increasing={"marker": {"color": GOLD}},
            totals={"marker": {"color": ACCENT}},
            hovertemplate="%{x}<br>%{y:,.2f} USD billions<extra></extra>",
        )
    )
    fig.update_traces(textfont=dict(color=TEXT, size=12), cliponaxis=False)
    return apply_chart_style(
        fig,
        "Liquidity Buffer Bridge: From Legacy Reserve to Tokenized Reserve",
        y_title="USD billions",
    )


def plot_cost_of_debt_waterfall(result, params):
    values = [
        result["legacy_kd"] * 100,
        -params["collateral_efficiency_spread"] * 100,
        params["technology_risk_premium"] * 100,
        result["tokenized_kd"] * 100,
    ]
    fig = go.Figure(
        go.Waterfall(
            measure=["absolute", "relative", "relative", "absolute"],
            x=[
                "Legacy cost of debt",
                "Collateral efficiency spread",
                "Technology risk premium",
                "Tokenized cost of debt",
            ],
            y=values,
            text=[format_chart_label(value, "percent") for value in values],
            textposition="outside",
            connector={"line": {"color": GRID}},
            decreasing={"marker": {"color": POSITIVE}},
            increasing={"marker": {"color": CAUTION}},
            totals={"marker": {"color": ACCENT}},
            hovertemplate="%{x}<br>%{y:.2f}%<extra></extra>",
        )
    )
    fig.update_traces(textfont=dict(color=TEXT, size=12), cliponaxis=False)
    return apply_chart_style(
        fig,
        "Cost of Debt Bridge: Efficiency Gain vs. Technology Risk",
        y_title="Percent",
    )


def plot_heatmap(df, value_col, title, value_label, show_as_pp=False, diverging=False):
    plot_df = df.copy()
    plot_df["Plot Value"] = plot_df[value_col] * 100 if show_as_pp else plot_df[value_col]
    pivot = plot_df.pivot(
        index="Scenario", columns="Adoption Label", values="Plot Value"
    ).loc[list(STRESS_SCENARIOS.keys())]
    pivot = pivot[[format_percent(value) for value in ADOPTION_SCENARIOS.values()]]
    cell_unit = "pp" if show_as_pp else "currency"
    text = (
        pivot.map(lambda value: format_chart_label(value, cell_unit))
        if hasattr(pivot, "map")
        else pivot.applymap(lambda value: format_chart_label(value, cell_unit))
    )
    colorscale = DIVERGING_SCALE if diverging else SEQUENTIAL_SCALE
    zmin = None
    zmax = None
    if diverging:
        max_abs = float(np.nanmax(np.abs(pivot.values))) or 1.0
        zmin = -max_abs
        zmax = max_abs

    heatmap_options = {
        "z": pivot.values,
        "x": pivot.columns,
        "y": pivot.index,
        "colorscale": colorscale,
        "zmin": zmin,
        "zmax": zmax,
        "colorbar": {"title": value_label},
        "text": text.values,
        "texttemplate": "%{text}",
        "textfont": {"color": TEXT, "size": 12},
        "hovertemplate": (
            "Scenario: %{y}<br>"
            "Adoption ratio: %{x}<br>"
            f"{value_label}: " + "%{z:.2f}<extra></extra>"
        ),
    }
    if diverging:
        heatmap_options["zmid"] = 0

    fig = go.Figure(
        go.Heatmap(**heatmap_options)
    )
    return apply_chart_style(
        fig,
        title,
        x_title="Tokenized adoption ratio",
        y_title="Market scenario",
    )


def plot_grouped_bar(df):
    plot_df = df.copy()
    plot_df["Label"] = plot_df["Additional Usable Collateral"].map(
        lambda value: format_chart_label(value, "currency")
    )
    fig = px.bar(
        plot_df,
        x="Scenario",
        y="Additional Usable Collateral",
        color="Adoption Label",
        barmode="group",
        text="Label",
        color_discrete_sequence=[ACCENT_LIGHT, ACCENT, POSITIVE],
        category_orders={
            "Scenario": list(STRESS_SCENARIOS.keys()),
            "Adoption Label": [format_percent(value) for value in ADOPTION_SCENARIOS.values()],
        },
        hover_data={
            "Additional Usable Collateral": ":,.2f",
            "Adoption": ":.0%",
            "Adoption Label": False,
        },
    )
    fig.update_traces(
        textposition="outside",
        textfont=dict(color=TEXT, size=11),
        cliponaxis=False,
    )
    fig.update_layout(uniformtext_minsize=10, uniformtext_mode="hide")
    return apply_chart_style(
        fig,
        "Additional Usable Collateral by Scenario and Adoption Level",
        x_title="Market scenario",
        y_title="USD billions",
    )


def plot_dumbbell(df, title, x_title):
    fig = go.Figure()
    unit = "currency" if "USD" in x_title else "percent"
    for _, row in df.iterrows():
        fig.add_trace(
            go.Scatter(
                x=[row["Legacy"], row["Tokenized"]],
                y=[row["Metric"], row["Metric"]],
                mode="lines",
                line=dict(color="#aab4c3", width=4),
                showlegend=False,
                hoverinfo="skip",
            )
        )
        fig.add_annotation(
            x=row["Legacy"],
            y=row["Metric"],
            text=format_chart_label(row["Legacy"], unit),
            showarrow=False,
            xshift=-34,
            yshift=16,
            font=dict(color=MUTED, size=11),
            bgcolor="rgba(255,255,255,0.85)",
        )
        fig.add_annotation(
            x=row["Tokenized"],
            y=row["Metric"],
            text=format_chart_label(row["Tokenized"], unit),
            showarrow=False,
            xshift=34,
            yshift=16,
            font=dict(color=ACCENT, size=11),
            bgcolor="rgba(255,255,255,0.85)",
        )
    fig.add_trace(
        go.Scatter(
            x=df["Legacy"],
            y=df["Metric"],
            mode="markers",
            name="Legacy",
            marker=dict(color=MUTED, size=12, line=dict(color="#ffffff", width=1)),
            hovertemplate="Legacy %{y}: %{x:.2f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["Tokenized"],
            y=df["Metric"],
            mode="markers",
            name="Tokenized",
            marker=dict(color=ACCENT, size=12, line=dict(color="#ffffff", width=1)),
            hovertemplate="Tokenized %{y}: %{x:.2f}<extra></extra>",
        )
    )
    minimum = df[["Legacy", "Tokenized"]].min().min()
    maximum = df[["Legacy", "Tokenized"]].max().max()
    padding = max((maximum - minimum) * 0.20, 0.5)
    fig = apply_chart_style(fig, title, x_title=x_title, y_title="", height=360)
    fig.update_xaxes(range=[minimum - padding, maximum + padding])
    return fig


def plot_stress_wacc_bar(stress_df):
    plot_df = stress_df.copy()
    plot_df["WACC Change (pp)"] = plot_df["WACC Change"] * 100
    plot_df["Label"] = plot_df["WACC Change (pp)"].map(
        lambda value: format_chart_label(value, "pp")
    )
    fig = px.bar(
        plot_df,
        x="Scenario",
        y="WACC Change (pp)",
        color="WACC Change (pp)",
        text="Label",
        color_continuous_scale=DIVERGING_SCALE,
        color_continuous_midpoint=0,
        hover_data={"WACC Change (pp)": ":.2f"},
    )
    fig.update_traces(
        textposition="outside",
        textfont=dict(color=TEXT, size=11),
        cliponaxis=False,
    )
    fig.add_hline(y=0, line_width=1, line_color=TEXT)
    fig.update_layout(coloraxis_showscale=False)
    return apply_chart_style(
        fig,
        "WACC Change Under Market Stress Conditions",
        x_title="Market scenario",
        y_title="Percentage points",
    )


def plot_histogram_with_markers(df, column, title, x_title, show_as_pp=False):
    values = df[column] * 100 if show_as_pp else df[column]
    mean_value = values.mean()
    median_value = values.median()
    unit = "pp" if show_as_pp else "currency"
    fig = go.Figure(
        go.Histogram(
            x=values,
            nbinsx=45,
            marker_color=ACCENT,
            marker_line=dict(color="#ffffff", width=0.5),
            opacity=0.86,
            hovertemplate=f"{x_title}: %{{x:.2f}}<br>Frequency: %{{y}}<extra></extra>",
        )
    )
    fig.add_vline(
        x=mean_value,
        line_color=CAUTION,
        annotation_text=f"Mean {format_chart_label(mean_value, unit)}",
        annotation_position="top",
    )
    fig.add_vline(
        x=median_value,
        line_color=POSITIVE,
        annotation_text=f"Median {format_chart_label(median_value, unit)}",
        annotation_position="top",
    )
    if show_as_pp:
        fig.add_vline(
            x=0,
            line_color=TEXT,
            line_dash="dash",
            annotation_text="Zero 0.00 pp",
            annotation_position="bottom",
        )
    return apply_chart_style(fig, title, x_title=x_title, y_title="Frequency")


def plot_boxplot(df, columns, title, y_title, show_as_pp=False):
    fig = go.Figure()
    unit = "pp" if show_as_pp else "currency"
    for column in columns:
        values = df[column] * 100 if show_as_pp else df[column]
        median_value = values.median()
        fig.add_trace(
            go.Box(
                y=values,
                name=column,
                marker_color=ACCENT if column == columns[0] else GOLD,
                boxmean=True,
            )
        )
        fig.add_annotation(
            x=column,
            y=median_value,
            text=f"Median {format_chart_label(median_value, unit)}",
            showarrow=False,
            yshift=16,
            font=dict(color=TEXT, size=11),
            bgcolor="rgba(255,255,255,0.88)",
        )
    return apply_chart_style(fig, title, y_title=y_title)


def plot_tornado(df, value_col, title, x_title, show_as_pp=False):
    plot_df = df.sort_values(value_col, ascending=True).copy()
    values = plot_df[value_col] * 100 if show_as_pp else plot_df[value_col]
    unit = "pp" if show_as_pp else "currency"
    plot_df["Label"] = [format_chart_label(value, unit) for value in values]
    fig = px.bar(
        plot_df.assign(Impact=values),
        x="Impact",
        y="Variable",
        orientation="h",
        text="Label",
        color_discrete_sequence=[ACCENT],
        hover_data={"Impact": ":.2f"},
    )
    fig.update_traces(
        textposition="outside",
        textfont=dict(color=TEXT, size=11),
        cliponaxis=False,
    )
    return apply_chart_style(fig, title, x_title=x_title, y_title="")


def plot_sankey(result):
    labels = [
        f"Total liquid assets<br>{format_currency_b(APPLE_DATA['total_liquid_assets'])}",
        f"Marketable securities<br>{format_currency_b(APPLE_DATA['total_marketable_securities'])}",
        f"Tokenized collateral pool<br>{format_currency_b(result['tokenized_pool'])}",
        f"Usable collateral<br>{format_currency_b(result['tokenized_usable_collateral'])}",
        f"Liquidity buffer reduction<br>{format_currency_b(result['capital_liberated'])}",
        f"Capital liberated<br>{format_currency_b(result['capital_liberated'])}",
        f"Additional income<br>{format_currency_b(result['additional_income'])}",
        f"Adjusted ROE<br>{format_percent(result['adjusted_roe'])}",
    ]
    fig = go.Figure(
        go.Sankey(
            node=dict(
                pad=18,
                thickness=16,
                line=dict(color=GRID, width=0.5),
                label=labels,
                color=[
                    "#d9e3ef",
                    "#b8cce0",
                    ACCENT_LIGHT,
                    ACCENT_LIGHT,
                    "#93b5a6",
                    POSITIVE,
                    GOLD,
                    ACCENT,
                ],
            ),
            link=dict(
                source=[0, 1, 2, 3, 4, 5, 6],
                target=[1, 2, 3, 4, 5, 6, 7],
                value=[
                    APPLE_DATA["total_marketable_securities"],
                    result["tokenized_pool"],
                    result["tokenized_usable_collateral"],
                    result["capital_liberated"],
                    result["capital_liberated"],
                    result["additional_income"],
                    max(result["additional_income"], 0.01),
                ],
                color=[
                    "rgba(23,59,99,0.18)",
                    "rgba(23,59,99,0.25)",
                    "rgba(23,59,99,0.32)",
                    "rgba(47,111,78,0.28)",
                    "rgba(47,111,78,0.35)",
                    "rgba(200,164,106,0.35)",
                    "rgba(23,59,99,0.35)",
                ],
            ),
        )
    )
    return apply_chart_style(
        fig,
        "Simulation Mechanism: From Liquid Assets to Capital Efficiency",
        height=460,
    )


def build_amount_dumbbell_data(result):
    return pd.DataFrame(
        [
            {
                "Metric": "Usable collateral",
                "Legacy": result["legacy_usable_collateral"],
                "Tokenized": result["tokenized_usable_collateral"],
            },
            {
                "Metric": "Liquidity buffer",
                "Legacy": result["legacy_buffer"],
                "Tokenized": result["tokenized_buffer"],
            },
        ]
    )


def build_rate_dumbbell_data(result):
    return pd.DataFrame(
        [
            {
                "Metric": "Cost of debt",
                "Legacy": result["legacy_kd"] * 100,
                "Tokenized": result["tokenized_kd"] * 100,
            },
            {
                "Metric": "WACC",
                "Legacy": result["legacy_wacc"] * 100,
                "Tokenized": result["tokenized_wacc"] * 100,
            },
            {
                "Metric": "ROE",
                "Legacy": result["legacy_roe"] * 100,
                "Tokenized": result["adjusted_roe"] * 100,
            },
        ]
    )


def matrix_pivot(df, value_col):
    pivot = df.pivot(
        index="Scenario", columns="Adoption Label", values=value_col
    ).loc[list(STRESS_SCENARIOS.keys())]
    return pivot[[format_percent(value) for value in ADOPTION_SCENARIOS.values()]]


def style_matrix(pivot, formatter, favorable="high"):
    numeric = pivot.astype(float)
    max_abs = numeric.abs().max().max() or 1
    max_value = numeric.max().max() or 1
    fills = {
        POSITIVE: "47, 111, 78",
        CAUTION: "180, 35, 24",
    }

    def cell_style(value):
        if favorable == "negative":
            intensity = min(abs(value) / max_abs, 1)
            color = POSITIVE if value < 0 else CAUTION
        else:
            intensity = min(max(value, 0) / max_value, 1)
            color = POSITIVE
        alpha = 0.10 + intensity * 0.24
        return f"background-color: rgba({fills[color]}, {alpha:.2f});"

    styler = pivot.style.format(formatter)
    return styler.map(cell_style) if hasattr(styler, "map") else styler.applymap(cell_style)


def render_adoption_analysis(params):
    st.header("Scenario Matrix Analysis")
    note(
        "The scenario matrix combines four market conditions with three adoption "
        "levels, using the same model calculations as the selected baseline case."
    )
    df = run_scenario_matrix(params)

    cols = st.columns(2)
    with cols[0]:
        st.plotly_chart(
            plot_heatmap(
                df,
                "Capital Liberated",
                "Capital Liberated Across Adoption and Market Scenarios",
                "USD billions",
            ),
            use_container_width=True,
        )
    with cols[1]:
        st.plotly_chart(
            plot_heatmap(
                df,
                "WACC Change",
                "WACC Change Across Adoption and Market Scenarios",
                "Percentage points",
                show_as_pp=True,
                diverging=True,
            ),
            use_container_width=True,
        )
    note(
        "The heatmap shows how liquidity release changes jointly with market stress "
        "and tokenization adoption. Negative WACC values indicate a reduction in WACC, "
        "while positive values indicate that tokenization-related risk costs outweigh "
        "the collateral efficiency benefit."
    )

    cols = st.columns(2)
    with cols[0]:
        st.plotly_chart(
            plot_heatmap(
                df,
                "ROE Change",
                "ROE Change Across Adoption and Market Scenarios",
                "Percentage points",
                show_as_pp=True,
                diverging=True,
            ),
            use_container_width=True,
        )
    with cols[1]:
        st.plotly_chart(plot_grouped_bar(df), use_container_width=True)
    note(
        "ROE change reflects the assumed redeployment of liberated capital at an "
        "after-tax reinvestment return. Additional usable collateral captures the "
        "collateral-efficiency channel from lower tokenized haircuts."
    )

    with st.expander("Scenario Matrix Tables", expanded=True):
        table_cols = st.columns(2)
        with table_cols[0]:
            st.caption("Capital liberated")
            st.dataframe(
                style_matrix(
                    matrix_pivot(df, "Capital Liberated"),
                    lambda value: format_currency_b(value),
                ),
                use_container_width=True,
            )
            st.caption("Additional usable collateral")
            st.dataframe(
                style_matrix(
                    matrix_pivot(df, "Additional Usable Collateral"),
                    lambda value: format_currency_b(value),
                ),
                use_container_width=True,
            )
        with table_cols[1]:
            st.caption("WACC change")
            st.dataframe(
                style_matrix(
                    matrix_pivot(df, "WACC Change"),
                    lambda value: format_pp(value),
                    favorable="negative",
                ),
                use_container_width=True,
            )
            st.caption("ROE change")
            st.dataframe(
                style_matrix(
                    matrix_pivot(df, "ROE Change"),
                    lambda value: format_pp(value),
                ),
                use_container_width=True,
            )
        note(
            "The matrix view provides a compact summary of the twelve scenario "
            "outcomes produced by the four market conditions and three adoption levels."
        )


def render_stress_analysis(params):
    st.header("Stress Scenario Analysis")
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

    cols = st.columns(2)
    with cols[0]:
        st.plotly_chart(plot_stress_wacc_bar(df), use_container_width=True)
        note(
            "The zero line separates scenarios where tokenization reduces WACC from "
            "scenarios where higher risk premia offset the funding benefit."
        )
    with cols[1]:
        buffer_df = df.melt(
            id_vars="Scenario",
            value_vars=["Legacy Liquidity Buffer", "Tokenized Liquidity Buffer"],
            var_name="Buffer Type",
            value_name="USD Billions",
        )
        buffer_df["Label"] = buffer_df["USD Billions"].map(
            lambda value: format_chart_label(value, "currency")
        )
        buffer_fig = px.bar(
            buffer_df,
            x="Scenario",
            y="USD Billions",
            color="Buffer Type",
            barmode="group",
            text="Label",
            color_discrete_sequence=[MUTED, ACCENT],
            title="Liquidity Buffer Comparison Under Stress",
        )
        buffer_fig.update_traces(
            textposition="outside",
            textfont=dict(color=TEXT, size=11),
            cliponaxis=False,
        )
        st.plotly_chart(
            apply_chart_style(
                buffer_fig,
                "Liquidity Buffer Comparison Under Stress",
                x_title="Market scenario",
                y_title="USD billions",
            ),
            use_container_width=True,
        )

    chart_df = df.melt(
        id_vars="Scenario",
        value_vars=["Capital Liberated", "Usable Collateral Difference"],
        var_name="Metric",
        value_name="USD Billions",
    )
    chart_df["Label"] = chart_df["USD Billions"].map(
        lambda value: format_chart_label(value, "currency")
    )
    stress_fig = px.bar(
        chart_df,
        x="Scenario",
        y="USD Billions",
        color="Metric",
        barmode="group",
        text="Label",
        color_discrete_sequence=[ACCENT, ACCENT_LIGHT],
        title="Stress Scenario Collateral and Liquidity Effects",
    )
    stress_fig.update_traces(
        textposition="outside",
        textfont=dict(color=TEXT, size=11),
        cliponaxis=False,
    )
    st.plotly_chart(
        apply_chart_style(
            stress_fig,
            "Stress Scenario Collateral and Liquidity Effects",
            x_title="Market scenario",
            y_title="USD billions",
        ),
        use_container_width=True,
    )


def render_monte_carlo(params):
    st.header("Robustness and Sensitivity")
    st.subheader("Monte Carlo Robustness Testing")
    note(
        "The Monte Carlo simulation evaluates whether the model's conclusions remain "
        "stable when key assumptions vary within plausible ranges."
    )
    mc_df = run_monte_carlo(params)
    summary_cols = [
        "Capital Liberated",
        "Additional Usable Collateral",
        "WACC Change",
        "ROE Change",
    ]
    summary = mc_df[summary_cols].agg(["mean", "median", "std", "min", "max"])
    summary.loc["5th percentile"] = mc_df[summary_cols].quantile(0.05)
    summary.loc["95th percentile"] = mc_df[summary_cols].quantile(0.95)
    formatted_summary = summary.copy()
    formatted_summary["Capital Liberated"] = formatted_summary["Capital Liberated"].map(
        format_currency_b
    )
    formatted_summary["Additional Usable Collateral"] = formatted_summary[
        "Additional Usable Collateral"
    ].map(format_currency_b)
    formatted_summary["WACC Change"] = formatted_summary["WACC Change"].map(format_pp)
    formatted_summary["ROE Change"] = formatted_summary["ROE Change"].map(format_pp)
    st.dataframe(formatted_summary, use_container_width=True)

    cols = st.columns(2)
    with cols[0]:
        st.plotly_chart(
            plot_histogram_with_markers(
                mc_df,
                "WACC Change",
                "Monte Carlo Distribution of WACC Change",
                "WACC change, percentage points",
                show_as_pp=True,
            ),
            use_container_width=True,
        )
        note(
            "The Monte Carlo distribution shows whether the WACC effect remains "
            "stable when key assumptions vary within predefined ranges."
        )
    with cols[1]:
        st.plotly_chart(
            plot_histogram_with_markers(
                mc_df,
                "Capital Liberated",
                "Monte Carlo Distribution of Capital Liberated",
                "Capital liberated, USD billions",
            ),
            use_container_width=True,
        )
        note(
            "This distribution shows the range of possible liquidity release outcomes "
            "under uncertainty."
        )

    tabs = st.tabs(["USD outcomes", "Percentage-point outcomes"])
    with tabs[0]:
        st.plotly_chart(
            plot_boxplot(
                mc_df,
                ["Capital Liberated", "Additional Usable Collateral"],
                "Monte Carlo Output Dispersion: USD Outcomes",
                "USD billions",
            ),
            use_container_width=True,
        )
    with tabs[1]:
        st.plotly_chart(
            plot_boxplot(
                mc_df,
                ["WACC Change", "ROE Change"],
                "Monte Carlo Output Dispersion: Percentage-Point Outcomes",
                "Percentage points",
                show_as_pp=True,
            ),
            use_container_width=True,
        )
    note(
        "Box plots summarize the dispersion of model outcomes and help identify "
        "whether results are concentrated or highly sensitive to assumption changes."
    )


def render_sensitivity(params):
    st.subheader("Sensitivity Analysis")
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

    cols = st.columns(2)
    with cols[0]:
        st.plotly_chart(
            plot_tornado(
                df,
                "WACC Change Range",
                "Sensitivity of WACC Change to Key Assumptions",
                "Percentage-point range",
                show_as_pp=True,
            ),
            use_container_width=True,
        )
        note(
            "The WACC tornado chart identifies which assumptions have the greatest "
            "influence on the cost-of-capital result."
        )
    with cols[1]:
        st.plotly_chart(
            plot_tornado(
                df,
                "Capital Liberated Range",
                "Sensitivity of Capital Liberated to Key Assumptions",
                "USD billions",
            ),
            use_container_width=True,
        )
        note(
            "The capital liberated tornado chart shows whether liquidity efficiency "
            "is mainly driven by adoption intensity or by buffer-ratio assumptions."
        )


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


def render_interpretation_and_limitations(result):
    st.header("Model Logic")
    st.plotly_chart(plot_sankey(result), use_container_width=True)
    note(
        "The Sankey diagram summarizes the logic of the simulation: tokenization "
        "converts part of the marketable securities pool into programmable collateral, "
        "which may increase usable collateral, reduce liquidity buffers, liberate "
        "capital, and affect ROE through reinvestment."
    )

    st.subheader("Academic Interpretation")
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
    render_core_kpis(result)
    st.divider()
    render_baseline_data()
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
    render_interpretation_and_limitations(result)


if __name__ == "__main__":
    main()
