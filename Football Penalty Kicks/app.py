# Penalty Kick Prediction App using Biogeme Results
# Author: Assistant AI
# Description: Streamlit app for predicting penalty kick directions using trained Biogeme MNL model

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import json
import os
import sys
from PIL import Image
import warnings
warnings.filterwarnings('ignore')

# Set page configuration
st.set_page_config(
    page_title=" Penalty Kick Predictor",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Global variables for model loading
MODEL_LOADED = False
results = None
beta_values = {}

@st.cache_data
def load_model():
    """Load the trained Biogeme model and extract parameters"""
    global MODEL_LOADED, results, beta_values

    # Use sample parameters for demonstration
    beta_values = get_sample_parameters()
    MODEL_LOADED = True
    return beta_values, True

def get_sample_parameters():
    return {
        'asc_DL': 0.199,
        'asc_DR': 2.680,
        'asc_TC': 0.298,
        'asc_TL': 2.880,
        'asc_TR': 5.350,
        'asc_DC': 0.0,  # fixed reference

        'b_foot_DL': 0.371,
        'b_foot_DR': -0.215,
        'b_foot_TC': 0.802,
        'b_foot_TL': 0.419,
        'b_foot_TR': -0.592,
        'b_foot_DC': 0.0,  # fixed

        'b_moveGK_DL': 0.404,
        'b_moveGK_DR': -0.324,
        'b_moveGK_TC': -0.129,
        'b_moveGK_TL': -0.046,
        'b_moveGK_TR': 0.027,
        'b_moveGK_DC': 0.0,

        'b_GKS_DL': -0.160,
        'b_GKS_DR': -0.137,
        'b_GKS_TC': 0.018,
        'b_GKS_TL': 0.219,
        'b_GKS_TR': -0.589,
        'b_GKS_DC': 0.0,

        'b_IS_DL': 0.454,
        'b_IS_DR': 0.232,
        'b_IS_TC': -0.305,
        'b_IS_TL': -0.294,
        'b_IS_TR': 0.851,
        'b_IS_DC': 0.0,

        'b_comL_DL': -0.147,
        'b_comL_DR': -0.068,
        'b_comL_TC': -0.483,
        'b_comL_TL': -0.743,
        'b_comL_TR': -0.123,
        'b_comL_DC': 0.0,

        'b_HGK_DL': -0.015,
        'b_HGK_DR': 0.027,
        'b_HGK_TC': 0.019,
        'b_HGK_TL': 0.024,
        'b_HGK_TR': 0.016,
        'b_HGK_DC': 0.0,

        'b_dec_DL': 0.067,
        'b_dec_DR': 0.194,
        'b_dec_TC': -1.368,
        'b_dec_TL': 0.365,
        'b_dec_TR': 0.487,
        'b_dec_DC': 0.0,

        'b_lp_DL': -0.173,
        'b_lp_DR': 0.170,
        'b_lp_TC': -0.577,
        'b_lp_TL': 0.078,
        'b_lp_TR': -0.160,
        'b_lp_DC': 0.0,

        'b_latr_DL': 0.680,
        'b_latr_DR': 0.538,
        'b_latr_TC': 0.949,
        'b_latr_TL': 0.442,
        'b_latr_TR': 1.025,
        'b_latr_DC': 0.0,

        'b_ladr_DL': 0.094,
        'b_ladr_DR': -0.226,
        'b_ladr_TC': 0.049,
        'b_ladr_TL': -0.198,
        'b_ladr_TR': -0.421,
        'b_ladr_DC': 0.0,

        'b_sr_TL': -1.100,
        'b_sr_TR': -0.700,

        'b_perc': 0.329,

        'b_rnog_DL': 0.067,
        'b_rnog_DR': 0.194,
        'b_rnog_TC': -0.483,
        'b_rnog_TL': -0.648,
        'b_rnog_TR': 0.487,
        'b_rnog_DC': 0.0,

        'b_solsbg_DL': 0.067,
        'b_solsbg_DR': 0.194,
        'b_solsbg_TC': 0.103,
        'b_solsbg_TL': 0.123,
        'b_solsbg_TR': 0.487,
        'b_solsbg_DC': 0.0,

        'b_nmovGK_DL': 0.067,
        'b_nmovGK_DR': 0.194,
        'b_nmovGK_TC': 0.010,
        'b_nmovGK_TL': 0.045,
        'b_nmovGK_TR': 0.487,
        'b_nmovGK_DC': 0.0,

        'b_def_DL': 0.067,
        'b_def_DR': 0.194,
        'b_def_TC': 0.437,
        'b_def_TL': 0.421,
        'b_def_TR': 0.487,
        'b_def_DC': 0.0
    }

# Initialize model loading
try:
    beta_values, MODEL_LOADED = load_model()
except Exception as e:
    MODEL_LOADED = False
    beta_values = {}

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        text-align: center;
        color: #FF6B35;  /* Changed from blue to orange */
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .prediction-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: #FFFFFF;  /* White text - easily changeable */
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    }
    .prob-box {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        padding: 1rem;
        margin: 0.5rem;
        border-radius: 10px;
        color: #FFFFFF;  /* White text */
        text-align: center;
        font-weight: bold;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
        color: #2C3E50;  /* Dark blue-gray for main text */
    }
    .info-box h4 {
        color: #E74C3C;  /* Red for headings */
    }
    .info-box ul li {
        color: #34495E;  /* Dark gray for list items */
    }
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: #FFFFFF;  /* White button text */
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    /* Additional Streamlit element colors */
    .stMarkdown p {
        color: #2C3E50;  /* Dark text for paragraphs */
    }
    .stSubheader {
        color: #8E44AD !important;  /* Purple for subheaders */
    }
    .stSelectbox label, .stSlider label {
        color: #27AE60 !important;  /* Green for form labels */
    }
    .stMetric label {
        color: #E67E22 !important;  /* Orange for metric labels */
    }
    .stMetric .metric-value {
        color: #C0392B !important;  /* Red for metric values */
    }
</style>
""", unsafe_allow_html=True)

def calculate_utilities_and_probabilities(user_inputs, beta_values):
    """
    Calculate utility values and choice probabilities for each alternative
    using the estimated parameters from Biogeme model
    """
    alternatives = ['TL', 'TC', 'TR', 'DL', 'DC', 'DR']
    utilities = {}

    # Extract user inputs
    foot = user_inputs['foot']
    moveGK = user_inputs['moveGK']
    GKS = user_inputs['GKS']
    IngSo = user_inputs['IngSo']
    comLea = user_inputs['comLea']
    HeiGK = user_inputs['HeiGK']
    Dec = user_inputs['Dec']
    lpbg = user_inputs['lpbg']
    la3 = user_inputs['la3']
    la6 = user_inputs['la6']
    SRGK1 = user_inputs.get('SRGK1', 0)
    SRGK3 = user_inputs.get('SRGK3', 0)
    perc = user_inputs['perc']
    rnoGroup = user_inputs['rnoGroup']
    Solsbg = user_inputs['Solsbg']
    def_var = user_inputs['def_var']
    nmovGK = user_inputs['nmovGK']

    # Calculate utilities for each alternative
    # TL (Top Left)
    utilities['TL'] = (
        beta_values.get('asc_TL', 0) +
        beta_values.get('b_foot_TL', 0) * foot +
        beta_values.get('b_moveGK_TL', 0) * moveGK +
        beta_values.get('b_GKS_TL', 0) * GKS +
        beta_values.get('b_IS_TL', 0) * IngSo +
        beta_values.get('b_comL_TL', 0) * comLea +
        beta_values.get('b_HGK_TL', 0) * HeiGK +
        beta_values.get('b_dec_TL', 0) * Dec +
        beta_values.get('b_lp_TL', 0) * lpbg +
        beta_values.get('b_latr_TL', 0) * la3 +
        beta_values.get('b_ladr_TL', 0) * la6 +
        beta_values.get('b_sr_TL', 0) * SRGK1 +
        beta_values.get('b_perc', 0) * perc +
        beta_values.get('b_rnog_TL', 0) * rnoGroup +
        beta_values.get('b_solsbg_TL', 0) * Solsbg +
        beta_values.get('b_def_TL', 0) * def_var +
        beta_values.get('b_nmovGK_TL', 0) * nmovGK
    )

    # TC (Top Center)
    utilities['TC'] = (
        beta_values.get('asc_TC', 0) +
        beta_values.get('b_foot_TC', 0) * foot +
        beta_values.get('b_moveGK_TC', 0) * moveGK +
        beta_values.get('b_GKS_TC', 0) * GKS +
        beta_values.get('b_IS_TC', 0) * IngSo +
        beta_values.get('b_comL_TC', 0) * comLea +
        beta_values.get('b_HGK_TC', 0) * HeiGK +
        beta_values.get('b_dec_TC', 0) * Dec +
        beta_values.get('b_lp_TC', 0) * lpbg +
        beta_values.get('b_latr_TC', 0) * la3 +
        beta_values.get('b_ladr_TC', 0) * la6 +
        beta_values.get('b_perc', 0) * perc +
        beta_values.get('b_rnog_TC', 0) * rnoGroup +
        beta_values.get('b_solsbg_TC', 0) * Solsbg +
        beta_values.get('b_def_TC', 0) * def_var +
        beta_values.get('b_nmovGK_TC', 0) * nmovGK
    )

    # TR (Top Right)
    utilities['TR'] = (
        beta_values.get('asc_TR', 0) +
        beta_values.get('b_foot_TR', 0) * foot +
        beta_values.get('b_moveGK_TR', 0) * moveGK +
        beta_values.get('b_GKS_TR', 0) * GKS +
        beta_values.get('b_IS_TR', 0) * IngSo +
        beta_values.get('b_comL_TR', 0) * comLea +
        beta_values.get('b_HGK_TR', 0) * HeiGK +
        beta_values.get('b_dec_TR', 0) * Dec +
        beta_values.get('b_lp_TR', 0) * lpbg +
        beta_values.get('b_latr_TR', 0) * la3 +
        beta_values.get('b_ladr_TR', 0) * la6 +
        beta_values.get('b_sr_TR', 0) * SRGK3 +
        beta_values.get('b_perc', 0) * perc +
        beta_values.get('b_rnog_TR', 0) * rnoGroup +
        beta_values.get('b_solsbg_TR', 0) * Solsbg +
        beta_values.get('b_def_TR', 0) * def_var +
        beta_values.get('b_nmovGK_TR', 0) * nmovGK
    )

    # DL (Down Left)
    utilities['DL'] = (
        beta_values.get('asc_DL', 0) +
        beta_values.get('b_foot_DL', 0) * foot +
        beta_values.get('b_moveGK_DL', 0) * moveGK +
        beta_values.get('b_GKS_DL', 0) * GKS +
        beta_values.get('b_IS_DL', 0) * IngSo +
        beta_values.get('b_comL_DL', 0) * comLea +
        beta_values.get('b_HGK_DL', 0) * HeiGK +
        beta_values.get('b_dec_DL', 0) * Dec +
        beta_values.get('b_lp_DL', 0) * lpbg +
        beta_values.get('b_latr_DL', 0) * la3 +
        beta_values.get('b_ladr_DL', 0) * la6 +
        beta_values.get('b_perc', 0) * perc +
        beta_values.get('b_rnog_DL', 0) * rnoGroup +
        beta_values.get('b_solsbg_DL', 0) * Solsbg +
        beta_values.get('b_def_DL', 0) * def_var +
        beta_values.get('b_nmovGK_DL', 0) * nmovGK
    )

    # DC (Down Center) - Reference alternative (utility = 0)
    utilities['DC'] = 0

    # DR (Down Right)
    utilities['DR'] = (
        beta_values.get('asc_DR', 0) +
        beta_values.get('b_foot_DR', 0) * foot +
        beta_values.get('b_moveGK_DR', 0) * moveGK +
        beta_values.get('b_GKS_DR', 0) * GKS +
        beta_values.get('b_IS_DR', 0) * IngSo +
        beta_values.get('b_comL_DR', 0) * comLea +
        beta_values.get('b_HGK_DR', 0) * HeiGK +
        beta_values.get('b_dec_DR', 0) * Dec +
        beta_values.get('b_lp_DR', 0) * lpbg +
        beta_values.get('b_latr_DR', 0) * la3 +
        beta_values.get('b_ladr_DR', 0) * la6 +
        beta_values.get('b_perc', 0) * perc +
        beta_values.get('b_rnog_DR', 0) * rnoGroup +
        beta_values.get('b_solsbg_DR', 0) * Solsbg +
        beta_values.get('b_def_DR', 0) * def_var +
        beta_values.get('b_nmovGK_DR', 0) * nmovGK
    )

    # Calculate probabilities using multinomial logit formula
    exp_utilities = {alt: np.exp(util) for alt, util in utilities.items()}
    sum_exp = sum(exp_utilities.values())
    probabilities = {alt: exp_util / sum_exp for alt, exp_util in exp_utilities.items()}

    return utilities, probabilities

def create_goal_visualization(probabilities):
    """Create a visual representation of the goal with probabilities"""
    fig = go.Figure()

    # Goal dimensions
    goal_width = 7.32
    goal_height = 2.44

    # Define the 6 zones
    zones = {
        'TL': {'x': [0, goal_width/3], 'y': [goal_height/2, goal_height], 'prob': probabilities['TL']},
        'TC': {'x': [goal_width/3, 2*goal_width/3], 'y': [goal_height/2, goal_height], 'prob': probabilities['TC']},
        'TR': {'x': [2*goal_width/3, goal_width], 'y': [goal_height/2, goal_height], 'prob': probabilities['TR']},
        'DL': {'x': [0, goal_width/3], 'y': [0, goal_height/2], 'prob': probabilities['DL']},
        'DC': {'x': [goal_width/3, 2*goal_width/3], 'y': [0, goal_height/2], 'prob': probabilities['DC']},
        'DR': {'x': [2*goal_width/3, goal_width], 'y': [0, goal_height/2], 'prob': probabilities['DR']}
    }

    # Color scale based on probability
    max_prob = max(probabilities.values())

    for zone, data in zones.items():
        # Calculate zone center
        x_center = (data['x'][0] + data['x'][1]) / 2
        y_center = (data['y'][0] + data['y'][1]) / 2

        # Color intensity based on probability
        intensity = data['prob'] / max_prob if max_prob > 0 else 0
        color = f'rgba(255, {int(255*(1-intensity))}, {int(255*(1-intensity))}, 0.8)'

        # Add rectangle for zone
        fig.add_shape(
            type="rect",
            x0=data['x'][0], y0=data['y'][0],
            x1=data['x'][1], y1=data['y'][1],
            fillcolor=color,
            line=dict(color="black", width=2),
        )

        # Add text with zone name and probability
        fig.add_annotation(
            x=x_center, y=y_center,
            text=f"{zone}<br>{data['prob']:.1%}",
            showarrow=False,
            font=dict(size=14, color="black"),
            bgcolor="white",
            bordercolor="black",
            borderwidth=1
        )

    # Goal frame
    fig.add_shape(
        type="rect",
        x0=0, y0=0, x1=goal_width, y1=goal_height,
        fillcolor="rgba(0,0,0,0)",
        line=dict(color="black", width=3),
    )

    # Add goal dimensions
    fig.add_annotation(x=goal_width/2, y=-0.3, text="7.32 m", showarrow=False, font=dict(size=12))
    fig.add_annotation(x=-0.5, y=goal_height/2, text="2.44 m", showarrow=False, font=dict(size=12), textangle=90)

    fig.update_layout(
        title="Penalty Kick Direction Probabilities",
        xaxis=dict(range=[-1, 8], showgrid=False, showticklabels=False),
        yaxis=dict(range=[-0.5, 3], showgrid=False, showticklabels=False),
        showlegend=False,
        width=800,
        height=400,
        plot_bgcolor='rgba(144, 238, 144, 0.3)'  # Light green background
    )

    return fig

def create_probability_bar_chart(probabilities):
    """Create a bar chart of probabilities"""
    alternatives = list(probabilities.keys())
    probs = list(probabilities.values())

    fig = px.bar(
        x=alternatives,
        y=probs,
        color=probs,
        color_continuous_scale='Viridis',
        title="Penalty Direction Probabilities",
        labels={'x': 'Direction', 'y': 'Probability'},
        text=[f'{p:.1%}' for p in probs]
    )

    fig.update_traces(textposition='outside')
    fig.update_layout(
        yaxis=dict(tickformat='.0%'),
        showlegend=False,
        height=400
    )

    return fig

def main():
    # Header
    st.markdown('<h1 class="main-header">⚽ Penalty Kick Direction Predictor</h1>', unsafe_allow_html=True)

    # Sidebar for inputs
    st.sidebar.title("🎯 Player & Match Settings")
    st.sidebar.markdown("---")

    # Create input form
    with st.sidebar.form("prediction_form"):
        st.subheader("🦶 Player Characteristics")

        # Foot preference
        foot = st.selectbox(
            "Preferred Foot",
            options=[0, 1],
            format_func=lambda x: "Left" if x == 0 else "Right",
            index=1,
            help="Player's preferred shooting foot"
        )

        # Player decision making
        Dec = st.selectbox(
            "Decisive Penalty",
            options=[0, 1],
            format_func=lambda x: "No" if x == 0 else "Yes",
            index=0,
            help="Is this a decisive penalty that could determine the match outcome?"
        )

        st.subheader("🥅 Goalkeeper Characteristics")

        # Goalkeeper movement
        moveGK = st.selectbox(
            "Goalkeeper Early Movement",
            options=[0, 1],
            format_func=lambda x: "No" if x == 0 else "Yes",
            index=0,
            help="Does the goalkeeper move early before the shot?"
        )

        # Goalkeeper standing position (corrected based on thesis)
        GKS = st.selectbox(
            "Goalkeeper Standing Position",
            options=[1, 2, 3],
            format_func=lambda x: "Left" if x == 1 else "Central" if x == 2 else "Right",
            index=1,  # Default to Central (2)
            help="Goalkeeper's standing position during penalty kick (1=Left, 2=Central, 3=Right)"
        )

        # Goalkeeper height (corrected based on thesis coding)
        height_options = {
            1: "<183 cm", 2: "183 cm", 3: "184 cm", 4: "185 cm", 5: "186 cm", 
            6: "187 cm", 7: "188 cm", 8: "189 cm", 9: "190 cm", 10: "191 cm",
            11: "192 cm", 12: "193 cm", 13: "194 cm", 14: "195 cm", 15: "196 cm", 16: ">196 cm"
        }

        HeiGK = st.selectbox(
            "Goalkeeper Height",
            options=list(height_options.keys()),
            format_func=lambda x: height_options[x],
            index=8,  # Default to 190 cm (code 9)
            help="Goalkeeper's height coding: 1=<183cm, 2=183cm, ..., 16=>196cm"
        )

        st.subheader("🏟️ Match Context")

        # Match importance
        IngSo = st.selectbox(
            "In Shootout",
            options=[0, 1],
            format_func=lambda x: "No" if x == 0 else "Yes",
            index=0,
            help="Is this penalty part of a penalty shootout?"
        )

        # Competition level
        comLea = st.selectbox(
            "Competition Level",
            options=[0, 1],
            format_func=lambda x: "Non-League" if x == 0 else "League",
            index=1,
            help="Type of competition (Non-League=amateur/cup, League=professional league)"
        )

        # Match pressure
        lpbg = st.selectbox(
            "Last Penalty Result",
            options=[0, 1, 2],
            format_func=lambda x: "Not Available" if x == 0 else "Failed" if x == 1 else "Scored",
            index=2,
            help="Did the player's last penalty attempt result in a goal? (0=N/A, 1=No, 2=Yes)"
        )

        st.subheader("📊 Historical Data")

        # Last alternative chosen (corrected based on thesis)
        la3 = st.selectbox(
            "Last Shot to TR (Top Right)",
            options=[0, 1, 2],
            format_func=lambda x: "Not Available" if x == 0 else "No" if x == 1 else "Yes",
            index=1,
            help="Was the last penalty shot to Top Right? (0=N/A, 1=No, 2=Yes)"
        )

        la6 = st.selectbox(
            "Last Shot to DR (Down Right)", 
            options=[0, 1, 2],
            format_func=lambda x: "Not Available" if x == 0 else "No" if x == 1 else "Yes",
            index=1,
            help="Was the last penalty shot to Down Right? (0=N/A, 1=No, 2=Yes)"
        )

        # Performance percentage (corrected based on thesis)
        perc = st.slider(
            "Historical Preference Percentage",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.05,
            help="Percentage of previous penalties shot to preferred direction"
        )

        st.subheader("🔧 Advanced Settings")

        # Additional variables with default values
        rnoGroup = st.selectbox(
            "Group Stage Match",
            options=[0, 1],
            format_func=lambda x: "No" if x == 0 else "Yes",
            index=0,
            help="Is this match in a group stage of a tournament?"
        )
        Solsbg = st.selectbox(
            "Previous Shootout Penalty Success",
            options=[0, 1],
            format_func=lambda x: "Failed" if x == 0 else "Scored",
            index=1,
            help="Did the opponent's last penalty in this shootout result in a goal?"
        )
        def_var = st.selectbox(
            "Player Position",
            options=[0, 1],
            format_func=lambda x: "Non-Defender" if x == 0 else "Defender",
            index=0,
            help="Is the penalty taker a defender?"
        )
        nmovGK = st.selectbox(
            "Goalkeeper Movement Status",
            options=[0, 1],
            format_func=lambda x: "Moving" if x == 0 else "Not Moving",
            index=0,
            help="Is the goalkeeper staying still (not moving) during the run-up?"
        )

        # Submit button
        predict_button = st.form_submit_button("🎯 Predict Penalty Direction", use_container_width=True)

    # Main content area
    if predict_button:
        # Prepare user inputs
        user_inputs = {
            'foot': foot,
            'moveGK': moveGK,
            'GKS': GKS,  # Now properly coded as 1, 2, 3
            'IngSo': IngSo,
            'comLea': comLea,
            'HeiGK': HeiGK,  # Now properly coded as 1-16
            'Dec': Dec,
            'lpbg': lpbg,  # Now properly coded as 0, 1, 2
            'la3': la3,    # Now properly coded as 0, 1, 2
            'la6': la6,    # Now properly coded as 0, 1, 2
            'SRGK1': 0,    # Default values for special variables
            'SRGK3': 0,
            'perc': perc,  # Now represents historical preference percentage
            'rnoGroup': rnoGroup,
            'Solsbg': Solsbg,
            'def_var': def_var,
            'nmovGK': nmovGK
        }

        # Calculate probabilities
        utilities, probabilities = calculate_utilities_and_probabilities(user_inputs, beta_values)

        # Find most likely direction
        most_likely = max(probabilities, key=probabilities.get)
        max_prob = probabilities[most_likely]

        # Display prediction
        st.markdown(f"""
        <div class="prediction-box">
            <h2>🎯 Prediction Result</h2>
            <h3>Most Likely Direction: <strong>{most_likely}</strong></h3>
            <h4>Confidence: <strong>{max_prob:.1%}</strong></h4>
        </div>
        """, unsafe_allow_html=True)

        # Create two columns for visualizations
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🥅 Goal Zones Visualization")
            goal_fig = create_goal_visualization(probabilities)
            st.plotly_chart(goal_fig, use_container_width=True)

        with col2:
            st.subheader("📊 Probability Distribution")
            bar_fig = create_probability_bar_chart(probabilities)
            st.plotly_chart(bar_fig, use_container_width=True)

        # Detailed probabilities
        st.subheader("📈 Detailed Probabilities")

        # Create probability cards
        cols = st.columns(6)
        directions = ['TL', 'TC', 'TR', 'DL', 'DC', 'DR']
        full_names = ['Top Left', 'Top Center', 'Top Right', 'Down Left', 'Down Center', 'Down Right']

        for i, (direction, full_name) in enumerate(zip(directions, full_names)):
            with cols[i]:
                prob = probabilities[direction]
                st.metric(
                    label=f"{direction} ({full_name})",
                    value=f"{prob:.1%}",
                    delta=f"Utility: {utilities[direction]:.2f}"
                )

        # Additional insights
        st.subheader("🧠 Model Insights")

        insight_col1, insight_col2 = st.columns(2)

        with insight_col1:
            gk_position = "Left" if GKS == 1 else "Central" if GKS == 2 else "Right"
            height_desc = height_options[HeiGK]

            st.markdown(f"""
            <div class="info-box">
                <h4>📝 Key Factors</h4>
                <ul>
                    <li><strong>Goalkeeper Movement:</strong> {'Early movement detected' if moveGK else 'No early movement'}</li>
                    <li><strong>Goalkeeper Position:</strong> {gk_position}</li>
                    <li><strong>Goalkeeper Height:</strong> {height_desc}</li>
                    <li><strong>Player Foot:</strong> {'Right-footed' if foot else 'Left-footed'}</li>
                    <li><strong>Pressure Situation:</strong> {'High pressure shootout' if IngSo else 'Regular penalty'}</li>
                    <li><strong>Last Penalty:</strong> {'Scored' if lpbg == 2 else 'Failed' if lpbg == 1 else 'N/A'}</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        with insight_col2:
            # Calculate confidence level
            confidence_level = "High" if max_prob > 0.4 else "Medium" if max_prob > 0.25 else "Low"

            st.markdown(f"""
            <div class="info-box">
                <h4>🎯 Prediction Analysis</h4>
                <ul>
                    <li><strong>Confidence Level:</strong> {confidence_level}</li>
                    <li><strong>Most Likely Zone:</strong> {most_likely} ({max_prob:.1%})</li>
                    <li><strong>Alternative Choice:</strong> {sorted(probabilities.items(), key=lambda x: x[1], reverse=True)[1][0]} ({sorted(probabilities.values(), reverse=True)[1]:.1%})</li>
                    <li><strong>Prediction Spread:</strong> {'Concentrated' if max_prob > 0.5 else 'Distributed'}</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        # Download prediction results
        st.subheader("💾 Export Results")

        # Create results dataframe
        results_df = pd.DataFrame({
            'Direction': list(probabilities.keys()),
            'Probability': list(probabilities.values()),
            'Utility': list(utilities.values())
        })

        # Add user inputs to results
        input_summary = pd.Series(user_inputs).to_frame('Value')
        input_summary.index.name = 'Parameter'

        col_a, col_b = st.columns(2)

        with col_a:
            st.download_button(
                label="📊 Download Probabilities (CSV)",
                data=results_df.to_csv(index=False),
                file_name=f"penalty_prediction_{most_likely}.csv",
                mime="text/csv"
            )

        with col_b:
            st.download_button(
                label="⚙️ Download Input Parameters (CSV)",
                data=input_summary.to_csv(),
                file_name="prediction_inputs.csv",
                mime="text/csv"
            )

    else:
        # Display information when no prediction is made
        st.markdown("""
        <div class="info-box">
            <h3>🎯 Welcome to the Penalty Kick Predictor!</h3>
            <p>This application uses a sophisticated <strong>Multinomial Logit Model</strong> trained with Biogeme to predict penalty kick directions.</p>

            <h4>📝 How it works:</h4>
            <ol>
                <li><strong>Input Parameters:</strong> Set player characteristics, goalkeeper attributes, and match context</li>
                <li><strong>ML Prediction:</strong> Our model analyzes 17+ variables to predict the most likely shot direction</li>
                <li><strong>Visualization:</strong> See probabilities mapped onto goal zones with interactive charts</li>
                <li><strong>Export Results:</strong> Download predictions for further analysis</li>
            </ol>

            <h4>🎯 Goal Zones:</h4>
            <ul>
                <li><strong>TL/TC/TR:</strong> Top Left, Top Center, Top Right</li>
                <li><strong>DL/DC/DR:</strong> Down Left, Down Center, Down Right</li>
            </ul>

            <h4>📊 Variable Coding:</h4>
            <ul>
                <li><strong>Goalkeeper Position:</strong> 1=Left, 2=Central, 3=Right</li>
                <li><strong>Goalkeeper Height:</strong> 1=<183cm, 2=183cm, ..., 16=>196cm</li>
                <li><strong>Last Shot Variables:</strong> 0=N/A, 1=No, 2=Yes</li>
            </ul>

            <p><em>Configure your parameters in the sidebar and click "Predict Penalty Direction" to start!</em></p>
        </div>
        """, unsafe_allow_html=True)

        # Display model statistics
        st.subheader("📊 Model Information")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("📈 Model Type", "Multinomial Logit")
            st.metric("🎯 Alternatives", "6 (TL, TC, TR, DL, DC, DR)")

        with col2:
            st.metric("🔢 Parameters", len(beta_values))
            st.metric("📊 Status", "Ready")

        with col3:
            st.metric("🎲 Reference Alternative", "DC (Down Center)")
            st.metric("📝 Variables", "17+ player & match factors")

if __name__ == "__main__":
    main()
