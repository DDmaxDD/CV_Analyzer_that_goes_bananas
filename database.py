import sqlite3
from datetime import datetime, date
import json

def init_db():
    conn = sqlite3.connect('token_usage.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS daily_usage
        (date TEXT PRIMARY KEY, tokens INTEGER, count INTEGER)
    ''')
    conn.commit()
    conn.close()

def get_daily_usage():
    today = date.today().isoformat()
    conn = sqlite3.connect('token_usage.db')
    c = conn.cursor()
    c.execute('SELECT tokens, count FROM daily_usage WHERE date = ?', (today,))
    result = c.fetchone()
    conn.close()
    
    if result:
        return result[0], result[1]
    return 0, 0

def update_daily_usage(tokens):
    today = date.today().isoformat()
    conn = sqlite3.connect('token_usage.db')
    c = conn.cursor()
    
    # Get current usage
    c.execute('SELECT tokens, count FROM daily_usage WHERE date = ?', (today,))
    result = c.fetchone()
    
    if result:
        current_tokens, current_count = result
        new_tokens = current_tokens + tokens
        new_count = current_count + 1
        c.execute('''
            UPDATE daily_usage 
            SET tokens = ?, count = ?
            WHERE date = ?
        ''', (new_tokens, new_count, today))
    else:
        c.execute('''
            INSERT INTO daily_usage (date, tokens, count)
            VALUES (?, ?, ?)
        ''', (today, tokens, 1))
    
    conn.commit()
    conn.close()

def get_usage_stats():
    conn = sqlite3.connect('token_usage.db')
    c = conn.cursor()
    c.execute('SELECT date, tokens, count FROM daily_usage ORDER BY date DESC LIMIT 7')
    results = c.fetchall()
    conn.close()
    
    return [{
        'date': row[0],
        'tokens': row[1],
        'count': row[2]
    } for row in results] 