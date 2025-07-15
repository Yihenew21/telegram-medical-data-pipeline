-- telegram_dbt_project/models/staging/stg_yolo_detections.sql

WITH raw_yolo_data AS (
    SELECT
        detection_data AS full_json_record -- Now select from the JSONB column
    FROM {{ source('raw', 'yolo_detections') }} -- Corrected source table name
),

flattened_detections AS (
    SELECT
        CAST(detection ->> 'message_id' AS INTEGER) AS message_id,
        detection ->> 'detected_object_class' AS detected_object_class,
        CAST(detection ->> 'confidence_score' AS NUMERIC) AS confidence_score,
        CAST(detection ->> 'detection_timestamp' AS TIMESTAMP) AS detection_timestamp,
        (detection ->> 'box_top_left_x')::NUMERIC AS box_top_left_x,
        (detection ->> 'box_top_left_y')::NUMERIC AS box_top_left_y,
        (detection ->> 'box_width')::NUMERIC AS box_width,
        (detection ->> 'box_height')::NUMERIC AS box_height,

        -- Manual MD5 hashing for surrogate key
        MD5(
            COALESCE(detection ->> 'message_id', '') ||
            COALESCE(detection ->> 'detected_object_class', '') ||
            COALESCE(CAST(detection ->> 'confidence_score' AS TEXT), '') ||
            COALESCE(CAST(detection ->> 'detection_timestamp' AS TEXT), '')
        ) AS yolo_detection_key
    FROM
        raw_yolo_data,
        LATERAL jsonb_array_elements(full_json_record) AS detection
)

SELECT * FROM flattened_detections