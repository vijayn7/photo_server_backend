from databases import Database
import sqlalchemy
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import select, insert, update, delete, func
from datetime import datetime
import os

DATABASE_URL = "sqlite+aiosqlite:///./photos/photo_server.db"
SYNC_DATABASE_URL = "sqlite:///./photos/photo_server.db"

database = Database(DATABASE_URL)
metadata = MetaData()

# User table definition
users_table = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("username", String(50), unique=True, nullable=False),
    Column("email", String(100), nullable=True),
    Column("full_name", String(100), nullable=True),
    Column("hashed_password", String(255), nullable=False),
    Column("disabled", Boolean, default=False, nullable=False),
    Column("admin", Boolean, default=False, nullable=False),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
)

# Photo metadata table (for future use)
photos_table = Table(
    "photos",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("filename", String(255), unique=True, nullable=False),
    Column("original_name", String(255), nullable=False),
    Column("uploaded_by", String(50), nullable=False),
    Column("upload_date", DateTime, default=datetime.utcnow, nullable=False),
    Column("file_size", Integer, nullable=False),
    Column("file_type", String(10), nullable=False),
    Column("is_favorite", Boolean, default=False, nullable=False),
    Column("metadata_json", Text, nullable=True),  # Store additional metadata as JSON
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
)

# Create database and tables
def create_tables():
    """Create database tables if they don't exist"""
    engine = create_engine(SYNC_DATABASE_URL)
    metadata.create_all(engine)
    engine.dispose()

# Initialize database
def init_database():
    """Initialize the database and create tables"""
    # Ensure the directory exists
    os.makedirs("./photos", exist_ok=True)
    create_tables()
