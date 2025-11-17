"""
Setup Admin User Script
Creates an admin user with admin role in the auth service database
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "auth-service"))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(project_root / ".env")
load_dotenv(project_root / "auth-service" / ".env")

from sqlalchemy.orm import Session
from auth_server.database import SessionLocal, engine, Base
from auth_server.models.user import User
from auth_server.models.role import Role
from auth_server.models.user_role import UserRole
from auth_server.security.auth import get_password_hash
import getpass

# Create all tables
Base.metadata.create_all(bind=engine)

def setup_admin_user():
    """Setup admin user with admin role"""
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("Admin User Setup")
        print("=" * 80)
        print()
        
        # Get admin credentials
        print("Enter admin user details:")
        username = input("Username (default: admin): ").strip() or "admin"
        email = input("Email (default: admin@example.com): ").strip() or "admin@example.com"
        
        # Get password
        while True:
            password = getpass.getpass("Password: ")
            if len(password) < 6:
                print("❌ Password must be at least 6 characters long")
                continue
            
            confirm_password = getpass.getpass("Confirm password: ")
            if password != confirm_password:
                print("❌ Passwords do not match")
                continue
            
            break
        
        print()
        print("Setting up admin user...")
        
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            print(f"⚠️  User already exists!")
            print(f"   Username: {existing_user.username}")
            print(f"   Email: {existing_user.email}")
            
            update = input("\nUpdate password for existing user? (y/n): ").lower()
            if update == 'y':
                existing_user.hashed_password = get_password_hash(password)
                db.commit()
                print("✅ Password updated successfully!")
                user = existing_user
            else:
                print("❌ Setup cancelled")
                return
        else:
            # Create new user
            user = User(
                username=username,
                email=email,
                hashed_password=get_password_hash(password),
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"✅ User '{username}' created successfully!")
        
        # Ensure admin role exists
        admin_role = db.query(Role).filter_by(name="admin").first()
        if not admin_role:
            print("   Creating 'admin' role...")
            admin_role = Role(name="admin")
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)
            print("   ✅ Admin role created")
        
        # Check if user already has admin role
        existing_user_role = db.query(UserRole).filter_by(
            user_id=user.id,
            role_id=admin_role.id
        ).first()
        
        if not existing_user_role:
            # Assign admin role to user
            user_role = UserRole(user_id=user.id, role_id=admin_role.id)
            db.add(user_role)
            db.commit()
            print("   ✅ Admin role assigned to user")
        else:
            print("   ℹ️  User already has admin role")
        
        print()
        print("=" * 80)
        print("✅ Admin setup complete!")
        print("=" * 80)
        print()
        print("Admin User Details:")
        print(f"  Username: {user.username}")
        print(f"  Email: {user.email}")
        print(f"  User ID: {user.id}")
        print(f"  Roles: admin")
        print()
        print("You can now login with these credentials at http://localhost:3000")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def list_admin_users():
    """List all admin users"""
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("Current Admin Users")
        print("=" * 80)
        print()
        
        # Get admin role
        admin_role = db.query(Role).filter_by(name="admin").first()
        
        if not admin_role:
            print("❌ No admin role found in database")
            return
        
        # Get all users with admin role
        user_roles = db.query(UserRole).filter_by(role_id=admin_role.id).all()
        
        if not user_roles:
            print("❌ No admin users found")
            return
        
        print(f"Found {len(user_roles)} admin user(s):")
        print()
        
        for ur in user_roles:
            user = db.query(User).filter_by(id=ur.user_id).first()
            if user:
                status = "✅ Active" if user.is_active else "❌ Inactive"
                print(f"  • {user.username}")
                print(f"    Email: {user.email}")
                print(f"    ID: {user.id}")
                print(f"    Status: {status}")
                print()
        
    finally:
        db.close()

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--list":
        list_admin_users()
    else:
        setup_admin_user()

if __name__ == "__main__":
    main()
