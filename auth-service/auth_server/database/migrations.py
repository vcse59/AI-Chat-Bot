"""Database migration utilities for handling schema changes."""
from sqlalchemy import text, inspect
from .db import engine, SessionLocal


def migrate_add_theme_preference():
    """Add theme_preference column to users table if it doesn't exist."""
    db = SessionLocal()
    try:
        # Check if column exists
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('users')]
        
        if 'theme_preference' not in columns:
            print("Adding theme_preference column to users table...")
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE users ADD COLUMN theme_preference VARCHAR(50) DEFAULT 'dark' NOT NULL"))
                conn.commit()
            print("theme_preference column added successfully!")
        else:
            print("theme_preference column already exists.")
    except Exception as e:
        print(f"Migration error: {e}")
        raise
    finally:
        db.close()


def run_all_migrations():
    """Run all pending migrations."""
    migrate_add_theme_preference()
