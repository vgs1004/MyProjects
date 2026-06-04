
---

# Modeling Penalty Kick Behavior using Discrete Choice Models

An advanced sports analytics pipeline that applies econometric **Discrete Choice Models (DCMs)** to predict and evaluate penalty kick target selection in elite football. The repository combines data processing, statistical estimation using `Biogeme`, and an interactive web deployment dashboard built with `Streamlit`.

## 📊 Project Overview

Penalty kicks are isolated, high-pressure, game-theoretic duels that drastically impact match outcomes. While open play is dynamic and chaotic, the penalty kick provides a highly standardized, controlled environment featuring a finite choice set.

This project discretizes the football goal into **6 distinct target zones** based on height and lateral alignment:

* **Top-Left (TL)** | **Top-Center (TC)** | **Top-Right (TR)** 


* **Down-Left (DL)** | **Down-Center (DC)** | **Down-Right (DR)** 



By analyzing **2,358 elite-level penalty kicks** (2006–2021) across premier competitions like the FIFA World Cup, UEFA Champions League, and German Bundesliga, this study investigates how player characteristics, match context, and goalkeeper movements probabilistically influence target choice.

---

## 🛠️ Methodology & Modeling

### 1. Econometric Framework

The project implements a **Multinomial Logit (MNL) framework** and expands into panel structures to capture longitudinal player behavior across repeated measures. The operational utility ($U$) for selecting a specific goal alternative $i$ by a player at instance $t$ is expressed as:

$$U_{it} = ASC_i + \sum_{k} \beta_{ik} X_{kt} + \epsilon_{it}$$

Where:

* **$ASC_i$**: Alternative-Specific Constant reflecting the baseline popularity of a target area (using *Down-Center (DC)* as the reference alternative fixed to 0).


* **$\beta_{ik}$**: Estimated coefficients for the vector of explanatory covariates ($X_{kt}$).


* **$\epsilon_{it}$**: An independent and identically distributed (i.i.d.) Gumbel error term.



### 2. Primary Explanatory Covariates (16 Total Variables)

* **Player Characteristics**: Strong foot/footedness (`foot`: 0 = Left, 1 = Right), tactical position (Defender, Midfielder, Striker), and age brackets.


* **Goalkeeper Attributes**: Height scale (`HeiGK`), starting position line-bias (`GKS`), and visible movement patterns (`moveGK`).


* **Situational Context**: Match timing/fatigue tracking, match importance/pressure metrics, and game format (`IngSo`: In-Match vs. Shootout knockout context).


* **Historical Performance**: Lagged outcomes (`lpbg`: goal, save, miss), short-term directional history (`la3`, `la6`), and long-term conversation percentages.



---

## 📈 Key Findings & Insights

* **Baseline Distribution**: Lower targets are heavily favored, accounting for **75.57%** of all historical selections (DL: 37.23%, DR: 31.51%). This strongly indicates a preference for placement-oriented strategies over power-based variants.


* **The "Natural Side" Phenomenon**: Clear biomechanical biases exist. Right-footed players disproportionately target the left-hand side of the goal (DL/TL), whereas left-footed players favor right-hand sides (DR/TR) to optimize accuracy when shooting across their bodies.


* **Psychological Loss Aversion**: Despite strategic advantages to shooting down the center, players actively avoid the *Down-Center (DC)* area (6.8% frequency) to dodge the high psychological blame associated with a goalkeeper making a stationary, effortless save.


* **Predictive Performance**: The comprehensive MNL model reaches a **42.24% directional prediction accuracy**, outperforming naive baselines by 5.0 percentage points and proving that penalty choices are not entirely random.



---

## 📂 Repository Code Structure

```text
├── data/
│   └── penalties_dataset.csv     # Scraped and verified historical event data (2,358 entries)
├── estimation/
│   ├── model_estimation.py       # Core python engine utilizing Biogeme for maximum likelihood
│   └── naive_baseline.py         # Baseline constant-only (ASC) reference script
├── dashboard/
│   └── app.py                    # Interactive Streamlit frontend deployment application
├── requirements.txt              # Project environment dependencies
└── README.md                     # Repository documentation

```

### ⚠️ Python File Retention Notice

> Do **NOT** delete any python scripts! `model_estimation.py` is essential for compiling your econometric parameters inside the `Biogeme` modeling framework. `app.py` serves as your visual web interface tool that brings your mathematical formulas into an accessible space for sports coaches and broadcast analysts. Both are required for the project pipeline to work.
> 
> 

---

## 🚀 Getting Started

### Prerequisites

Ensure you have Python 3.9+ installed along with the critical structural package dependencies:

```bash
pip install pip --upgrade
pip install -r requirements.txt

```

*(Your `requirements.txt` must explicitly contain `pandas`, `biogeme`, and `streamlit`.)*

### Running the Estimation Engine

To run the Maximum Likelihood Estimation and view the output metrics (Log-Likelihood, AIC, BIC, parameter $t$-tests):

```bash
python estimation/model_estimation.py

```

### Launching the Interactive Dashboard

To deploy the prediction model into a local, user-friendly browser graphical user interface:

```bash
streamlit run dashboard/app.py

```
