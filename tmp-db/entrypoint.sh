#!/bin/sh

set -e

# Check if pocketbase binary exists
if [ ! -f ./pocketbase ]; then
  echo "Error: pocketbase binary not found"
  exit 1
fi

echo "Starting initial PocketBase to create DB..."
./pocketbase serve --http 0.0.0.0:8090 --automigrate=0 &
PB_PID=$!

# Wait for PocketBase to start
sleep 3

# Stop the temporary PocketBase instance
echo "Stopping temporary PocketBase instance..."
kill $PB_PID 2>/dev/null || echo "PocketBase didn't start properly, no process to kill"
wait $PB_PID 2>/dev/null || true

# Create admin user if ENV vars are set
if [ -n "$PRIVATE_POCKETBASE_ADMIN" ] && [ -n "$PRIVATE_POCKETBASE_PASSWORD" ]; then
  echo "Creating admin user..."
  if ./pocketbase --help | grep -q "superuser"; then
    ./pocketbase superuser upsert "$PRIVATE_POCKETBASE_ADMIN" "$PRIVATE_POCKETBASE_PASSWORD" || echo "Failed to create admin user"
  else
    echo "Admin creation not supported in this PocketBase version; please create it manually via http://0.0.0.0:8090/_/"
  fi
else
  echo "Admin ENV vars not set, skipping admin creation"
fi

echo "Starting PocketBase for real..."
exec ./pocketbase serve --http 0.0.0.0:8090 --automigrate=0
