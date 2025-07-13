# Telegram Data Engineering Project

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

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.8+
- PostgreSQL (local installation)
- Telegram API credentials

### 1. Clone Repository
```bash
git clone <repository-url>
cd telegram_data_product
```

### 2. Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create `.env` file in project root:
```env
# Telegram API Configuration
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
PHONE_NUMBER=your_phone_number

# PostgreSQL Configuration
POSTGRES_DB=telegram_warehouse
POSTGRES_USER=telegram_user
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

### 4. Database Setup
```bash
# Connect to PostgreSQL
psql -U postgres

# Create database and user
CREATE DATABASE telegram_warehouse;
CREATE USER telegram_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE telegram_warehouse TO telegram_user;
```

### 5. Run the Pipeline

#### Option A: Using Docker (Recommended)
```bash
# Build and start containers
docker-compose up --build -d

# Execute scraping
docker exec telegram_app python src/scrape.py

# Load raw data to PostgreSQL
docker exec telegram_app python src/load_raw_data.py

# Run dbt transformations
docker exec telegram_app dbt run --project-dir telegram_dbt_project

# Run dbt tests
docker exec telegram_app dbt test --project-dir telegram_dbt_project
```

#### Option B: Local Development
```bash
# Activate virtual environment
source venv/bin/activate

# Run scraping
python src/scrape.py

# Load raw data
python src/load_raw_data.py

# Run dbt (from project root)
cd telegram_dbt_project
dbt run
dbt test
```

## 📁 Project Structure

```
telegram_data_product/
├── src/
│   ├── scrape.py              # Telegram data extraction
│   ├── load_raw_data.py       # Raw data loading to PostgreSQL
│   └── config.py              # Configuration management
├── telegram_dbt_project/
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
│   └── dbt_project.yml
├── data/
│   └── raw/
│       └── telegram_messages/
│           └── YYYY-MM-DD/
│               └── channel_name.json
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env
└── README.md
```

## 🔧 Data Pipeline Components

### 1. Data Extraction (`src/scrape.py`)
- **Purpose**: Scrapes messages from specified Telegram channels
- **Technology**: Telethon (Telegram API client)
- **Output**: Partitioned JSON files in `data/raw/telegram_messages/`
- **Features**:
  - Asynchronous processing for multiple channels
  - Comprehensive logging
  - Media metadata extraction
  - Date-based partitioning

### 2. Data Loading (`src/load_raw_data.py`)
- **Purpose**: Loads raw JSON data into PostgreSQL
- **Target**: `raw.telegram_messages` table
- **Features**:
  - Incremental loading (prevents duplicates)
  - JSONB storage for flexible querying
  - Transaction management
  - Error handling and logging

### 3. Data Transformation (dbt)
- **Purpose**: Transforms raw data into analytical star schema
- **Layers**:
  - **Staging**: `stg_telegram_messages` - initial cleaning and type casting
  - **Marts**: Dimensional tables for analytics
- **Features**:
  - Surrogate key generation
  - Referential integrity
  - Comprehensive testing

## 🧪 Testing Strategy

### Built-in dbt Tests
- **Uniqueness**: Primary keys in all dimension tables
- **Not Null**: Critical columns cannot be empty
- **Relationships**: Foreign key integrity between fact and dimension tables

### Custom Tests
- **Business Rules**: `no_negative_views.sql` ensures views_count ≥ 0
- **Data Quality**: Custom SQL tests for specific business logic

### Running Tests
```bash
# Run all tests
docker exec telegram_app dbt test --project-dir telegram_dbt_project

# Run specific test
docker exec telegram_app dbt test --select test_name --project-dir telegram_dbt_project
```

## 📖 Documentation

### Generate dbt Documentation
```bash
# Generate documentation
docker exec telegram_app dbt docs generate --project-dir telegram_dbt_project

# Serve documentation locally
docker exec telegram_app dbt docs serve --project-dir telegram_dbt_project --port 8080
```

Access documentation at: `http://localhost:8080`

## 🔍 Data Quality & Monitoring

### Logging
- **Scraping**: `scrape.log` - tracks extraction progress and errors
- **Loading**: `load_raw_data.log` - monitors data loading operations
- **Transformations**: dbt logs - transformation and test results

### Data Validation
- Automated tests run with each dbt execution
- Data freshness checks
- Schema validation
- Business rule enforcement

## 🚨 Troubleshooting

### Common Issues

#### 1. Telegram Authentication
```bash
# If authentication fails, remove session file and re-authenticate
rm telegram_scraper_session.session*
python src/scrape.py
```

#### 2. Database Connection
```bash
# Test PostgreSQL connection
docker exec telegram_app python src/config.py
```

#### 3. dbt Connection Issues
```bash
# Debug dbt connection
docker exec telegram_app dbt debug --project-dir telegram_dbt_project
```

### Log Locations
- Scraping logs: `scrape.log`
- Loading logs: `load_raw_data.log`
- dbt logs: `telegram_dbt_project/logs/`

## 📈 Usage Examples

### Query the Analytics Schema
```sql
-- Top channels by message volume
SELECT 
    dc.channel_username,
    COUNT(*) as message_count,
    AVG(fm.views_count) as avg_views
FROM analytics.fct_messages fm
JOIN analytics.dim_channels dc ON fm.channel_pk = dc.channel_pk
GROUP BY dc.channel_username
ORDER BY message_count DESC;

-- Daily message trends
SELECT 
    dd.scraped_date,
    COUNT(*) as daily_messages,
    SUM(fm.views_count) as total_views
FROM analytics.fct_messages fm
JOIN analytics.dim_dates dd ON fm.date_pk = dd.date_pk
GROUP BY dd.scraped_date
ORDER BY dd.scraped_date;
```

## 🔄 Maintenance

### Regular Operations
```bash
# Daily data refresh
docker exec telegram_app python src/scrape.py
docker exec telegram_app python src/load_raw_data.py
docker exec telegram_app dbt run --project-dir telegram_dbt_project

# Weekly testing
docker exec telegram_app dbt test --project-dir telegram_dbt_project
```

### Adding New Channels
Edit `TARGET_CHANNELS` list in `src/scrape.py`:
```python
TARGET_CHANNELS = [
    '@existing_channel',
    '@new_channel_to_add'
]
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -m 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit pull request

## 📋 Requirements

### Python Dependencies
```
telethon>=1.24.0
psycopg2-binary>=2.9.0
python-dotenv>=0.19.0
dbt-postgres>=1.4.0
```

### System Requirements
- Docker 20.10+
- Docker Compose 2.0+
- PostgreSQL 13+
- Python 3.8+

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For questions or issues:
1. Check the troubleshooting section
2. Review logs in the respective log files
3. Open an issue in the repository

---

**Note**: This project is for educational purposes. Ensure compliance with Telegram's Terms of Service and applicable data protection regulations when scraping data.