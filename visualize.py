import os
import pandas as pd
import psycopg2
import plotly.express as px
from dotenv import load_dotenv

# .env файлын жүктеу
load_dotenv(dotenv_path='/Users/birzhanmeyrkhan/webnovel-analytics/.env')

def create_visualization():
    # Базаға қосылу
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )
    
    # Күнделікті метрикаларды кітаптың атымен бірге JOIN арқылы суырып алу
    query = """
        SELECT n.title, m.recorded_date, m.view_count, m.chapter_count
        FROM novel_daily_metrics m
        JOIN novels n ON m.novel_id = n.novel_id
        ORDER BY m.recorded_date ASC;
    """
    
    # Деректерді Pandas DataFrame-ге оқу
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if df.empty:
        print("Базада әлі график сызатындай дерек жоқ!")
        return

    # Pandas кейде датаны мәтін қылып алуы мүмкін, соны нақты дата форматына өткіземіз
    df['recorded_date'] = pd.to_datetime(df['recorded_date'])

    # Интерактивті сызықты график жасау (Plotly Express)
    fig_views = px.line(
        df, 
        x="recorded_date", 
        y="view_count", 
        color="title",
        title="Webnovel Views Growth Over Time (Қаралымдардың өсу динамикасы)",
        labels={"recorded_date": "Date (Күні)", "view_count": "Total Views (Жалпы қаралым)", "title": "Novel (Кітап аты)"},
        markers=True
    )
    fig_views.update_xaxes(
        dtick="D1",            # Тек күн сайын көрсету
        tickformat="%Y-%m-%d"  # Сағаттарды алып тастау
    )
    # Графиктің дизайнын сәл заманауи қылу
    fig_views.update_layout(
        hovermode="x unified",
        template="plotly_white"
    )
    
    # Графикті автоматты түрде браузерде ашу
    print("График дайындалды! Браузерден қара...")
    fig_views.show()

if __name__ == "__main__":
    create_visualization()
