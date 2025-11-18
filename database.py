# database.py
# SQLite helpers: init DB, user management, bills CRUD, backup/restore

import sqlite3
import datetime
import pandas as pd
from typing import Optional

DB_PATH = "electricity_bills.db"

def get_conn(path: str = DB_PATH):
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    # users table: store hashed passwords
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',
        created_at TEXT
    )
    """)

    # bills table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS bills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bill_no TEXT NOT NULL,
        customer_name TEXT NOT NULL,
        customer_type TEXT NOT NULL,
        units REAL,
        energy_charge REAL,
        fixed_charge REAL,
        gst REAL,
        total REAL,
        status TEXT DEFAULT 'Unpaid',
        created_at TEXT
    )
    """)

    # ensure admin exists: default password is '1234' (hashed externally)
    # Admin creation will be handled from app on first run (or create here if needed)
    conn.commit()
    conn.close()

# -------- Users ----------
def create_user(username: str, password_hash: str, role: str = "user"):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
        (username, password_hash, role, datetime.datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def get_user(username: str) -> Optional[sqlite3.Row]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    return row

# -------- Bills ----------
def save_bill(bill: dict):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO bills
        (bill_no, customer_name, customer_type, units, energy_charge, fixed_charge, gst, total, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        bill["bill_no"],
        bill["customer_name"],
        bill["customer_type"],
        bill["units"],
        bill["energy_charge"],
        bill["fixed_charge"],
        bill["gst"],
        bill["total"],
        bill.get("status", "Unpaid"),
        bill["created_at"]
    ))
    conn.commit()
    conn.close()

def update_bill_status(bill_no: str, status: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE bills SET status = ? WHERE bill_no = ?", (status, bill_no))
    conn.commit()
    conn.close()

def fetch_bills(date_from: str = None, date_to: str = None, customer_type: str = None, status: str = None):
    conn = get_conn()
    cur = conn.cursor()
    q = "SELECT * FROM bills WHERE 1=1"
    params = []
    if customer_type and customer_type != "All":
        q += " AND customer_type = ?"
        params.append(customer_type)
    if status and status != "All":
        q += " AND status = ?"
        params.append(status)
    if date_from:
        q += " AND date(created_at) >= date(?)"
        params.append(date_from)
    if date_to:
        q += " AND date(created_at) <= date(?)"
        params.append(date_to)
    q += " ORDER BY created_at DESC"
    cur.execute(q, params)
    rows = cur.fetchall()
    conn.close()
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame([dict(r) for r in rows])

# -------- Backup / Restore ----------
def backup_db_bytes() -> bytes:
    with open(DB_PATH, "rb") as f:
        return f.read()

def restore_db_bytes(b: bytes):
    with open(DB_PATH, "wb") as f:
        f.write(b)
