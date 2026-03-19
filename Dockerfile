FROM python:3.11-slim

WORKDIR /app

# yt-dlp needs ffmpeg
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r backend/requirements.txt

# Copy source
COPY . .

# Create data dir
RUN mkdir -p data/runs

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "backend.api:app", "--host", "0.0.0.0", "--port", "8000"]
