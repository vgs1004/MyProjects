# Tableau Build Guide

How the dashboard in `E-Commerce Partner and Pricing Analytics.twbx` was
built. Tested in Tableau Public (2025+ desktop app).

## 1. Data sources

Each gold CSV is its own data source. Do not put several CSVs on one
Data Source canvas: the tables share no join keys, and Tableau will show
"Unrelated Tables" errors.

For each file: **Data > New Data Source > Text file > pick the CSV > Open.**

Used: gold_category_sell_through, gold_seller_performance,
gold_discount_depth_vs_volume, gold_delivery_time_by_seller.

## 2. Sheets

### Top 15 Categories by Revenue (gold_category_sell_through)
- Rows: Category. Columns: SUM(Total Revenue). Mark: Bar.
- Filter: Category > Top 15 by SUM(Total Revenue). Sort descending.

### Partner Performance (gold_seller_performance)
- Columns: SUM(Total Revenue). Rows: AVG(On Time Rate), formatted as %.
- Detail: Seller Id (one dot per seller; without it Tableau shows one dot).
- Size: Total Orders. Color: AVG(Avg Delivery Days), red-green reversed.
- Filter: Total Orders at least 10. Mark: Circle.

### Pricing Dynamics (gold_discount_depth_vs_volume)
Calculated fields:
```
Price Index = [Avg Price Paid] / {FIXED [Category] : AVG([Avg Price Paid])}

Price Band =
IF [Price Index] < 0.5 THEN "1. Under 50%"
ELSEIF [Price Index] < 0.8 THEN "2. 50-80%"
ELSEIF [Price Index] <= 1.2 THEN "3. 80-120%"
ELSEIF [Price Index] <= 2 THEN "4. 120-200%"
ELSE "5. Over 200%"
END
```
- Price Band must be a dimension (right-click > Convert to Dimension).
- Columns: Price Band. Rows: AVG(Units Sold). Label: AVG(Units Sold).

### Delivery Time (gold_delivery_time_by_seller)
Calculated field: `Seller = LEFT([Seller Id], 8) + " (" + [Seller State] + ")"`
- Rows: Seller. Columns: AVG(Avg Delivery Days). Mark: Bar.
- Filter: Seller > Top 15 by AVG(Avg Delivery Days). Sort descending.
- Color: AVG(On Time Rate), red-green (low = red).
- To add a minimum order count, Order Count must be a dimension filter
  added to context; otherwise the Top 15 is computed first and the order
  filter removes most of the bars.

### KPI Tiles
One text sheet using data blending across sources: SUM(Total Revenue) and
CNTD(Seller Id) from gold_seller_performance, AVG(On Time Rate) and
AVG(Avg Delivery Days) from gold_delivery_time_by_seller.

## 3. Dashboard
- Size: Fixed, 1400 x 1000.
- Layout: 2 x 2 grid of charts, KPI tiles and legends on the right,
  source and methodology note at the bottom.

## 4. Publish
File > Save to Tableau Public As. Then File > Save As > Tableau Packaged
Workbook (.twbx) for the copy kept in this repo.
