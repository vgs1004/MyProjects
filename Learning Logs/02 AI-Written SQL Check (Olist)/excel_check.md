# Checking the numbers in Excel

Goal: work out revenue and average order value per month for 2017 **without SQL**, so the result does not depend on how the query was written.

Decide the definitions first and write them down. Suggested:

- **Revenue** = sum of `price` + `freight_value` from order_items (what the customer was charged for products and shipping)
- **Orders counted** = all except `order_status` = canceled or unavailable
- **Month** = month of `order_purchase_timestamp`
- **Average order value** = revenue ÷ number of distinct orders

## Steps

1. **Open** `olist_order_items_dataset.csv` in Excel (about 112,000 rows). Format it as a table: Ctrl+T.
2. **Bring in the order date and status.** Open `olist_orders_dataset.csv` in the same workbook as a second sheet. In the items sheet add two columns:
   - `purchase` : `=XLOOKUP([@order_id], orders[order_id], orders[order_purchase_timestamp])`
   - `status` : `=XLOOKUP([@order_id], orders[order_id], orders[order_status])`
3. **Add helper columns:**
   - `month` : `=TEXT([@purchase], "yyyy-mm")`
   - `line_total` : `=[@price] + [@freight_value]`
4. **Pivot table** (Insert → PivotTable, tick "Add this data to the Data Model" so you can count distinct orders):
   - Filters: `status` (untick canceled and unavailable)
   - Rows: `month` (keep only 2017-01 to 2017-12)
   - Values: Sum of `line_total`, and Distinct Count of `order_id`
5. **Average order value** = sum of line_total ÷ distinct count of orders, as a column next to the pivot.
6. **Write the 12 months** into the Results table in the README.

## Things to watch

- If the date column comes in as text, use Data → Text to Columns, or `=DATEVALUE(LEFT([@purchase],10))`.
- Count **orders**, not rows: one order can have several items.
- Save the workbook as `excel_check.xlsx` in this folder.
