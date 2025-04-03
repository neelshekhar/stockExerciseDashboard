# Install required packages before running:
# pip install streamlit pandas plotly

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Constants
BASE_OPTIONS = 2131
current_fmv = 4150  # FMV at time of early exercise
strike_price = 12   # Strike price of the options
income_tax_rate = 36.67 / 100
ltcg_rate = 12.5 / 100

# Function to calculate data
def calculate_data(adjusted_options):
    data = []
    for val in range(1, 11):
        ipo_fmv = current_fmv * (val / 3)

        # Value of options at IPO FMV
        option_value = round(adjusted_options * ipo_fmv / 100000)

        # Tax if not exercised early (entire gain taxed as income)
        tax_without_exercise = round(adjusted_options * (ipo_fmv - strike_price) * income_tax_rate / 100000)

        # Tax if exercised now (split into perquisite + LTCG)
        perquisite_tax = round(adjusted_options * (current_fmv - strike_price) * income_tax_rate / 100000)
        ltcg_tax = round(adjusted_options * max(ipo_fmv - current_fmv, 0) * ltcg_rate / 100000)
        total_tax_with_exercise = round(perquisite_tax + ltcg_tax)

        tax_savings = round(tax_without_exercise - total_tax_with_exercise)

        data.append({
            'IPO Valuation': val,
            'Value of Options': option_value,
            'Tax Without Exercise': tax_without_exercise,
            'Perquisite Tax': perquisite_tax,
            'LTCG Tax': ltcg_tax,
            'Total Tax with Exercise': total_tax_with_exercise,
            'Potential Tax Savings': tax_savings
        })

    return pd.DataFrame(data)

# App Setup
st.set_page_config(page_title="ESOP Tax Simulator", layout="wide")
st.markdown("""
    <style>
        body {
            background-color: #F4F4F9;
        }
        .css-18e3th9, .css-1d391kg {
            background-color: #F4F4F9;
        }
        .stMetricValue {
            font-size: 14px !important;
        }
    </style>
""", unsafe_allow_html=True)

st.title("💼 ESOP Tax Impact Simulator")

# Toggle for adjustment type
adjust_mode = st.radio("Adjust Options To Exercise By:", ["Percentage", "Absolute Number"], horizontal=True)
if adjust_mode == "Percentage":
    option_pct = st.slider("% of Options to Exercise", min_value=0, max_value=100, value=100, step=5)
    adjusted_options = BASE_OPTIONS * (option_pct / 100)
else:
    adjusted_options = st.number_input("Enter Number of Options to Exercise", min_value=0, value=BASE_OPTIONS, step=100)

# Valuation input
valuation = st.slider("Select IPO Valuation (in ₹ Billion)", min_value=1, max_value=10, value=3)

# Data Calculation
df = calculate_data(adjusted_options)
filtered = df[df["IPO Valuation"] <= valuation]
current_row = df[df["IPO Valuation"] == valuation].iloc[0]

# Explanation Panel
with st.expander("ℹ️ Explanation of Calculations", expanded=False):
    ipo_fmv = current_fmv * (valuation / 3)
    gain_no_exercise = ipo_fmv - strike_price
    tax_no_exercise = round(adjusted_options * gain_no_exercise * income_tax_rate)
    perquisite_gain = current_fmv - strike_price
    perquisite_tax = round(adjusted_options * perquisite_gain * income_tax_rate)
    ltcg_gain = max(ipo_fmv - current_fmv, 0)
    ltcg_tax = round(adjusted_options * ltcg_gain * ltcg_rate)
    total_tax_exercise_now = perquisite_tax + ltcg_tax
    tax_savings = tax_no_exercise - total_tax_exercise_now

    st.markdown(f"""
    **🔧 Key Constants:**
    - **Strike Price:** ₹{strike_price} (amount you pay per share)
    - **Current FMV:** ₹{current_fmv} (value of share today, at exercise)
    - **Income Tax Rate:** {income_tax_rate * 100}%
    - **LTCG Tax Rate:** {ltcg_rate * 100}%

    **📊 Based on Your Selection:**
    - **IPO Valuation:** ₹{valuation} Billion
    - **Number of Options Exercised:** {int(adjusted_options)}
    - **IPO FMV per share:** ₹{int(ipo_fmv)}

    **💼 Option Value:**
    - {int(adjusted_options)} × ₹{int(ipo_fmv)} = ₹{int(adjusted_options * ipo_fmv):,}

    **❌ If You Don't Exercise Now:**
    - Entire gain taxed as income at IPO:
      - Gain: ₹{int(ipo_fmv)} − ₹{strike_price} = ₹{int(gain_no_exercise)}
      - Tax: {int(adjusted_options)} × ₹{int(gain_no_exercise)} × {income_tax_rate * 100}% = ₹{tax_no_exercise:,}

    **✅ If You Exercise Now:**
    - **Two tax events occur:**
      1. **Perquisite Tax applies at current FMV**:
         - Gain: ₹{current_fmv} − ₹{strike_price} = ₹{perquisite_gain}
         - Tax: {int(adjusted_options)} × ₹{perquisite_gain} × {income_tax_rate * 100}% = ₹{perquisite_tax:,}
      2. **LTCG (if IPO FMV > current FMV)**:
         - Gain: ₹{int(ipo_fmv)} − ₹{current_fmv} = ₹{int(ltcg_gain)}
         - Tax: {int(adjusted_options)} × ₹{int(ltcg_gain)} × {ltcg_rate * 100}% = ₹{ltcg_tax:,}
      - **Total Tax if Exercised Now** = ₹{total_tax_exercise_now:,}

    **💰 Potential Tax Savings:** ₹{tax_savings:,}
    """)

# Summary
st.markdown(f"""
### 📊 Valuation: ₹{valuation}B  
- Options to Exercise: {int(adjusted_options)}  
- 💼 Option Value: ₹{current_row['Value of Options']} Lacs  
- 💸 Potential Tax Savings: ₹{current_row['Potential Tax Savings']} Lacs
""")

# Chart and metrics side by side
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📉 Tax Liability Comparison Across Valuation Scenarios")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=filtered['IPO Valuation'], y=filtered['Tax Without Exercise'],
        mode='lines+markers+text', name='Without Early Exercise',
        text=filtered['Tax Without Exercise'], textposition="top center",
        line=dict(color='#6C7A89')
    ))
    fig.add_trace(go.Scatter(
        x=filtered['IPO Valuation'], y=filtered['Total Tax with Exercise'],
        mode='lines+markers+text', name='With Early Exercise',
        text=filtered['Total Tax with Exercise'], textposition="bottom center",
        line=dict(color='#3E6C99')
    ))
    fig.update_layout(
        xaxis_title="IPO Valuation (B)",
        yaxis_title="Tax Liability (in Lacs)",
        plot_bgcolor='#FFFFFF', paper_bgcolor='#FFFFFF',
        font=dict(family='Segoe UI', color='#2E3B4E', size=16),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📌 Detailed Metrics at Selected Valuation")
    st.markdown("### ❌ If You Don't Exercise Now")
    st.metric("Total Tax Liability", f"₹{current_row['Tax Without Exercise']} Lacs")

    st.markdown("### ✅ If You Exercise Now")
    st.metric("Perquisite Tax", f"₹{current_row['Perquisite Tax']} Lacs")
    st.metric("Capital Gains Tax", f"₹{current_row['LTCG Tax']} Lacs")
    st.metric("Total Tax Liability", f"₹{current_row['Total Tax with Exercise']} Lacs")
    st.metric("Tax Savings", f"₹{current_row['Potential Tax Savings']} Lacs")

# Breakdown Table
st.subheader("📄 Tax Scenario Breakdown Across All Valuations")
st.dataframe(df.style.format({
    'Value of Options': '₹{:,.0f} Lacs',
    'Tax Without Exercise': '₹{:,.0f} Lacs',
    'Perquisite Tax': '₹{:,.0f} Lacs',
    'LTCG Tax': '₹{:,.0f} Lacs',
    'Total Tax with Exercise': '₹{:,.0f} Lacs',
    'Potential Tax Savings': '₹{:,.0f} Lacs'
}))