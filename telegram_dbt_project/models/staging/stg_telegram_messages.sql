-- models/staging/stg_telegram_messages.sql

SELECT
    message_id,
    channel_username,
    scraped_date,
    message_data ->> 'date' AS message_timestamp_utc,
    message_data ->> 'text' AS message_text,
    -- Add COALESCE to handle potential NULLs for counts
    COALESCE((message_data ->> 'views')::INT, 0) AS views_count,
    COALESCE((message_data ->> 'forwards')::INT, 0) AS forwards_count,
    COALESCE((message_data ->> 'replies_count')::INT, 0) AS replies_count,
    (message_data ->> 'has_media')::BOOLEAN AS has_media,
    message_data ->> 'media_type' AS media_type,
    message_data ->> 'file_name' AS media_file_name,
    message_data ->> 'mime_type' AS media_mime_type,
    COALESCE((message_data ->> 'file_size')::BIGINT, 0) AS media_file_size, -- Also apply to file_size
    (message_data ->> 'is_photo')::BOOLEAN AS is_photo,
    (message_data ->> 'is_document')::BOOLEAN AS is_document,
    inserted_at
FROM
    {{ source('raw', 'telegram_messages') }}
-- Add any basic filtering or deduplication if necessary at this stage.
-- For example, if message_id + channel_username is not inherently unique in source
-- SELECT *, ROW_NUMBER() OVER(PARTITION BY message_id, channel_username ORDER BY inserted_at DESC) as rn
-- FROM {{ source('raw', 'telegram_messages') }}
-- QUALIFY rn = 1