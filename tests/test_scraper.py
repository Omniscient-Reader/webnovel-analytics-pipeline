import pytest
from app.scraper import clean_single_genre, extract_genre_name

def test_clean_single_genre_url():
    # URL араласып келген жанрды дұрыс тазалауын тексеру
    assert clean_single_genre("https://www.royalroad.com/fictions/active-popular?genre=action") == "Action"
    assert clean_single_genre("/genres/sci-fi") == "Sci Fi"

def test_clean_single_genre_normal():
    # Қалыпты сөз келгенде дұрыс шығаруын тексеру
    assert clean_single_genre("adventure") == "Adventure"
    assert clean_single_genre("") == "Unknown"

def test_extract_genre_name_list():
    # Тізім болып келгенде үтірмен біріктіруін тексеру
    genres = ["comedy", "drama", "/tag/magic"]
    assert extract_genre_name(genres) == "Comedy, Drama, Magic"
