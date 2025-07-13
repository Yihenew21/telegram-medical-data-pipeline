# Telegram Medical Data Pipeline

A comprehensive ELT (Extract, Load, Transform) data pipeline that collects Telegram channel messages, stores them in a data lake, loads them into a PostgreSQL data warehouse, and transforms them into an analytical star schema using dbt.

## 🏆 Project Highlights

✅ **Complete ELT Pipeline**: Fully functional end-to-end data pipeline  
✅ **Docker Orchestration**: Containerized application with PostgreSQL integration  
✅ **dbt Transformations**: Comprehensive star schema with staging and mart layers  
✅ **Data Quality Testing**: Built-in and custom dbt tests ensuring data integrity  
✅ **Production-Ready**: Robust error handling, logging, and monitoring  
✅ **Comprehensive Documentation**: Auto-generated dbt docs and detailed setup guides  

## 🏗️ Architecture Overview

```
Telegram API → Raw Data Lake → PostgreSQL (Raw) → dbt Transformations → Analytics Schema
     ↓              ↓              ↓                    ↓
  scrape.py    JSON Files    load_raw_data.py    Star Schema Tables
```

## 📊 Data Model - Star Schema

### Dimensional Design
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   dim_channels  │    │   fct_messages  │    │   dim_dates     │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ channel_pk (PK) │◄───┤ channel_pk (FK) │───►│ date_pk (PK)    │
│ channel_username│    │ date_pk (FK)    │    │ scraped_date    │
│ channel_title   │    │ message_id      │    │ year            │
│ channel_type    │    │ message_text    │    │ month           │
└─────────────────┘    │ views_count     │    │ quarter         │
                       │ forwards_count  │    │ day_of_week     │
                       │ replies_count   │    └─────────────────┘
                       │ media_type      │
                       │ created_at      │
                       └─────────────────┘
```

## 🚀 Quick Start Guide

### Prerequisites
- Docker & Docker Compose (20.10+)
- Python 3.8+
- PostgreSQL 13+ (local installation)
- Telegram API credentials ([Get them here](https://my.telegram.org))

### One-Command Setup
```bash
# Clone and setup
git clone <repository-url>
cd telegram_data_product
cp .env.example .env  # Edit with your credentials
docker-compose up --build -d

# Run complete pipeline
./run_pipeline.sh
```

### Environment Configuration

Create `.env` file with your credentials:
```env
# Telegram API Configuration
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here  
PHONE_NUMBER=+1234567890

# PostgreSQL Configuration
POSTGRES_DB=telegram_warehouse
POSTGRES_USER=telegram_user
POSTGRES_PASSWORD=secure_password_123
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

### Local PostgreSQL Setup
```bash
# Create database and user
psql -U postgres
CREATE DATABASE telegram_warehouse;
CREATE USER telegram_user WITH PASSWORD 'secure_password_123';
GRANT ALL PRIVILEGES ON DATABASE telegram_warehouse TO telegram_user;
\q
```

## 🔧 Pipeline Components

### 1. Data Extraction (`src/scrape.py`)
**Advanced Telegram scraping with comprehensive logging**

```python
# Target channels configuration
TARGET_CHANNELS = [
    '@CheMed123',
    '@lobelia4cosmetics', 
    '@tikvahpharma'
]
```

**Key Features:**
- ✅ Asynchronous concurrent processing
- ✅ Comprehensive media metadata extraction
- ✅ Date-based partitioning (`YYYY-MM-DD/channel_name.json`)
- ✅ Robust error handling and retry mechanisms
- ✅ Session management and authentication
- ✅ Detailed logging to `logs/scrape.log`

**Output Structure:**
```json
{
  "message_id": 123,
  "date": "2024-01-15T10:30:00+00:00",
  "text": "Sample message text",
  "views": 150,
  "forwards": 5,
  "replies": 2,
  "media_type": "photo",
  "channel_username": "channel1",
  "channel_title": "Sample Channel"
}
```

### 2. Data Loading (`src/load_raw_data.py`)
**Efficient raw data loading with incremental processing**

**Key Features:**
- ✅ Incremental loading (prevents duplicates)
- ✅ JSONB storage for flexible querying
- ✅ Transaction management with rollback
- ✅ Comprehensive error handling
- ✅ Progress tracking and logging

**Database Schema:**
```sql
CREATE SCHEMA IF NOT EXISTS raw;
CREATE TABLE IF NOT EXISTS raw.telegram_messages (
    message_id BIGINT,
    channel_username VARCHAR(255),
    scraped_date DATE,
    message_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (message_id, channel_username)
);
```

### 3. dbt Transformations (`telegram_dbt_project/`)
**Complete dimensional modeling with comprehensive testing**

#### 📁 dbt Project Structure
```
telegram_dbt_project/
├── models/
│   ├── staging/
│   │   ├── stg_telegram_messages.sql     # Data cleaning & standardization
│   │   └── sources.yml                   # Source definitions
│   └── marts/
│       ├── dim_channels.sql              # Channel dimension
│       ├── dim_dates.sql                 # Date dimension
│       ├── fct_messages.sql              # Message fact table
│       └── schema.yml                    # Model tests & documentation
├── tests/
│   └── no_negative_views.sql             # Custom business rule test
├── dbt_project.yml                       # dbt configuration
└── packages.yml                          # dbt packages
```

#### 🔄 Transformation Layers

##### **Staging Layer** (`models/staging/`)
```sql
-- stg_telegram_messages.sql
-- Cleans and standardizes raw JSONB data
SELECT 
    (message_data->>'message_id')::BIGINT as message_id,
    COALESCE((message_data->>'views')::INT, 0) as views_count,
    TO_TIMESTAMP(message_data->>'date', 'YYYY-MM-DD"T"HH24:MI:SS') as created_at,
    -- Additional transformations...
FROM {{ source('telegram_raw', 'telegram_messages') }}
```

##### **Mart Layer** (`models/marts/`)
- **`dim_channels`**: Unique channel information with surrogate keys
- **`dim_dates`**: Date dimension with calendar attributes  
- **`fct_messages`**: Central fact table with all metrics

#### 🧪 Data Quality Testing

##### **Built-in dbt Tests**
```yaml
# models/marts/schema.yml
models:
  - name: fct_messages
    columns:
      - name: message_id
        tests:
          - unique
          - not_null
      - name: channel_pk
        tests:
          - relationships:
              to: ref('dim_channels')
              field: channel_pk
```

##### **Custom Business Rule Tests**
```sql
-- tests/no_negative_views.sql
-- Ensures views_count is never negative
SELECT *
FROM {{ ref('fct_messages') }}
WHERE views_count < 0
```

## 📊 Complete Pipeline Execution

### Automated Pipeline Script
```bash
#!/bin/bash
# run_pipeline.sh - Complete pipeline execution

echo "🚀 Starting Telegram Data Pipeline..."

# Step 1: Data Extraction
echo "📥 Extracting data from Telegram channels..."
docker exec telegram_app python src/scrape.py

# Step 2: Data Loading  
echo "💾 Loading raw data to PostgreSQL..."
docker exec telegram_app python src/load_raw_data.py

# Step 3: dbt Transformations
echo "🔄 Running dbt transformations..."
docker exec telegram_app dbt run --project-dir telegram_dbt_project

# Step 4: Data Quality Tests
echo "🧪 Running data quality tests..."
docker exec telegram_app dbt test --project-dir telegram_dbt_project

# Step 5: Generate Documentation
echo "📚 Generating documentation..."
docker exec telegram_app dbt docs generate --project-dir telegram_dbt_project

echo "✅ Pipeline completed successfully!"
```

### Manual Step-by-Step Execution
```bash
# Build and start containers
docker-compose up --build -d

# Execute pipeline steps
docker exec telegram_app python src/scrape.py
docker exec telegram_app python src/load_raw_data.py
docker exec telegram_app dbt run --project-dir telegram_dbt_project
docker exec telegram_app dbt test --project-dir telegram_dbt_project

# Generate and serve documentation
docker exec telegram_app dbt docs generate --project-dir telegram_dbt_project
docker exec telegram_app dbt docs serve --project-dir telegram_dbt_project --port 8080
```

## 🔍 Data Quality & Testing

### Testing Strategy
1. **Built-in dbt Tests**: `unique`, `not_null`, `relationships`
2. **Custom Business Rules**: Domain-specific validation
3. **Data Freshness**: Source data recency checks
4. **Referential Integrity**: Foreign key relationships

### Test Execution
```bash
# Run all tests
docker exec telegram_app dbt test --project-dir telegram_dbt_project

# Run specific test types
docker exec telegram_app dbt test --select test_type:generic
docker exec telegram_app dbt test --select test_type:singular

# Test specific models
docker exec telegram_app dbt test --select fct_messages
```

## 📊 Analytics Examples

### Business Intelligence Queries
```sql
-- Top performing channels by engagement
SELECT 
    dc.channel_username,
    dc.channel_title,
    COUNT(*) as total_messages,
    AVG(fm.views_count) as avg_views,
    SUM(fm.forwards_count) as total_forwards
FROM analytics.fct_messages fm
JOIN analytics.dim_channels dc ON fm.channel_pk = dc.channel_pk
GROUP BY dc.channel_pk, dc.channel_username, dc.channel_title
ORDER BY avg_views DESC;

-- Daily engagement trends
SELECT 
    dd.scraped_date,
    dd.day_of_week,
    COUNT(*) as message_count,
    AVG(fm.views_count) as avg_views,
    SUM(fm.views_count) as total_views
FROM analytics.fct_messages fm
JOIN analytics.dim_dates dd ON fm.date_pk = dd.date_pk
GROUP BY dd.date_pk, dd.scraped_date, dd.day_of_week
ORDER BY dd.scraped_date DESC;
```

## 🔧 Verification & Monitoring

### Data Verification Commands
```bash
# Check raw data files
ls -la data/raw/telegram_messages/

# Verify PostgreSQL data
docker exec telegram_app psql -h localhost -U telegram_user -d telegram_warehouse \
  -c "SELECT COUNT(*) FROM raw.telegram_messages;"

# Check analytics tables
docker exec telegram_app psql -h localhost -U telegram_user -d telegram_warehouse \
  -c "SELECT COUNT(*) FROM analytics.fct_messages;"
```

### Health Checks
```bash
# Container health
docker-compose ps

# Database connectivity test
docker exec telegram_app python -c "
from src.config import get_db_connection
try:
    conn = get_db_connection()
    print('✅ Database connection successful')
    conn.close()
except Exception as e:
    print(f'❌ Database connection failed: {e}')
"

# dbt connection test
docker exec telegram_app dbt debug --project-dir telegram_dbt_project
```

## 📚 Documentation

### Auto-Generated dbt Documentation
```bash
# Generate comprehensive docs
docker exec telegram_app dbt docs generate --project-dir telegram_dbt_project

# Serve documentation locally
docker exec telegram_app dbt docs serve --project-dir telegram_dbt_project --port 8080
```

**Access documentation at:** `http://localhost:8080`

**Documentation includes:**
- 📊 Model lineage and dependencies
- 📋 Column descriptions and data types  
- 🧪 Test results and data quality metrics
- 📈 Model performance statistics
- 🔄 Transformation logic and SQL code

## 🛠️ Troubleshooting

### Common Issues & Solutions

#### Telegram Authentication
```bash
# Clear session and re-authenticate
rm telegram_scraper_session.session*
docker exec -it telegram_app python src/scrape.py
```

#### Database Connection Issues
```bash
# Test connection
docker exec telegram_app psql -h localhost -U telegram_user -d telegram_warehouse -c "SELECT 1;"

# Check PostgreSQL status
sudo systemctl status postgresql
```

#### dbt Issues
```bash
# Debug dbt connection
docker exec telegram_app dbt debug --project-dir telegram_dbt_project

# Check profiles configuration
docker exec telegram_app cat ~/.dbt/profiles.yml
```

## 📁 Project Structure

```
telegram_data_product/
├── src/                              # Source code
│   ├── scrape.py                    # Telegram data extraction
│   ├── load_raw_data.py             # PostgreSQL data loading
│   └── config.py                    # Configuration management
├── telegram_dbt_project/            # dbt project (COMPLETE)
│   ├── models/
│   │   ├── staging/
│   │   │   ├── stg_telegram_messages.sql
│   │   │   └── sources.yml
│   │   └── marts/
│   │       ├── dim_channels.sql
│   │       ├── dim_dates.sql
│   │       ├── fct_messages.sql
│   │       └── schema.yml
│   ├── tests/
│   │   └── no_negative_views.sql
│   ├── dbt_project.yml
│   └── packages.yml
├── data/
│   └── raw/
│       └── telegram_messages/        # Partitioned data lake
│           └── YYYY-MM-DD/
│               └── channel_name.json
├── logs/                            # Application logs
│   ├── scrape.log
│   ├── load_raw_data.log
│   └── dbt.log
├── docker-compose.yml               # Container orchestration
├── Dockerfile                       # Application container
├── requirements.txt                 # Python dependencies
├── run_pipeline.sh                  # Automated pipeline execution
├── .env                            # Environment variables
├── .gitignore                      # Git ignore rules
└── README.md                       # This comprehensive guide
```

## 🎯 Implementation Summary

### ✅ Completed Features

1. **Project Structure & Environment**
   - Modular codebase with clear separation of concerns
   - Docker containerization with PostgreSQL integration
   - Secure credential management via `.env`
   - Comprehensive `.gitignore` configuration

2. **Data Extraction & Storage**
   - Asynchronous Telegram scraping with `telethon`
   - Partitioned data lake structure (`YYYY-MM-DD/channel.json`)
   - Robust error handling and logging
   - Media metadata extraction

3. **Data Loading & Raw Storage**
   - Incremental PostgreSQL loading
   - JSONB storage for flexible querying
   - Transaction management and error recovery
   - Duplicate prevention mechanisms

4. **dbt Transformation Pipeline**
   - Complete staging layer with data cleaning
   - Dimensional star schema (fact + dimension tables)
   - Surrogate key generation with `dbt-utils`
   - Comprehensive model documentation

5. **Data Quality & Testing**
   - Built-in dbt tests (`unique`, `not_null`, `relationships`)
   - Custom business rule tests
   - Data freshness monitoring
   - Referential integrity validation

6. **Documentation & Monitoring**
   - Auto-generated dbt documentation
   - Comprehensive README with examples
   - Health check scripts
   - Performance monitoring queries

## 🚀 Next Steps

1. **Execute the pipeline**: Run `./run_pipeline.sh` 
2. **Explore the data**: Use provided SQL examples
3. **View documentation**: Access `http://localhost:8080`
4. **Monitor pipeline**: Check logs and health metrics

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review log files in `logs/`
3. Test individual components
4. Verify environment configuration

---

**🎯 Project Status**: Production Ready ✅  
**📊 Pipeline Coverage**: Complete ELT Implementation  
**🏆 Quality Score**: All Tests Passing  
**📚 Documentation**: Comprehensive & Auto-Generated