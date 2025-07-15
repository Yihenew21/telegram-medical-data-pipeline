# Telegram Medical Data Product Pipeline

A comprehensive end-to-end data engineering pipeline that scrapes medical-related Telegram channels, enriches the data with AI-powered object detection, and provides analytical insights through a robust API.

## 🚀 Features

- **Data Collection**: Automated scraping of Telegram channels with rate limiting and error handling
- **AI Enhancement**: YOLOv8 object detection for image analysis and content enrichment
- **Data Transformation**: dbt-powered ELT pipeline with dimensional modeling
- **API Layer**: FastAPI endpoints for analytical queries and reporting
- **Orchestration**: Dagster-based pipeline scheduling and monitoring
- **Containerization**: Full Docker support for reproducible deployments

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Telegram      │    │   YOLO Object   │    │   PostgreSQL    │
│   Scraper       │───▶│   Detection     │───▶│   Data Lake     │
│   (Telethon)    │    │   (YOLOv8)      │    │   (Raw Schema)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI       │    │   dbt           │    │   Analytics     │
│   Endpoints     │◀───│   Transformations│◀───│   Schema        │
│   (Analytics)   │    │   (Star Schema) │    │   (Fact/Dim)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                ▲
                                │
                    ┌─────────────────┐
                    │   Dagster       │
                    │   Orchestration │
                    │   & Monitoring  │
                    └─────────────────┘
```

## 📋 Prerequisites

- Python 3.12+
- PostgreSQL 13+
- Docker & Docker Compose
- Telegram API credentials
- Git

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/telegram_data_product.git
cd telegram_data_product
```

### 2. Environment Setup

Create a `.env` file with your credentials:

```bash
# Telegram API Configuration
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
PHONE_NUMBER=your_phone_number

# PostgreSQL Configuration
POSTGRES_DB=telegram_warehouse
POSTGRES_USER=telegram_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

### 3. Docker Setup

```bash
# Build and start the application
docker-compose up --build -d

# Verify containers are running
docker-compose ps
```

### 4. Database Initialization

```bash
# Set up PostgreSQL database and user
psql -U postgres -c "CREATE DATABASE telegram_warehouse;"
psql -U postgres -c "CREATE USER telegram_user WITH PASSWORD 'your_secure_password';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE telegram_warehouse TO telegram_user;"
```

## 📊 Data Collection Pipeline

### Telegram Data Scraping

The pipeline uses Telethon to scrape data from public Telegram channels:

```python
# Target channels configuration
TARGET_CHANNELS = [
    "medicalchannel1",
    "healthnews",
    "pharmainfo"
]
```

**Features:**
- Asynchronous scraping for optimal performance
- Date-based partitioning (`YYYY-MM-DD` format)
- Comprehensive logging with `scrape.log`
- Rate limiting and error handling
- Media download and processing

**File Structure:**
```
data/raw/telegram_messages/
├── 2024-01-15/
│   ├── medicalchannel1.json
│   └── healthnews.json
└── 2024-01-16/
    └── pharmainfo.json
```

### Usage

```bash
# Manual scraping
docker exec telegram_app python src/scrape.py

# View logs
docker exec telegram_app tail -f scrape.log
```

## 🤖 AI-Powered Object Detection

### YOLOv8 Integration

The pipeline integrates YOLOv8 for automatic object detection in scraped images:

```python
# Object detection processing
python src/yolo_detector.py
```

**Capabilities:**
- Pre-trained YOLOv8n model for object detection
- Confidence score extraction
- Bounding box coordinate capture
- Medical product identification
- Batch processing of media files

**Detection Output:**
```json
{
    "message_id": "12345",
    "detected_object_class": "bottle",
    "confidence_score": 0.85,
    "box_coordinates": [100, 150, 200, 300]
}
```

## 🔄 Data Transformation (dbt)

### Star Schema Design

The dbt project implements a dimensional star schema optimized for analytics:

```sql
-- Staging Layer
models/staging/
├── stg_telegram_messages.sql
└── stg_yolo_detections.sql

-- Data Marts
models/marts/
├── dim_channels.sql
├── dim_dates.sql
├── fct_messages.sql
└── fct_image_detections.sql
```

#### Star Schema Architecture

```
                    ┌─────────────────────────────────────┐
                    │            dim_dates                │
                    │_____________________________________│
                    │  • date_pk (PK)                     │
                    │  • date_value                       │
                    │  • day_of_week                      │
                    │  • day_of_month                     │
                    │  • day_of_year                      │
                    │  • week_of_year                     │
                    │  • month_name                       │
                    │  • month_number                     │
                    │  • quarter                          │
                    │  • year                             │
                    │  • is_weekend                       │
                    └─────────────────────────────────────┘
                                        │
                                        │
                                        ▼
┌─────────────────────────────────────┐ │ ┌─────────────────────────────────────┐
│           dim_channels              │ │ │          fct_messages               │
│_____________________________________│ │ │_____________________________________│
│  • channel_pk (PK)                  │◄┼─┤  • message_id (PK)                  │
│  • channel_username                 │ │ │  • channel_pk (FK)                  │
│  • channel_title                    │ │ │  • date_pk (FK)                     │
│  • channel_description              │ │ │  • message_text                     │
│  • channel_type                     │ │ │  • views_count                      │
│  • is_verified                      │ │ │  • forwards_count                   │
│  • subscriber_count                 │ │ │  • replies_count                    │
│  • created_date                     │ │ │  • message_timestamp_utc            │
└─────────────────────────────────────┘ │ │  • has_media                        │
                                        │ │  • media_type                       │
                                        │ │  • is_photo                         │
                                        │ │  • is_document                      │
                                        │ │  • file_size                        │
                                        │ │  • file_name                        │
                                        │ └─────────────────────────────────────┘
                                        │                   │
                                        │                   │
                                        │                   ▼
                                        │ ┌─────────────────────────────────────┐
                                        │ │      fct_image_detections           │
                                        │ │_____________________________________│
                                        └─┤  • yolo_detection_key (PK)          │
                                          │  • message_id (FK)                  │
                                          │  • detected_object_class            │
                                          │  • confidence_score                 │
                                          │  • box_top_left_x                   │
                                          │  • box_top_left_y                   │
                                          │  • box_width                        │
                                          │  • box_height                       │
                                          │  • detection_timestamp              │
                                          │  • file_name                        │
                                          └─────────────────────────────────────┘
```

#### Schema Relationships

**Primary Fact Tables:**
- `fct_messages`: Core messaging metrics and content analysis
- `fct_image_detections`: AI-powered object detection results

**Dimension Tables:**
- `dim_channels`: Channel metadata and characteristics
- `dim_dates`: Time-based dimensional attributes

**Key Relationships:**
- `fct_messages.channel_pk` → `dim_channels.channel_pk`
- `fct_messages.date_pk` → `dim_dates.date_pk`
- `fct_image_detections.message_id` → `fct_messages.message_id`

### Model Layers

**Staging Layer:**
- Data cleansing and type casting
- NULL value handling
- Column standardization

**Dimensional Layer:**
- `dim_channels`: Channel metadata and attributes
- `dim_dates`: Time dimension with date hierarchies
- `fct_messages`: Message-level metrics and content
- `fct_image_detections`: AI detection results with confidence scores

### Data Quality Tests

```yaml
# Built-in tests
tests:
  - unique
  - not_null
  - relationships

# Custom business rules
tests/no_negative_views.sql
```

### dbt Commands

```bash
# Run transformations
docker exec telegram_app dbt run

# Test data quality
docker exec telegram_app dbt test

# Generate documentation
docker exec telegram_app dbt docs generate
docker exec telegram_app dbt docs serve --port 8080
```

## 🚀 API Endpoints

### FastAPI Application

The API provides analytical endpoints built with FastAPI and Pydantic validation:

```python
# Start the API server
uvicorn my_project.main:app --host 0.0.0.0 --port 8000
```

### Available Endpoints

#### 1. Top Products Analysis
```http
GET /api/reports/top-products?limit=10
```

**Response:**
```json
{
  "products": [
    {
      "detected_object_class": "bottle",
      "detection_count": 156,
      "confidence_avg": 0.87
    }
  ]
}
```

#### 2. Channel Activity Analysis
```http
GET /api/channels/{channel_username}/activity
```

**Response:**
```json
{
  "channel_username": "medicalchannel1",
  "activity_date": "2024-01-15",
  "message_count": 45,
  "total_views": 12500,
  "total_forwards": 230,
  "messages_with_media": 12
}
```

#### 3. Message Search
```http
GET /api/search/messages?query=paracetamol
```

**Response:**
```json
{
  "messages": [
    {
      "message_id": "12345",
      "message_text": "New paracetamol research findings...",
      "views_count": 1200,
      "channel_username": "medicalchannel1"
    }
  ]
}
```

### API Documentation

Access interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## ⚙️ Pipeline Orchestration

### Dagster Integration

The pipeline is orchestrated using Dagster for scheduling and monitoring:

```python
# Pipeline definition
@job
def telegram_etl_pipeline():
    transformed_data = run_dbt_transformations(
        loaded_data=load_raw_to_postgres(
            enriched_data=run_yolo_enrichment(
                scraped_data=scrape_telegram_data()
            )
        )
    )
```

### Scheduling

```python
# Daily automated execution
@schedule(
    job=telegram_etl_pipeline,
    cron_schedule="0 0 * * *"  # Daily at midnight UTC
)
def daily_telegram_etl_schedule():
    return {}
```

### Monitoring Dashboard

Access the Dagster UI at `http://localhost:3000` for:
- Pipeline visualization
- Run monitoring and logs
- Schedule management
- Asset lineage tracking

## 🔧 Development

### Local Development Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Activate virtual environment
source venv/bin/activate

# Run individual components
python src/scrape.py
python src/yolo_detector.py
python src/load_raw_data.py
```

### Testing

```bash
# Run dbt tests
dbt test

# API testing
pytest tests/

# Data quality validation
python tests/data_quality_tests.py
```

## 📁 Project Structure

```
telegram_medical_data_pipline/
├── src/                         # Source code
│   ├── scrape.py                # Telegram scraping logic
│   ├── yolo_detector.py         # Object detection
│   ├── load_raw_data.py         # Data loading
│   └── config.py                # Configuration management
├── telegram_dbt_project/        # dbt transformation project
│   ├── models/                  # Data models
│   │   ├── staging/             # Staging models (stg_telegram_messages, stg_yolo_detections)
│   │   └── marts/               # Data mart models (dim_channels, dim_dates, fct_messages, fct_image_detections)
│   ├── tests/                   # Custom data tests
│   └── dbt_project.yml          # dbt configuration
├── my_project/                  # FastAPI application
│   ├── main.py                  # API entry point
│   ├── models.py                # SQLAlchemy models
│   ├── database.py              # SQLAlchemy database configuration
│   ├── schemas.py               # Pydantic schemas
│   └── crud.py                  # Database operations
├── dagster_project/             # Pipeline orchestration
│   ├── __init__.py              # Dagster package initialization
│   ├── repository.py            # Dagster repository definition
│   ├── jobs.py                  # Pipeline definitions
│   ├── ops.py                   # Individual operations
│   └── schedules.py             # Scheduling configuration
├── data/                        # Data storage
│   ├── raw/                     # Raw data lake
│   │   ├── telegram_messages/{date}/{channel_name}.json   # Partitioned message data
│   │   ├── telegram_media/      # Downloaded media files
│   │   └── yolo_detections/     # AI detection results
├── Dockerfile                   # Container configuration
├── docker-compose.yml           # Service orchestration
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables
├── .gitignore                   # Git ignore rules
└── README.md                    # readme file
```

## 🔒 Security & Configuration

### Environment Variables

All sensitive credentials are managed via `.env` file:

```bash
# Never commit .env to version control
echo ".env" >> .gitignore
```

### Docker Security

```dockerfile
# Use non-root user in production
RUN adduser --disabled-password --gecos '' appuser
USER appuser
```

### Database Security

- SSL-enabled PostgreSQL connections
- Role-based access control
- Encrypted credential storage

## 🚀 Deployment

### Production Deployment

```bash
# Build production image
docker build -t telegram-data-product:latest .

# Deploy with environment-specific configuration
docker-compose -f docker-compose.prod.yml up -d
```

### Monitoring

- **Dagster UI**: Pipeline execution monitoring
- **PostgreSQL logs**: Database performance tracking
- **Application logs**: Centralized logging with structured output

## 📈 Performance Optimization

### Database Optimization

```sql
-- Indexes for query performance
CREATE INDEX idx_messages_channel_date ON fct_messages(channel_pk, date_pk);
CREATE INDEX idx_detections_confidence ON fct_image_detections(confidence_score);
```

### Caching Strategy

- API response caching for frequently accessed data
- Database query result caching
- Media file caching for object detection

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Standards

- Follow PEP 8 for Python code
- Use type hints for all functions
- Write comprehensive docstrings
- Maintain test coverage above 80%

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For issues and questions:
- Create an issue on GitHub
- Check the [documentation](docs/)
- Review the [FAQ](docs/FAQ.md)

## 🔄 Changelog

### v1.0.0 (2024-01-15)
- Initial release with full ETL pipeline
- Telegram data scraping with Telethon
- YOLOv8 object detection integration
- dbt-powered data transformations
- FastAPI analytical endpoints
- Dagster orchestration and scheduling

---

**Built with ❤️ for medical data analytics**