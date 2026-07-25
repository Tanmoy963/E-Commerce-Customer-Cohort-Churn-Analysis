USE ecommerce_analytics;

WITH customer_cohorts AS (
    SELECT 
        customer_id,
        DATE_FORMAT(MIN(invoice_date), '%Y-%m-01') AS cohort_month
    FROM raw_transactions
    WHERE customer_id IS NOT NULL AND customer_id != ''
    GROUP BY customer_id
),
monthly_activity AS (
    SELECT DISTINCT
        customer_id,
        DATE_FORMAT(invoice_date, '%Y-%m-01') AS activity_month
    FROM raw_transactions
    WHERE customer_id IS NOT NULL AND customer_id != ''
)
SELECT 
    c.cohort_month,
    PERIOD_DIFF(
        DATE_FORMAT(a.activity_month, '%Y%m'), 
        DATE_FORMAT(c.cohort_month, '%Y%m')
    ) AS cohort_index,
    COUNT(DISTINCT c.customer_id) AS active_customers
FROM customer_cohorts c
JOIN monthly_activity a ON c.customer_id = a.customer_id
GROUP BY c.cohort_month, cohort_index
ORDER BY c.cohort_month, cohort_index;
