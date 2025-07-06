import sqlite3
from typing import List, Dict, Optional
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'automateagent.db')

SCHEMA = '''
CREATE TABLE IF NOT EXISTS processed_ids (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pdf_filename TEXT,
    municipality TEXT,
    township TEXT,
    sectional_scheme_name TEXT,
    unit TEXT,
    size TEXT,
    name TEXT,
    identifier TEXT,
    status TEXT,
    processed_at TEXT
);
'''

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_conn() as conn:
        conn.execute(SCHEMA)
        conn.commit()

def insert_record(pdf_filename: str, municipality: str, township: str, sectional_scheme_name: str, unit: str, size: str, name: str, identifier: str, status: str = 'pending'):
    with get_conn() as conn:
        conn.execute(
            '''INSERT INTO processed_ids (pdf_filename, municipality, township, sectional_scheme_name, unit, size, name, identifier, status, processed_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)''',
            (pdf_filename, municipality, township, sectional_scheme_name, unit, size, name, identifier, status)
        )
        conn.commit()

def update_status(record_id: int, status: str):
    with get_conn() as conn:
        conn.execute(
            'UPDATE processed_ids SET status=?, processed_at=? WHERE id=?',
            (status, datetime.now().isoformat() if status == 'done' else None, record_id)
        )
        conn.commit()

def get_pending_ids(pdf_filename: str) -> List[Dict]:
    with get_conn() as conn:
        cur = conn.execute(
            'SELECT * FROM processed_ids WHERE pdf_filename=? AND status="pending"',
            (pdf_filename,)
        )
        cols = [desc[0] for desc in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]

def get_done_ids(pdf_filename: str) -> List[Dict]:
    with get_conn() as conn:
        cur = conn.execute(
            'SELECT * FROM processed_ids WHERE pdf_filename=? AND status="done"',
            (pdf_filename,)
        )
        cols = [desc[0] for desc in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]

def get_all_records(pdf_filename: str) -> List[Dict]:
    with get_conn() as conn:
        cur = conn.execute(
            'SELECT * FROM processed_ids WHERE pdf_filename=?',
            (pdf_filename,)
        )
        cols = [desc[0] for desc in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]

# Call this at app startup
def ensure_db():
    init_db() 