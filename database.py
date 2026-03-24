import sqlite3
from datetime import datetime

DB_NAME = "analysis_history.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Analysis results table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            score REAL,
            risk TEXT,
            total_snippets INTEGER,
            dark_snippets INTEGER,
            timestamp TEXT
        )
    """)

    # Monitored websites table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS monitored_sites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            is_active INTEGER DEFAULT 1
        )
    """)

    conn.commit()
    conn.close()


def save_analysis(url, score, risk, total, dark):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO analyses (url, score, risk, total_snippets, dark_snippets, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        url,
        score,
        risk,
        total,
        dark,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


def get_all_analyses():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM analyses ORDER BY timestamp ASC")
    rows = cursor.fetchall()

    conn.close()
    return rows


# =========================
# Monitoring Functions
# =========================

def add_monitored_site(url):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO monitored_sites (url, is_active)
            VALUES (?, 1)
        """, (url,))
        conn.commit()
    except:
        pass

    conn.close()


def get_monitored_sites():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT id, url, is_active FROM monitored_sites")
    rows = cursor.fetchall()

    conn.close()
    return rows


def get_active_sites():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT url FROM monitored_sites WHERE is_active = 1")
    rows = cursor.fetchall()

    conn.close()
    return [row[0] for row in rows]


def toggle_site_status(site_id, status, clean_history=False):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Update active status
    cursor.execute("""
        UPDATE monitored_sites
        SET is_active = ?
        WHERE id = ?
    """, (status, site_id))

    # If clean requested, delete history
    if clean_history and status == 0:
        cursor.execute("""
            DELETE FROM analyses
            WHERE url = (
                SELECT url FROM monitored_sites WHERE id = ?
            )
        """, (site_id,))

    conn.commit()
    conn.close()


def delete_site_completely(site_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT url FROM monitored_sites WHERE id = ?", (site_id,))
    row = cursor.fetchone()

    if row:
        url = row[0]

        cursor.execute("DELETE FROM analyses WHERE url = ?", (url,))
        cursor.execute("DELETE FROM monitored_sites WHERE id = ?", (site_id,))

    conn.commit()
    conn.close()