"""
Database setup and initialization for WhatCanICook.
Creates SQLite database and executes schema.
"""

import sqlite3
import os
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent.parent.parent / "data" / "recipes.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def get_connection():
    """
    Get a connection to the SQLite database.
    Creates the database file if it doesn't exist.
    
    Returns:
        sqlite3.Connection: Database connection object
    """
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
    return conn


def init_database():
    """
    Initialize the database by executing the schema.sql file.
    Creates all tables, indexes, and constraints.
    """
    # Ensure data directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Read schema file
    with open(SCHEMA_PATH, 'r') as f:
        schema_sql = f.read()
    
    # Execute schema
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executescript(schema_sql)
    conn.commit()
    conn.close()
    
    print(f"✓ Database initialized successfully at: {DB_PATH}")


def reset_database():
    """
    Delete the database file and reinitialize.
    WARNING: This will delete all data!
    """
    if DB_PATH.exists():
        DB_PATH.unlink()
        print(f"✓ Deleted existing database at: {DB_PATH}")
    
    init_database()


if __name__ == "__main__":
    # Run this script directly to initialize the database
    print("Initializing WhatCanICook database...")
    init_database()
    
    # Verify tables were created
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    conn.close()
    
    print(f"\nTables created: {[table[0] for table in tables]}")
