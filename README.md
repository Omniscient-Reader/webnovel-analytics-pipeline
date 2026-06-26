# 📚 Webnovel Analytics Pipeline

An automated, production-ready ETL pipeline that tracks light novel metrics (views, chapters, ratings) from Royal Road, stores historical snapshots in PostgreSQL, and visualizes trends through an interactive Streamlit dashboard.

---

## 📂 Project Structure

```text
webnovel-analytics/
├── Dockerfile                  # Docker container configuration
├── README.md                   # Project documentation
├── app/
│   ├── __init__.py
│   ├── scraper.py              # Core ETL pipeline & web scraper
│   └── dashboard.py            # Streamlit analytics dashboard
├── logs/
│   ├── scraper.log             # General pipeline logs
│   └── scraper_error.log       # Error logs
├── requirements.txt            # Python dependencies
└── tests/
    └── test_scraper.py         # Automated unit tests
```

---

# 💡 Data Engineering Concepts Demonstrated (Quick & Simple)

### 🏗️ ETL Pipeline
Automatically fetches raw web data (**Extract**), cleans it (**Transform**), and loads it into PostgreSQL (**Load**) without manual intervention.

### 🔄 Automated Ingestion
The pipeline visits Royal Road's trending page, discovers newly popular novels, and automatically inserts them into the database.

### 🗄️ Relational Modeling
Separates permanent novel metadata (`novels`) from changing daily metrics (`novel_daily_metrics`) using relational keys and cascading deletes.

### 📸 Historical Snapshots
Stores one snapshot per novel each day without overwriting previous records, enabling complete time-series analysis.

### 🧼 Data Cleaning
Normalizes messy genre URLs and raw scraped values into consistent, structured data.

### ⚙️ Workflow Automation
Runs automatically every night using macOS LaunchAgents (`launchd`) without requiring user interaction.

### 📊 Analytical Visualization
Provides an interactive Streamlit dashboard with Plotly charts for exploring growth trends.

### 🪵 Production Logging & Resiliency

**Auto-Archive**

Uses `RotatingFileHandler` with a 5 MB limit so log files never grow indefinitely.

**Crash Proof**

If one novel fails during processing, the pipeline safely logs the error, rolls back the failed database transaction, and continues processing the remaining novels.

---

# 🛠️ Tech Stack & Tools

| Component | Technology |
|-----------|------------|
| Language | Python 3.10+ |
| Database | PostgreSQL |
| Web Scraping | Requests, BeautifulSoup4 |
| Database Driver | Psycopg2 |
| Data Analysis | Pandas |
| Visualization | Streamlit, Plotly Express |
| Testing | Pytest |
| DevOps | Docker |

---

# 🚀 How to Run Locally

## 1. Setup Environment

Clone the repository and create a `.env` file inside the project root.

```env
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
```

---

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 3. Run Automated Tests

Before executing the pipeline, verify that all tests pass.

```bash
python3 -m pytest tests/
```

---

## 4. Run the ETL Pipeline

Execute the scraper manually.

```bash
python3 app/scraper.py
```

---

## 5. Launch the Analytics Dashboard

Start the interactive Streamlit application.

```bash
streamlit run app/dashboard.py
```

---

# 🐳 Docker Deployment

Build the Docker image.

```bash
docker build -t webnovel-analytics .
```

Run the container.

```bash
docker run -p 8501:8501 --env-file .env webnovel-analytics
```

Open your browser and navigate to:

```
http://localhost:8501
```

to explore the live analytics dashboard.| Database Management | DBeaver | Querying and administration |
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

## 💡 Data Engineering Concepts Demonstrated (Quick & Simple)

* 🏗️ **ETL Pipeline:** Automatically fetches raw web data (**E**xtract), cleans it (**T**ransform), and loads it into the database (**L**oad) without human help.
* 🔄 **Automated Ingestion:** The script automatically visits trending pages, discovers new popular books, and adds them to the database on its own.
* 🗄️ **Relational Modeling:** Separates permanent book info (`novels`) from changing daily numbers (`novel_daily_metrics`) to keep data organized.
* 📸 **Historical Snapshots:** Saves a daily "photo" of statistics without overwriting the past, creating a perfect history log for growth analysis.
* 🧼 **Data Cleaning:** Automatically strips messy web links and converts them into clean, structured text tags (e.g., `Action, Sci-Fi`).
* ⚙️ **Workflow Automation:** Scheduled via macOS `launchd` to run silently in the background every single night while you sleep.
* 📊 **Analytical Visualization:** Turns dry database numbers into a live, interactive timeline chart in your browser using Pandas and Plotly.
* 🪵 **Production Logging & Resiliency:** - **Auto-Archive:** Uses a 5MB cap (`RotatingFileHandler`) so log files never overload your computer's disk space.
  - **Crash Proof:** If one book fails, the script logs the error, rolls back the database safely (`rollback()`), and skips to the next book without crashing.

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
