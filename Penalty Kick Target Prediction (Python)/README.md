
---

# Penalty Kick Target Prediction (Python, Biogeme, Streamlit)

*MSc team project (Analytics Project, RWTH Aachen University). Full report: `Project_Report.pdf`.*

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
├── DataSetModel0NA6Alt.csv            # Penalty kick dataset used for estimation (2,358 kicks, ';' separated)
├── DataSetModelPlayer.csv             # Player-level panel version of the dataset
├── naive.py                           # Multinomial logit estimation in Biogeme (saves a .pickle of results)
├── unbalance.py                       # Nested logit estimation in Biogeme
├── mixedlogit.py                      # Streamlit view of mixed logit parameters (ASC, mu, sigma)
├── app.py                             # Streamlit prediction app (uses the estimated coefficients)
├── Streamlit_App_Guide.pdf            # Guide to the Streamlit app
├── Project_Report.pdf                 # Full project report
└── requirements.txt                   # Python dependencies
```

---

## 🚀 Getting Started

```bash
pip install -r requirements.txt
```

### Running the estimation

```bash
python naive.py        # multinomial logit
python unbalance.py    # nested logit
```

Each script prints the estimated parameters (with log-likelihood and fit statistics) and writes the Biogeme results files to the working directory.

### Launching the prediction app

```bash
streamlit run app.py
```

Set the player, goalkeeper and match inputs to see the predicted probability for each of the six target zones.
