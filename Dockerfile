FROM python:3.12-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
COPY scraper/requirements.txt ./scraper_requirements.txt
RUN pip install --no-cache-dir -r requirements.txt -r scraper_requirements.txt

# Copy the entire project
COPY . .

# Default command (can be overridden in docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8001"]