# Learning Log #2: I asked AI to write SQL. Then I checked it.

**Status:** in progress

## The idea

AI writes SQL in seconds, and it usually runs without errors. But "it runs" is not the same as "the number is right". In this log I ask AI one ordinary business question about a public e-commerce dataset, run its SQL, and then work out the same numbers myself in Excel to see whether they match.

**The business question** (asked the way a manager would ask it):

> What was our revenue and average order value per month in 2017?

This looks simple, but it hides the decisions an analyst has to make: what counts as revenue (product price only, or with shipping?), which orders count (cancelled ones?), which date (purchase or delivery?), and how to join tables without counting an order twice.

## Data

Olist Brazilian E-Commerce Public Dataset (about 100,000 orders, 2016 to 2018), the same data as my [E-Commerce Pricing and Partner Analytics](../../E-Commerce%20Pricing%20and%20Partner%20Analytics%20%28SQL%2C%20Tableau%29/) project. Three of its tables are used here; see [data/](data/).

## Steps

| # | Step | Who | Output |
|---|---|---|---|
| 1 | Give AI the question and the table layouts, nothing else ([prompt.md](prompt.md)) | Me | `ai_answer.sql` + a screenshot of the chat |
| 2 | Run AI's SQL as it is | Me | AI's 12 monthly numbers |
| 3 | Work out the same numbers in Excel, step by step ([excel_check.md](excel_check.md)) | Me | My 12 monthly numbers |
| 4 | Compare month by month and find out why any differ | Me | The "catch" |
| 5 | Note the assumptions AI made without asking | Me | List of assumptions |
| 6 | Write the log and the LinkedIn post | Me | Learning Log #2 |

## Results

*To be filled in after steps 2 to 5.*

| Month | AI's revenue | My revenue | Difference | Why |
|---|---:|---:|---:|---|
| 2017-01 | | | | |

**Assumptions AI made without asking:**

-

**What I'd tell someone else:**

-
