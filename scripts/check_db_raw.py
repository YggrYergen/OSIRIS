
import sqlite3
import os

def check_db_raw():
    db_path = os.path.join("backend", "osiris_demo.db")
    print(f"Checking DB at: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cursor.fetchall()]
        target_table = "message" if "message" in tables else "messages"
        
        # Check Task 1
        print(f"\n--- MESSAGES for Task 1 (UI Target) in '{target_table}' ---")
        try:
            cursor.execute(f"SELECT id, sender_type, content, timestamp FROM {target_table} WHERE task_id = 1 ORDER BY timestamp DESC LIMIT 5")
            rows = cursor.fetchall()
            if not rows:
                print("No messages found for Task 1.")
            for row in rows:
                content = row[2][:50].replace("\n", " ")
                print(f"[{row[3]}] {row[1]}: {content}...")
        except: pass

        # Check Task 2
        print(f"\n--- MESSAGES for Task 2 (Test Target) in '{target_table}' ---")
        try:
             cursor.execute(f"SELECT id, sender_type, content, timestamp FROM {target_table} WHERE task_id = 2 ORDER BY timestamp DESC LIMIT 5")
             rows = cursor.fetchall()
             if not rows:
                 print("No messages found for Task 2.")
             for row in rows:
                 content = row[2][:50].replace("\n", " ")
                 print(f"[{row[3]}] {row[1]}: {content}...")
        except: pass
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_db_raw()
