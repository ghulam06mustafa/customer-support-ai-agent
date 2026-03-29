import sqlite3
from datetime import datetime

def init_db():
    conn=sqlite3.connect("support.db")
    cursor=conn.cursor()


    cursor.execute("""
CREATE TABLE IF NOT EXISTS sessions(session_id TEXT PRIMARY KEY, created_at TEXT)
""")
    
    cursor.execute("""
CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT, role TEXT, content TEXT, timestamp TEXT)
""")
    
    conn.commit()
    conn.close()


def save_message(session_id, role, content):
    conn=sqlite3.connect("support.db")
    cursor=conn.cursor()

    cursor.execute(""" INSERT INTO messages(session_id, role, content, timestamp) VALUES(?,?,?,?)""",
                    (session_id, role, content, datetime.now().isoformat()))
    conn.commit()
    conn.close()



def get_chat_history(session_id):
    conn = sqlite3.connect("support.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT role, content FROM messages
        WHERE session_id = ?
        ORDER BY timestamp ASC
    """, (session_id,))
    
    messages = cursor.fetchall()
    conn.close()
    return messages

def create_session(session_id):
    conn = sqlite3.connect("support.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR IGNORE INTO sessions (session_id, created_at)
        VALUES (?, ?)
    """, (session_id, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()