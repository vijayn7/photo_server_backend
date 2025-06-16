"""
Custom configuration for Uvicorn ASGI server to support very large file uploads
"""

# Set a very large limit for request body size (10GB)
limit_max_body_size = 10 * 1024 * 1024 * 1024  # 10 GB

# Increase the timeout for handling larger uploads
timeout_keep_alive = 600  # seconds (10 minutes)

# Config for handling larger request bodies
limit_concurrency = 10
backlog = 2048

# Disable dev environment auto-reload
reload = False
