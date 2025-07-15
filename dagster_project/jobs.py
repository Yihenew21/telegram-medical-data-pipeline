# dagster_project/jobs.py
from dagster import job
from .ops import (
    scrape_telegram_data,
    run_yolo_enrichment,
    load_raw_to_postgres,
    run_dbt_transformations,
)


@job
def telegram_etl_pipeline():
    """
    A Dagster job that orchestrates the end-to-end Telegram data ETL pipeline.
    """
    # 1. Scrape Telegram data. This populates raw.telegram_messages directly.
    scraped_data_status = scrape_telegram_data()

    # 2. Run YOLO enrichment. This processes scraped media and saves YOLO detections as JSON files.
    # It implicitly depends on the scraping having provided the messages.
    yolo_enrichment_status = run_yolo_enrichment(start_after=[scraped_data_status])

    # 3. Load raw YOLO detection files into raw.yolo_detections in Postgres.
    # This explicitly depends on the YOLO enrichment generating the files.
    loaded_raw_status = load_raw_to_postgres(start_after=[yolo_enrichment_status])

    # 4. Run dbt transformations. This builds the data marts in public_analytics.
    # It depends on all necessary raw data being loaded into Postgres.
    run_dbt_transformations(start_after=[loaded_raw_status])
