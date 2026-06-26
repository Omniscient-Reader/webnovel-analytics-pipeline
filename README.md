# 📚 Webnovel Analytics Pipeline

An automated, production-ready ETL pipeline that tracks light novel metrics (views, chapters, ratings) from Royal Road, stores historical snapshots in PostgreSQL, and visualizes trends through an interactive Streamlit dashboard.

---

# 📂 Project Structure

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

# 💡 Data Engineering Concepts Demonstrated

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

Runs automatically every night using macOS LaunchAgents (`launchd`) or cron without requiring user interaction.

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

# 📊 Useful SQL Analytics Queries

Since the pipeline tracks daily time-series metrics, you can run the following SQL queries in your PostgreSQL terminal to extract meaningful insights.

## 1. Top 5 Most Viewed Novels Today

Finds the most popular novels based on the latest crawled snapshot.

```sql
SELECT
    n.title,
    m.view_count,
    m.rating_score,
    m.chapter_count
FROM novel_daily_metrics m
JOIN novels n
    ON m.novel_id = n.novel_id
WHERE m.recorded_date = CURRENT_DATE
ORDER BY m.view_count DESC
LIMIT 5;
```

---

## 2. Novel Growth Tracker (Views Gained Over Time)

Calculates how many new views each novel has gained since it was first tracked.

```sql
SELECT
    n.title,
    MIN(m.view_count) AS initial_views,
    MAX(m.view_count) AS current_views,
    (MAX(m.view_count) - MIN(m.view_count)) AS views_gained
FROM novel_daily_metrics m
JOIN novels n
    ON m.novel_id = n.novel_id
GROUP BY n.title
ORDER BY views_gained DESC;
```

---

## 3. Average Rating and Total Chapters per Genre

Aggregates scraped data to identify which genres perform best.

```sql
SELECT
    n.genre,
    COUNT(DISTINCT n.novel_id) AS total_books,
    ROUND(AVG(m.rating_score)::numeric, 2) AS avg_rating,
    MAX(m.chapter_count) AS max_chapters
FROM novels n
JOIN novel_daily_metrics m
    ON n.novel_id = m.novel_id
WHERE m.recorded_date = CURRENT_DATE
GROUP BY n.genre
ORDER BY total_books DESC;
```

---

# 🚀 How to Run Locally

Follow these step-by-step instructions to clone the repository, configure your environment, and run the pipeline locally.

## 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/webnovel-analytics.git
cd webnovel-analytics
```

> Replace `YOUR_USERNAME` with your actual GitHub username.

---

## 2. Create a Virtual Environment (Recommended)

```bash
# Create the virtual environment
python3 -m venv venv

# Activate on macOS/Linux
source venv/bin/activate

# Activate on Windows PowerShell
# .\venv\Scripts\Activate.ps1
```

---

## 3. Configure Environment Variables

Create a `.env` file in the project root.

```bash
touch .env
```

Fill it with your PostgreSQL credentials.

```env
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
```

---

## 4. Install Dependencies

```bash
python3 -m pip install -r requirements.txt
```

---

## 5. Verify the Installation

Run the automated unit tests.

```bash
python3 -m pytest tests/
```

---

## 6. Run the ETL Pipeline

Execute the scraper manually.

```bash
python3 app/scraper.py
```

---

## 7. Launch the Analytics Dashboard

Start the Streamlit dashboard.

```bash
streamlit run app/dashboard.py
```

Then open:

```
http://localhost:8501
```

in your browser.

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

to explore the live analytics dashboard.
