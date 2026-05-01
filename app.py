import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="Applied Simulation of Tokenized Treasury Collateral",
    page_icon="",
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
    "shareholders_equity_book": 73.733,
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
    legacy_usable = tokenized_pool * (1 - legacy_haircut)
    tokenized_usable = tokenized_pool * (1 - tokenized_haircut)
    return legacy_usable, tokenized_usable, tokenized_usable - legacy_usable


def calculate_effective_tokenized_buffer_ratio(
    legacy_buffer_ratio, tokenized_buffer_ratio, tokenized_share
):
    return legacy_buffer_ratio - (
        (legacy_buffer_ratio - tokenized_buffer_ratio) * tokenized_share
    )


def calculate_liquidity_buffers(
    liquid_asset_base, legacy_buffer_ratio, tokenized_buffer_ratio, tokenized_share
):
    effective_ratio = calculate_effective_tokenized_buffer_ratio(
        legacy_buffer_ratio, tokenized_buffer_ratio, tokenized_share
    )
    legacy_buffer = liquid_asset_base * legacy_buffer_ratio
    tokenized_buffer = liquid_asset_base * effective_ratio
    return legacy_buffer, tokenized_buffer, effective_ratio


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
    return safe_divide(net_income, shareholders_equity)


def get_capital_structure_values(params):
    debt_value = APPLE_DATA["total_debt"]
    if params["capital_structure_basis"] == "Market Values":
        equity_value = params["market_cap"]
    else:
        equity_value = APPLE_DATA["shareholders_equity_book"]
    return debt_value, equity_value


def run_single_case(params):
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
        APPLE_DATA["net_income"], APPLE_DATA["shareholders_equity_book"]
    )
    additional_income = (
        capital_liberated * params["after_tax_reinvestment_return"]
    )
    adjusted_net_income = APPLE_DATA["net_income"] + additional_income
    adjusted_roe = calculate_roe(
        adjusted_net_income, APPLE_DATA["shareholders_equity_book"]
    )

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
        "adjusted_roe": adjusted_roe,
        "roe_change": adjusted_roe - legacy_roe,
        "legacy_liquidity_efficiency": legacy_liquidity_efficiency,
        "tokenized_liquidity_efficiency": tokenized_liquidity_efficiency,
        "liquidity_efficiency_change": (
            tokenized_liquidity_efficiency - legacy_liquidity_efficiency
        ),
    }


def run_scenario(params):
    return run_single_case(params)


def run_adoption_scenarios(params):
    interpretations = {
        "Conservative": "Limited institutional experimentation",
        "Moderate": "Partial treasury integration",
        "Aggressive": "Advanced but still partial adoption",
    }
    rows = []
    for name, share in ADOPTION_SCENARIOS.items():
        scenario_params = {**params, "tokenized_share": share}
        result = run_scenario(scenario_params)
        rows.append(
            {
                "Scenario": name,
                "Tokenized Share": share,
                "Interpretation": interpretations[name],
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
    for name, scenario_values in STRESS_SCENARIOS.items():
        scenario_params = {**params, **scenario_values}
        result = run_scenario(scenario_params)
        rows.append(
            {
                "Scenario": name,
                "Capital Liberated": result["capital_liberated"],
                "Tokenized Cost of Debt": result["tokenized_kd"],
                "WACC Change": result["wacc_change"],
                "ROE Change": result["roe_change"],
                "Additional Usable Collateral": result["usable_collateral_difference"],
            }
        )
    return pd.DataFrame(rows)


def run_monte_carlo(params, simulations=5000, seed=42):
    rng = np.random.default_rng(seed)
    shares = rng.uniform(0.10, 0.40, simulations)
    legacy_haircuts = rng.uniform(0.04, 0.18, simulations)
    tokenized_haircut_upper = np.minimum(0.12, legacy_haircuts)
    tokenized_haircuts = rng.uniform(0.02, tokenized_haircut_upper)
    legacy_buffer_ratios = rng.uniform(0.15, 0.35, simulations)
    tokenized_buffer_upper = np.minimum(0.24, legacy_buffer_ratios)
    tokenized_buffer_ratios = rng.uniform(0.10, tokenized_buffer_upper)
    collateral_spreads = rng.uniform(0.002, 0.012, simulations)
    technology_premiums = rng.uniform(0.001, 0.008, simulations)
    reinvestment_returns = rng.uniform(0.03, 0.08, simulations)

    rows = []
    for idx in range(simulations):
        run_params = {
            **params,
            "tokenized_share": shares[idx],
            "legacy_haircut": legacy_haircuts[idx],
            "tokenized_haircut": tokenized_haircuts[idx],
            "legacy_buffer_ratio": legacy_buffer_ratios[idx],
            "tokenized_buffer_ratio": tokenized_buffer_ratios[idx],
            "collateral_efficiency_spread": collateral_spreads[idx],
            "technology_risk_premium": technology_premiums[idx],
            "after_tax_reinvestment_return": reinvestment_returns[idx],
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
    ranges = {
        "Tokenized Asset Share": ("tokenized_share", np.linspace(0.10, 0.40, 25)),
        "Tokenized Haircut": ("tokenized_haircut", np.linspace(0.02, 0.12, 25)),
        "Tokenized Liquidity Buffer Ratio": (
            "tokenized_buffer_ratio",
            np.linspace(0.10, 0.24, 25),
        ),
        "Collateral Efficiency Spread": (
            "collateral_efficiency_spread",
            np.linspace(0.002, 0.012, 25),
        ),
        "Technology Risk Premium": (
            "technology_risk_premium",
            np.linspace(0.001, 0.008, 25),
        ),
    }

    rows = []
    details = []
    for label, (key, values) in ranges.items():
        outputs = []
        for value in values:
            scenario_params = {**params, key: value}
            if key == "tokenized_haircut":
                scenario_params["tokenized_haircut"] = min(
                    scenario_params["tokenized_haircut"],
                    scenario_params["legacy_haircut"],
                )
            if key == "tokenized_buffer_ratio":
                scenario_params["tokenized_buffer_ratio"] = min(
                    scenario_params["tokenized_buffer_ratio"],
                    scenario_params["legacy_buffer_ratio"],
                )
            result = run_scenario(scenario_params)
            outputs.append(result)
            details.append(
                {
                    "Variable": label,
                    "Value": value,
                    "WACC Change": result["wacc_change"],
                    "Capital Liberated": result["capital_liberated"],
                    "ROE Change": result["roe_change"],
                }
            )

        rows.append(
            {
                "Variable": label,
                "WACC Change Range": max(x["wacc_change"] for x in outputs)
                - min(x["wacc_change"] for x in outputs),
                "Capital Liberated Range": max(x["capital_liberated"] for x in outputs)
                - min(x["capital_liberated"] for x in outputs),
                "ROE Change Range": max(x["roe_change"] for x in outputs)
                - min(x["roe_change"] for x in outputs),
            }
        )
    return pd.DataFrame(rows), pd.DataFrame(details)


def safe_divide(numerator, denominator):
    if denominator == 0:
        return np.nan
    return numerator / denominator


def format_currency_b(value):
    return f"${value:,.2f}B"


def format_percent(value):
    return f"{value * 100:.2f}%"


def format_pp(value):
    return f"{value * 100:.2f} pp"


def scenario_sentence(result):
    wacc_direction = "lower" if result["wacc_change"] < 0 else "higher"
    roe_direction = "higher" if result["roe_change"] > 0 else "lower"
    return (
        f"Under the current assumptions, the tokenized case releases "
        f"{format_currency_b(result['capital_liberated'])} of liquidity buffer capacity, "
        f"while the modeled WACC is {format_pp(abs(result['wacc_change']))} {wacc_direction} "
        f"than the legacy case. Adjusted ROE is {format_pp(abs(result['roe_change']))} "
        f"{roe_direction}, assuming liberated capital earns the selected after-tax return."
    )


def render_explanation(title, body):
    st.markdown(
        f"""
        <div class="explanation-box">
            <div class="explanation-title">{title}</div>
            <div>{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_label(text):
    st.markdown(f'<div class="section-label">{text}</div>', unsafe_allow_html=True)


def style_app():
    st.markdown(
        """
        <style>
        :root {
            --accent: #15324d;
            --muted: #596575;
            --border: #d6dce3;
            --surface: #f6f8fa;
            --ink: #17212b;
        }
        .stApp {
            background: #fafbfc;
            color: var(--ink);
        }
        h1, h2, h3 {
            color: #162536;
            letter-spacing: 0;
        }
        .block-container {
            padding-top: 2.25rem;
            padding-bottom: 3rem;
            max-width: 1280px;
        }
        .section-label {
            color: #52606d;
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            margin-bottom: 0.35rem;
            text-transform: uppercase;
        }
        .thesis-note {
            border-left: 4px solid var(--accent);
            background: var(--surface);
            padding: 0.9rem 1rem;
            margin: 0.75rem 0 1.25rem 0;
            color: #263442;
        }
        .method-strip {
            border: 1px solid var(--border);
            border-radius: 8px;
            background: #ffffff;
            padding: 1rem;
            margin: 1rem 0 1.25rem 0;
        }
        .method-strip strong {
            color: #102a43;
        }
        .explanation-box {
            border: 1px solid var(--border);
            border-radius: 8px;
            background: #ffffff;
            padding: 0.9rem 1rem;
            margin: 0.8rem 0 1rem 0;
            color: #263442;
            line-height: 1.5;
        }
        .explanation-title {
            color: #102a43;
            font-weight: 700;
            margin-bottom: 0.35rem;
        }
        .kpi-card {
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 0.95rem 1rem;
            background: #ffffff;
            min-height: 112px;
        }
        .kpi-label {
            color: var(--muted);
            font-size: 0.84rem;
            margin-bottom: 0.35rem;
        }
        .kpi-value {
            color: #102a43;
            font-size: 1.45rem;
            font-weight: 700;
            line-height: 1.15;
        }
        .kpi-help {
            color: var(--muted);
            font-size: 0.78rem;
            margin-top: 0.4rem;
        }
        hr {
            border: none;
            border-top: 1px solid var(--border);
            margin: 1.75rem 0;
        }
        div[data-testid="stMetricValue"] {
            color: #102a43;
        }
        div[data-testid="stDataFrame"] {
            border: 1px solid var(--border);
            border-radius: 8px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def initialize_state():
    for key, value in DEFAULTS.items():
        st.session_state.setdefault(key, value)
    st.session_state.setdefault("scenario_selector", "Custom")
    st.session_state.setdefault("capital_structure_basis", "Market Values")


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

    st.sidebar.subheader("Adoption and Collateral")
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

    st.sidebar.subheader("Liquidity")
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

    st.sidebar.subheader("Funding")
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

    st.sidebar.subheader("WACC")
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

    st.sidebar.subheader("ROE")
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
    render_section_label("Institutional Treasury Simulation")
    st.title("Applied Simulation of Tokenized Treasury Collateral")
    st.caption("A counterfactual model using Apple Inc. 2025 financial data")
    st.markdown(
        """
        <div class="thesis-note">
        This dashboard does not claim that Apple currently uses RWA tokenization.
        Apple's data are used as a real-company baseline to simulate how tokenized
        collateral infrastructure could affect liquidity and capital efficiency.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_institutional_frame(result):
    st.header("3.1 Introduction and Institutional Model Frame")
    render_explanation(
        "Analytical premise",
        "The dashboard treats tokenized Treasury collateral as an institutional market "
        "infrastructure layer. The question is not whether tokenization creates value by "
        "itself, but whether programmable ownership, faster collateral movement, and "
        "segregated collateral control could reduce balance-sheet frictions under "
        "defined assumptions.",
    )

    cols = st.columns(4)
    pillars = [
        (
            "Collateral mobility",
            "Marketable securities are converted into a more operationally usable collateral pool.",
        ),
        (
            "Liquidity reserve efficiency",
            "Required liquidity buffers may decline gradually as tokenized adoption increases.",
        ),
        (
            "Funding spread channel",
            "Improved collateral usability may compress debt cost, partly offset by technology risk.",
        ),
        (
            "Risk architecture",
            "Institutional adoption depends on segregation, counterparty isolation, custody, and controls.",
        ),
    ]
    for col, (title, body) in zip(cols, pillars):
        with col:
            render_kpi(title, "", body)

    flow = pd.DataFrame(
        [
            ["1", "Balance-sheet proxy", "Apple liquid assets and marketable securities define scale."],
            ["2", "Collateral transformation", "A selected share of securities enters the tokenized pool."],
            ["3", "Risk adjustment", "Haircuts, buffers, and technology premium adjust usable value."],
            ["4", "Financial transmission", "Funding cost, WACC, and adjusted ROE capture modeled impact."],
        ],
        columns=["Step", "Institutional concept", "Role in the simulation"],
    )
    st.dataframe(flow, use_container_width=True, hide_index=True)
    render_explanation("Current institutional read-through", scenario_sentence(result))
    st.markdown(
        """
        <div class="method-strip">
        <strong>Research design:</strong> real-company case study, counterfactual scenario
        simulation, deterministic scenario analysis, Monte Carlo robustness testing, and
        one-variable-at-a-time sensitivity analysis. The dashboard treats tokenization as
        an institutional collateral infrastructure question, not as a speculative asset
        pricing exercise.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_baseline_data():
    st.header("3.2-3.3 Case Selection, Data, and Model Assumptions")
    render_explanation(
        "Why Apple is used",
        "Apple is used as a large institutional treasury proxy because its balance sheet "
        "contains substantial liquid assets, marketable securities, debt, and equity. "
        "The model does not infer that Apple has adopted tokenized collateral; it uses "
        "Apple's financial scale to make the counterfactual economically concrete.",
    )
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
        "shareholders_equity_book": "Book shareholders' equity",
        "tax_rate": "Effective tax rate",
    }
    rows = []
    for key, label in labels.items():
        value = APPLE_DATA[key]
        rows.append(
            {
                "Variable": label,
                "Value": format_percent(value)
                if key == "tax_rate"
                else format_currency_b(value),
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def render_outputs(result):
    st.header("3.4-3.5 Financial Model and Calculation Logic")
    render_explanation(
        "How to read this panel",
        "The first group estimates how much of the marketable securities portfolio is "
        "treated as tokenizable collateral. The second group compares liquidity buffer "
        "requirements. The final group translates the funding and capital effects into "
        "WACC and ROE measures. These outputs are scenario results, not forecasts.",
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
        for col, (label, value, help_text) in zip(cols, kpis[start : start + 3]):
            with col:
                render_kpi(label, value, help_text)

    st.info(
        "Book-value WACC uses accounting values from Apple's financial statements. "
        "Market-value WACC uses Apple's market capitalization as the equity value. "
        "Market-value WACC is often preferred in valuation, while book-value WACC is "
        "kept for accounting consistency. Current basis: "
        f"{result['capital_structure_basis']}."
    )
    st.warning(
        "ROE is calculated using book equity. Apple's book equity can be affected by "
        "share repurchases, which may inflate ROE and distort book-value capital "
        "structure weights."
    )
    render_explanation("Current scenario interpretation", scenario_sentence(result))


def render_comparison_table(result, params):
    st.header("3.6 Results and Discussion: Legacy vs Tokenized")
    render_explanation(
        "Purpose of the comparison",
        "This table holds the asset pool constant and changes the infrastructure "
        "assumptions. The difference column therefore represents the modeled impact of "
        "haircuts, liquidity buffer treatment, and funding spreads under the selected "
        "counterfactual assumptions.",
    )
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


def display_scenario_table(df):
    formatted = df.copy()
    currency_cols = [
        "Tokenized Pool",
        "Legacy Usable Collateral",
        "Tokenized Usable Collateral",
        "Additional Usable Collateral",
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
    st.dataframe(formatted, use_container_width=True, hide_index=True)


def render_adoption_analysis(params):
    st.header("3.6 Results and Discussion: Adoption Scenario Analysis")
    render_explanation(
        "What adoption changes",
        "Adoption is modeled as the share of marketable securities that becomes available "
        "for tokenized collateral use. Higher adoption does not automatically eliminate "
        "liquidity buffers; the buffer benefit scales gradually through the effective "
        "tokenized buffer ratio.",
    )
    df = run_adoption_scenarios(params)
    display_scenario_table(df)

    capital_fig = px.bar(
        df,
        x="Scenario",
        y="Capital Liberated",
        color="Scenario",
        color_discrete_sequence=["#6c7f93", "#173b63", "#8aa6bf"],
        title="Liquidity buffer capacity released by adoption level",
    )
    capital_fig.update_layout(
        yaxis_title="USD billions", showlegend=False, title_x=0.0
    )
    st.plotly_chart(capital_fig, use_container_width=True)

    chart_rates = df.copy()
    chart_rates["WACC Change (pp)"] = chart_rates["WACC Change"] * 100
    chart_rates["ROE Change (pp)"] = chart_rates["ROE Change"] * 100

    wacc_fig = px.bar(
        chart_rates,
        x="Scenario",
        y="WACC Change (pp)",
        color="Scenario",
        color_discrete_sequence=["#6c7f93", "#173b63", "#8aa6bf"],
        title="WACC change by adoption level",
    )
    wacc_fig.update_layout(
        yaxis_title="Percentage points", showlegend=False, title_x=0.0
    )
    st.plotly_chart(wacc_fig, use_container_width=True)

    roe_fig = px.bar(
        chart_rates,
        x="Scenario",
        y="ROE Change (pp)",
        color="Scenario",
        color_discrete_sequence=["#6c7f93", "#173b63", "#8aa6bf"],
        title="ROE change by adoption level",
    )
    roe_fig.update_layout(
        yaxis_title="Percentage points", showlegend=False, title_x=0.0
    )
    st.plotly_chart(roe_fig, use_container_width=True)


def render_stress_analysis(params):
    st.header("3.6 Results and Discussion: Market Stress Scenario Analysis")
    render_explanation(
        "Stress logic",
        "Stress scenarios raise haircuts and liquidity buffers while reducing the "
        "collateral efficiency spread and increasing technology risk premia. This tests "
        "whether the modeled benefit depends on calm-market assumptions.",
    )
    st.info(
        "The 2008-style liquidity shock is used as a stress-test reference. It does "
        "not imply that tokenized collateral existed during the 2008 crisis."
    )
    df = run_stress_scenarios(params)
    display_scenario_table(df)

    chart_df = df.melt(
        id_vars="Scenario",
        value_vars=["Capital Liberated", "Additional Usable Collateral"],
        var_name="Metric",
        value_name="USD Billions",
    )
    fig = px.bar(
        chart_df,
        x="Scenario",
        y="USD Billions",
        color="Metric",
        barmode="group",
        color_discrete_sequence=["#173b63", "#7895b2"],
    )
    fig.update_layout(legend_title_text="")
    st.plotly_chart(fig, use_container_width=True)

    chart_rates = df.copy()
    chart_rates["WACC Change (pp)"] = chart_rates["WACC Change"] * 100
    chart_rates["ROE Change (pp)"] = chart_rates["ROE Change"] * 100

    wacc_fig = px.line(
        chart_rates,
        x="Scenario",
        y="WACC Change (pp)",
        markers=True,
        color_discrete_sequence=["#173b63"],
        title="WACC change under market stress scenarios",
    )
    wacc_fig.update_layout(yaxis_title="Percentage points", title_x=0.0)
    st.plotly_chart(wacc_fig, use_container_width=True)

    roe_fig = px.line(
        chart_rates,
        x="Scenario",
        y="ROE Change (pp)",
        markers=True,
        color_discrete_sequence=["#7895b2"],
        title="ROE change under market stress scenarios",
    )
    roe_fig.update_layout(yaxis_title="Percentage points", title_x=0.0)
    st.plotly_chart(roe_fig, use_container_width=True)


def render_monte_carlo(params):
    st.header("3.6 Results and Discussion: Monte Carlo Robustness Testing")
    render_explanation(
        "Robustness question",
        "The Monte Carlo simulation evaluates whether the model's conclusions remain "
        "stable when key assumptions vary within plausible ranges. Each run samples "
        "adoption, haircuts, buffer ratios, funding spread, technology risk premium, "
        "and reinvestment return while preserving the core constraints of the model.",
    )
    if st.button("Run Monte Carlo Simulation", type="primary"):
        mc_df = run_monte_carlo(params)
        summary = mc_df[
            [
                "Capital Liberated",
                "Additional Usable Collateral",
                "Tokenized WACC",
                "WACC Change",
                "Adjusted ROE",
                "ROE Change",
            ]
        ].agg(["mean", "median", "std", "min", "max"])
        summary.loc["5th percentile"] = mc_df[
            [
                "Capital Liberated",
                "Additional Usable Collateral",
                "Tokenized WACC",
                "WACC Change",
                "Adjusted ROE",
                "ROE Change",
            ]
        ].quantile(0.05)
        summary.loc["95th percentile"] = mc_df[
            [
                "Capital Liberated",
                "Additional Usable Collateral",
                "Tokenized WACC",
                "WACC Change",
                "Adjusted ROE",
                "ROE Change",
            ]
        ].quantile(0.95)
        formatted_summary = summary.copy()
        for col in formatted_summary.columns:
            if col in ["Capital Liberated", "Additional Usable Collateral"]:
                formatted_summary[col] = formatted_summary[col].map(format_currency_b)
            elif col in ["Tokenized WACC", "Adjusted ROE"]:
                formatted_summary[col] = formatted_summary[col].map(format_percent)
            else:
                formatted_summary[col] = formatted_summary[col].map(format_pp)
        st.dataframe(formatted_summary, use_container_width=True)

        render_explanation(
            "Monte Carlo interpretation",
            "A stable result is indicated when most sampled outcomes remain in the same "
            "direction as the deterministic scenario. Wide distributions should be read "
            "as assumption sensitivity rather than model failure; they show where the "
            "thesis argument depends most strongly on parameter choices.",
        )

        cols = st.columns(3)
        charts = [
            ("WACC Change", "WACC change distribution"),
            ("Capital Liberated", "Capital liberated distribution"),
            ("ROE Change", "ROE change distribution"),
        ]
        for col, (metric, title) in zip(cols, charts):
            with col:
                fig = px.histogram(
                    mc_df,
                    x=metric,
                    nbins=45,
                    title=title,
                    color_discrete_sequence=["#173b63"],
                )
                st.plotly_chart(fig, use_container_width=True)


def render_sensitivity(params):
    st.header("3.6 Results and Discussion: Sensitivity Analysis")
    render_explanation(
        "Sensitivity logic",
        "This section changes one assumption at a time while keeping the other parameters "
        "at their current values. It is designed to show which assumption has the greatest "
        "influence on the result, rather than to represent a full probability model.",
    )
    summary_df, _ = run_sensitivity_analysis(params)
    formatted = summary_df.copy()
    formatted["WACC Change Range"] = formatted["WACC Change Range"].map(format_pp)
    formatted["Capital Liberated Range"] = formatted["Capital Liberated Range"].map(
        format_currency_b
    )
    formatted["ROE Change Range"] = formatted["ROE Change Range"].map(format_pp)
    st.dataframe(formatted, use_container_width=True, hide_index=True)

    chart_df = summary_df.sort_values("Capital Liberated Range", ascending=True)
    fig = px.bar(
        chart_df,
        x="Capital Liberated Range",
        y="Variable",
        orientation="h",
        color_discrete_sequence=["#173b63"],
        title="Sensitivity by capital liberated range",
    )
    fig.update_layout(xaxis_title="USD billions", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)


def render_risk_architecture():
    st.header("Institutional Risk Architecture")
    render_explanation(
        "Why architecture matters",
        "The tokenized scenario assumes an isolated institutional architecture rather "
        "than a fully open pooled liquidity model. This reflects the idea that large "
        "corporations and regulated institutions are unlikely to use tokenized "
        "collateral systems that expose them to broad contagion risk.",
    )
    architecture = pd.DataFrame(
        [
            ["Collateral exposure", "Shared across participants", "Segregated by position or vault"],
            ["Contagion risk", "Higher", "Lower"],
            ["Institutional suitability", "Limited", "Stronger"],
            ["Risk transparency", "Moderate", "Higher"],
            ["Operational logic", "Open liquidity pool", "Controlled collateral structure"],
        ],
        columns=[
            "Feature",
            "Pooled Tokenized Structure",
            "Isolated Institutional Architecture",
        ],
    )
    st.dataframe(architecture, use_container_width=True, hide_index=True)
    st.info(
        "Protocols and market designs such as Aave Horizon and isolated lending markets "
        "such as Morpho illustrate the broader movement toward permissioned or "
        "risk-segregated collateral structures. They are used here only as conceptual "
        "examples, not as direct case studies."
    )

    controls = pd.DataFrame(
        [
            [
                "Legal enforceability",
                "Clear claim on collateral and bankruptcy-remote treatment where applicable.",
                "Reduces ambiguity around ownership and recovery.",
            ],
            [
                "Custody and key management",
                "Institutional custody, access controls, approval workflows, and audit trails.",
                "Limits operational loss and unauthorized movement.",
            ],
            [
                "Counterparty isolation",
                "Dedicated collateral accounts or vault-like structures rather than pooled exposure.",
                "Reduces contagion from unrelated market participants.",
            ],
            [
                "Oracle and valuation controls",
                "Independent pricing, haircut governance, and exception handling.",
                "Prevents collateral value from becoming mechanically overstated.",
            ],
            [
                "Operational resilience",
                "Fallback procedures for settlement delays, smart contract incidents, and outages.",
                "Keeps treasury operations viable under stress.",
            ],
        ],
        columns=["Control domain", "Institutional requirement", "Why it matters"],
    )
    st.subheader("Institutional Control Requirements")
    st.dataframe(controls, use_container_width=True, hide_index=True)


def render_interpretation_and_limits():
    st.header("3.7 Limitations of the Model")
    with st.expander("Model Limitations", expanded=True):
        st.markdown(
            """
            - The model is counterfactual and not a forecast.
            - Apple is used as a proxy and is not assumed to use RWA tokenization.
            - Some assumptions are scenario-based due to limited historical data.
            - The WACC can be calculated using book or market values; each has limitations.
            - Apple's book equity is affected by share repurchases, so ROE should be interpreted carefully.
            - The model focuses only on collateral mobility and treasury efficiency, not the entire financial market.
            - Regulatory, legal, custody, and oracle risks are simplified.
            - Results should be interpreted as indicative, not predictive.
            """
        )

    st.header("3.8 Conclusion of the Chapter")
    st.markdown(
        """
        <div class="thesis-note">
        The simulation evaluates tokenized collateral as a financial infrastructure
        mechanism. The expected benefit comes mainly from improved collateral mobility,
        reduced liquidity buffer requirements, and potential cost of debt compression.
        These effects may influence financial market efficiency by improving the usability
        of liquid assets in secured funding markets.
        <br><br>
        The results are conditional on the model assumptions. Tokenization benefits may
        be reduced if technology risk, custody risk, legal uncertainty, or weak
        institutional architecture offset the efficiency gains.
        </div>
        """,
        unsafe_allow_html=True,
    )

    institutional_reading = pd.DataFrame(
        [
            [
                "Efficiency channel",
                "Collateral mobility and lower liquidity reserve needs.",
                "Potential improvement in capital efficiency.",
            ],
            [
                "Funding channel",
                "Better collateral usability may reduce secured funding spreads.",
                "Potential reduction in WACC if risk premia remain contained.",
            ],
            [
                "Risk channel",
                "Technology, custody, oracle, and legal risk may offset operational benefits.",
                "Benefits are conditional, not automatic.",
            ],
            [
                "Governance channel",
                "Controls determine whether tokenized collateral is institutionally acceptable.",
                "Architecture matters as much as settlement speed.",
            ],
        ],
        columns=["Channel", "Mechanism", "Interpretation"],
    )
    st.subheader("Institutional Interpretation Matrix")
    st.dataframe(institutional_reading, use_container_width=True, hide_index=True)


def main():
    style_app()
    initialize_state()
    params = sidebar_controls()
    result = run_scenario(params)

    render_header()
    render_institutional_frame(result)
    st.divider()
    render_baseline_data()
    st.divider()
    render_outputs(result)
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
    render_interpretation_and_limits()


if __name__ == "__main__":
    main()
