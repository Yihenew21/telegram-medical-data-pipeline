-- tests/no_negative_views.sql
SELECT
    message_id,
    views_count
FROM
    {{ ref('fct_messages') }}
WHERE
    views_count < 0