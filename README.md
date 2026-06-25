# 📊 Webnovel Analytics & Time-Series Data Pipeline

An automated data engineering pipeline that dynamically discovers popular Royal Road novels, scrapes daily performance metrics, stores snapshots in PostgreSQL, and tracks growth trends over time.

Designed to run as a lightweight background service on macOS using native scheduling tools.

---

## 🏗️ Architecture & Data Flow

The project separates novel metadata from daily performance metrics to support historical analysis and time-series forecasting.

### Workflow

### 1. Automated Discovery Engine
- Scrapes Royal Road's Active Popular page to dynamically discover trending novels.
- Automatically inserts newly discovered novels into the database.

### 2. Target Tracking (`novels` table)
- Stores novel URLs, titles, authors, genres, and metadata.
- Serves as the central catalog of tracked novels.

### 3. Extraction Engine (`scraper.py`)
- Retrieves active novel pages using custom request headers.
- Extracts:
  - Total views
  - Chapter count
  - Rating score
  - Author information
  - Genre information
- Normalizes raw genre values into a consistent format.

### 4. Historical Storage (`novel_daily_metrics` table)
- Records daily metric snapshots.
- Uses PostgreSQL upserts (`ON CONFLICT`) to prevent duplicate records.
- Preserves historical data for trend analysis and forecasting.

### 5. Automation (`launchd`)
- Executes the pipeline automatically every night.
- Runs silently in the background without requiring an active terminal session.

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|------------|------------|---------|
| Language | Python 3 | Core ETL logic |
| Database | PostgreSQL | Relational data storage |
| Database Management | DBeaver | Querying and administration |
| Scraping | Requests, BeautifulSoup4 | Data extraction |
| Database Driver | psycopg2-binary | PostgreSQL connectivity |
| Data Analytics | Pandas | Data manipulation |
| Visualization | Plotly Express | Interactive dashboards |
| Configuration | python-dotenv | Environment management |
| Scheduling | macOS launchd | Background job scheduling |

---

## 📈 Analytical Capabilities

The schema is designed for time-series analytics and supports advanced SQL analysis.

### Genre Popularity Analysis

Genres are stored as comma-separated values and can be expanded using PostgreSQL functions:

```sql
SELECT
    TRIM(genre_name) AS genre,
    SUM(view_count) AS total_views
FROM (
    SELECT
        UNNEST(STRING_TO_ARRAY(n.genre, ',')) AS genre_name,
        m.view_count
    FROM novels n
    JOIN novel_daily_metrics m
        ON n.novel_id = m.novel_id
) t
GROUP BY genre
ORDER BY total_views DESC;
```

### Daily Growth Tracking

Measure daily view growth using window functions:

```sql
SELECT
    novel_id,
    recorded_date,
    view_count,
    view_count -
    LAG(view_count)
        OVER (
            PARTITION BY novel_id
            ORDER BY recorded_date
        ) AS daily_growth
FROM novel_daily_metrics;
```

---

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Omniscient-Reader/webnovel-analytics-pipeline.git

cd webnovel-analytics-pipeline
```

### 2. Install Dependencies

```bash
pip install requests beautifulsoup4 psycopg2-binary python-dotenv pandas plotly
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
DB_NAME=webnovel_analytics
DB_USER=your_db_username
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
```

---

## 🗄️ Database Schema

Run the following SQL script in PostgreSQL:

```sql
CREATE TABLE novels (
    novel_id SERIAL PRIMARY KEY,
    source_url VARCHAR(255) UNIQUE NOT NULL,
    title VARCHAR(255),
    author TEXT,
    genre TEXT,
    chapter_count INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE novel_daily_metrics (
    metric_id SERIAL PRIMARY KEY,
    novel_id INT REFERENCES novels(novel_id) ON DELETE CASCADE,
    recorded_date DATE DEFAULT CURRENT_DATE,
    view_count BIGINT,
    chapter_count INT,
    rating_score NUMERIC(3,2),
    UNIQUE (novel_id, recorded_date)
);
```

**Note:** `view_count` uses `BIGINT` to safely accommodate large traffic volumes.

---

## ▶️ Running the Pipeline

Execute the scraper manually:

```bash
python3 scraper.py
```

The scraper will:

- Discover trending novels
- Update novel metadata
- Record daily snapshots
- Store results in PostgreSQL

---

## 📊 Interactive Data Visualization

The project includes a dedicated visualization module powered by Plotly Express and Pandas.

### Run the Visualizer

```bash
python3 visualize.py
```

### Features

- Interactive line charts
- Browser-based visualization
- Zoom and pan support
- Hover tooltips
- Multi-novel comparison
- Time-series trend tracking

---

## ⏰ Background Automation (macOS)

### Copy the Launch Agent

```bash
cp com.devsoul.novelfetcher.plist ~/Library/LaunchAgents/
```

### Load the Schedule

```bash
launchctl load ~/Library/LaunchAgents/com.devsoul.novelfetcher.plist
```

### Run a Test

```bash
launchctl start com.devsoul.novelfetcher
```

### Verify Status

```bash
launchctl list | grep novelfetcher
```

---

## 📂 Project Structure

```text
webnovel-analytics-pipeline/
│
├── scraper.py
├── visualize.py
├── .env
├── .gitignore
└── README.md
```

---

## 💡 Data Engineering Concepts Demonstrated

- ETL pipeline development
- Automated data ingestion
- PostgreSQL relational modeling
- Time-series data storage
- Historical snapshot tracking
- Data cleaning and normalization
- Scheduled workflow automation
- Interactive analytical visualization

---

## 📈 Future Improvements

- Daily ranking change tracking
- Automated anomaly detection
- Data quality monitoring
- Forecasting models for growth prediction
- Multi-source scraping support
- Streamlit analytics dashboard
- Docker containerization
- Apache Airflow orchestration

---

## 📄 License

This project is intended for educational, research, and portfolio purposes.
