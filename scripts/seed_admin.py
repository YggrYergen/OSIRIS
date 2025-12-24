import sqlite3
import traceback
from passlib.hash import pbkdf2_sha256

# GENERATE PBKDF2 HASH FOR "admin123"
# We use the library directly here to match what the backend will use
NEW_HASH = pbkdf2_sha256.hash("admin123")

DB_PATH = "D:/OSIRIS/backend/osiris_demo.db"

def seed_sync():
    print(f"--- SYNC SEEDING WITH PBKDF2 {DB_PATH} ---")
    print(f"New Hash: {NEW_HASH}")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        email = "admin@osiris.dev"
        
        # Check existing
        cursor.execute("SELECT id FROM user WHERE email = ?", (email,))
        existing = cursor.fetchone()
        
        if existing:
            print("User exists. Updating hash...")
            cursor.execute("UPDATE user SET hashed_password = ? WHERE email = ?", (NEW_HASH, email))
        else:
            print("Creating new user...")
            cursor.execute("""
                INSERT INTO user (email, username, full_name, hashed_password, role, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
            """, (email, "admin", "System Admin", NEW_HASH, "admin", 1))
            
        conn.commit()
        print("✅ Committed successfully.")
        
        # Verify
        cursor.execute("SELECT email, hashed_password FROM user")
        rows = cursor.fetchall()
        print(f"VERIFY DUMP: {rows}")
        
        conn.close()
    except Exception:
        traceback.print_exc()

if __name__ == "__main__":
    seed_sync()
