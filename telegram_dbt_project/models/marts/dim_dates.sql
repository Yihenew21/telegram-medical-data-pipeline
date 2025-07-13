-- models/marts/dim_dates.sql

SELECT
    DISTINCT scraped_date AS date_pk,
    scraped_date AS full_date,
    EXTRACT(DAY FROM scraped_date) AS day_of_month,
    EXTRACT(MONTH FROM scraped_date) AS month,
    TO_CHAR(scraped_date, 'Month') AS month_name,
    EXTRACT(YEAR FROM scraped_date) AS year,
    EXTRACT(QUARTER FROM scraped_date) AS quarter,
    EXTRACT(DOW FROM scraped_date) AS day_of_week, -- Sunday = 0, Saturday = 6
    TO_CHAR(scraped_date, 'Day') AS day_name,
    CASE WHEN EXTRACT(DOW FROM scraped_date) IN (0, 6) THEN TRUE ELSE FALSE END AS is_weekend
FROM
    {{ ref('stg_telegram_messages') }}
ORDER BY
    scraped_date