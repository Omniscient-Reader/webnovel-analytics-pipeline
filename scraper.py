import os
import json
import requests
from bs4 import BeautifulSoup
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(dotenv_path='/Users/birzhanmeyrkhan/webnovel-analytics/.env')

def scrape_and_update():
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )
    cursor = conn.cursor()

    cursor.execute("SELECT novel_id, title, source_url FROM novels;")
    novels = cursor.fetchall()

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }

    for novel_id, title, source_url in novels:
        try:
            print(f"Scraping: {title}...")
            response = requests.get(source_url, headers=headers, timeout=15)
            
            if response.status_code != 200:
                print(f"Skipping {title}: HTTP Status {response.status_code}")
                continue
                
            soup = BeautifulSoup(response.text, 'html.parser')

            # Қаралым мен Рейтингті JSON-LD ішінен таза күйінде аламыз
            json_element = soup.find('script', type='application/ld+json')
            views = 0
            rating_score = 0.0

            if json_element:
                data = json.loads(json_element.string)
                if 'interactionStatistic' in data:
                    views = int(data['interactionStatistic'].get('userInteractionCount', 0))
                if 'aggregateRating' in data:
                    rating_score = float(data['aggregateRating'].get('ratingValue', 0.0))
            
            # Түзетілді: Тарау санын (chapter_count) Royal Road-тың кестесінен (tbody) дәлме-дәл есептейміз
            chapters = 0
            chapters_table = soup.find('table', id='chapters')
            if chapters_table:
                # Кестедегі әрбір <tr> (жол) — бұл бір тарау
                chapters = len(chapters_table.find_all('tr', class_='chapter-row'))
            
            # Егер кестеден табылмаса, ескі әдіспен іздеп көреді
            if chapters == 0:
                chapters_element = soup.find(string=lambda t: t and 'Chapters' in t)
                if chapters_element:
                    try:
                        chapters = int(''.join(filter(str.isdigit, chapters_element)))
                    except ValueError:
                        chapters = 0

            cursor.execute(
                """
                INSERT INTO novel_daily_metrics (novel_id, recorded_date, chapter_count, view_count, rating_score)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (novel_id, recorded_date) DO UPDATE 
                SET chapter_count = EXCLUDED.chapter_count, view_count = EXCLUDED.view_count, rating_score = EXCLUDED.rating_score;
                """,
                (novel_id, datetime.today().date(), chapters, views, rating_score)
            )
            print(f"Successfully updated metrics for {title}. Views: {views}, Rating: {rating_score}, Chapters: {chapters}")

        except Exception as e:
            print(f"Error processing {title}: {e}")

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    scrape_and_update()
