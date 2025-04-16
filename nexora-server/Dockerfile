# Place this file in the nexora-server directory as Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables if needed
ENV PYTHONUNBUFFERED=1

# Command to run the server
CMD ["python", "run.py"]