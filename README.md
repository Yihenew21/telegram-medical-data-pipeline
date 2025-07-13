# Telegram Medical Data Pipline

This project aims to build a comprehensive data engineering pipeline to extract, transform, and analyze Telegram message data, focusing on creating a structured data product for analytical purposes. The pipeline leverages various modern data tools including Git for version control, Docker for containerization, Telethon for data extraction, PostgreSQL as a data warehouse, dbt for data transformation, YOLO for image object detection, FastAPI for API exposure, and Dagster for orchestration.

## Table of Contents

- [Telegram Medical Data Pipline](#telegram-medical-data-pipline)
  - [Table of Contents](#table-of-contents)
  - [Project Overview](#project-overview)
  - [Architecture](#architecture)
  - [Features](#features)
  - [Current Progress](#current-progress)
  - [Setup and Installation](#setup-and-installation)
    - [Prerequisites](#prerequisites)
    - [Project Setup & Environment Management (Task 0)](#project-setup--environment-management-task-0)
    - [Data Scraping and Collection (Task 1)](#data-scraping-and-collection-task-1)
    - [Data Modeling and Transformation (Task 2)](#data-modeling-and-transformation-task-2)
  - [Running the End-to-End Pipeline](#running-the-end-to-end-pipeline)
  - [Usage](#usage)
  - [Project Structure](#project-structure)
  - [Contributing](#contributing)
  - [License](#license)

## Project Overview

The core objective of this project is to build a robust and reproducible data pipeline that collects raw message data from public Telegram channels, processes it into a clean, structured format, enriches it with insights from image analysis, and exposes it via a high-performance API. This enables downstream analytical applications to consume the data effectively.

## Architecture

The project follows an ELT (Extract, Load, Transform) paradigm:

-   **Extract (E):** Data is extracted from Telegram channels using the `Telethon` library.
-   **Load (L):** Raw data is stored in a data lake (JSON files) and then loaded into a PostgreSQL database.
-   **Transform (T):** Data is transformed and modeled using `dbt` within PostgreSQL into a star schema for analytical querying.
-   **Enrichment:** Image data within messages is processed using YOLO for object detection.
-   **Serve:** Cleaned and enriched data is exposed via a `FastAPI` application.
-   **Orchestration:** The entire pipeline is managed and scheduled using `Dagster`.

## Features

* **Version Control:** Git for tracking all code changes.
* **Containerization:** Docker and Docker Compose for consistent and isolated environments for the application and database.
* **Secure Configuration:** `.env` files and `python-dotenv` for managing sensitive credentials.
* **Telegram Data Scraping:** `Telethon` for extracting messages and media information from public Telegram channels.
* **Data Lake Storage:** Raw data stored in a partitioned JSON format.
* **Relational Data Warehouse:** PostgreSQL for structured data storage.
* **Data Transformation:** `dbt` for defining and executing SQL-based data transformations, creating a dimensional star schema (`dim_channels`, `dim_dates`, `fct_messages`).
* **Data Quality:** `dbt` built-in and custom tests to ensure data integrity and business rule adherence.
* **Automated Documentation:** `dbt docs` for generating comprehensive project documentation.
* **Data Enrichment (In Progress):** Integration with YOLO for object detection in images.
* **Analytical API (Planned):** `FastAPI` for exposing analytical endpoints.
* **Pipeline Orchestration (Planned):** `Dagster` for scheduling and monitoring the data pipeline.

## Current Progress

The following tasks have been successfully completed:

* **Task 0: Project Setup & Environment Management**
    * Git repository initialized.
    * `requirements.txt` created and dependencies managed with a virtual environment.
    * `Dockerfile` and `docker-compose.yml` set up for application containerization.
    * `.env` file created for secure secret storage and added to `.gitignore`.
    * `python-dotenv` configured to load environment variables into the application.
* **Task 1: Data Scraping and Collection (Extract & Load)**
    * `Telethon` integrated for scraping Telegram messages.
    * `src/scrape.py` developed to extract messages and store them as JSON files in a partitioned data lake (`data/raw/telegram_messages`).
    * Initial `Telethon` authentication handled and session files added to `.gitignore`.
    * Robust logging implemented for scraping activities.
* **Task 2: Data Modeling and Transformation (Transform)**
    * `psycopg2-binary` added for PostgreSQL connectivity.
    * `src/load_raw_data.py` developed to load raw JSON data from the data lake into the `raw.telegram_messages` table in PostgreSQL, utilizing the `JSONB` data type.
    * Project configured to connect to a local PostgreSQL instance.
    * `dbt` environment set up, `dbt-postgres` installed, and `dbt init` executed.
    * `profiles.yml` configured to connect `dbt` to the local PostgreSQL database using environment variables and Docker volume mounts.
    * `dbt_project.yml` configured for the `telegram_project` profile and default `analytics` schema.
    * `dbt debug` successfully verified the database connection.
    * **dbt Models Developed:**
        * **Staging Layer:** `stg_telegram_messages` created for initial cleaning, type casting, and extraction from raw JSONB data.
        * **Data Mart Layer (Dimensional Star Schema):**
            * `dim_channels`: Dimension table with `channel_pk` as a surrogate key.
            * `dim_dates`: Standard date dimension table.
            * `fct_messages`: Fact table with core message metrics and foreign keys to `dim_channels` and `dim_dates`.
    * **Testing and Documentation Implemented:**
        * Built-in `unique`, `not_null`, and `relationships` tests applied to dbt models.
        * Custom data test (`no_negative_views.sql`) created to ensure `views_count` is non-negative.
        * Descriptions added to sources, models, and columns for documentation.
        * `dbt docs generate` and `dbt docs serve` configured and executed for local documentation Browse.

The project is currently working on **Task 3: Data Enrichment with Object Detection (YOLO)**.

## Setup and Installation

### Prerequisites

* Git
* Docker and Docker Compose
* Python 3.8+
* Poetry (recommended for Python dependency management, though `venv` and `pip` are also used)
* A running PostgreSQL instance (local or remote). For development, we connect to a local PostgreSQL instance for easier debugging and management, but a containerized database could be added for production environments.

### Project Setup & Environment Management (Task 0)

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd telegram_data_product
    ```
2.  **Initialize Git:** (Already done if cloned)
    ```bash
    git init
    ```
3.  **Create and activate Python virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
4.  **Create `requirements.txt` and install dependencies:**
    ```bash
    # Create requirements.txt manually or using pip freeze > requirements.txt
    pip install python-dotenv telethon psycopg2-binary dbt-postgres
    pip freeze > requirements.txt
    ```
    Then, install:
    ```bash
    pip install -r requirements.txt
    ```
5.  **Create `.env` file:**
    Create a file named `.env` in the project root and populate it with your credentials:
    ```
    TELEGRAM_API_ID=YOUR_API_ID
    TELEGRAM_API_HASH=YOUR_API_HASH
    PHONE_NUMBER=YOUR_PHONE_NUMBER (e.g., +1234567890)

    POSTGRES_DB=telegram_warehouse
    POSTGRES_USER=telegram_user
    POSTGRES_PASSWORD=your_postgres_password
    POSTGRES_HOST=localhost # or your PostgreSQL host
    POSTGRES_PORT=5432
    ```
6.  **Add `.env` to `.gitignore`:**
    Ensure your `.gitignore` file contains:
    ```
    .env
    venv/
    data/raw/
    telegram_scraper_session.session*
    ```
7.  **Create `Dockerfile`:**
    ```dockerfile
    # Example Dockerfile content (as described in your report.md)
    FROM python:3.9-slim-buster

    WORKDIR /app

    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt

    COPY . .

    # You might want to specify an entrypoint or command if not using docker exec
    # ENTRYPOINT ["python"]
    # CMD ["src/scrape.py"]
    ```
8.  **Create `docker-compose.yml`:**
    ```yaml
    # Example docker-compose.yml (without a db service, as per your report.md)
    version: '3.8'
    services:
      app:
        build: .
        restart: always
        env_file:
          - .env
        volumes:
          - .:/app
          - ~/.dbt:/root/.dbt # Mount host's dbt profiles
          - ./data:/app/data
        ports:
          - "8080:8080" # For dbt docs serve
        # If you were to add a db service, it would look something like this:
        # depends_on:
        #   - db
    # If you were to add a db service, you'd also define a volume here:
    # volumes:
    #   postgres_data:
    ```

### Data Scraping and Collection (Task 1)

1.  **Update `requirements.txt` with `telethon` and install:**
    ```bash
    pip install telethon
    pip freeze > requirements.txt
    ```
2.  **Run initial `scrape.py` locally for Telethon authentication:**
    ```bash
    python src/scrape.py
    ```
    Follow the prompts for your phone number, verification code, and 2FA password. This will generate a `.session` file.
3.  **Add `telegram_scraper_session.session*` to `.gitignore`:** (See Task 0, step 6)
4.  **Execute scraping within Docker:**
    ```bash
    docker-compose up --build -d app # Start the app container
    docker exec telegram_app python src/scrape.py
    ```
    Raw data will be stored in `data/raw/telegram_messages/`.

### Data Modeling and Transformation (Task 2)

1.  **Ensure Local PostgreSQL is running:**
    Create the database and user as specified in your `.env` file.
    ```sql
    CREATE DATABASE telegram_warehouse;
    CREATE USER telegram_user WITH PASSWORD 'your_postgres_password';
    GRANT ALL PRIVILEGES ON DATABASE telegram_warehouse TO telegram_user;
    ```
2.  **Update `requirements.txt` with `psycopg2-binary` and `dbt-postgres` and install:**
    ```bash
    pip install psycopg2-binary dbt-postgres
    pip freeze > requirements.txt
    ```
3.  **Load Raw Data to PostgreSQL:**
    ```bash
    docker exec telegram_app python src/load_raw_data.py
    ```
    This will create the `raw.telegram_messages` table and load your scraped data.
4.  **Initialize `dbt` project:**
    ```bash
    dbt init telegram_dbt_project
    ```
    *Choose `postgres` as the database.*
5.  **Configure `profiles.yml`:**
    Create/edit `~/.dbt/profiles.yml` on your **host machine**:
    ```yaml
    telegram_project:
      target: dev
      outputs:
        dev:
          type: postgres
          host: host.docker.internal # This allows Docker container to connect to host's localhost
          port: "{{ env_var('POSTGRES_PORT') }}"
          user: "{{ env_var('POSTGRES_USER') }}"
          password: "{{ env_var('POSTGRES_PASSWORD') }}"
          dbname: "{{ env_var('POSTGRES_DB') }}"
          schema: analytics
    ```
6.  **Mount `~/.dbt` in `docker-compose.yml`:**
    Ensure your `app` service in `docker-compose.yml` has the following volume mount:
    ```yaml
        volumes:
          - .:/app
          - ~/.dbt:/root/.dbt # Mount host's dbt profiles
          - ./data:/app/data
    ```
7.  **Update `dbt_project.yml`:**
    In `telegram_dbt_project/dbt_project.yml`, ensure:
    ```yaml
    name: 'telegram_dbt_project'
    version: '1.0.0'
    config-version: 2

    profile: 'telegram_project'

    model-paths: ["models"]
    analysis-paths: ["analyses"]
    test-paths: ["tests"]
    seed-paths: ["seeds"]
    macro-paths: ["macros"]
    snapshot-paths: ["snapshots"]

    target-path: "target"  # directory to write compiled SQL to
    clean-targets:         # directories to clean when `dbt clean` is run
        - "target"
        - "dbt_packages"
        - "logs"
    

    models:
      telegram_dbt_project:
        +materialized: view
        +schema: analytics
    ```
8.  **Test dbt connection:**
    ```bash
    docker-compose up --build -d app
    docker exec telegram_app dbt debug --project-dir telegram_dbt_project
    ```
9.  **Run dbt models:**
    ```bash
    docker exec telegram_app dbt run --project-dir telegram_dbt_project
    ```
10. **Run dbt tests:**
    ```bash
    docker exec telegram_app dbt test --project-dir telegram_dbt_project
    ```
11. **Generate and serve dbt documentation:**
    Modify `docker-compose.yml` to expose port 8080 on the `app` service for dbt docs:
    ```yaml
        ports:
          - "8080:8080" # For dbt docs serve
    ```
    Then, run:
    ```bash
    docker exec telegram_app dbt docs generate --project-dir telegram_dbt_project
    docker exec telegram_app dbt docs serve --host 0.0.0.0 --port 8080 --project-dir telegram_dbt_project
    ```
    Access documentation at `http://localhost:8080`.

## Running the End-to-End Pipeline

To run the complete data pipeline from scraping to transformation, follow these steps:

1.  **Start Docker services:**
    ```bash
    docker-compose up --build -d
    ```
2.  **Perform initial Telegram authentication (if not already done):**
    ```bash
    docker exec telegram_app python src/scrape.py # Follow prompts for auth
    ```
3.  **Execute the full pipeline sequence:**
    ```bash
    # Step 1: Scrape raw data
    docker exec telegram_app python src/scrape.py

    # Step 2: Load raw data to PostgreSQL
    docker exec telegram_app python src/load_raw_data.py

    # Step 3: Run dbt transformations (staging and marts)
    docker exec telegram_app dbt run --project-dir telegram_dbt_project

    # Step 4: Run dbt tests to ensure data quality
    docker exec telegram_app dbt test --project-dir telegram_dbt_project
    ```
4.  **Access dbt documentation:**
    ```bash
    docker exec telegram_app dbt docs generate --project-dir telegram_dbt_project
    docker exec telegram_app dbt docs serve --host 0.0.0.0 --port 8080 --project-dir telegram_dbt_project
    ```
    Open your browser to `http://localhost:8080`.

*(Note: Integration with YOLO and Dagster will further automate this flow once Task 3, 4, and 5 are complete.)*

## Usage

Once the setup is complete, you can:

* **Scrape data:** Run `docker exec telegram_app python src/scrape.py` to collect new Telegram messages.
* **Load raw data:** Run `docker exec telegram_app python src/load_raw_data.py` to ingest new raw data into PostgreSQL.
* **Transform data:** Run `docker exec telegram_app dbt run --project-dir telegram_dbt_project` to update your analytical models.
* **Check data quality:** Run `docker exec telegram_app dbt test --project-dir telegram_dbt_project` to validate data.
* **Browse documentation:** Access `http://localhost:8080` after running `dbt docs serve`.


## Project Structure

```bash
├── .env                  # Environment variables (IGNORED by Git)
├── .gitignore            # Specifies intentionally untracked files
├── Dockerfile            # Instructions for building the Python application image
├── README.md             # Project documentation
├── requirements.txt      # Python package dependencies
├── docker-compose.yml    # Defines multi-container Docker application
├── data/
│   └── raw/
│       └── telegram_messages/ # Raw JSON data lake (e.g., YYYY-MM-DD/channel_name.json)
├── src/
│   ├── init.py
│   ├── config.py         # Script to test environment variable loading
│   ├── scrape.py         # Telegram data scraping script
│   └── load_raw_data.py  # Script to load raw data from data lake to PostgreSQL
└── telegram_dbt_project/ # dbt project directory
    ├── models/           # dbt models
    │   ├── marts/        # Data Mart layer (star schema)
    │   │   ├── dim_channels.sql
    │   │   ├── dim_dates.sql
    │   │   └── fct_messages.sql
    │   └── staging/      # Staging layer
    │       ├── sources.yml
    │       └── stg_telegram_messages.sql
    ├── tests/            # dbt tests
    │   └── no_negative_views.sql # Custom data test
    └── dbt_project.yml   # dbt project configuration
