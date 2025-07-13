# Telegram Medical Data Pipline

A comprehensive ELT (Extract, Load, Transform) data pipeline that collects Telegram channel messages, stores them in a data lake, loads them into a PostgreSQL data warehouse, and transforms them into an analytical star schema using dbt.

## 🏗️ Architecture Overview

```
Telegram API → Raw Data Lake → PostgreSQL (Raw) → dbt Transformations → Analytics Schema
     ↓              ↓              ↓                    ↓
  scrape.py    JSON Files    load_raw_data.py    Star Schema Tables
```

## 🎯 Project Objectives

- **Extract**: Scrape message data from public Telegram channels using Telethon
- **Load**: Store raw data in partitioned JSON files and PostgreSQL raw schema
- **Transform**: Create dimensional star schema for analytics using dbt
- **Quality**: Implement comprehensive testing and documentation

## 📊 Data Model

### Star Schema Design
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

## 🚀 Complete Setup Guide

### Prerequisites
- Docker & Docker Compose (20.10+)
- Python 3.8+
- PostgreSQL 13+ (local installation)
- Telegram API credentials (from my.telegram.org)

### Step 1: Environment Preparation

#### 1.1 Clone Repository
```bash
git clone <repository-url>
cd telegram_data_product
```

#### 1.2 Python Virtual Environment
```bash
# Create and activate virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 1.3 PostgreSQL Setup
```bash
# Connect to PostgreSQL as superuser
psql -U postgres

# Create database and user
CREATE DATABASE telegram_warehouse;
CREATE USER telegram_user WITH PASSWORD 'secure_password_123';
GRANT ALL PRIVILEGES ON DATABASE telegram_warehouse TO telegram_user;
\q
```

### Step 2: Configuration

#### 2.1 Environment Variables
Create `.env` file in project root:
```env
# Telegram API Configuration (Get from https://my.telegram.org)
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

#### 2.2 dbt Profile Configuration
Create `~/.dbt/profiles.yml`:
```yaml
telegram_project:
  target: dev
  outputs:
    dev:
      type: postgres
      host: host.docker.internal
      user: "{{ env_var('POSTGRES_USER') }}"
      password: "{{ env_var('POSTGRES_PASSWORD') }}"
      port: 5432
      dbname: "{{ env_var('POSTGRES_DB') }}"
      schema: analytics
      threads: 4
      keepalives_idle: 0
```

### Step 3: Running the Complete Pipeline

#### 3.1 Docker Method (Recommended)
```bash
# Build and start containers
docker-compose up --build -d

# Verify containers are running
docker-compose ps

# Execute complete pipeline
./run_pipeline.sh
```

#### 3.2 Manual Step-by-Step Execution
```bash
# Step 1: Data Extraction
docker exec telegram_app python src/scrape.py

# Step 2: Data Loading
docker exec telegram_app python src/load_raw_data.py

# Step 3: dbt Transformations
docker exec telegram_app dbt run --project-dir telegram_dbt_project

# Step 4: Data Quality Tests
docker exec telegram_app dbt test --project-dir telegram_dbt_project

# Step 5: Generate Documentation
docker exec telegram_app dbt docs generate --project-dir telegram_dbt_project
docker exec telegram_app dbt docs serve --project-dir telegram_dbt_project --port 8080
```

### Step 4: Verification

#### 4.1 Data Verification
```bash
# Check raw data files
ls -la data/raw/telegram_messages/

# Verify PostgreSQL data
docker exec telegram_app psql -h localhost -U telegram_user -d telegram_warehouse -c "SELECT COUNT(*) FROM raw.telegram_messages;"

# Check analytics tables
docker exec telegram_app psql -h localhost -U telegram_user -d telegram_warehouse -c "SELECT COUNT(*) FROM analytics.fct_messages;"
```

## 📁 Project Structure

```
Telegram Medical Data Pipline/
├── src/                           # Source code
│   ├── scrape.py                 # Telegram data extraction
│   ├── load_raw_data.py          # Raw data loading to PostgreSQL
│   └── config.py                 # Configuration management
├── telegram_dbt_project/         # dbt project
│   ├── models/
│   │   ├── staging/
│   │   │   ├── stg_telegram_messages.sql  # Staging transformations
│   │   │   └── sources.yml               # Source definitions
│   │   └── marts/
│   │       ├── dim_channels.sql          # Channel dimension
│   │       ├── dim_dates.sql             # Date dimension
│   │       ├── fct_messages.sql          # Message fact table
│   │       └── schema.yml                # Model tests and docs
│   ├── tests/
│   │   └── no_negative_views.sql         # Custom data test
│   ├── dbt_project.yml                   # dbt configuration
│   └── packages.yml                      # dbt packages
├── data/
│   └── raw/
│       └── telegram_messages/            # Raw data lake
│           └── YYYY-MM-DD/
│               └── channel_name.json
├── logs/                                 # Application logs
├── docker-compose.yml                    # Docker orchestration
├── Dockerfile                           # Container definition
├── requirements.txt                     # Python dependencies
├── .env                                 # Environment variables
├── .gitignore                          # Git ignore rules
├── run_pipeline.sh                     # Pipeline execution script
└── README.md                           # This file
```

## 🔧 Detailed Component Documentation

### 1. Data Extraction (`src/scrape.py`)

**Purpose**: Asynchronously scrapes messages from specified Telegram channels using Telethon

**Key Features**:
- Concurrent processing of multiple channels
- Comprehensive logging with rotation
- Media metadata extraction (photos, documents, videos)
- Date-based partitioning for efficient storage
- Error handling and retry mechanisms
- Session management for authentication

**Configuration**:
```python
# Edit TARGET_CHANNELS in src/scrape.py
TARGET_CHANNELS = [
    '@CheMed123',
    '@lobelia4cosmetics',
    '@tikvahpharma'
]

# Adjust message limits
MESSAGE_LIMIT = 100  # Messages per channel
```

**Output Format**:
```json
{
  "message_id": 123,
  "date": "2024-01-15T10:30:00+00:00",
  "text": "Sample message text",
  "views": 150,
  "forwards": 5,
  "replies": 2,
  "media_type": "photo",
  "file_name": "image.jpg",
  "file_size": 1024000,
  "channel_username": "channel1",
  "channel_title": "Sample Channel"
}
```

### 2. Data Loading (`src/load_raw_data.py`)

**Purpose**: Loads raw JSON data into PostgreSQL with incremental processing

**Key Features**:
- Incremental loading (prevents duplicates)
- JSONB storage for flexible querying
- Transaction management with rollback
- Comprehensive error handling
- Progress tracking and logging

**Database Schema**:
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

### 3. dbt Transformations

#### 3.1 Staging Layer (`models/staging/`)

**`stg_telegram_messages.sql`**:
- Extracts and cleans data from raw JSONB
- Handles null values and type casting
- Standardizes column names
- Applies basic business rules

```sql
-- Example transformation
SELECT 
    (message_data->>'message_id')::BIGINT as message_id,
    COALESCE((message_data->>'views')::INT, 0) as views_count,
    TO_TIMESTAMP(message_data->>'date', 'YYYY-MM-DD"T"HH24:MI:SS') as created_at,
    -- ... other transformations
FROM {{ source('telegram_raw', 'telegram_messages') }}
```

#### 3.2 Mart Layer (`models/marts/`)

**Dimensional Tables**:
- `dim_channels`: Channel information with surrogate keys
- `dim_dates`: Date dimension with calendar attributes
- `fct_messages`: Central fact table with metrics

**Relationships**:
```sql
-- Foreign key relationships in fct_messages
{{ ref('dim_channels') }} ON channel_pk
{{ ref('dim_dates') }} ON date_pk
```

### 4. Testing Strategy

#### 4.1 Built-in dbt Tests
```yaml
# In models/marts/schema.yml
tests:
  - unique:
      column_name: channel_pk
  - not_null:
      column_name: channel_username
  - relationships:
      to: ref('dim_channels')
      field: channel_pk
```

#### 4.2 Custom Tests
```sql
-- tests/no_negative_views.sql
SELECT *
FROM {{ ref('fct_messages') }}
WHERE views_count < 0
```

#### 4.3 Test Execution
```bash
# Run all tests
dbt test --project-dir telegram_dbt_project

# Run specific test type
dbt test --select test_type:generic --project-dir telegram_dbt_project
dbt test --select test_type:singular --project-dir telegram_dbt_project

# Test specific model
dbt test --select fct_messages --project-dir telegram_dbt_project
```

## 🚀 Complete Pipeline Execution

### Automated Pipeline Script (`run_pipeline.sh`)
```bash
#!/bin/bash
set -e

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
echo "📊 Access documentation at: http://localhost:8080"
```

### Make script executable:
```bash
chmod +x run_pipeline.sh
```

## 🔍 Monitoring and Logging

### Log Files and Locations
```
logs/
├── scrape.log              # Data extraction logs
├── load_raw_data.log       # Data loading logs
└── dbt.log                 # dbt transformation logs
```

### Log Monitoring
```bash
# Real-time log monitoring
tail -f logs/scrape.log
tail -f logs/load_raw_data.log

# Log analysis
grep "ERROR" logs/*.log
grep "WARNING" logs/*.log
```

### Health Checks
```bash
# Container health
docker-compose ps

# Database connectivity
docker exec telegram_app python -c "
from src.config import get_db_connection
try:
    conn = get_db_connection()
    print('✅ Database connection successful')
    conn.close()
except Exception as e:
    print(f'❌ Database connection failed: {e}')
"

# dbt connection
docker exec telegram_app dbt debug --project-dir telegram_dbt_project
```

## 📈 Usage Examples and Analytics

### Basic Analytics Queries
```sql
-- 1. Top performing channels by engagement
SELECT 
    dc.channel_username,
    dc.channel_title,
    COUNT(*) as total_messages,
    AVG(fm.views_count) as avg_views,
    SUM(fm.forwards_count) as total_forwards,
    SUM(fm.replies_count) as total_replies
FROM analytics.fct_messages fm
JOIN analytics.dim_channels dc ON fm.channel_pk = dc.channel_pk
GROUP BY dc.channel_pk, dc.channel_username, dc.channel_title
ORDER BY avg_views DESC
LIMIT 10;

-- 2. Daily message trends with engagement metrics
SELECT 
    dd.scraped_date,
    dd.day_of_week,
    COUNT(*) as message_count,
    AVG(fm.views_count) as avg_views,
    SUM(fm.views_count) as total_views,
    COUNT(CASE WHEN fm.media_type IS NOT NULL THEN 1 END) as media_messages
FROM analytics.fct_messages fm
JOIN analytics.dim_dates dd ON fm.date_pk = dd.date_pk
GROUP BY dd.date_pk, dd.scraped_date, dd.day_of_week
ORDER BY dd.scraped_date DESC;

-- 3. Media type distribution analysis
SELECT 
    fm.media_type,
    COUNT(*) as message_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage,
    AVG(fm.views_count) as avg_views
FROM analytics.fct_messages fm
WHERE fm.media_type IS NOT NULL
GROUP BY fm.media_type
ORDER BY message_count DESC;

-- 4. Channel performance comparison
SELECT 
    dc.channel_username,
    COUNT(*) as messages,
    AVG(fm.views_count) as avg_views,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY fm.views_count) as median_views,
    MAX(fm.views_count) as max_views,
    COUNT(CASE WHEN fm.forwards_count > 0 THEN 1 END) as forwarded_messages
FROM analytics.fct_messages fm
JOIN analytics.dim_channels dc ON fm.channel_pk = dc.channel_pk
GROUP BY dc.channel_pk, dc.channel_username
HAVING COUNT(*) > 10
ORDER BY avg_views DESC;
```

### Advanced Analytics
```sql
-- 5. Weekly engagement trends
SELECT 
    DATE_TRUNC('week', dd.scraped_date) as week_start,
    COUNT(*) as weekly_messages,
    AVG(fm.views_count) as avg_weekly_views,
    SUM(fm.forwards_count) as weekly_forwards
FROM analytics.fct_messages fm
JOIN analytics.dim_dates dd ON fm.date_pk = dd.date_pk
GROUP BY DATE_TRUNC('week', dd.scraped_date)
ORDER BY week_start DESC;

-- 6. Content performance by length
SELECT 
    CASE 
        WHEN LENGTH(fm.message_text) <= 100 THEN 'Short (≤100)'
        WHEN LENGTH(fm.message_text) <= 500 THEN 'Medium (101-500)'
        ELSE 'Long (>500)'
    END as message_length_category,
    COUNT(*) as message_count,
    AVG(fm.views_count) as avg_views,
    AVG(fm.forwards_count) as avg_forwards
FROM analytics.fct_messages fm
WHERE fm.message_text IS NOT NULL
GROUP BY 
    CASE 
        WHEN LENGTH(fm.message_text) <= 100 THEN 'Short (≤100)'
        WHEN LENGTH(fm.message_text) <= 500 THEN 'Medium (101-500)'
        ELSE 'Long (>500)'
    END
ORDER BY avg_views DESC;
```

## 🛠️ Troubleshooting Guide

### Common Issues and Solutions

#### 1. Telegram Authentication Issues
**Problem**: Authentication fails or session expires
```bash
# Solution: Clear session and re-authenticate
rm telegram_scraper_session.session*
docker exec -it telegram_app python src/scrape.py
# Follow prompts to enter verification code
```

#### 2. Database Connection Problems
**Problem**: Can't connect to PostgreSQL
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Verify credentials
docker exec telegram_app python src/config.py

# Test connection manually
docker exec telegram_app psql -h localhost -U telegram_user -d telegram_warehouse -c "SELECT 1;"
```

#### 3. Docker Issues
**Problem**: Container fails to start
```bash
# Check logs
docker-compose logs app

# Rebuild containers
docker-compose down
docker-compose up --build -d

# Clear Docker cache if needed
docker system prune -f
```

#### 4. dbt Connection Issues
**Problem**: dbt can't connect to database
```bash
# Debug dbt connection
docker exec telegram_app dbt debug --project-dir telegram_dbt_project

# Check profiles.yml
docker exec telegram_app cat ~/.dbt/profiles.yml

# Verify environment variables
docker exec telegram_app env | grep POSTGRES
```

#### 5. Data Quality Issues
**Problem**: Tests fail or data looks incorrect
```bash
# Run specific tests
docker exec telegram_app dbt test --select no_negative_views --project-dir telegram_dbt_project

# Check source data
docker exec telegram_app psql -h localhost -U telegram_user -d telegram_warehouse -c "
SELECT message_data->>'views' as views, COUNT(*) 
FROM raw.telegram_messages 
GROUP BY message_data->>'views' 
ORDER BY COUNT(*) DESC LIMIT 10;
"
```

### Error Codes and Solutions

| Error Code | Description | Solution |
|------------|-------------|----------|
| `CONN_001` | Database connection failed | Check PostgreSQL service and credentials |
| `AUTH_001` | Telegram authentication failed | Re-authenticate with fresh session |
| `DBT_001` | dbt compilation error | Check SQL syntax in models |
| `DATA_001` | Data quality test failed | Investigate source data quality |
| `DOCKER_001` | Container startup failed | Check Docker logs and rebuild |

## 🔄 Maintenance and Operations

### Daily Operations
```bash
# Quick health check
./health_check.sh

# Run incremental pipeline
./run_pipeline.sh

# Check data freshness
docker exec telegram_app dbt source freshness --project-dir telegram_dbt_project
```

### Weekly Maintenance
```bash
# Full data refresh
docker exec telegram_app dbt run --full-refresh --project-dir telegram_dbt_project

# Comprehensive testing
docker exec telegram_app dbt test --project-dir telegram_dbt_project

# Log rotation
find logs/ -name "*.log" -size +100M -exec gzip {} \;
```

### Monthly Tasks
```bash
# Update documentation
docker exec telegram_app dbt docs generate --project-dir telegram_dbt_project

# Performance analysis
docker exec telegram_app psql -h localhost -U telegram_user -d telegram_warehouse -f maintenance/performance_analysis.sql

# Backup database
pg_dump -h localhost -U telegram_user telegram_warehouse > backup_$(date +%Y%m%d).sql
```

## 📊 Performance Optimization

### Database Optimization
```sql
-- Create indexes for better query performance
CREATE INDEX idx_fct_messages_date ON analytics.fct_messages(date_pk);
CREATE INDEX idx_fct_messages_channel ON analytics.fct_messages(channel_pk);
CREATE INDEX idx_raw_messages_date ON raw.telegram_messages(scraped_date);

-- Analyze table statistics
ANALYZE analytics.fct_messages;
ANALYZE analytics.dim_channels;
ANALYZE analytics.dim_dates;
```

### dbt Optimization
```yaml
# In dbt_project.yml
models:
  telegram_dbt_project:
    marts:
      +materialized: table
      +indexes:
        - columns: [date_pk]
        - columns: [channel_pk]
```

## 🤝 Contributing Guidelines

### Development Setup
```bash
# Fork repository
git clone https://github.com/yourusername/telegram_data_product.git

# Create feature branch
git checkout -b feature/your-feature-name

# Install development dependencies
pip install -r requirements-dev.txt

# Run pre-commit hooks
pre-commit install
```

### Code Standards
- Follow PEP 8 for Python code
- Use meaningful variable names and functions
- Include docstrings for all functions
- Add inline comments for complex logic
- Update tests when adding new features

### Pull Request Process
1. Ensure all tests pass
2. Update documentation if needed
3. Add/update tests for new features
4. Follow conventional commit messages
5. Request review from maintainers

## 📋 System Requirements

### Minimum Requirements
- **CPU**: 2 cores
- **RAM**: 4GB
- **Storage**: 10GB free space
- **Network**: Stable internet connection

### Recommended Requirements
- **CPU**: 4+ cores
- **RAM**: 8GB+
- **Storage**: 50GB+ SSD
- **Network**: High-speed internet

### Software Dependencies
```
Docker: 20.10+
Docker Compose: 2.0+
Python: 3.8+
PostgreSQL: 13+
Git: 2.30+
```

## 🔒 Security Considerations

### Environment Security
- Never commit `.env` files to version control
- Use strong passwords for database credentials
- Regularly rotate API keys and passwords
- Limit database user permissions

### Data Privacy
- Comply with applicable data protection regulations
- Implement data retention policies
- Consider anonymization for sensitive data
- Regular security audits

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support and Contact

### Getting Help
1. Check this README for common solutions
2. Review the troubleshooting section
3. Check existing issues in the repository
4. Create a new issue with detailed information

### Issue Template
When creating issues, include:
- Operating system and version
- Python version
- Docker version
- Complete error message
- Steps to reproduce
- Expected vs actual behavior

### Community
- **Documentation**: [Project Wiki](wiki-link)
- **Issues**: [GitHub Issues](issues-link)
- **Discussions**: [GitHub Discussions](discussions-link)

---

**⚠️ Important Notes:**
- This project is for educational purposes
- Ensure compliance with Telegram's Terms of Service
- Follow applicable data protection regulations
- Test thoroughly before production use
- Keep dependencies updated for security

**🌟 Project Status:** Active Development

**📊 Current Version:** 1.0.0

**🏆 Quality Assurance:** All tests passing ✅