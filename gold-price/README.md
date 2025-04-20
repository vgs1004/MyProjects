# Gold Price Forecasting Project

## Overview
This project focuses on forecasting gold prices using two powerful time series forecasting techniques: **ARIMA** and **LSTM (Long Short-Term Memory)**. The goal is to analyze historical gold price trends and build predictive models to estimate future price movements for better investment decisions.

## Dataset
The dataset used in this project is `gold_price.csv`, which contains daily gold prices in multiple currencies, including **INR**. The data includes date-wise gold prices, which are parsed and indexed by date.

## Key Steps

### 1. **Data Cleaning & Preparation**
- Removed commas in numeric fields.
- Converted all values to numeric types.
- Selected a currency column (INR) for forecasting.

### 2. **Stationarity Check**
- Used **ADF Test (Augmented Dickey-Fuller Test)** to verify if the series is stationary.

### 3. **ARIMA Forecasting**
- Applied the ARIMA model for linear forecasting.
- Visualized the ARIMA forecast against the last 100 actual data points.
- ARIMA: AutoRegressive Integrated Moving Average
- ARIMA is a classic statistical method used for time series forecasting. It’s powerful for modeling linear dependencies in time series data.
- AR (AutoRegressive): Uses past values to predict the future.
- I (Integrated): Differencing the series to make it stationary (removing trends).
- MA (Moving Average): Uses past errors in predictions to improve future predictions.
- Why ARIMA?
- Great for data with consistent linear trends or seasonality.
- Interpretable and fast to train.
- Works well with a relatively small dataset.

### 4. **LSTM Forecasting**
- Scaled the time series using **MinMaxScaler**.
- Created input sequences for the LSTM model.
- Trained an LSTM model with two layers and forecasted the next 30 days.
- Visualized LSTM results alongside the original series.
-  LSTM: Long Short-Term Memory Networks
-  LSTM is a special kind of Recurrent Neural Network (RNN) capable of learning long-term dependencies in time series data. Unlike ARIMA, it can capture non-linear and complex patterns in data.
-  LSTM layers have memory cells that preserve information over time.
-  Useful when traditional models like ARIMA fall short, especially in chaotic or seasonal data.
-  Requires more data and computation than ARIMA, but potentially gives better forecasts in complex scenarios.
-  Why LSTM?
-  Can handle non-stationary, non-linear, and multi-dimensional time series.
-  Useful for deep learning-based predictions that adapt to sudden shifts or unknown trends.

## Results
Both ARIMA and LSTM provide forecasts for the next 30 days. The plots help compare the effectiveness of each approach in capturing gold price trends.

## Tools & Libraries Used
- `pandas`, `numpy` for data processing
- `matplotlib` for visualization
- `statsmodels` for ARIMA and stationarity testing
- `scikit-learn` for scaling
- `keras` for LSTM neural networks

## Folder Structure
```
MyProjects/
└── gold-price/
    ├── gold_price.csv              # Dataset
    ├── gold_forecasting.ipynb      # Colab notebook with full analysis
    └── README.md                   # This documentation
```

## Author
Varshini Gayathri Suresh

## Notes
- The model can be extended to include other currencies.
- LSTM may benefit from further hyperparameter tuning or additional data.

---
Feel free to explore the notebook and modify it for more granular or multi-currency forecasting!


