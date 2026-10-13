# E-Commerce Supply, Partner and Pricing Analytics

A Databricks SQL pipeline (raw, cleaned, gold layers) feeding a Tableau
dashboard on seller (partner) performance, delivery reliability and pricing
dynamics, built on the Brazilian E-Commerce Public Dataset by Olist (Kaggle).

![Dashboard](screenshots/Dashboard%201.png)

## Key findings

- **Revenue:** R$ 13.6M across all orders (R$ 13.2M from delivered orders).
  The top three categories (health_beauty, watches_gifts, bed_bath_table)
  each bring in over R$ 1M.
- **Partners:** 2,970 sellers tracked. The average seller delivers 92.1% of
  orders on time, with an average delivery time of 11.9 days.
- **Delivery risk:** the 15 slowest sellers (min. 5 orders) take 27 to 38
  days on average, 2 to 3 times the typical seller. These are the partners
  to review first.
- **Pricing:** products priced close to their category average (80-120%)
  sell the most, 10.4 units on average, versus 7.3 for products priced at
  more than 2x the category average.

## What it is

- Public dataset: Olist Brazilian E-Commerce
  (https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce), around
  100k orders, 2016 to 2018. No proprietary or employer data.
- A three-layer SQL pipeline in Databricks: raw tables loaded from the
  source CSVs, a cleaned joined view, and five gold aggregate tables.
- A Tableau dashboard built from the gold layer.

## Tools used

- Databricks Community Edition (Spark SQL, Delta tables)
- SQL (joins, window functions, aggregation) for all three layers
- Tableau (calculated fields, FIXED LOD expressions, context filters,
  Top N filters, data blending for KPI tiles, dashboard design)

## Pipeline

Raw layer: the 7 source CSVs loaded as-is into Delta tables under the
olist_raw schema.

Cleaned layer: one joined view (cleaned_order_items) combining order
items, orders, sellers, and products with English category names and
computed delivery timing (delivery_days, is_on_time).

Gold layer, five tables:
- gold_seller_performance: revenue, order count, delivery speed, and
  on-time rate per seller (delivered orders)
- gold_category_sell_through: units sold, revenue, and average price
  per category (all orders)
- gold_discount_depth_vs_volume: units sold and average price paid per
  product (products with 3+ sales)
- gold_delivery_time_by_seller: average delivery days and on-time rate
  per seller (sellers with 5+ delivered orders)
- gold_revenue_by_category: total revenue and share of revenue per
  category

## Dashboard

| View | Question it answers |
|---|---|
| KPI tiles | Delivered revenue, sellers tracked, on-time %, average delivery days |
| Partner Performance (scatter) | Which sellers combine high revenue with reliable delivery? |
| Pricing Dynamics (bars) | Do products priced above their category average sell less? |
| 15 slowest sellers (bars) | Which partners are the biggest delivery risk? |
| Top 15 categories by revenue | Where does revenue concentrate? |

## Methodology notes

- **Pricing metric.** Olist has no list-price field, so a true discount
  cannot be measured. The original `avg_discount_pct` column in the gold
  table turned out to be 0 for every product (each product was compared
  with its own average price, which cancels out). The dashboard therefore
  uses a price index: each product's average price divided by the average
  product price in its category, grouped into five bands. This is
  documented in the notebook, which also contains the equivalent SQL.
- **Seller averages.** On-time rate and delivery days in the KPI tiles are
  simple averages across sellers, not weighted by order volume.
- **Revenue.** Category revenue includes all orders; seller revenue and the
  KPI tile include delivered orders only, which explains the R$ 13.6M vs
  R$ 13.2M difference.

## Files

| File | Purpose |
|---|---|
| notebook/olist_supply_partner_pricing_analytics.sql | The full Databricks notebook (raw, cleaned, gold layers), importable directly into Databricks |
| gold_data/ | The five gold CSVs exported from Databricks, used as the Tableau data sources |
| E-Commerce Partner and Pricing Analytics.twbx | Packaged Tableau workbook (data included, opens anywhere) |
| TABLEAU_BUILD_GUIDE.md | How each sheet and the dashboard were built |
| screenshots/ | Dashboard image |

## Links

- Tableau Public dashboard: (added once published)
- Portfolio: https://github.com/vgs1004/MyProjects

Note: the raw Olist CSVs are not included in this repo (available free
from the Kaggle dataset page linked above); run the notebook's raw-layer
cell after uploading them to Databricks to reproduce the pipeline.
