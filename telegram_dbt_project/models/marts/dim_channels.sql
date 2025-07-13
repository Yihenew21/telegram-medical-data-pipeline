-- models/marts/dim_channels.sql

SELECT
    {{ dbt_utils.generate_surrogate_key(['channel_username']) }} AS channel_pk,
    channel_username
FROM
    {{ ref('stg_telegram_messages') }}
GROUP BY
    channel_username