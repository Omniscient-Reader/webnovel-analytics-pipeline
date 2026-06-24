# 📊 Webnovel Analytics & Time-Series Data Pipeline

An automated data engineering pipeline that scrapes metadata and performance metrics from Royal Road novels, stores daily snapshots in PostgreSQL, and tracks growth trends over time.

Designed to run as a lightweight background service on macOS using native scheduling tools.

---

## 🏗️ Architecture & Data Flow

The project separates novel metadata from daily performance metrics to support historical analysis and time-series forecasting.

### Workflow

1. **Target Tracking (`novels` table)**
   - Stores Royal Road novel URLs and static metadata.

2. **Extraction Engine (`scraper.py`)**
   - Retrieves novel pages using randomized user agents.
   - Extracts metrics such as views, chapter count, and rating score.

3. **Historical Storage (`novel_daily_metrics` table)**
   - Records daily metric snapshots.
   - Preserves historical data for trend analysis.

4. **Automation (`launchd`)**
   - Runs the scraper automatically every night.
   - Continues running even when no terminal window is open.

---

## 🛠️ Tech Stack

| Component | Technology |
|------------|------------|
| Language | Python 3 |
| Database | PostgreSQL |
| Database Management | DBeaver |
| Scraping | Requests, BeautifulSoup4, fake-useragent |
| Database Driver | psycopg2-binary |
| Configuration | python-dotenv |
| Scheduling | macOS launchd |

---

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Omniscient-Reader/webnovel-analytics-pipeline.git
cd webnovel-analytics-pipeline
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install requests beautifulsoup4 fake-useragent psycopg2-binary python-dotenv
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
DB_NAME=webnovel_analytics
DB_USER=your_db_username
DB_PASS=your_secure_password
DB_HOST=localhost
DB_PORT=5432
```

The `.env` file should remain excluded from version control.

---

## 🗄️ Database Schema

Run the following SQL script in PostgreSQL:

```sql
CREATE TABLE novels (
    novel_id SERIAL PRIMARY KEY,
    source_url VARCHAR(500) UNIQUE NOT NULL,
    title VARCHAR(255),
    author VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE novel_daily_metrics (
    metric_id SERIAL PRIMARY KEY,
    novel_id INT REFERENCES novels(novel_id) ON DELETE CASCADE,
    recorded_date DATE DEFAULT CURRENT_DATE,
    view_count INT,
    chapter_count INT,
    rating_score NUMERIC(4,2),
    UNIQUE (novel_id, recorded_date)
);
```

---

## ▶️ Running the Scraper

Execute the scraper manually:

```bash
python3 scraper.py
```

Example output:

```text
Scraping: https://www.royalroad.com/fiction/21220/mother-of-learning

Mother of Learning
Views: 247631
Chapters: 109
Rating: 4.83

Saved snapshot successfully.
```

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

### Run a Test Execution

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
├── requirements.txt
├── .env
├── .gitignore
├── com.devsoul.novelfetcher.plist
└── README.md
```

---

## 📈 Future Improvements

- Growth-rate calculations
- Daily ranking change tracking
- Automated anomaly detection
- Dashboard visualization with Streamlit
- Forecasting models for view growth
- Multi-source scraping support

---

## 📄 License

This project is intended for educational and portfolio purposes.

---

## 💡 Data Engineering Concepts Demonstrated

- Web scraping and data extraction
- Scheduled ETL pipelines
- PostgreSQL relational database design
- Time-series data modeling
- Environment-based secret management
- Automated background job scheduling
- Historical snapshot tracking
- Defensive data collection practices
