import sqlite3

conn = sqlite3.connect('/app/data/app.db')
cursor = conn.cursor()

# Check tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cursor.fetchall()]
print(f"Tables: {tables}\n")

if 'users' in tables:
    cursor.execute("SELECT username, email FROM users")
    users = cursor.fetchall()
    if users:
        print("Registered users:")
        for u in users:
            print(f"  - Username: {u[0]}, Email: {u[1]}")
    else:
        print("No users registered yet.")
else:
    print("Users table doesn't exist. Database not initialized.")

conn.close()
