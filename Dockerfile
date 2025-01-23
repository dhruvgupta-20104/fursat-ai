# Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install reddis
RUN pip install --no-cache-dir redis

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p downloads generated logs

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# ENV MONGODB_CONNECTION_STRING=${MONGODB_CONNECTION_STRING}
# ENV OPENAI_API_KEY=${OPENAI_API_KEY}
# ENV TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
# ENV YOUTUBE_API_KEY=${YOUTUBE_API_KEY}
# ENV REDIS_URL=${REDIS_URL}

EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]