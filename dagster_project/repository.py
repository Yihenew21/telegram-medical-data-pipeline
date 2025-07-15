# dagster_project/repository.py
from dagster import repository
from .jobs import telegram_etl_pipeline
from .schedules import daily_telegram_etl_schedule


@repository
def telegram_data_product_repository():
    """
    The central repository for all jobs and schedules in the Telegram data product.
    """
    return [
        telegram_etl_pipeline,
        daily_telegram_etl_schedule,
    ]
