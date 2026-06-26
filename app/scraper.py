import os
import json
import re
import requests
from bs4 import BeautifulSoup
import psycopg2
from datetime import datetime
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "scraper.log"

load_dotenv(dotenv_path=BASE_DIR / ".env")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if logger.hasHandlers():
    logger.handlers.clear()

formatter = logging.Formatter('%(asctime)s [%(levelname)s] [%(name)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding='utf-8')
file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Accept-Language": "en-US,en;q=0.9"
}

def clean_single_genre(genre_str):
    if not genre_str or not isinstance(genre_str, str):
        return "Unknown"
    if "http" in genre_str or "/" in genre_str:
        match = re.search(r'(?:genre=|/tag/|/genres/)([^&]+)', genre_str, re.IGNORECASE)
        if match:
            genre_name = match.group(1)
        else:
            genre_name = genre_str.split('/')[-1].split('?')[0]
        return genre_name.replace('-', ' ').title()
    return genre_str.title()

def extract_genre_name(genre_data):
    if not genre_data:
        return "Unknown"
    if isinstance(genre_data, list):
        cleaned_genres = [clean_single_genre(g) for g in genre_data if g]
        return ", ".join(cleaned_genres) if cleaned_genres else "Unknown"
    return clean_single_genre(genre_data)

def discover_popular_novels(cursor, conn):
    logger.info("Royal Road-тан танымал кітаптар тізімін автоматты түрде оқу басталды...")
    popular_url = "https://www.royalroad.com/fictions/active-popular"
    new_novels_count = 0
    try:
        response = requests.get(popular_url, headers=headers, timeout=15)
        if response.status_code != 200:
            logger.error(f"Тізімді оқу мүмкін болмады. HTTP {response.status_code}")
            return new_novels_count
        soup = BeautifulSoup(response.text, 'html.parser')
        novel_links = soup.find_all('h2', class_='fiction-title')
        for link_element in novel_links:
            a_tag = link_element.find('a')
            if a_tag and 'href' in a_tag.attrs:
                title = a_tag.text.strip()
                full_url = "https://www.royalroad.com" + a_tag['href']
                cursor.execute("SELECT novel_id FROM novels WHERE source_url = %s;", (full_url,))
                exists = cursor.fetchone()
                if not exists:
                    cursor.execute("INSERT INTO novels (title, source_url) VALUES (%s, %s);", (title, full_url))
                    conn.commit()
                    new_novels_count += 1
    except Exception as e:
        logger.exception(f"Танымал кітаптарды іздеу кезінде қате кетті: {e}")
    return new_novels_count

def scrape_and_update():
    start_time = datetime.now()
    stats = {"processed": 0, "success": 0, "failed": 0, "new_novels": 0}
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        cursor = conn.cursor()
    except Exception as e:
        logger.error(f"Базаға қосылу сәтсіз аяқталды: {e}")
        return

    stats["new_novels"] = discover_popular_novels(cursor, conn)
    cursor.execute("SELECT novel_id, title, source_url FROM novels;")
    novels = cursor.fetchall()
    stats["processed"] = len(novels)

    for novel_id, title, source_url in novels:
        try:
            response = requests.get(source_url, headers=headers, timeout=15)
            if response.status_code != 200:
                stats["failed"] += 1
                continue
            soup = BeautifulSoup(response.text, 'html.parser')
            json_element = soup.find('script', type='application/ld+json')
            views, rating_score, author, genre = 0, 0.0, "Unknown Author", "Unknown"
            if json_element:
                data = json.loads(json_element.string)
                if 'interactionStatistic' in data:
                    views = int(data['interactionStatistic'].get('userInteractionCount', 0))
                if 'aggregateRating' in data:
                    rating_score = float(data['aggregateRating'].get('ratingValue', 0.0))
                if 'author' in data and 'name' in data['author']:
                    author = data['author']['name']
                if 'genre' in data:
                    genre = extract_genre_name(data['genre'])
            chapters = 0
            chapters_table = soup.find('table', id='chapters')
            if chapters_table:
                chapters = len(chapters_table.find_all('tr', class_='chapter-row'))

            cursor.execute("UPDATE novels SET title = %s, author = %s, genre = %s WHERE novel_id = %s;", (title, author, genre, novel_id))
            cursor.execute("""
                INSERT INTO novel_daily_metrics (novel_id, recorded_date, chapter_count, view_count, rating_score)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (novel_id, recorded_date) DO UPDATE 
                SET chapter_count = EXCLUDED.chapter_count, view_count = EXCLUDED.view_count, rating_score = EXCLUDED.rating_score;
            """, (novel_id, datetime.today().date(), chapters, views, rating_score))
            conn.commit()
            stats["success"] += 1
        except Exception as e:
            conn.rollback()
            stats["failed"] += 1
            logger.error(f"[{title}] өңдеуде қате: {e}")

    cursor.close()
    conn.close()
    duration = (datetime.now() - start_time).total_seconds()
    logger.info(f"ETL Аяқталды. Табысты: {stats['success']}, Қате: {stats['failed']}, Уақыты: {duration:.2f} сек")

if __name__ == '__main__':
    scrape_and_update()
