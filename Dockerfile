FROM python:3.10-slim

WORKDIR /workspace

# Жүйелік кітапханаларды орнату (PostgreSQL-ге байланыс үшін қажет)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Тәуелділіктерді көшіру және орнату
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Жобаның кодын көшіру
COPY . .

# Streamlit жұмыс істейтін портты ашу
EXPOSE 8501

# Контейнер іске қосылғанда бірден Streamlit веб-сайтын ашады
CMD ["streamlit", "run", "app/dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
