import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '../lab_memory.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    
    # Sessions Table (for future multi-session support)
    c.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Messages Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            sender_type TEXT, -- user, bot, system
            sender_name TEXT, -- e.g. Operator, Coda, Carmel
            content TEXT,
            msg_type TEXT DEFAULT 'text', -- text, image, audio
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            meta TEXT -- JSON blob for extra data (image URLs, etc)
        )
    ''')
    
    # Ensure default session
    c.execute('INSERT OR IGNORE INTO sessions (id, name) VALUES (?, ?)', ('main', 'Main Terminal'))
    
    conn.commit()
    conn.close()
    print(f"Memory Core initialized at {DB_PATH}")

def log_message(session_id, sender_type, sender_name, content, msg_type='text', meta=None):
    conn = get_db()
    c = conn.cursor()
    meta_json = json.dumps(meta) if meta else None
    c.execute('''
        INSERT INTO messages (session_id, sender_type, sender_name, content, msg_type, meta)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (session_id, sender_type, sender_name, content, msg_type, meta_json))
    conn.commit()
    conn.close()

def get_history(session_id='main', limit=50):
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        SELECT * FROM messages 
        WHERE session_id = ? 
        ORDER BY created_at DESC 
        LIMIT ?
    ''', (session_id, limit))
    rows = c.fetchall()
    conn.close()
    
    # Return reversed (oldest first)
    return [dict(row) for row in reversed(rows)]

def clear_history(session_id='main'):
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM messages WHERE session_id = ?', (session_id,))
    conn.commit()
    conn.close()

# Initialize immediately on import check
if not os.path.exists(DB_PATH):
    init_db()
