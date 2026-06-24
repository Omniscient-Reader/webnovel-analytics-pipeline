# 📊 Webnovel Analytics & Time-Series Data Pipeline

An automated, secure data engineering pipeline that scrapes metadata and 
performance metrics from Royal Road novels, logs daily snapshots into a 
PostgreSQL time-series database, and tracks growth velocity over time. 

Built defensively to run seamlessly as a background microservice on macOS 
using native automation tools.

---

## 🏗️ Architecture & Data Flow

The project separates core book identity information from daily 
performance metrics to enable clean time-series forecasting and trend 
mapping.

1. **Target Tracking (novels table):** The scraping engine scans this 
table for novel source URLs.
2. **Extraction Engine (scraper.py):** Hits Royal Road using dynamic 
headers via fake-useragent and parses active metrics (Views, Chapters, 
Ratings) via BeautifulSoup.
3. **Historical Storage (novel_daily_metrics table):** Appends a 
structured chronological snapshot mapped directly to a historical 
timeline.
4. **Automation (launchd / Daemon):** Triggers silently every night at 
midnight, running independent of terminal window sessions.

---

## 🛠️ Tech Stack & Dependencies

* Language: Python 3.13+
* Database: PostgreSQL (with DBeaver for database management)
* Scraping Libraries: requests, BeautifulSoup4, fake-useragent
* Database Driver: psycopg2-binary
* Security: python-dotenv (keeps environmental secrets isolated)
* OS Scheduler: Apple launchd

---

## 🚀 Local Installation & Setup

### 1. Clone & Initialize Workspace
git clone 
[https://github.com/Omniscient-Reader/webnovel-analytics-pipeline.git](https://github.com/Omniscient-Reader/webnovel-analytics-pipeline.git)
cd webnovel-analytics-pipeline
2. Configure Environment Secrets
Create a .env file in the root directory (this file is excluded from Git 
tracking via .gitignore to protect production database passwords):
Plaintext
DB_NAME=webnovel_analytics
DB_USER=your_db_username
DB_PASS=your_secure_password
DB_HOST=localhost
DB_PORT=5432
3. Create the Database Schema
Execute the following DDL script inside your PostgreSQL SQL editor to 
prepare the storage schemas:
SQL
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
    rating_score NUMERIC(3,2),
    UNIQUE (novel_id, recorded_date)
);
4. Running the Scraper Manually
Plaintext
python3 scraper.py
⏰ Background Automation Setup (macOS)
The background pipeline runs automatically every night at 00:00 
(Midnight). To register the daemon with macOS launch services:
Copy the tracking .plist profile file into your local system library:
Plaintext
cp com.devsoul.novelfetcher.plist ~/Library/LaunchAgents/
Activate and load the automated schedule:
Plaintext
launchctl load ~/Library/LaunchAgents/com.devsoul.novelfetcher.plist
Force a test trigger to confirm database entry population:
Plaintext
launchctl start com.devsoul.novelfetcher
