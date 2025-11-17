#!/usr/bin/env python3
"""
Database Migration Script: Consolidate Three Databases into One

This script migrates data from three separate SQLite databases:
- auth.db (users, roles, user_roles)
- openai_chatbot.db (conversations, messages)
- analytics.db (user_activity, conversation_metrics, message_metrics, api_usage, daily_stats)

Into a single unified database: chatbot.db
"""

import sqlite3
import os
from pathlib import Path
from datetime import datetime

def get_docker_volume_path():
    """Get the path to the Docker volume for shared_data"""
    # For Windows with Docker Desktop
    # Docker volumes are typically stored in WSL2 or Docker Desktop's data directory
    print("\n⚠️  Docker Volume Migration Required")
    print("=" * 60)
    print("Since you're using Docker volumes, you need to migrate data inside the container.")
    print("\nOption 1 - Copy old databases to shared volume:")
    print("  docker cp auth-server:/app/data/auth.db ./backup_auth.db")
    print("  docker cp analytics-service:/app/analytics.db ./backup_analytics.db")
    print("  docker cp openai-chatbot-api:/app/data/openai_chatbot.db ./backup_openai.db")
    print("\nOption 2 - Run migration inside container:")
    print("  docker exec -it auth-server python /app/migrate_to_single_db.py")
    print("\n" + "=" * 60)
    return None

def check_database_exists(db_path):
    """Check if a database file exists"""
    return os.path.exists(db_path)

def backup_database(db_path, backup_dir="./backups"):
    """Create a backup of the database"""
    if not os.path.exists(db_path):
        print(f"⚠️  Database not found: {db_path}")
        return None
    
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    db_name = os.path.basename(db_path)
    backup_path = os.path.join(backup_dir, f"{db_name}.{timestamp}.backup")
    
    try:
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✅ Backed up {db_name} to {backup_path}")
        return backup_path
    except Exception as e:
        print(f"❌ Failed to backup {db_name}: {e}")
        return None

def get_table_info(cursor, table_name):
    """Get column information for a table"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    return cursor.fetchall()

def table_exists(cursor, table_name):
    """Check if a table exists in the database"""
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    return cursor.fetchone() is not None

def migrate_table(source_cursor, target_cursor, table_name, force=False):
    """Migrate a table from source to target database"""
    try:
        # Check if table exists in source
        if not table_exists(source_cursor, table_name):
            print(f"  ⚠️  Table '{table_name}' not found in source database")
            return 0
        
        # Get table schema
        source_cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        create_sql = source_cursor.fetchone()
        
        if not create_sql:
            print(f"  ⚠️  Could not get schema for table '{table_name}'")
            return 0
        
        # Create table in target if it doesn't exist or force=True
        if force or not table_exists(target_cursor, table_name):
            if force and table_exists(target_cursor, table_name):
                print(f"  🗑️  Dropping existing table '{table_name}'")
                target_cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            
            print(f"  📋 Creating table '{table_name}'")
            target_cursor.execute(create_sql[0])
        
        # Copy data
        source_cursor.execute(f"SELECT * FROM {table_name}")
        rows = source_cursor.fetchall()
        
        if rows:
            # Get column names
            columns = [description[0] for description in source_cursor.description]
            placeholders = ','.join(['?' for _ in columns])
            insert_sql = f"INSERT OR REPLACE INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"
            
            target_cursor.executemany(insert_sql, rows)
            print(f"  ✅ Migrated {len(rows)} rows from '{table_name}'")
            return len(rows)
        else:
            print(f"  ℹ️  No data in table '{table_name}'")
            return 0
            
    except Exception as e:
        print(f"  ❌ Error migrating table '{table_name}': {e}")
        return 0

def migrate_databases(auth_db_path, chatbot_db_path, analytics_db_path, target_db_path, force=False):
    """Main migration function"""
    print("\n" + "=" * 60)
    print("DATABASE MIGRATION: Consolidating to Single Database")
    print("=" * 60)
    
    # Check if source databases exist
    databases = {
        "Auth DB": auth_db_path,
        "Chatbot DB": chatbot_db_path,
        "Analytics DB": analytics_db_path
    }
    
    found_dbs = []
    for name, path in databases.items():
        if check_database_exists(path):
            print(f"✅ Found {name}: {path}")
            found_dbs.append(path)
        else:
            print(f"⚠️  {name} not found: {path}")
    
    if not found_dbs:
        print("\n❌ No source databases found! Cannot proceed with migration.")
        return False
    
    # Create backups
    print("\n📦 Creating backups...")
    for path in found_dbs:
        backup_database(path)
    
    # Create target database
    print(f"\n🎯 Target database: {target_db_path}")
    
    try:
        # Connect to target database
        target_conn = sqlite3.connect(target_db_path)
        target_cursor = target_conn.cursor()
        
        total_migrated = 0
        
        # Migrate from auth.db
        if check_database_exists(auth_db_path):
            print(f"\n📚 Migrating from Auth Database...")
            auth_conn = sqlite3.connect(auth_db_path)
            auth_cursor = auth_conn.cursor()
            
            for table in ['roles', 'users', 'user_roles']:
                total_migrated += migrate_table(auth_cursor, target_cursor, table, force)
            
            auth_conn.close()
        
        # Migrate from openai_chatbot.db
        if check_database_exists(chatbot_db_path):
            print(f"\n💬 Migrating from Chatbot Database...")
            chatbot_conn = sqlite3.connect(chatbot_db_path)
            chatbot_cursor = chatbot_conn.cursor()
            
            for table in ['conversations', 'messages']:
                total_migrated += migrate_table(chatbot_cursor, target_cursor, table, force)
            
            chatbot_conn.close()
        
        # Migrate from analytics.db
        if check_database_exists(analytics_db_path):
            print(f"\n📊 Migrating from Analytics Database...")
            analytics_conn = sqlite3.connect(analytics_db_path)
            analytics_cursor = analytics_conn.cursor()
            
            for table in ['user_activity', 'conversation_metrics', 'message_metrics', 'api_usage', 'daily_stats']:
                total_migrated += migrate_table(analytics_cursor, target_cursor, table, force)
            
            analytics_conn.close()
        
        # Commit changes
        target_conn.commit()
        target_conn.close()
        
        print("\n" + "=" * 60)
        print(f"✅ Migration completed successfully!")
        print(f"📊 Total rows migrated: {total_migrated}")
        print(f"🎯 Unified database: {target_db_path}")
        print("=" * 60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        return False

def verify_migration(target_db_path):
    """Verify the migration by checking table counts"""
    print("\n🔍 Verifying migration...")
    
    try:
        conn = sqlite3.connect(target_db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"\n📋 Tables in unified database:")
        for (table_name,) in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  - {table_name}: {count} rows")
        
        conn.close()
        print("\n✅ Verification complete!")
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate three databases into one unified database")
    parser.add_argument("--auth-db", default="./auth.db", help="Path to auth.db")
    parser.add_argument("--chatbot-db", default="./openai_chatbot.db", help="Path to openai_chatbot.db")
    parser.add_argument("--analytics-db", default="./analytics.db", help="Path to analytics.db")
    parser.add_argument("--target-db", default="./data/chatbot.db", help="Path to target unified database")
    parser.add_argument("--force", action="store_true", help="Force overwrite existing tables")
    parser.add_argument("--docker", action="store_true", help="Show Docker volume migration instructions")
    
    args = parser.parse_args()
    
    if args.docker:
        get_docker_volume_path()
    else:
        # Ensure target directory exists
        target_dir = os.path.dirname(args.target_db)
        if target_dir:
            os.makedirs(target_dir, exist_ok=True)
        
        # Run migration
        success = migrate_databases(
            args.auth_db,
            args.chatbot_db,
            args.analytics_db,
            args.target_db,
            force=args.force
        )
        
        if success:
            verify_migration(args.target_db)
            
            print("\n📝 Next Steps:")
            print("1. Update your docker-compose.yml to use the new database")
            print("2. Restart your services: docker compose down && docker compose up -d")
            print("3. Test all functionality to ensure everything works")
            print("4. Once verified, you can safely delete the old database files\n")
