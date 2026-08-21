FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY Ovi/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the Ovi codebase
COPY Ovi/ .

# Hugging Face Spaces expects container to listen on port 7860
ENV PORT=7860
EXPOSE 7860

# Run Flask server
CMD ["python", "server.py"]
