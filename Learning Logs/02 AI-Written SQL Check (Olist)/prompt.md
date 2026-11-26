# The prompt

Paste this into a **new** chat with the AI assistant, exactly as written. Do not add hints about joins, cancelled orders or shipping costs: the point is to see what the AI decides on its own.

---

I have three tables from an e-commerce company in a SQL database.

**orders**: order_id, customer_id, order_status, order_purchase_timestamp, order_approved_at, order_delivered_carrier_date, order_delivered_customer_date, order_estimated_delivery_date

**order_items**: order_id, order_item_id, product_id, seller_id, shipping_limit_date, price, freight_value

**order_payments**: order_id, payment_sequential, payment_type, payment_installments, payment_value

Write a SQL query that shows our revenue and average order value per month for 2017.

---

## Afterwards

1. Copy the AI's SQL into `ai_answer.sql` in this folder.
2. Take a screenshot of the chat (the question and the start of the answer) for the post.
3. Note which AI tool and model you used, and the date.
