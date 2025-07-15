# dagster_project/schedules.py
from dagster import schedule
from .jobs import telegram_etl_pipeline


@schedule(
    cron_schedule="0 0 * * *",  # This cron string means "run daily at midnight UTC"
    job=telegram_etl_pipeline,
    execution_timezone="UTC",  # Important for scheduling. You can set it to "Africa/Nairobi" for EAT.
)
def daily_telegram_etl_schedule(context):
    """
    A daily schedule for the Telegram ETL pipeline.
    """
    # You can return config here if your job needs dynamic configuration based on the schedule.
    # For a simple daily run without specific config, return an empty dictionary.
    return {}
