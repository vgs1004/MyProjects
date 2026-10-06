# Unbalanced Mixed Logit Model Visualization App
# Author: Assistant AI
# Description: Streamlit app to visualize ASC, mu, and sigma parameters from an estimated model

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import warnings
warnings.filterwarnings('ignore')

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Mixed Logit Model Results",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- MODEL PARAMETERS ---
MODEL_PARAMETERS = {
    'ASC2': -2.0974810983520484,
    'ASC3': -3.6048400995542726,
    'ASC4': 12.105745967771702,
    'ASC5': -3.082691896012108,
    'ASC6': 0.8864352765009443,
    'mu_foot': 8.634703462481175e-15,
    'mu_inertia': -0.432655412183192,
    'mu_moveGK': -8.042687067876587e-15,
    'mu_ri': 0.0,
    'sigma_foot': 0.9999999999999818,
    'sigma_inertia': 0.6935375345508964,
    'sigma_moveGK': 1.0000000000000158,
    'sigma_ri': 1.0000000000000244
}

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        text-align: center;
        color: #FF6B35;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
        color: #2C3E50;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<h1 class="main-header">📊 Mixed Logit Model Results</h1>', unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.title("Model Settings")
parameter_type = st.sidebar.selectbox("Parameter View", ["All", "ASC only", "Mu only", "Sigma only"])
show_table = st.sidebar.checkbox("Show Table", True)
show_bar = st.sidebar.checkbox("Show Bar Chart", True)

# --- DATA PROCESSING ---
df = pd.DataFrame(list(MODEL_PARAMETERS.items()), columns=["Parameter", "Value"])

if parameter_type == "ASC only":
    df = df[df["Parameter"].str.startswith("ASC")]
elif parameter_type == "Mu only":
    df = df[df["Parameter"].str.startswith("mu")]
elif parameter_type == "Sigma only":
    df = df[df["Parameter"].str.startswith("sigma")]

# --- TABLE DISPLAY ---
if show_table:
    st.subheader("📋 Model Coefficients Table")
    st.dataframe(df, use_container_width=True)

# --- BAR CHART ---
if show_bar:
    st.subheader("📊 Parameter Values Bar Chart")
    fig = px.bar(df, x="Parameter", y="Value", color="Value",
                 color_continuous_scale="Viridis", text_auto=".2f")
    fig.update_traces(textposition="outside")
    fig.update_layout(yaxis_title="Value", xaxis_title="Parameter", height=500)
    st.plotly_chart(fig, use_container_width=True)

# --- DOWNLOAD ---
csv = df.to_csv(index=False)
st.download_button("📥 Download CSV", data=csv, file_name="model_parameters.csv", mime="text/csv")

# --- MODEL INFORMATION ---
st.subheader("ℹ️ Model Info")
st.markdown("""
<div class="info-box">
    <h4>Model Summary</h4>
    <ul>
        <li><strong>Model Type:</strong> Unbalanced Mixed Logit</li>
        <li><strong>Number of Parameters:</strong> {}</li>
        <li><strong>Alternatives:</strong> 2, 3, 4, 5, 6</li>
        <li><strong>Random Parameters:</strong> foot, inertia, moveGK, ri</li>
    </ul>
</div>
""".format(len(MODEL_PARAMETERS)), unsafe_allow_html=True)
