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
    scraped_data_signal = scrape_telegram_data()
    yolo_enrichment_signal = run_yolo_enrichment(start=scraped_data_signal)
    loaded_raw_signal = load_raw_to_postgres(start=yolo_enrichment_signal)
    run_dbt_transformations(start=loaded_raw_signal)
