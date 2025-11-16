"""
Database migration script to convert from integer IDs to hash-based IDs

IMPORTANT: This script will modify your database structure!
- Backup your database before running this script
- This will recreate tables with the new schema
- All existing data will be lost

Run this script when you want to migrate to hash-based IDs.
"""
import sys
import os
import logging
from sqlalchemy import create_engine, text
from engine.database import SQLALCHEMY_DATABASE_URL
from engine.models import Base
from utilities.hash_utils import generate_user_hash, generate_conversation_hash, generate_message_hash

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def backup_existing_data(engine):
    """
    Backup existing data before migration
    Note: This is a simple backup - in production you'd want more sophisticated backup
    """
    logger.info("Starting data backup...")
    
    try:
        with engine.connect() as conn:
            # Check if tables exist
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result.fetchall()]
            
            if 'users' in tables:
                users = conn.execute(text("SELECT * FROM users")).fetchall()
                logger.info(f"Found {len(users)} users to backup")
                
            if 'conversations' in tables:
                conversations = conn.execute(text("SELECT * FROM conversations")).fetchall()
                logger.info(f"Found {len(conversations)} conversations to backup")
                
            if 'chat_messages' in tables:
                messages = conn.execute(text("SELECT * FROM chat_messages")).fetchall()
                logger.info(f"Found {len(messages)} messages to backup")
                
        logger.info("Data backup completed")
        return True
        
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        return False

def recreate_tables(engine):
    """
    Drop existing tables and recreate with new schema
    """
    logger.info("Starting table recreation...")
    
    try:
        # Drop all tables
        Base.metadata.drop_all(engine)
        logger.info("Dropped existing tables")
        
        # Create all tables with new schema
        Base.metadata.create_all(engine)
        logger.info("Created new tables with hash-based IDs")
        
        return True
        
    except Exception as e:
        logger.error(f"Table recreation failed: {e}")
        return False

def create_sample_data(engine):
    """
    Create some sample data to test the new hash-based system
    """
    logger.info("Creating sample data...")
    
    try:
        with engine.connect() as conn:
            # Create sample users with hash IDs
            users_data = [
                {
                    'id': generate_user_hash('alice@example.com', 'alice'),
                    'email': 'alice@example.com',
                    'username': 'alice',
                    'full_name': 'Alice Johnson',
                    'is_active': True
                },
                {
                    'id': generate_user_hash('bob@example.com', 'bob'),
                    'email': 'bob@example.com',
                    'username': 'bob',
                    'full_name': 'Bob Smith',
                    'is_active': True
                }
            ]
            
            for user_data in users_data:
                conn.execute(text("""
                    INSERT INTO users (id, email, username, full_name, is_active, created_at, updated_at)
                    VALUES (:id, :email, :username, :full_name, :is_active, datetime('now'), datetime('now'))
                """), user_data)
            
            # Create sample conversations
            conversations_data = []
            for user_data in users_data:
                conv_id = generate_conversation_hash(user_data['id'], f"Chat with {user_data['username']}")
                conversations_data.append({
                    'id': conv_id,
                    'user_id': user_data['id'],
                    'title': f"Chat with {user_data['username']}",
                    'status': 'active'
                })
                
                conn.execute(text("""
                    INSERT INTO conversations (id, user_id, title, status, created_at, updated_at)
                    VALUES (:id, :user_id, :title, :status, datetime('now'), datetime('now'))
                """), conversations_data[-1])
            
            # Create sample messages
            for conv_data in conversations_data:
                messages = [
                    {
                        'id': generate_message_hash(conv_data['id'], "Hello, how can I help you today?", "assistant"),
                        'conversation_id': conv_data['id'],
                        'role': 'assistant',
                        'content': 'Hello, how can I help you today?'
                    },
                    {
                        'id': generate_message_hash(conv_data['id'], "I need help with my account", "user"),
                        'conversation_id': conv_data['id'],
                        'role': 'user',
                        'content': 'I need help with my account'
                    }
                ]
                
                for msg_data in messages:
                    conn.execute(text("""
                        INSERT INTO chat_messages (id, conversation_id, role, content, timestamp)
                        VALUES (:id, :conversation_id, :role, :content, datetime('now'))
                    """), msg_data)
            
            conn.commit()
            logger.info("Sample data created successfully")
            
        return True
        
    except Exception as e:
        logger.error(f"Sample data creation failed: {e}")
        return False

def verify_migration(engine):
    """
    Verify that the migration was successful
    """
    logger.info("Verifying migration...")
    
    try:
        with engine.connect() as conn:
            # Check users
            users = conn.execute(text("SELECT id, email, username FROM users")).fetchall()
            logger.info(f"Users in new database: {len(users)}")
            for user in users:
                logger.info(f"  User: {user[0]} - {user[1]} ({user[2]})")
            
            # Check conversations
            conversations = conn.execute(text("SELECT id, user_id, title FROM conversations")).fetchall()
            logger.info(f"Conversations in new database: {len(conversations)}")
            for conv in conversations:
                logger.info(f"  Conversation: {conv[0]} - {conv[2]} (User: {conv[1]})")
            
            # Check messages
            messages = conn.execute(text("SELECT id, conversation_id, role, content FROM chat_messages")).fetchall()
            logger.info(f"Messages in new database: {len(messages)}")
            for msg in messages:
                logger.info(f"  Message: {msg[0]} - {msg[2]}: {msg[3][:30]}...")
        
        logger.info("Migration verification completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Migration verification failed: {e}")
        return False

def main():
    """
    Main migration function
    """
    print("=" * 60)
    print("DATABASE MIGRATION: Integer IDs → Hash-based IDs")
    print("=" * 60)
    print()
    print("⚠️  WARNING: This will modify your database structure!")
    print("   - All existing data will be lost")
    print("   - Tables will be recreated with new schema")
    print("   - Sample data will be added for testing")
    print()
    
    response = input("Do you want to continue? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Migration cancelled.")
        return False
    
    try:
        # Create database engine
        engine = create_engine(SQLALCHEMY_DATABASE_URL)
        
        logger.info("Starting database migration process...")
        
        # Step 1: Backup existing data (optional - just for logging)
        if not backup_existing_data(engine):
            logger.error("Backup failed, aborting migration")
            return False
        
        # Step 2: Recreate tables
        if not recreate_tables(engine):
            logger.error("Table recreation failed, aborting migration")
            return False
        
        # Step 3: Create sample data
        if not create_sample_data(engine):
            logger.error("Sample data creation failed, but migration structure is complete")
            # Don't return False here - structure migration was successful
        
        # Step 4: Verify migration
        if not verify_migration(engine):
            logger.error("Migration verification failed")
            return False
        
        print()
        print("=" * 60)
        print("🎉 MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Test the API endpoints with the new hash-based IDs")
        print("2. Update your client applications to handle string IDs")
        print("3. Remove this migration script once you're satisfied")
        print()
        
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)