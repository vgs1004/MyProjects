# Concrete Compressive Strength Prediction (Python, scikit-learn)

Regression models predicting the compressive strength of concrete (MPa) from its mix and age, using the UCI Concrete Compressive Strength dataset.

## Data

`Concrete_Data.csv`: 1,030 records, 8 input features and 1 target. Source: UCI Machine Learning Repository (I-Cheng Yeh), public dataset.

| Inputs (kg per m³ of mixture, plus age) | Target |
|---|---|
| Cement, Blast Furnace Slag, Fly Ash, Water, Superplasticizer, Coarse Aggregate, Fine Aggregate, Age (days) | Compressive strength (MPa) |

## Approach

- Exploratory analysis of distributions and correlations, with z-score outlier checks
- Train and test split with feature scaling
- Models compared: Linear Regression, Polynomial (quadratic) Regression, Ridge and Lasso
- Hyperparameter tuning with GridSearchCV and K-fold cross-validation
- Feature selection to identify which mix components drive strength
- Models compared on mean squared error and R²

## How to run

```bash
pip install -r requirements.txt
jupyter notebook Concrete_Strength_Regression.ipynb
```

## Files

| File | Purpose |
|---|---|
| `Concrete_Strength_Regression.ipynb` | Full analysis and modelling |
| `Concrete_Data.csv` | Dataset |
| `requirements.txt` | Python dependencies |
