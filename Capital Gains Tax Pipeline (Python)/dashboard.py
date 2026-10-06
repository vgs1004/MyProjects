import streamlit as st
import pandas as pd
import plotly.express as px
import os

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
TAX_FILE    = os.path.join(BASE_DIR, "data", "output", "final_tax_computation.csv")
EXCEL_FILE  = os.path.join(BASE_DIR, "data", "output", "Strategic_Tax_Report.xlsx")
BUDGET_DATE = pd.Timestamp("2024-07-23")

st.set_page_config(page_title="Capital Gains Tax Dashboard", page_icon="📊", layout="wide")

st.markdown("""
<style>
    .block-container { padding-top: 1.2rem; padding-bottom: 1rem; }
    .kpi-card {
        background: #FFFFFF;
        border-radius: 8px;
        padding: 16px 18px;
        text-align: center;
        border-top: 3px solid #5B8DB8;
        box-shadow: 0 1px 3px rgba(0,0,0,0.07);
        margin-bottom: 8px;
    }
    .kpi-gain  { border-top-color: #4A9B6F; }
    .kpi-loss  { border-top-color: #B05A52; }
    .kpi-save  { border-top-color: #C49A2A; }
    .kpi-label { color: #6B7280; font-size: 11px; text-transform: uppercase;
                 letter-spacing: 0.6px; margin-bottom: 5px; }
    .kpi-value { color: #111827; font-size: 20px; font-weight: 700; }
    .kpi-sub   { color: #9CA3AF; font-size: 11px; margin-top: 3px; }
    .sec-title {
        color: #374151; font-size: 14px; font-weight: 600;
        border-bottom: 1px solid #E5E7EB;
        padding-bottom: 5px; margin: 16px 0 10px 0;
    }
</style>
""", unsafe_allow_html=True)

PL = dict(
    plot_bgcolor='#FFFFFF',
    paper_bgcolor='#FFFFFF',
    font=dict(color='#374151', size=11),
    margin=dict(t=10, b=30, l=10, r=10),
    xaxis=dict(gridcolor='#F3F4F6', linecolor='#E5E7EB', tickfont=dict(color='#374151')),
    yaxis=dict(gridcolor='#F3F4F6', linecolor='#E5E7EB', tickfont=dict(color='#374151')),
)
LEGEND_H = dict(orientation='h', y=1.1, bgcolor='#FFFFFF', font=dict(color='#374151'))

C_BLUE  = '#5B8DB8'
C_SAGE  = '#4A9B6F'
C_ROSE  = '#B05A52'
C_AMBER = '#C49A2A'

# load and cache the tax computation file
@st.cache_data
def load():
    df = pd.read_csv(TAX_FILE)
    df.columns = [c.strip() for c in df.columns]
    df['Purchase Date']      = pd.to_datetime(df['Purchase Date'], errors='coerce')
    df['Sell Date']          = pd.to_datetime(df['Sell Date'],     errors='coerce')
    df['Holding Period']     = pd.to_numeric(df['Holding Period'], errors='coerce')
    df['Realized_Gain_Loss'] = (df['Sell Value'] - df['Buy Value']).round(2)
    df['Tax_Category']       = df['Holding Period'].apply(
                                   lambda x: 'LTCG' if x > 365 else 'STCG')
    df['Sell_Month']         = df['Sell Date'].dt.to_period('M').astype(str)
    nm = (df['Holding Period'].between(300, 365) &
          (df['Realized_Gain_Loss'] > 0) & (df['Tax_Category'] == 'STCG'))
    df['Potential_Saving'] = 0.0
    df.loc[nm, 'Potential_Saving'] = df.loc[nm].apply(
        lambda r: r['Realized_Gain_Loss'] * (
            0.05 if r['Sell Date'] < BUDGET_DATE else 0.075), axis=1)
    return df

if not os.path.exists(TAX_FILE):
    st.error("Run `python tax_engine.py` first — file not found.")
    st.stop()

df = load()

# sidebar navigation and filters
with st.sidebar:
    st.markdown("""
    <div style='background:#5B8DB8;padding:14px;border-radius:8px;
                text-align:center;margin-bottom:16px;'>
      <div style='color:#FFFFFF;font-size:13px;font-weight:700;'>
          GRESHMA SHARES & STOCKS</div>
      <div style='color:#D6E8F7;font-size:11px;margin-top:3px;'>
          Capital Gains · FY 2024-25</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
    "Navigation",
    ["📊 Overview", "👤 Client View", "📥 Export"],
    label_visibility="collapsed"
    )

    st.markdown("---")
    cat_filter = st.radio("Category", ["All", "STCG only", "LTCG only"])
    st.markdown("---")
    st.caption(f"**{len(df)}** trades · **{df['Client_Source'].nunique()}** clients")
    st.caption("SEBI: INZ000190130 | CDSL: 63000")

dff = df.copy()
if cat_filter == "STCG only":
    dff = dff[dff['Tax_Category'] == 'STCG']
elif cat_filter == "LTCG only":
    dff = dff[dff['Tax_Category'] == 'LTCG']

# helper functions
def kpi(col, label, value, sub="", variant=""):
    col.markdown(f"""
    <div class='kpi-card {variant}'>
      <div class='kpi-label'>{label}</div>
      <div class='kpi-value'>{value}</div>
      <div class='kpi-sub'>{sub}</div>
    </div>""", unsafe_allow_html=True)

def sec(title):
    st.markdown(f"<div class='sec-title'>{title}</div>", unsafe_allow_html=True)

def colour_pl(val):
    if isinstance(val, float) and val > 0:
        return 'background-color: #D6EAD8; color: #1E5E2E; font-weight: 600'
    elif isinstance(val, float) and val < 0:
        return 'background-color: #F5D5D3; color: #7B2020; font-weight: 600'
    return ''

# overview page
if "Overview" in page:
    st.markdown("### Portfolio Overview — FY 2024-25")
    st.caption("Budget 2024 rates applied · Intra-head set-off computed")

    net    = dff['Realized_Gain_Loss'].sum()
    tax    = dff['Calculated_Tax_Liability'].sum()
    saves  = dff['Potential_Saving'].sum()
    wins   = (dff['Realized_Gain_Loss'] > 0).sum()
    losses = (dff['Realized_Gain_Loss'] < 0).sum()

    c1, c2, c3, c4, c5 = st.columns(5)
    kpi(c1, "Net Portfolio P/L",   f"₹{net:,.0f}",
        "Gain" if net >= 0 else "Loss",
        "kpi-gain" if net >= 0 else "kpi-loss")
    kpi(c2, "Total Tax Liability", f"₹{tax:,.0f}", "After set-off")
    kpi(c3, "Near-Miss Savings",   f"₹{saves:,.0f}", "Recoverable", "kpi-save")
    kpi(c4, "Winning Trades",      str(wins),  f"of {len(dff)} total", "kpi-gain")
    kpi(c5, "Loss Trades",         str(losses), f"of {len(dff)} total", "kpi-loss")

    st.markdown("")
    col1, col2 = st.columns(2)

    with col1:
        sec("Tax Liability by Client")
        cs = dff.groupby('Client_Source')['Calculated_Tax_Liability'].sum() \
               .reset_index().sort_values('Calculated_Tax_Liability', ascending=False)
        fig1 = px.bar(cs, x='Client_Source', y='Calculated_Tax_Liability',
                      labels={'Client_Source':'', 'Calculated_Tax_Liability':'Tax (₹)'},
                      color_discrete_sequence=[C_BLUE])
        fig1.update_layout(**PL, showlegend=False, xaxis_tickangle=-40)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        sec("Net P/L by Client")
        cs2 = dff.groupby('Client_Source')['Realized_Gain_Loss'].sum().reset_index()
        cs2['Type'] = cs2['Realized_Gain_Loss'].apply(
            lambda x: 'Gain' if x >= 0 else 'Loss')
        fig2 = px.bar(
            cs2.sort_values('Realized_Gain_Loss', ascending=False),
            x='Client_Source', y='Realized_Gain_Loss', color='Type',
            color_discrete_map={'Gain': C_SAGE, 'Loss': C_ROSE},
            labels={'Client_Source':'', 'Realized_Gain_Loss':'Net P/L (₹)'}
        )
        fig2.update_layout(**PL, xaxis_tickangle=-40, legend=LEGEND_H)
        fig2.add_hline(y=0, line_dash='dot', line_color='#9CA3AF', opacity=0.5)
        st.plotly_chart(fig2, use_container_width=True)

    sec("Monthly Net P/L + Tax Trend")
    monthly = dff.groupby('Sell_Month').agg(
        Net=('Realized_Gain_Loss', 'sum'),
        Tax=('Calculated_Tax_Liability', 'sum')
    ).reset_index().sort_values('Sell_Month')
    fig3 = px.line(monthly, x='Sell_Month', y='Net', markers=True,
                   labels={'Sell_Month':'Month', 'Net':'Net P/L (₹)'},
                   color_discrete_sequence=[C_BLUE])
    fig3.add_bar(x=monthly['Sell_Month'], y=monthly['Tax'],
                 name='Tax', marker_color='rgba(176,90,82,0.3)')
    fig3.add_hline(y=0, line_dash='dot', line_color='#9CA3AF', opacity=0.4)
    fig3.update_layout(**PL, legend=LEGEND_H)
    st.plotly_chart(fig3, use_container_width=True)

# client drilldown page
elif "Client" in page:
    st.markdown("### Client View")

    client = st.selectbox("Select Client", sorted(df['Client_Source'].unique()))
    cdf = df[df['Client_Source'] == client]

    net  = cdf['Realized_Gain_Loss'].sum()
    tax  = cdf['Calculated_Tax_Liability'].sum()
    eff  = tax / net * 100 if net > 0 else 0
    save = cdf['Potential_Saving'].sum()

    c1, c2, c3, c4 = st.columns(4)
    kpi(c1, "Total Trades",     str(len(cdf)), "")
    kpi(c2, "Net Realised P/L", f"₹{net:,.0f}",
        "Gain" if net >= 0 else "Loss",
        "kpi-gain" if net >= 0 else "kpi-loss")
    kpi(c3, "Tax Liability",    f"₹{tax:,.2f}", f"Eff. rate {eff:.1f}%")
    kpi(c4, "Near-Miss Saving", f"₹{save:,.2f}",
        "Recoverable" if save > 0 else "None",
        "kpi-save" if save > 0 else "")

    col1, col2 = st.columns(2)
    with col1:
        sec("P/L by Scrip")
        sp = cdf.groupby('Scrip Name')['Realized_Gain_Loss'].sum().reset_index()
        sp['Type'] = sp['Realized_Gain_Loss'].apply(
            lambda x: 'Gain' if x >= 0 else 'Loss')
        fig_s = px.bar(
            sp.sort_values('Realized_Gain_Loss'),
            x='Realized_Gain_Loss', y='Scrip Name', orientation='h',
            color='Type', color_discrete_map={'Gain': C_SAGE, 'Loss': C_ROSE},
            labels={'Realized_Gain_Loss':'Net P/L (₹)', 'Scrip Name':''}
        )
        fig_s.update_layout(**PL, showlegend=False)
        fig_s.add_vline(x=0, line_dash='dot', line_color='#9CA3AF', opacity=0.5)
        st.plotly_chart(fig_s, use_container_width=True)

    with col2:
        sec("STCG vs LTCG Split")
        cat = cdf.groupby('Tax_Category')['Realized_Gain_Loss'].sum().reset_index()
        fig_c = px.pie(cat, names='Tax_Category', values='Realized_Gain_Loss',
                       hole=0.52,
                       color_discrete_map={'STCG': C_BLUE, 'LTCG': C_SAGE})
        fig_c.update_layout(**PL)
        fig_c.update_traces(textfont_color='#374151')
        st.plotly_chart(fig_c, use_container_width=True)

    sec("All Transactions")
    display = cdf[[
        'Scrip Name','Purchase Date','Sell Date','Units',
        'Holding Period','Buy Value','Sell Value',
        'Realized_Gain_Loss','Tax_Category','Calculated_Tax_Liability'
    ]].sort_values('Sell Date').copy()
    display['Purchase Date'] = display['Purchase Date'].dt.strftime('%d-%b-%Y')
    display['Sell Date']     = display['Sell Date'].dt.strftime('%d-%b-%Y')
    st.dataframe(
        display.style
        .format({
            'Buy Value':'₹{:,.2f}', 'Sell Value':'₹{:,.2f}',
            'Realized_Gain_Loss':'₹{:,.2f}',
            'Calculated_Tax_Liability':'₹{:,.2f}'
        })
        .applymap(colour_pl, subset=['Realized_Gain_Loss']),
        use_container_width=True, height=400
    )

# # scrip view - commented out, can enable later
# elif "Scrip" in page:
#     st.markdown("### Scrip-wise Analysis")

#     ss = dff.groupby('Scrip Name').agg(
#         Trades   = ('Client_Source',           'count'),
#         Net_PL   = ('Realized_Gain_Loss',       'sum'),
#         Tax      = ('Calculated_Tax_Liability', 'sum'),
#         Avg_Hold = ('Holding Period',           'mean'),
#     ).reset_index().sort_values('Net_PL', ascending=False)

#     col1, col2 = st.columns(2)
#     with col1:
#         sec("Net P/L by Scrip")
#         ss['Type'] = ss['Net_PL'].apply(lambda x: 'Gain' if x >= 0 else 'Loss')
#         fig_sp = px.bar(ss, x='Scrip Name', y='Net_PL', color='Type',
#                         color_discrete_map={'Gain': C_SAGE, 'Loss': C_ROSE},
#                         labels={'Scrip Name':'', 'Net_PL':'Net P/L (₹)'})
#         fig_sp.update_layout(**PL, showlegend=False, xaxis_tickangle=-45)
#         st.plotly_chart(fig_sp, use_container_width=True)

#     with col2:
#         sec("Avg Holding Period by Scrip")
#         fig_h = px.bar(
#             ss.sort_values('Avg_Hold', ascending=False),
#             x='Scrip Name', y='Avg_Hold',
#             color='Avg_Hold',
#             color_continuous_scale=[[0,'#C8DCF0'],[1,'#2C6FAC']],
#             labels={'Scrip Name':'', 'Avg_Hold':'Avg Days Held'},
#             text_auto='.0f'
#         )
#         fig_h.add_hline(y=365, line_dash='dash', line_color=C_AMBER,
#                         annotation_text='LTCG threshold (365d)',
#                         annotation_font_color=C_AMBER,
#                         annotation_font_size=11)
#         fig_h.update_layout(**PL, coloraxis_showscale=False, xaxis_tickangle=-45)
#         st.plotly_chart(fig_h, use_container_width=True)

#     sec("Scrip Summary Table")
#     st.dataframe(
#         ss[['Scrip Name','Trades','Net_PL','Tax','Avg_Hold']].style
#         .format({
#             'Net_PL':'₹{:,.2f}', 'Tax':'₹{:,.2f}', 'Avg_Hold':'{:.0f} days'
#         })
#         .applymap(colour_pl, subset=['Net_PL']),
#         use_container_width=True
#     )

# export page
elif "Export" in page:
    st.markdown("### Downloads")

    col1, col2 = st.columns(2)
    with col1:
        sec("Full Excel Report")
        st.caption("6 sheets: Cover · KPI · Optimization · Scrip · Monthly · Audit Trail")
        if os.path.exists(EXCEL_FILE):
            with open(EXCEL_FILE, 'rb') as f:
                st.download_button(
                    "⬇ Download Excel Report",
                    data=f.read(),
                    file_name="Tax_Report_FY2024-25.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
        else:
            st.warning("Run `python excel_generator.py` first.")

    with col2:
        sec("Filtered CSV")
        st.caption("Current view exported as CSV")
        st.download_button(
            "⬇ Download CSV",
            data=dff.to_csv(index=False),
            file_name="Filtered_FY2024-25.csv",
            mime="text/csv",
            use_container_width=True
        )

    sec("Client Tax Summary")
    summary = dff.groupby('Client_Source').agg(
        Trades = ('Scrip Name',              'count'),
        Net_PL = ('Realized_Gain_Loss',       'sum'),
        Tax    = ('Calculated_Tax_Liability', 'sum'),
        Saving = ('Potential_Saving',         'sum'),
    ).reset_index()
    summary['Eff_Rate %'] = (
        summary['Tax'] / summary['Net_PL'].clip(lower=0.01) * 100
    ).round(2)
    st.dataframe(
        summary.style.format({
            'Net_PL':'₹{:,.2f}', 'Tax':'₹{:,.2f}',
            'Saving':'₹{:,.2f}', 'Eff_Rate %':'{:.2f}%'
        }).applymap(colour_pl, subset=['Net_PL']),
        use_container_width=True
    )