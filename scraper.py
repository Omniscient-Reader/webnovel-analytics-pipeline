import os
import json
import re
import requests
from bs4 import BeautifulSoup
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(dotenv_path='/Users/birzhanmeyrkhan/webnovel-analytics/.env')

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

            json_element = soup.find('script', type='application/ld+json')
            views = 0
            rating_score = 0.0
            author = "Unknown Author"
            genre = "Unknown"

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

            # --- ТАРАУ САНЫН ТАБУ ---
            chapters = 0
            chapters_table = soup.find('table', id='chapters')
            if chapters_table:
                chapters = len(chapters_table.find_all('tr', class_='chapter-row'))
            
            if chapters == 0:
                chapters = len(soup.find_all('tr', class_='chapter-row'))
                
            if chapters == 0:
                for li in soup.find_all('li'):
                    if 'Chapters' in li.text:
                        match = re.search(r'Chapters\s*:\s*(\d+)', li.text, re.IGNORECASE)
                        if match:
                            chapters = int(match.group(1))
                            break

            # ТҮЗЕТІЛДІ: Енді novels кестесінің өзінде де chapter_count жаңарады!
            cursor.execute(
                """
                UPDATE novels 
                SET author = %s, genre = %s, chapter_count = %s
                WHERE novel_id = %s;
                """,
                (author, genre, chapters, novel_id)
            )

            cursor.execute(
                """
                INSERT INTO novel_daily_metrics (novel_id, recorded_date, chapter_count, view_count, rating_score)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (novel_id, recorded_date) DO UPDATE 
                SET chapter_count = EXCLUDED.chapter_count, view_count = EXCLUDED.view_count, rating_score = EXCLUDED.rating_score;
                """,
                (novel_id, datetime.today().date(), chapters, views, rating_score)
            )
            conn.commit()
            print(f"Updated {title}. Author: {author}, Genre: {genre}, Views: {views}, Chapters: {chapters}")

        except Exception as e:
            conn.rollback()
            print(f"Error processing {title}: {e}")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    scrape_and_update()
