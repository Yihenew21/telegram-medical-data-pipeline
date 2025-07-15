## Task 0: Project Setup & Environment Management

**Overall Objective:** To establish a robust, reproducible, and securely configured development environment for the data engineering project, leveraging Git, Docker, and environment variables.

### 0.1 Initialize Git Repository

**Objective:** To establish version control for the project.
**Implementation:**
1.  Created the root project directory `telegram_data_product`.
2.  Initialized Git using `git init`.
3.  Performed an initial commit.
**Outcome:** Git repository configured, ready for tracking changes.

### 0.2 Create `requirements.txt`

**Objective:** To manage Python package dependencies for reproducibility.
**Implementation:**
1.  Created `requirements.txt` in the root.
2.  Added `python-dotenv` as the initial dependency.
3.  Set up and activated a Python virtual environment (`venv`).
4.  Installed dependencies using `pip install -r requirements.txt`.
**Outcome:** Project dependencies are explicitly defined and managed within an isolated virtual environment.

### 0.3 Create `Dockerfile` and `docker-compose.yml`

**Objective:** To containerize the application and its services (Python app, PostgreSQL DB) for consistent environment management.
**Implementation:**
1.  Created `Dockerfile` with instructions to build the Python application image (base image, working directory, copying `requirements.txt`, installing dependencies, copying application code).
2.  Created `docker-compose.yml` to orchestrate multi-container services, defining:
    * An `app` service for the Python application, building from `Dockerfile`, mounting volumes for code and data persistence, mapping ports, loading `.env` variables, and depending on the `db` service.
    * A `db` service for PostgreSQL, using `postgres:13` image, configuring environment variables from `.env`, mapping ports, and persisting data via a named volume (`pg_data`).
    * A custom Docker network (`telegram_network`) for inter-service communication.
**Outcome:** Project is containerized, enabling easy spin-up of the application and database environment.

### 0.4 Create `.env` file for Secrets

**Objective:** To securely store sensitive credentials and configuration settings.
**Implementation:**
1.  Created a `.env` file in the project root.
2.  Populated `.env` with placeholder values for Telegram API credentials (`TELEGRAM_API_ID`, `TELEGRAM_API_HASH`, `PHONE_NUMBER`) and PostgreSQL database credentials (`POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`).
**Outcome:** Centralized and secure storage for sensitive configuration.

### 0.5 Add `.env` to `.gitignore`

**Objective:** To prevent sensitive information from being committed to the Git repository.
**Implementation:**
1.  Modified (or created) the `.gitignore` file.
2.  Added `.env`, `venv/`, `data/raw/`, and other common development-related files/directories to `.gitignore`.
**Outcome:** Ensured that sensitive data and transient files are excluded from version control, enhancing security and repository cleanliness.

### 0.6 Use `python-dotenv` to Load Secrets

**Objective:** To programmatically load environment variables from the `.env` file into the Python application.
**Implementation:**
1.  Created a test script `src/config.py`.
2.  Used `from dotenv import load_dotenv` and `load_dotenv()` to load variables.
3.  Accessed variables using `os.getenv()`.
4.  Tested variable loading both locally (after activating virtual environment) and inside the Docker `app` container using `docker exec telegram_app python src/config.py`.
**Outcome:** Verified that environment variables are correctly loaded and accessible within the Python application, ensuring secure configuration management.

---

**Consolidated Git Commit for Task 0:**
A single commit was made after completing all sub-tasks in Task 0, reflecting a complete foundational setup:
`git commit -m "feat: Initial project setup with Docker, .env, and basic structure"`




## Task 1: Data Scraping and Collection (Extract & Load)

### 1.1 Setting up Telethon and Initial Scraping Script

**Objective:** To extract raw message data from specified public Telegram channels using Telethon and store it in a partitioned Data Lake structure, along with robust logging.

**Implementation Steps:**
1.  **Dependency Update:** Added `telethon` to `requirements.txt` and installed it via `pip install -r requirements.txt` within the Python virtual environment.
2.  **API Credential Verification:** Confirmed `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`, and `PHONE_NUMBER` are correctly configured in the `.env` file.
3.  **`scrape.py` Development:**
    * Created `src/scrape.py` to house the scraping logic.
    * Implemented `python-dotenv` for secure loading of API credentials.
    * Configured `logging` to output to both console and a `scrape.log` file.
    * Defined `RAW_DATA_DIR` to point to `data/raw/telegram_messages` for data lake storage.
    * Created an asynchronous function `scrape_channel_data` to:
        * Connect to a specified Telegram channel.
        * Iterate through messages (with a `limit`).
        * Extract key message attributes (ID, date, text, views, media info).
        * Identify media type (photo, document) and extract relevant file metadata.
        * Save the collected messages as JSON files, partitioned by date (`YYYY-MM-DD`) and channel name (`channel_name.json`), into the `data/raw/telegram_messages` directory.
    * Implemented a `main` asynchronous function to:
        * Initialize and connect the `Telethon` client.
        * Handle initial user authorization (prompting for code/password if needed).
        * Orchestrate concurrent scraping of multiple `TARGET_CHANNELS`.
4.  **Initial Authentication & `gitignore` update:** Ran `python src/scrape.py` locally once to perform the initial `Telethon` authentication and generate the `telegram_scraper_session.session` file. Subsequently, added `telegram_scraper_session.session*` to `.gitignore`.
5.  **Dockerized Execution:** Tested the script's execution within the Docker `app` container using `docker-compose up --build -d` and `docker exec telegram_app python src/scrape.py`.

**Key Concepts Applied:**
* **Data Extraction (E in ELT):** Utilizing `Telethon` to programmatically pull data from an external source (Telegram API).
* **Data Lake (L in ELT):** Storing raw, unstructured/semi-structured data in its native JSON format.
* **Data Partitioning:** Organizing data by `YYYY-MM-DD` and `channel_name` for optimized storage, retrieval, and incremental processing.
* **Asynchronous Programming:** Employing `asyncio` for efficient handling of I/O-bound tasks like API calls, allowing concurrent scraping of multiple channels.
* **Robust Logging:** Implementing detailed logging to monitor script execution, track progress, and facilitate debugging.

**Outcome:**
The `scrape.py` script was successfully developed and executed. Raw Telegram message data, including basic media information, is now being collected and stored in the `data/raw/telegram_messages/{date}/{channel_name}.json` structure within the project's data lake. A `scrape.log` file captures all operational details.


## Task 2: Data Modeling and Transformation (Transform)

### 2.1 Load Raw Data to PostgreSQL

**Objective:** To transfer raw Telegram message data from the Data Lake (JSON files) into a dedicated `raw` schema within the PostgreSQL data warehouse, preserving the original JSON structure.

**Implementation Steps:**
1.  **Dependency Update:** Added `psycopg2-binary` to `requirements.txt` and installed it.
2.  **`load_raw_data.py` Development:**
    * Created `src/load_raw_data.py` to manage the loading process.
    * Configured database connection parameters using environment variables from `.env`.
    * Implemented `get_db_connection()` for robust database connectivity.
    * Developed `create_raw_table()` to:
        * Create a `raw` schema if it doesn't exist.
        * Define the `raw.telegram_messages` table with `message_id`, `channel_username`, `scraped_date`, and a `message_data` column of `JSONB` type to store the complete original JSON message.
        * Added an index for efficient querying.
    * Implemented `load_json_to_postgres()` to:
        * Discover all JSON files within the `data/raw/telegram_messages` directory using `glob`.
        * Extract `scraped_date` and `channel_username` from the file path for each record.
        * Perform an incremental load check: before inserting, verify if a message with the same `message_id` and `channel_username` already exists to prevent duplicates.
        * Insert new messages into `raw.telegram_messages`, storing the entire JSON message in the `message_data` column.
        * Included comprehensive error handling and transaction management (`conn.commit()`, `conn.rollback()`).
    * Configured logging for the loading process to `load_raw_data.log`.
3.  **Execution & Verification:**
    * Ensured Docker `db` and `app` containers were running.
    * Executed the script via `docker exec telegram_app python src/load_raw_data.py`.
    * Verified data ingestion by connecting to the PostgreSQL database (e.g., using `psql`) and querying the `raw.telegram_messages` table.

**Key Concepts Applied:**
* **Load (L in ELT):** The process of moving data from the data lake into the data warehouse.
* **Raw Data Layer:** Creating a schema (`raw`) and table (`telegram_messages`) to hold data in its original, untransformed state within the relational database.
* **`JSONB` Data Type:** Leveraging PostgreSQL's `JSONB` for efficient storage and querying of semi-structured JSON data.
* **Incremental Loading:** Implementing logic to avoid re-inserting existing records, improving efficiency on subsequent runs.
* **Error Handling & Transactions:** Ensuring data integrity and process robustness during data loading.

**Outcome:**
Raw Telegram message data is now successfully loaded from the Data Lake into the `raw.telegram_messages` table in the PostgreSQL data warehouse. This sets the stage for the crucial transformation steps using `dbt`.




### Adjustment for Local PostgreSQL Database

**Objective:** To reconfigure the project to connect to a locally installed PostgreSQL instance instead of a Dockerized database service.

**Implementation Steps:**
1.  **`.env` File Update:**
    * Changed `POSTGRES_HOST` from `db` to `localhost`.
    * Confirmed `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_PORT` match the credentials of the local PostgreSQL setup.
2.  **`docker-compose.yml` Modification:**
    * Removed the entire `db` service definition block.
    * Removed the `pg_data` named volume definition.
    * Removed `depends_on: - db` from the `app` service configuration.
3.  **Local PostgreSQL Setup Verification/Execution:**
    * Ensured the local PostgreSQL server is installed and running.
    * Used `psql` to create the `telegram_warehouse` database and `telegram_user` with the corresponding password, and granted necessary privileges.
4.  **Script Execution:**
    * Rebuilt and ran the `app` container using `docker-compose up --build -d`.
    * Executed `docker exec telegram_app python src/load_raw_data.py` to test the connection and data loading into the local PostgreSQL instance.

**Key Change:** The data pipeline's `Load` step now targets an external, host-managed PostgreSQL database, simplifying the Docker Compose configuration while maintaining separation of concerns.

**Outcome:** The project's `app` container can now successfully connect to and load data into the locally installed PostgreSQL database.


### 2.2 dbt Setup

**Objective:** To integrate dbt into the project by setting up its environment, initializing a dbt project, and configuring its connection to the local PostgreSQL database.

**Implementation Steps:**
1.  **Dependency Addition:** Added `dbt-postgres` to `requirements.txt` and installed it using `pip install -r requirements.txt`.
2.  **dbt Project Initialization:** Executed `dbt init telegram_dbt_project` from the project root to create the dbt project structure, specifying `postgres` as the database type.
3.  **`profiles.yml` Configuration:**
    * Created `profiles.yml` in the host's `~/.dbt/` directory.
    * Configured a profile named `telegram_project` with `type: postgres`.
    * Set `host: host.docker.internal` to enable connection from the Docker container to the local PostgreSQL instance.
    * Utilized `env_var()` functions (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`) to securely retrieve credentials from the container's environment (sourced from `.env`).
    * Set `schema: analytics` as the default target schema for dbt models.
4.  **Docker Compose Volume Mount:** Added `- ~/.dbt:/root/.dbt` to the `volumes` section of the `app` service in `docker-compose.yml`, mounting the host's dbt profiles directory into the container.
5.  **`dbt_project.yml` Update:** Configured `telegram_dbt_project/dbt_project.yml` to use the `telegram_project` profile and set default model materialization to `view` and schema to `analytics`.
6.  **Connection Test:** Executed `docker-compose up --build -d` followed by `docker exec telegram_app dbt debug` to verify successful connection to the PostgreSQL database.

**Key Concepts Applied:**
* **Data Transformation (T in ELT):** Establishing `dbt` as the primary tool for in-database transformations.
* **`dbt-postgres` Adapter:** Enabling `dbt` to interact with the PostgreSQL data warehouse.
* **`profiles.yml`:** Centralized configuration for database connections in `dbt`.
* **Secure Credential Management:** Using `env_var()` in `profiles.yml` in conjunction with Docker Compose's `env_file` to keep sensitive credentials out of source code.
* **Docker Volume Mounts:** Sharing host files (`profiles.yml`) with containers for configuration.
* **`dbt debug`:** A fundamental `dbt` command for validating connectivity and setup.

**Outcome:**
The `dbt` environment is successfully configured and connected to the local PostgreSQL database, ready to define and execute transformation models.


# Sub-task 2.3: Develop dbt Models in Layers

## Objective
To transform the raw Telegram message data into a structured and analytically optimized dimensional star schema within PostgreSQL using dbt.

## Implementation

### Staging Layer (`stg_telegram_messages`)
A foundational model that directly queries the `raw.telegram_messages` source. It performs initial data cleaning, type casting (e.g., to `INT`, `BOOLEAN`), column renaming for consistency, and extracts key fields from the raw JSONB `message_data` column. Crucially, it handles potential `NULL` values for numerical counts (like views, forwards, replies) by `COALESCE`ing them to `0`, ensuring data integrity for subsequent transformations.

### Data Mart Layer (Dimensional Star Schema)
This layer builds the analytical tables optimized for querying.

- **`dim_channels`**: A dimension table providing unique channel information. It uses `dbt-utils.generate_surrogate_key` to create a stable `channel_pk` from `channel_username`, serving as its primary key.

- **`dim_dates`**: A standard date dimension table derived from the unique `scraped_date` in the staging layer. It extracts various date attributes (day, month, year, quarter, day of week, etc.), facilitating time-based analysis. `date_pk` serves as its primary key.

- **`fct_messages`**: The central fact table. It selects core message-level metrics (e.g., `views_count`, `forwards_count`, `message_text`) and joins with `dim_channels` and `dim_dates` using `LEFT JOIN` operations to bring in their respective primary keys (`channel_pk`, `date_pk`). These primary keys act as foreign keys, establishing the relationships within the star schema.

---

# Sub-task 2.4: Testing and Documentation

## Objective
To ensure data quality and provide comprehensive, automatically generated documentation for the dbt project.

## Implementation

### Built-in Tests

- **`unique` and `not_null` tests**: Applied to primary key columns (`channel_pk`, `date_pk`, `message_id`) in `dim_channels`, `dim_dates`, and `fct_messages` to enforce uniqueness and completeness. They are also applied to critical business keys like `channel_username`.

- **`relationships` tests**: Implemented on foreign key columns (`channel_pk`, `date_pk`) in `fct_messages` to ensure referential integrity between the fact table and its dimension tables (i.e., every foreign key value exists as a primary key in the referenced dimension).

### Custom Data Test
A specific SQL query (`tests/no_negative_views.sql`) was created to enforce a critical business rule: `views_count` in `fct_messages` must never be negative. This test passes if the query returns 0 rows, indicating no violations.

### Documentation Generation

- **Descriptions**: Added to sources, models, and individual columns in corresponding `.yml` files (`models/staging/sources.yml`, `models/marts/*.yml`).

- **Documentation compilation**: `dbt docs generate` was used to compile these descriptions along with model lineage and test results into a static documentation website.

- **Local browsing**: The `dbt docs serve` command was configured and executed (`docker-compose.yml` updated to expose port 8080) to allow local Browse of the generated documentation at `http://localhost:8080`. This provides a centralized and navigable data catalog for the project.


# Task 3: Data Enrichment with Object Detection (YOLO) - Progress Report

This report summarizes the objectives, challenges, and successful implementations for Task 3, focusing on integrating YOLOv8 object detection findings into the data warehouse.

## I. Objectives of Task 3

The primary goal of Task 3 was to enrich the existing Telegram message data by:

- Analyzing scraped images using a pre-trained YOLOv8 model
- Extracting detected objects and their confidence scores
- Integrating this new, valuable information into the data warehouse, specifically by creating a new fact table linked to message metadata

## II. Implementation Steps & Achievements

### A. Setting Up the Object Detection Environment

- **Installing ultralytics**: We ensured the ultralytics package, which provides the YOLOv8 model, was installed in the Docker environment
- **Model Loading**: The yolov8n.pt pre-trained model was successfully loaded within the detection script

### B. Developing the YOLO Object Detection Script (yolo_detector.py)

**Initial Script Creation**: We developed `src/yolo_detector.py` to:

- Scan for Telegram media files (images) from `data/raw/telegram_media/`
- Perform object detection on these images using the loaded YOLOv8 model
- Extract key detection details: `message_id`, `detected_object_class`, `confidence_score`, `detection_timestamp`, and bounding box coordinates (`box_top_left_x`, `box_top_left_y`, `box_width`, `box_height`)
- Save the processed detections as JSON files (e.g., `yolo_detections_YYYY-MM-DD_HHMMSS.json`) into `data/raw/yolo_detections/`

### C. Integrating Raw YOLO Data into PostgreSQL

This was a critical phase that involved refining the data loading mechanism:

**Initial sources.yml Configuration**: We initially attempted to configure `raw_data.yolo_detections_json` as an external source in `sources.yml` pointing directly to local file paths.

**Challenge**: This approach resulted in a `Compilation Error: Model depends on a source named 'raw_data.yolo_detections_json' which was not found`. This was due to a mismatch between the source name (`raw_data`) in the model and the actual source name (`raw`) defined in `sources.yml`.

**Resolution**: The `stg_yolo_detections.sql` model was corrected to use `{{ source('raw', 'yolo_detections_json') }}`.

**Addressing PostgreSQL "Relation Does Not Exist" Error**: Even with the sources.yml correction, a `Database Error: relation "public.yolo_detections_json" does not exist` occurred.

**Root Cause**: The dbt-postgres adapter does not inherently support defining external sources for directly querying local file paths as tables. PostgreSQL requires data to be loaded into a managed table or accessed via specific extensions like file_fdw.

**Solution Strategy**: We decided to explicitly load the YOLO JSON files into a PostgreSQL table first, rather than relying on dbt to treat files as external tables.

**Leveraging load_raw_data.py for YOLO Ingestion**: Instead of modifying `yolo_detector.py` for database loading, we opted to extend the existing `src/load_raw_data.py` script for this purpose, maintaining clear separation of concerns.

**load_raw_data.py Modifications**:

- Added `RAW_YOLO_DETECTIONS_PATH` configuration
- Implemented a new function `create_yolo_detections_table()` to create the `raw.yolo_detections` table (with `id SERIAL`, `detection_data JSONB`, `file_name`, `inserted_at`)
- Developed `load_yolo_detections_to_postgres()` to read each YOLO detection JSON file and insert its entire JSON array content as a single record into `raw.yolo_detections`. It includes logic to prevent duplicate file loading
- The main execution block was updated to call both the existing Telegram messages loader and the new YOLO detections loader

**yolo_detector.py Reversion**: The database insertion logic was removed from `yolo_detector.py` to keep it focused solely on detection and file generation.

**Updating sources.yml for Database-Loaded YOLO Data**: The `sources.yml` was modified to define `raw.yolo_detections` as a standard table source (no external property), reflecting its direct loading into PostgreSQL.

### D. Developing dbt Models for YOLO Findings (stg_yolo_detections and fct_image_detections)

**stg_yolo_detections Development**:

This staging model was created to process the `raw.yolo_detections` table.

- It uses `LATERAL jsonb_array_elements(full_json_record)` to flatten the `detection_data` JSONB arrays, creating a separate row for each individual detected object
- Data types were explicitly cast (e.g., `INTEGER`, `NUMERIC`, `TIMESTAMP`)

**Challenge (Persistent unexpected '>' error)**: The `dbt_utils.generate_surrogate_key` macro repeatedly caused `Compilation Error: unexpected '>'` when passed expressions with `->>`and explicit `::TEXT` casts. This indicated a parsing conflict within the macro.

**Resolution**: The `dbt_utils.generate_surrogate_key` macro was entirely bypassed. A manual MD5 hashing approach was implemented using `MD5(COALESCE(expression, '') || ...)` to generate the `yolo_detection_key`, ensuring compatibility with PostgreSQL's JSON operators.

**fct_image_detections Creation**: A fact table (`public_analytics.fct_image_detections`) was created, selecting all columns from `stg_yolo_detections` to serve as the final, denormalized layer for analysis.

## III. Verification

**Database Structure Confirmation**: Visual inspection of the PostgreSQL database confirmed the existence of:

- `raw.telegram_messages` and `raw.yolo_detections` tables in the `raw` schema
- `public_analytics.stg_yolo_detections` (view) and `public_analytics.fct_image_detections` (view) in the `public_analytics` schema

**Raw Data Query Verification**: Querying `SELECT * FROM raw.yolo_detections LIMIT 5;` correctly showed only 2 rows, confirming that each row represented a loaded JSON file (which contained an array of detections). This validated `load_raw_data.py`'s ingestion strategy.

**Transformed Data Query Verification**: Queries to `SELECT * FROM public_analytics.stg_yolo_detections LIMIT 10;` successfully returned multiple rows, with individual `yolo_detection_key`, `message_id`, `detected_object_class`, and `confidence_score` values. This confirmed the successful flattening and transformation by dbt.

## IV. Conclusion

Task 3 is now fully implemented and verified. We have established a robust pipeline for:

- Performing object detection on Telegram media
- Efficiently loading raw YOLO detection data into PostgreSQL
- Transforming and integrating this data into the data warehouse using dbt, creating valuable fact tables for analytical purposes


# Task 4: Build an Analytical API with FastAPI

## Overall Objective

To develop a robust and efficient analytical API using FastAPI that exposes key business insights derived from the dbt-transformed data marts. This API serves as a crucial layer for external applications or dashboards to consume clean, validated, and analytical data.

## Implementation Steps & Achievements

### 4.1 Setting Up the FastAPI Environment and Project Structure

**Objective:** To establish the necessary Python packages and project architecture for a FastAPI application.

**Implementation:**

- **Dependencies:** Added `fastapi` and `uvicorn` to `requirements.txt` to enable web service capabilities and an ASGI server.

- **Project Structure:** Created the `my_project/` directory to encapsulate the API's components, including:
  - `main.py` (FastAPI application entry point)
  - `database.py` (SQLAlchemy setup)
  - `models.py` (SQLAlchemy ORM models)
  - `schemas.py` (Pydantic data validation schemas)
  - `crud.py` (data interaction logic)

- **Docker Integration:** Updated `Dockerfile` to include the new FastAPI dependencies and configured `docker-compose.yml` to define and run the FastAPI service, exposing its port for external access. The `docker-compose.yml` was also adjusted to connect to the locally installed PostgreSQL instance, removing the previously containerized database service.

### 4.2 Developing Analytical Endpoints

**Objective:** To create specific API endpoints that address the defined business questions by querying the dbt-transformed data marts (`public_analytics.dim_channels`, `public_analytics.fct_messages`, `public_analytics.fct_image_detections`).

**Implementation:**

- **GET /api/reports/top-products?limit=10:**
  - Implemented a function in `crud.py` to query `fct_image_detections` and return the most frequently detected product classes based on `detected_object_class` and their `detection_count`.

- **GET /api/channels/{channel_username}/activity:**
  - Developed a function in `crud.py` to retrieve detailed posting activity for a specified channel. This function joins `dim_channels` and `fct_messages` (and optionally `fct_image_detections`) and aggregates metrics such as `message_count`, `detection_count`, `total_views`, `total_forwards`, `total_replies`, and `messages_with_media`, grouped by `activity_date`.

- **GET /api/search/messages?query=paracetamol:**
  - Created a function in `crud.py` to search `fct_messages` for keywords within `message_text`, returning relevant message details.

### 4.3 Data Validation and ORM Mapping

**Objective:** To ensure data consistency and integrity between the database, SQLAlchemy ORM models, and FastAPI's Pydantic response schemas.

**Implementation:**

#### SQLAlchemy ORM (models.py):

Defined SQLAlchemy models (`DimChannel`, `FctMessage`, `FctImageDetection`) that precisely map to the columns and data types of the dbt-generated database views. This included critical corrections such as:

- Renaming `channel_id` to `channel_pk` and `message_timestamp` to `message_timestamp_utc` in `FctMessage`, aligning with database schema.
- Adjusting data types to `Text` for `channel_pk` and `message_timestamp_utc`, and `Boolean` for `has_media`, `is_photo`, `is_document` to accurately reflect the PostgreSQL types.
- Establishing `ForeignKey` constraints and relationship attributes (e.g., `channel`, `detections`) to define ORM relationships between models.

#### Pydantic Schemas (schemas.py):

Created Pydantic `BaseModel` schemas (`Channel`, `Message`, `ImageDetection`, `TopProduct`, `ChannelActivity`) to define the structure and validate the data returned by the API endpoints.

**Critical Fixes for ResponseValidationError:** Extensive adjustments were made to `schemas.py` to resolve validation errors:

- Renamed `channel_id` to `channel_pk` and `message_timestamp` to `message_timestamp_utc` within the `Message` schema, and set their types to `str`.
- Updated `has_media` to `Optional[bool]` in the `Message` schema.
- Included all relevant fields from the `FctMessage` SQLAlchemy model (e.g., `views_count`, `forwards_count`, `replies_count`, `media_type`, `date_pk`) in the `Message` Pydantic schema with corresponding Python types.
- Ensured the `Channel` schema accurately reflected the `dim_channels` view's columns (e.g., `channel_pk`).
- Expanded the `ChannelActivity` schema to include all aggregated metrics calculated in `crud.py` (e.g., `total_views`, `total_forwards`, `total_replies`, `messages_with_media`).
- Confirmed `from_attributes = True` was correctly set in `Config` for all relevant Pydantic schemas to ensure ORM compatibility.

## Outcome

Task 4 is fully implemented and verified. The FastAPI analytical API successfully provides endpoints that query the dbt-transformed data marts. All three main API endpoints (`/api/reports/top-products`, `/api/channels/{channel_username}/activity`, `/api/search/messages`) were confirmed to be working correctly after resolving database-to-ORM and ORM-to-Pydantic schema mismatches. The API now serves as a reliable interface for accessing key analytical insights from the Telegram data warehouse.


# Comprehensive Report Documentation for Task 5: Pipeline Orchestration, Scheduling, and Monitoring with Dagster

## I. Objective

The primary objective of Task 5 is to establish robust orchestration, scheduling, and monitoring capabilities for the end-to-end Telegram medical data ETL pipeline using Dagster. This involves defining the pipeline as a Dagster job, setting up automated schedules for its execution, and enabling comprehensive visibility into pipeline runs and data assets.

## II. Implementation

### Dagster Environment Setup

**Containerization**: The entire application and its services (including the Python application with Dagster, PostgreSQL database) are containerized using Dockerfile and docker-compose.yml for consistent and reproducible environments.

**Dependency Management**: Python dependencies, including dagster and dagster-webserver, are managed via requirements.txt and installed within the Docker container.

**Environment Variables**: Sensitive configurations (e.g., Telegram API credentials, PostgreSQL connection details) are securely managed using a .env file, loaded by python-dotenv and accessible within the Dagster environment.

### Pipeline Definition (telegram_etl_pipeline)

The telegram_etl_pipeline is defined as a Dagster job within `dagster_project/jobs.py`.

It comprises four sequentially linked operations (ops), representing the core ETL stages:

1. **scrape_telegram_data**: Responsible for extracting raw Telegram messages.

2. **run_yolo_enrichment**: Performs object detection on media associated with the messages.

3. **load_raw_to_postgres**: Loads the scraped data and YOLO detection results into the PostgreSQL raw schema.

4. **run_dbt_transformations**: Executes dbt commands to transform data from raw to public_analytics schemas.

Dependencies between these ops are explicitly defined using Dagster's input/output chaining (e.g., `run_yolo_enrichment(start=scraped_data_signal)`), ensuring correct execution order. `In(Nothing)` and `Out(Nothing)` are used for ops that act as signals for downstream dependencies rather than passing explicit data.

### Scheduling (daily_telegram_etl_schedule)

A Dagster schedule named `daily_telegram_etl_schedule` is defined in `dagster_project/schedules.py`.

This schedule is configured to trigger the telegram_etl_pipeline job automatically at a specified interval (e.g., daily at midnight UTC).

The schedule ensures that the data pipeline runs regularly, keeping the data warehouse updated with the latest information.

### Local Development and UI (Dagit)

The Dagster development server (`dagster dev -m dagster_project`) allows local execution and interaction with the pipeline.

The Dagit UI (accessible via `http://127.0.0.1:3000`) provides a comprehensive interface for:

- **Job Visualization**: Viewing the graphical representation of the telegram_etl_pipeline, showing the flow and dependencies of its ops.

- **Manual Runs**: Initiating ad-hoc pipeline executions for testing or immediate data updates.

- **Run Monitoring**: Observing the real-time status of pipeline runs, including logs, execution duration, and op-level success/failure.

- **Schedule Management**: Activating and deactivating the daily_telegram_etl_schedule.

- **Asset Catalog**: (If assets are defined) Inspecting the data assets produced by the pipeline and their lineage.

## III. Verification

Once your Docker build completes and the Dagster UI is fully accessible, you can verify Task 5's successful implementation by:

1. **Job Graph Inspection**: Confirming the correct visual representation of telegram_etl_pipeline in Dagit.

2. **Manual Run Execution**: Successfully launching a manual run of the pipeline and observing all ops complete without errors. This will validate the execution flow and the correct setup of scrape.py, yolo_detector.py, load_raw_data.py, and dbt commands within the container.

3. **Schedule Activation**: Toggling on the daily_telegram_etl_schedule and confirming its active status, ready for automated runs.

4. **Log Review**: Examining the detailed logs for each op within the Dagster UI to ensure proper execution, data processing, and error handling.

This comprehensive setup ensures that your Telegram medical data pipeline is not only functional but also automated, observable, and maintainable.


# Task 5: Pipeline Orchestration

**Overall Objective:** To transform the collection of individual scripts into a robust, observable, and schedulable production pipeline using Dagster, leveraging its excellent local development experience.

## I. Implementation of Pipeline Orchestration with Dagster

This section details the steps taken to integrate Dagster into the project, define the ETL pipeline as a Dagster job, and configure its scheduling and monitoring.

### A. Dagster Installation and Environment Setup

- **Dependency Addition:** `dagster` and `dagster-webserver` were added to the `requirements.txt` file to ensure they are included in the project's Python dependencies.

- **Containerized Environment:** The entire application, including the Python environment with Dagster, is containerized using `Dockerfile` and orchestrated with `docker-compose.yml`. This provides a consistent and isolated environment for pipeline execution. The `Dockerfile` has been updated to utilize a more recent Python base image (e.g., `python:3.12-slim-bookworm`) to ensure stable installation of all Python and system dependencies.

- **Configuration Loading:** Environment variables crucial for pipeline operations (e.g., Telegram API credentials, PostgreSQL connection details) are loaded securely from the `.env` file using `python-dotenv`, making them accessible within the Dagster execution environment.

### B. Defining the Dagster Job (telegram_etl_pipeline)

The existing `run_pipeline.sh` logic has been refactored and converted into a structured Dagster job, defining the data flow and dependencies between operations.

- **Job Definition:** A central Dagster job, named `telegram_etl_pipeline`, is defined within `dagster_project/jobs.py`. This job serves as the executable unit that orchestrates the entire ETL process.

- **Operations (Ops):** The pipeline's core functionalities are encapsulated into distinct Dagster operations (ops), each representing a logical step in the workflow. These ops are defined in `dagster_project/ops.py`:

  - `scrape_telegram_data`: Responsible for extracting raw message data from specified Telegram channels.
  - `run_yolo_enrichment`: Executes the YOLO object detection script to enrich media data.
  - `load_raw_to_postgres`: Handles the loading of raw scraped and enriched data into the PostgreSQL database.
  - `run_dbt_transformations`: Triggers the dbt project to perform in-database transformations and create analytical models.

- **Dependency Graph:** The ops are explicitly chained within the `telegram_etl_pipeline` job, creating a directed acyclic graph (DAG) that defines their execution order. This ensures:
  - `run_yolo_enrichment` depends on `scrape_telegram_data`
  - `load_raw_to_postgres` depends on both `scrape_telegram_data` and `run_yolo_enrichment` (implicitly through data flow or explicit start signals)
  - `run_dbt_transformations` depends on `load_raw_to_postgres`

### C. Launching the Dagster UI (Dagit)

- **Webserver Command:** The Dagster UI, Dagit, is launched locally using the command `dagster dev -m dagster_project` (or as part of the `docker-compose up` process).

- **Interactive Interface:** Dagit provides a web-based interface (typically accessible at `http://127.0.0.1:3000`) for:
  - **Pipeline Inspection:** Visualizing the `telegram_etl_pipeline` job graph, showing the flow and dependencies of its ops.
  - **Manual Execution:** Triggering ad-hoc runs of the pipeline for testing or immediate data processing needs.
  - **Run Monitoring:** Observing the real-time status of pipeline runs, reviewing detailed logs, and tracking execution metrics.
  - **Error Diagnosis:** Providing clear error messages and stack traces to facilitate debugging, as demonstrated during the `ModuleNotFoundError` resolution.

### D. Adding a Schedule

- **Schedule Definition:** A Dagster schedule, `daily_telegram_etl_schedule`, is defined within `dagster_project/schedules.py`.

- **Automated Execution:** This schedule is configured to automatically trigger the `telegram_etl_pipeline` job at a specified regular interval (e.g., daily at 00:00 UTC), ensuring the data warehouse is consistently updated without manual intervention.

- **Schedule Management:** The Dagit UI allows for easy activation, deactivation, and monitoring of this schedule, providing control over automated pipeline runs.

## II. Verification

The successful implementation of Task 5 can be verified through the following:

- **Dagit UI Accessibility:** Confirming that the Dagster UI loads correctly at `http://127.0.0.1:3000`.

- **Job Graph Validation:** Visually inspecting the `telegram_etl_pipeline` job in Dagit to ensure all ops and their dependencies are correctly displayed.

- **Successful Pipeline Runs:** Initiating a manual run of the `telegram_etl_pipeline` from Dagit and verifying that all ops (`scrape_telegram_data`, `run_yolo_enrichment`, `load_raw_to_postgres`, `run_dbt_transformations`) complete successfully, indicated by green checkmarks and absence of errors in the logs.

- **Schedule Activation:** Activating the `daily_telegram_etl_schedule` in Dagit and confirming its "Active" status, indicating it is ready for automated executions.

- **Log Review:** Reviewing the detailed logs for each op within the Dagit UI to ensure data processing, loading, and transformations are occurring as expected.

Through these steps, the individual scripts are transformed into a robust, observable, and schedulable production pipeline, achieving the core objectives of Task 5.