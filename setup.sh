#!/bin/bash
# run.sh - Place this at the root of your project
# Make executable with: chmod +x run.sh

# Create necessary directories if they don't exist
mkdir -p nexora-server
mkdir -p tmp-s3/data
mkdir -p tmp-db/pb_data

# Create Dockerfile for nexora-server if it doesn't exist
if [ ! -f "nexora-server/Dockerfile" ]; then
  cat > nexora-server/Dockerfile << 'EOF'
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
EOF
  echo "Created Dockerfile for nexora-server"
fi

# Create docker-compose.yml at the project root
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  # Main nexora server
  nexora-server:
    build:
      context: ./nexora-server
      dockerfile: Dockerfile
    ports:
      - "8000:8000"  # Adjust port as needed
    volumes:
      - ./nexora-server:/app
    depends_on:
      - pocketbase
      - minio
    environment:
      - DB_HOST=pocketbase
      - S3_HOST=minio
    networks:
      - nexora-network

  # PocketBase database service from tmp-db
  pocketbase:
    build:
      context: ./tmp-db
      dockerfile: Dockerfile
    ports:
      - '8090:8090'
    environment:
      PRIVATE_POCKETBASE_ADMIN: 'admin@example.com'
      PRIVATE_POCKETBASE_PASSWORD: 'supersecurepassword'
    volumes:
      - ./tmp-db/pb_data:/home/pocketbase/pb_data
    networks:
      - nexora-network

  # MinIO S3 service from tmp-s3
  minio:
    image: quay.io/minio/minio
    container_name: minio-s3
    ports:
      - '9000:9000'
      - '9001:9001'
    volumes:
      - ./tmp-s3/data:/data
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin123
    command: server /data --console-address ":9001"
    networks:
      - nexora-network

networks:
  nexora-network:
    driver: bridge
EOF

echo "Created docker-compose.yml"

# Create Windows batch file for convenience
cat > run-nexora.bat << 'EOF'
@echo off
echo Starting Nexora services...
docker-compose up
EOF

echo "Setup complete! Run 'docker-compose up' to start all services."
echo "On Windows, you can also use the run-nexora.bat file."

# Start all services
docker-compose up