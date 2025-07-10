# A2A System Multi-Service Dockerfile
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy wheels for offline installation
COPY wheels/ /app/wheels/

# Copy requirements
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-index --find-links /app/wheels/ -r requirements.txt

# Copy application code
COPY . /app/

# Create necessary directories
RUN mkdir -p /app/logs /app/data

# Set environment variables defaults
ENV A2A_ENVIRONMENT=production \
    A2A_DEBUG=false \
    A2A_DB_TYPE=sqlite \
    A2A_DATABASE_URL=/app/data/a2a_system.db

# Initialize database
RUN python -c "from database.db_manager import db; db.init_database()"

# Expose ports
EXPOSE 5006 5003 5002

# Default command (can be overridden)
CMD ["python", "api/jules_server.py"]