-- Databricks notebook source
-- MAGIC %md
-- MAGIC # E-Commerce Supply, Partner and Pricing Analytics
-- MAGIC
-- MAGIC Built on the public **Olist Brazilian E-Commerce** dataset (Kaggle, ~100k
-- MAGIC orders, 2016-2018). No proprietary or employer data.
-- MAGIC
-- MAGIC Three layers, all in SQL:
-- MAGIC 1. **Raw** -- the source CSVs loaded as-is into Delta tables
-- MAGIC 2. **Cleaned** -- a single joined orders/items/sellers/products view
-- MAGIC 3. **Gold** -- five aggregated tables answering partner-lifecycle and
-- MAGIC    pricing-dynamics questions, exported as CSVs for the Tableau Public
-- MAGIC    dashboard (Tableau Public can't connect live to Community Edition,
-- MAGIC    so the gold layer is the hand-off point)
-- MAGIC
-- MAGIC **Before running this notebook:** upload the 7 Olist CSVs used here to a
-- MAGIC Unity Catalog Volume (Catalog > Add Data > Upload files to Volume; create
-- MAGIC a volume if prompted, e.g. workspace/default/volumev). Newer Databricks
-- MAGIC workspaces have the public DBFS root disabled, so the old
-- MAGIC `/FileStore/tables/` upload path won't work. Files needed:
-- MAGIC `olist_orders_dataset.csv`, `olist_order_items_dataset.csv`,
-- MAGIC `olist_customers_dataset.csv`, `olist_sellers_dataset.csv`,
-- MAGIC `olist_products_dataset.csv`, `olist_order_payments_dataset.csv`,
-- MAGIC `product_category_name_translation.csv`. Update `VOLUME_PATH` in the
-- MAGIC raw-layer cell below to match your volume's actual path.

-- COMMAND ----------

-- MAGIC %md ## 1. Raw layer
-- MAGIC Load each CSV from DBFS into a managed Delta table in a dedicated schema.

-- COMMAND ----------

CREATE SCHEMA IF NOT EXISTS olist_raw;

-- COMMAND ----------

-- MAGIC %python
-- MAGIC # Read each uploaded CSV (from a Unity Catalog Volume -- newer Databricks
-- MAGIC # workspaces have the public DBFS root disabled, so /FileStore/tables/
-- MAGIC # no longer works; files must live in a Volume instead) and write it out
-- MAGIC # as a raw Delta table. Adjust VOLUME_PATH below to match your own
-- MAGIC # catalog/schema/volume names if they differ.
-- MAGIC
-- MAGIC VOLUME_PATH = "/Volumes/workspace/default/volumev"
-- MAGIC
-- MAGIC files = {
-- MAGIC     "orders": "olist_orders_dataset.csv",
-- MAGIC     "order_items": "olist_order_items_dataset.csv",
-- MAGIC     "customers": "olist_customers_dataset.csv",
-- MAGIC     "sellers": "olist_sellers_dataset.csv",
-- MAGIC     "products": "olist_products_dataset.csv",
-- MAGIC     "payments": "olist_order_payments_dataset.csv",
-- MAGIC     "category_translation": "product_category_name_translation.csv",
-- MAGIC }
-- MAGIC
-- MAGIC for table_name, filename in files.items():
-- MAGIC     df = spark.read.csv(f"{VOLUME_PATH}/{filename}", header=True, inferSchema=True)
-- MAGIC     df.write.mode("overwrite").saveAsTable(f"olist_raw.{table_name}")
-- MAGIC     print(f"olist_raw.{table_name}: {df.count():,} rows")

-- COMMAND ----------

-- MAGIC %md ## 2. Cleaned layer
-- MAGIC One joined view: order items + orders + sellers + products (with
-- MAGIC English category names) + delivery timing. This is the base every gold
-- MAGIC table below aggregates from.

-- COMMAND ----------

CREATE OR REPLACE VIEW olist_raw.cleaned_order_items AS
SELECT
    oi.order_id,
    oi.order_item_id,
    oi.product_id,
    oi.seller_id,
    oi.price,
    oi.freight_value,
    o.customer_id,
    o.order_status,
    o.order_purchase_timestamp,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,
    DATEDIFF(o.order_delivered_customer_date, o.order_purchase_timestamp) AS delivery_days,
    CASE
        WHEN o.order_delivered_customer_date IS NULL THEN NULL
        WHEN o.order_delivered_customer_date <= o.order_estimated_delivery_date THEN 1
        ELSE 0
    END AS is_on_time,
    s.seller_state,
    COALESCE(ct.product_category_name_english, p.product_category_name, 'unknown') AS category
FROM olist_raw.order_items oi
JOIN olist_raw.orders o ON oi.order_id = o.order_id
LEFT JOIN olist_raw.sellers s ON oi.seller_id = s.seller_id
LEFT JOIN olist_raw.products p ON oi.product_id = p.product_id
LEFT JOIN olist_raw.category_translation ct ON p.product_category_name = ct.product_category_name;

-- COMMAND ----------

SELECT * FROM olist_raw.cleaned_order_items LIMIT 20;

-- COMMAND ----------

-- MAGIC %md ## 3. Gold layer
-- MAGIC Five tables, each answering one of the partner-lifecycle / pricing
-- MAGIC questions from the brief.

-- COMMAND ----------

-- MAGIC %md ### 3a. Seller / partner performance

-- COMMAND ----------

CREATE OR REPLACE TABLE olist_raw.gold_seller_performance AS
SELECT
    seller_id,
    seller_state,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(price), 2) AS total_revenue,
    ROUND(AVG(delivery_days), 1) AS avg_delivery_days,
    ROUND(AVG(is_on_time), 3) AS on_time_rate
FROM olist_raw.cleaned_order_items
WHERE order_status = 'delivered'
GROUP BY seller_id, seller_state;

SELECT * FROM olist_raw.gold_seller_performance ORDER BY total_revenue DESC LIMIT 20;

-- COMMAND ----------

-- MAGIC %md ### 3b. Category sell-through

-- COMMAND ----------

CREATE OR REPLACE TABLE olist_raw.gold_category_sell_through AS
SELECT
    category,
    COUNT(*) AS units_sold,
    COUNT(DISTINCT order_id) AS distinct_orders,
    ROUND(SUM(price), 2) AS total_revenue,
    ROUND(AVG(price), 2) AS avg_price
FROM olist_raw.cleaned_order_items
GROUP BY category
ORDER BY total_revenue DESC;

SELECT * FROM olist_raw.gold_category_sell_through;

-- COMMAND ----------

-- MAGIC %md ### 3c. Discount depth vs order volume
-- MAGIC
-- MAGIC **Note on methodology:** Olist's dataset has no list-price/MSRP field --
-- MAGIC `price` is simply what the customer paid. There is no true "discount"
-- MAGIC to measure directly. As a standard analyst workaround for this kind of
-- MAGIC gap, this table treats each product's own average selling price as its
-- MAGIC reference price, and measures how far individual sales sit below that
-- MAGIC reference -- i.e. relative pricing softness, not an actual promotional
-- MAGIC discount. This assumption is stated here and in the dashboard caption.

-- COMMAND ----------

CREATE OR REPLACE TABLE olist_raw.gold_discount_depth_vs_volume AS
WITH product_avg AS (
    SELECT product_id, AVG(price) AS product_avg_price
    FROM olist_raw.cleaned_order_items
    GROUP BY product_id
)
SELECT
    c.category,
    c.product_id,
    COUNT(*) AS units_sold,
    ROUND(AVG(c.price), 2) AS avg_price_paid,
    ROUND(pa.product_avg_price, 2) AS product_reference_price,
    ROUND(AVG((pa.product_avg_price - c.price) / NULLIF(pa.product_avg_price, 0)), 3) AS avg_discount_pct
FROM olist_raw.cleaned_order_items c
JOIN product_avg pa ON c.product_id = pa.product_id
GROUP BY c.category, c.product_id, pa.product_avg_price
HAVING COUNT(*) >= 3;  -- drop near-single-sale products; too noisy for a discount signal

SELECT * FROM olist_raw.gold_discount_depth_vs_volume ORDER BY units_sold DESC LIMIT 20;

-- COMMAND ----------

-- MAGIC %md **Known limitation found during the Tableau build:** `avg_discount_pct`
-- MAGIC above is 0 for every product. Because the reference price is the product's
-- MAGIC own average price, and rows are grouped by that same product, the average
-- MAGIC deviation from it always cancels out to zero. The column is kept so the
-- MAGIC exported CSV stays reproducible, but it is not used in the dashboard.
-- MAGIC
-- MAGIC The dashboard instead measures **price positioning**: each product's average
-- MAGIC price relative to the average product price in its category (a price index,
-- MAGIC where 1.0 = category average). In Tableau this is a calculated field with a
-- MAGIC FIXED LOD expression:
-- MAGIC `[Avg Price Paid] / {FIXED [Category] : AVG([Avg Price Paid])}`.
-- MAGIC The query below produces the same metric in SQL for reference.

-- COMMAND ----------

SELECT
    category,
    product_id,
    units_sold,
    avg_price_paid,
    ROUND(avg_price_paid / AVG(avg_price_paid) OVER (PARTITION BY category), 3) AS price_index_vs_category,
    CASE
        WHEN avg_price_paid / AVG(avg_price_paid) OVER (PARTITION BY category) < 0.5  THEN '1. Under 50%'
        WHEN avg_price_paid / AVG(avg_price_paid) OVER (PARTITION BY category) < 0.8  THEN '2. 50-80%'
        WHEN avg_price_paid / AVG(avg_price_paid) OVER (PARTITION BY category) <= 1.2 THEN '3. 80-120%'
        WHEN avg_price_paid / AVG(avg_price_paid) OVER (PARTITION BY category) <= 2   THEN '4. 120-200%'
        ELSE '5. Over 200%'
    END AS price_band
FROM olist_raw.gold_discount_depth_vs_volume;

-- COMMAND ----------

-- MAGIC %md ### 3d. Delivery time by seller

-- COMMAND ----------

CREATE OR REPLACE TABLE olist_raw.gold_delivery_time_by_seller AS
SELECT
    seller_id,
    seller_state,
    COUNT(DISTINCT order_id) AS order_count,
    ROUND(AVG(delivery_days), 1) AS avg_delivery_days,
    ROUND(AVG(is_on_time), 3) AS on_time_rate
FROM olist_raw.cleaned_order_items
WHERE order_status = 'delivered'
GROUP BY seller_id, seller_state
HAVING COUNT(DISTINCT order_id) >= 5;  -- drop near-single-order sellers; too noisy

SELECT * FROM olist_raw.gold_delivery_time_by_seller ORDER BY order_count DESC LIMIT 20;

-- COMMAND ----------

-- MAGIC %md ### 3e. Revenue by category

-- COMMAND ----------

CREATE OR REPLACE TABLE olist_raw.gold_revenue_by_category AS
SELECT
    category,
    ROUND(SUM(price), 2) AS total_revenue,
    ROUND(SUM(price) * 100.0 / SUM(SUM(price)) OVER (), 2) AS pct_of_total_revenue
FROM olist_raw.cleaned_order_items
GROUP BY category
ORDER BY total_revenue DESC;

SELECT * FROM olist_raw.gold_revenue_by_category;

-- COMMAND ----------

-- MAGIC %md ## 4. Export gold tables for Tableau Public
-- MAGIC
-- MAGIC Tableau Public can't connect live to Community Edition, so each gold
-- MAGIC table needs to come out as a CSV. Run the cell below, then for each
-- MAGIC table: click the download icon on the result grid (or use
-- MAGIC `display()` above and download from there) and save into this
-- MAGIC project's `gold_data/` folder.

-- COMMAND ----------

-- MAGIC %python
-- MAGIC for t in ["gold_seller_performance", "gold_category_sell_through",
-- MAGIC           "gold_discount_depth_vs_volume", "gold_delivery_time_by_seller",
-- MAGIC           "gold_revenue_by_category"]:
-- MAGIC     df = spark.table(f"olist_raw.{t}")
-- MAGIC     display(df)  # click the download arrow under this result to save as CSV