-- models/marts/fct_messages.sql

SELECT
    s.message_id,
    s.message_timestamp_utc,
    s.message_text,
    s.views_count,
    s.forwards_count,
    s.replies_count,
    s.has_media,
    s.media_type,
    s.media_file_name,
    s.media_mime_type,
    s.media_file_size,
    s.is_photo,
    s.is_document,
    -- Foreign Keys to Dimension Tables
    dc.channel_pk,
    dd.date_pk
FROM
    {{ ref('stg_telegram_messages') }} s
LEFT JOIN
    {{ ref('dim_channels') }} dc ON s.channel_username = dc.channel_username
LEFT JOIN
    {{ ref('dim_dates') }} dd ON s.scraped_date = dd.date_pk -- Assuming scraped_date is a DATE type in stg model