
# Green Capital: The Role of Natural Capital in Economic Growth

An empirical, data-driven macroeconomic analysis investigating the extent to which natural capital contributes to economic output, featuring comparative case studies of an industrialized economy (**Germany**) and a resource-dependent economy (**Brazil**).

## 📊 Project Overview

Traditional national accounting frameworks often undervalue or entirely omit natural capital from growth theories. This project bridges that gap by integrating environmental assets into macroeconomic modeling. Using a log-transformed **Cobb–Douglas Production Function**, we analyze historical asset data to evaluate how changes in natural capital affect economic output and to identify underlying asset substitution patterns across different economic models.

### 🔍 Core Research Questions

* To what extent does natural capital contribute to economic output in Germany and Brazil? 


* How does its economic footprint compare with human and produced capital? 


* Can declines in natural capital cause measurable output losses or trigger structural substitution? 



---

## 🛠️ Data & Methodology

### 📂 Dataset

The project utilizes time-series data covering the period **1995–2020** extracted from the World Bank's **Changing Wealth of Nations (CWON)** database. The data incorporates three primary wealth pillars:

1. **Produced Capital:** Infrastructure, machinery, and physical assets.


2. **Human Capital:** Value of the labor force, factoring in education and skills.


3. **Natural Capital:** Aggregated values of both renewable and non-renewable resources (forests, minerals, agricultural land, etc.).



### 🧮 Econometric Modeling

We evaluate capital elasticity by estimating a linearized, log-log Cobb–Douglas framework:

$$\ln(Y) = \ln(A) + \beta \ln(H) + \gamma \ln(N)$$

Where:

* **$Y$** = Economic output (proxied by produced capital) 


* **$H$** = Human capital stock 


* **$N$** = Natural capital stock 


* **$\beta, \gamma$** = Output elasticities of human and natural capital inputs respectively 


* **$A$** = Total Factor Productivity (TFP) constant 



To tackle potential multicollinearity stemming from parallel capital growth, the project also implements a **Capital Share Model** which normalizes inputs into fractions of total national wealth.

---

## 📈 Key Empirical Findings

| Metric / Result | 🇩🇪 Germany (Industrialized) | 🇧🇷 Brazil (Resource-Based) |
| --- | --- | --- |
| **Natural Capital Elasticity** | **-1.58** (Significant) 

 | **+1.56** (Not statistically significant) 

 |
| **Human Capital Elasticity** | **+0.78** (Significant) 

 | **+0.88** (Significant) 

 |
| **Model Fit ($R^2$)** | 0.978 (Log-Log) / 0.998 (Share) 

 | 0.956 (Log-Log) / 0.972 (Share) 

 |
| **10% Natural Capital Decline Scenario** | **+18.2%** decoupled output shift * due to historical asset substitution patterns.

 | **-15.2%** reduction in output, confirming strong structural environmental dependency.

 |

> ⚠️ *Note on Germany:* The positive output projection following a simulated 10% nature loss reflects a historical industrial substitution trend (where produced/human capital aggressively grew while natural capital flattened), rather than a causal economic benefit from environmental degradation.
> 
> 

---

## 🚀 Pipeline Architecture & Code Structure

The analytics engine is designed sequentially to ensure reproducibility:

1. **Data Preprocessing (`DEU` & `BRA`):** Filters, cleans, and reshapes World Bank raw data into time-series records.


2. **Exploratory Data Analysis (EDA):** Generates capital stock trajectories and correlation matrices to isolate high-value features.


3. **OLS Regression:** Employs the Python `statsmodels` library to run log-log regressions and parse coefficients.


4. **Scenario Simulation:** Executes stress-testing models simulating resource degradation to predict macro-level output shocks.



---

Would you like me to adjust any specific section or add installation instructions based on the libraries you are using?
