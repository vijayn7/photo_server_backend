#!/bin/sh
# Start the FastAPI application with custom Uvicorn settings for large file uploads

echo "Starting photo server with large file upload support (up to 10 GB)..."
uvicorn main:app --host 0.0.0.0 --port 8000 --log-level info --timeout-keep-alive 600
