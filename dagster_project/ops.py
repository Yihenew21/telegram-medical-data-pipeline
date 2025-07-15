# dagster_project/ops.py
import subprocess
import os
from dagster import op, get_dagster_logger, Out, In, Nothing


@op(out=Out(Nothing))  # This op will produce a 'Nothing' output to signal completion
def scrape_telegram_data():
    """
    Runs the src/scrape.py script to scrape messages and load directly to PostgreSQL.
    """
    logger = get_dagster_logger()
    logger.info("Starting Telegram data scraping...")
    command = ["python", "src/scrape.py"]
    result = subprocess.run(command, capture_output=True, text=True, check=False)

    if result.returncode != 0:
        logger.error(
            f"Telegram scraper failed with exit code {result.returncode}. Stderr: {result.stderr}"
        )
        raise Exception(f"Telegram scraper failed: {result.stderr}")

    logger.info(f"Telegram scraper stdout: {result.stdout}")
    logger.debug(f"Telegram scraper stderr: {result.stderr}")
    logger.info("Telegram data scraping completed successfully.")
    return None


@op(ins={"start": In(Nothing)}, out=Out(Nothing))
# REMOVED 'start' parameter from function signature:
def run_yolo_enrichment():
    """
    Runs the src/yolo_detector.py script to perform object detection on media
    and save detection results as JSON files.
    """
    logger = get_dagster_logger()
    logger.info("Starting YOLO enrichment...")
    command = ["python", "src/yolo_detector.py"]
    result = subprocess.run(command, capture_output=True, text=True, check=False)

    if result.returncode != 0:
        logger.error(
            f"YOLO enrichment failed with exit code {result.returncode}. Stderr: {result.stderr}"
        )
        raise Exception(f"YOLO enrichment failed: {result.stderr}")

    logger.info(f"YOLO enrichment stdout: {result.stdout}")
    logger.debug(f"YOLO enrichment stderr: {result.stderr}")
    logger.info("YOLO enrichment completed successfully.")
    return None


@op(ins={"start": In(Nothing)}, out=Out(Nothing))
# REMOVED 'start' parameter from function signature:
def load_raw_to_postgres():
    """
    Runs the src/load_raw_data.py script to load raw YOLO detection JSON files into raw.yolo_detections in Postgres.
    """
    logger = get_dagster_logger()
    logger.info("Starting raw data loading to Postgres...")
    command = ["python", "src/load_raw_data.py"]
    result = subprocess.run(command, capture_output=True, text=True, check=False)

    if result.returncode != 0:
        logger.error(
            f"Raw data loading failed with exit code {result.returncode}. Stderr: {result.stderr}"
        )
        raise Exception(f"Raw data loading failed: {result.stderr}")

    logger.info(f"Raw data loading stdout: {result.stdout}")
    logger.debug(f"Raw data loading stderr: {result.stderr}")
    logger.info("Raw data loading to Postgres completed successfully.")
    return None


@op(ins={"start": In(Nothing)})
# REMOVED 'start' parameter from function signature:
def run_dbt_transformations():
    """
    Runs dbt to build all models, transforming data from the raw schema to public_analytics.
    """
    logger = get_dagster_logger()
    logger.info("Starting dbt transformations...")
    dbt_project_dir = "./telegram_dbt_project"
    if not os.path.exists(dbt_project_dir):
        logger.error(f"dbt project directory not found at: {dbt_project_dir}")
        raise Exception(f"dbt project directory not found at: {dbt_project_dir}")

    command = ["dbt", "build", "--project-dir", dbt_project_dir]
    env_vars = {**os.environ, "DBT_PROFILES_DIR": "."}
    result = subprocess.run(
        command, capture_output=True, text=True, check=False, env=env_vars
    )

    if result.returncode != 0:
        logger.error(f"dbt transformations failed with exit code {result.returncode}.")
        logger.error(f"dbt stdout: {result.stdout}")
        logger.error(f"dbt stderr: {result.stderr}")
        raise Exception(f"dbt transformations failed. See logs for details.")

    logger.info(f"dbt stdout: {result.stdout}")
    logger.debug(f"dbt stderr: {result.stderr}")
    logger.info("dbt transformations completed successfully.")
