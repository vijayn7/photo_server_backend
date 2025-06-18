#!/bin/sh
# Start the FastAPI application with custom Uvicorn settings for large file uploads

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    # Only process lines that don't start with # and contain an equals sign
    export $(grep -v '^#' .env | grep '=' | xargs)
fi

echo "Starting photo server with large file upload support (up to 10 GB)..."
echo "Admin username is set to: ${PHOTO_SERVER_ADMIN:-vijayn7}"
if [ -n "$PHOTO_SERVER_ADMIN_PASSWORD" ]; then
    echo "Admin password is set from environment variable"
else
    echo "Admin password is using default value"
fi
uvicorn main:app --host 0.0.0.0 --port 8000 --log-level info --timeout-keep-alive 600
