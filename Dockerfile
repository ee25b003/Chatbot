# Use official Python slim image
FROM python:3.12-slim

# Prevent python writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps (if any) and pip dependencies
COPY requirements.txt /app/
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy application code
COPY . /app/

# Expose the port (Render will map it)
EXPOSE 5000

# Use gunicorn and allow $PORT to be used (bash expands ${PORT})
CMD ["bash", "-lc", "gunicorn app:app --workers 1 --bind 0.0.0.0:${PORT:-5000}"]
