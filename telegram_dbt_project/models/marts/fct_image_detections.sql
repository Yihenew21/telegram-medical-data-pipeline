-- telegram_dbt_project/models/marts/fct_image_detections.sql

{{ config(
    materialized='table', 
    unique_key='yolo_detection_key'
) }}

SELECT
    stg.yolo_detection_key,
    stg.message_id,
    stg.detected_object_class,
    stg.confidence_score,
    stg.detection_timestamp,
    stg.box_top_left_x,
    stg.box_top_left_y,
    stg.box_width,
    stg.box_height,
    CURRENT_TIMESTAMP AS dbt_inserted_at

FROM
    {{ ref('stg_yolo_detections') }} stg