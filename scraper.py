import sys
# Manually point Python to your background site packages directory path
sys.path.append("/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/site-packages")

import os
import requests
from bs4 import BeautifulSoup
import psycopg2
from datetime import datetime
import time
from fake_useragent import UserAgent
from dotenv import load_dotenv

# Load secret environment variables from the local .env file
load_dotenv()

# Secure Database Configurations (No hardcoded passwords!)
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")  
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

db_params = {
    "dbname": DB_NAME,
    "user": DB_USER,
    "password": DB_PASS,
    "host": DB_HOST,
    "port": DB_PORT
}

ua = UserAgent()

try:
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    
    cur.execute("SELECT novel_id, source_url FROM novels WHERE source_url IS NOT NULL;")
    tracked_novels = cur.fetchall()
    
    for novel_id, url in tracked_novels:
        print(f"\n🔄 Syncing Novel ID {novel_id} from: {url}")
        
        headers = {
            "User-Agent": ua.random,
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com/"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status() 
            
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract Basic Metadata
            title_element = soup.find("h1")
            title = title_element.text.strip() if title_element else "Unknown Title"
            
            author_element = soup.find("h4", class_="font-white")
            author = author_element.find("a").text.strip() if author_element and author_element.find("a") else "Unknown Author"
            
            genre_tags = [tag.text.strip() for tag in soup.find_all("a", class_="label-tags")]
            genre_string = ", ".join(genre_tags) if genre_tags else "Unknown Genre"

            # Extract Views
            view_count = 0
            stats_box = soup.find("div", class_="fiction-info")
            if stats_box:
                stats_list = stats_box.find_all("li")
                for i, li in enumerate(stats_list):
                    text = li.text.lower().strip()
                    if "views" in text and i + 1 < len(stats_list):
                        cleaned_val = "".join(c for c in stats_list[i+1].text if c.isdigit())
                        if cleaned_val:
                            view_count = int(cleaned_val)

            # Extract Chapter Count
            chapter_count = 0
            toc_body = soup.find("tbody")
            if toc_body:
                rows = toc_body.find_all("tr", class_="chapter-row")
                if rows:
                    chapter_count = len(rows)
            
            if chapter_count == 0:
                for target in soup.find_all("span"):
                    if "chapters" in target.text.lower():
                        words = target.text.strip().split()
                        for word in words:
                            if word.replace(",", "").isdigit():
                                chapter_count = int(word.replace(",", ""))
                                break

            # Extract Rating
            rating_score = 0.0
            rating_meta = soup.find("meta", property="books:rating:value")
            if rating_meta and rating_meta.get("content"):
                try:
                    rating_score = float(rating_meta["content"])
                except ValueError:
                    pass

            print(f"   📖 Metadata -> Title: '{title}' | Author: '{author}'")
            print(f"   📊 Metrics  -> Chapters: {chapter_count} | Views: {view_count} | Rating: {rating_score:.2f}")

            if title == "Unknown Title" and view_count == 0:
                print(f"⚠️ Scraping returned empty results. Skipping DB write to protect existing records.")
                continue

            # DB Operations
            cur.execute("""
                UPDATE novels 
                SET title = %s,
                    author = COALESCE(author, %s),
                    genre = COALESCE(genre, %s),
                    chapter_count = %s
                WHERE novel_id = %s;
            """, (title, author, genre_string, chapter_count, novel_id))

            cur.execute("""
                INSERT INTO novel_daily_metrics (novel_id, view_count, rating_score, chapter_count, recorded_date)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (novel_id, recorded_date) 
                DO UPDATE SET 
                    view_count = EXCLUDED.view_count,
                    rating_score = EXCLUDED.rating_score,
                    chapter_count = EXCLUDED.chapter_count;
            """, (novel_id, view_count, rating_score, chapter_count, datetime.today().date()))
            
            print(f"🚀 Saved log entry into both database tables!")
            conn.commit()
            
        except requests.exceptions.RequestException as req_err:
            print(f"❌ Network Error on {url}: {req_err}")
            conn.rollback()
        except Exception as item_err:
            print(f"❌ Processing Error on {url}: {item_err}")
            conn.rollback()
            
        time.sleep(3)

    print("\n✅ Run completed successfully!")
    
except Exception as e:
    print(f"\n❌ Global Database connection error: {e}")
finally:
    if 'conn' in locals() and conn:
        cur.close()
        conn.close()