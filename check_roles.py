import sqlite3
import sys

def check_user_roles(username):
    """Check roles for a user"""
    conn = sqlite3.connect('/app/data/auth.db')
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in cursor.fetchall()]
    print(f"Available tables: {tables}")
    
    if 'users' not in tables:
        print("ERROR: Users table doesn't exist. Database not initialized.")
        conn.close()
        return
    
    # Get user info
    cursor.execute("""
        SELECT u.id, u.username, u.email 
        FROM users u 
        WHERE u.username = ?
    """, (username,))
    user = cursor.fetchone()
    
    if not user:
        print(f"ERROR: User '{username}' not found")
        print("\nAvailable users:")
        cursor.execute("SELECT username, email FROM users")
        for u in cursor.fetchall():
            print(f"  - {u[0]} ({u[1]})")
        conn.close()
        return
    
    print(f"\nUser found: {user[1]} (ID: {user[0]}, Email: {user[2]})")
    
    # Get roles
    cursor.execute("""
        SELECT r.name 
        FROM user_roles ur 
        JOIN roles r ON ur.role_id = r.id 
        WHERE ur.user_id = ?
    """, (user[0],))
    roles = [r[0] for r in cursor.fetchall()]
    
    print(f"Current roles: {roles if roles else 'None'}")
    
    conn.close()
    return user[0], roles

def add_admin_role(username):
    """Add admin role to user"""
    conn = sqlite3.connect('/app/data/auth.db')
    cursor = conn.cursor()
    
    # Get user ID
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if not user:
        print(f"ERROR: User '{username}' not found")
        conn.close()
        return False
    
    user_id = user[0]
    
    # Get admin role ID
    cursor.execute("SELECT id FROM roles WHERE name = 'admin'")
    role = cursor.fetchone()
    if not role:
        print("ERROR: Admin role not found in database")
        conn.close()
        return False
    
    role_id = role[0]
    
    # Add role
    try:
        cursor.execute("""
            INSERT INTO user_roles (user_id, role_id) 
            VALUES (?, ?)
        """, (user_id, role_id))
        conn.commit()
        print(f"✓ Admin role added to user '{username}'")
        conn.close()
        return True
    except sqlite3.IntegrityError:
        print(f"User '{username}' already has admin role")
        conn.close()
        return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_roles.py <username> [add]")
        sys.exit(1)
    
    username = sys.argv[1]
    action = sys.argv[2] if len(sys.argv) > 2 else "check"
    
    if action == "add":
        print(f"Adding admin role to '{username}'...")
        add_admin_role(username)
        print("\n" + "="*50)
        print("Checking updated roles...")
        check_user_roles(username)
    else:
        check_user_roles(username)
