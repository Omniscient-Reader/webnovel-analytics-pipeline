import os
import pandas as pd
import psycopg2
import plotly.express as px
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

st.set_page_config(page_title="Webnovel Analytics Dashboard", layout="wide")
st.title("📊 Webnovel Performance Analytics")

@st.cache_data(ttl=600)  # Деректерді 10 минут сайын кэштеу
def load_data():
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )
    query = """
        SELECT n.title, m.recorded_date, m.view_count, m.chapter_count, m.rating_score
        FROM novel_daily_metrics m
        JOIN novels n ON m.novel_id = n.novel_id
        ORDER BY m.recorded_date ASC;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    df['recorded_date'] = pd.to_datetime(df['recorded_date'])
    return df

try:
    df = load_data()

    if df.empty:
        st.warning("Базада деректер әлі жоқ!")
    else:
        # Сүзгілер (Sidebar Filters)
        st.sidebar.header("⚙️ Сүзгілеу")
        all_books = df['title'].unique()
        selected_books = st.sidebar.multiselect("Кітаптарды таңдаңыз:", all_books, default=all_books[:3])

        filtered_df = df[df['title'].isin(selected_books)]

        # Негізгі көрсеткіштер (Metrics Cards)
        col1, col2, col3 = st.columns(3)
        col1.metric("Жалпы бақылаудағы кітаптар", len(all_books))
        col2.metric("Макс Қаралым", f"{df['view_count'].max():,}")
        col3.metric("Ең жоғары Рейтинг", f"{df['rating_score'].max():.2f}")

        # График
        st.subheader("📈 Қаралымдардың өсу динамикасы")
        fig = px.line(
            filtered_df, x="recorded_date", y="view_count", color="title",
            labels={"recorded_date": "Күні", "view_count": "Жалпы Қаралым", "title": "Кітап"},
            markers=True, template="plotly_white"
        )
        fig.update_layout(hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

        # Деректер кестесі
        st.subheader("📋 Шикі деректер кестесі")
        st.dataframe(filtered_df, use_container_width=True)

except Exception as e:
    st.error(f"Базадан мәлімет оқу кезінде қате шықты: {e}")
