"""Database helpers (SQLite). The schema lives in ../database/schema.sql."""
import sqlite3
from datetime import datetime, timedelta

from config import DB_PATH, SCHEMA_PATH, MISSING_AFTER_MINUTES

TIME_FMT = "%Y-%m-%d %H:%M:%S"


def now_str():
    return datetime.now().strftime(TIME_FMT)


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create tables from schema.sql the first time only."""
    conn = get_conn()
    exists = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='assets'"
    ).fetchone()
    if not exists:
        with open(SCHEMA_PATH, encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.commit()
    conn.close()


def ensure_camera(conn, camera_id, zone_names):
    conn.execute("INSERT OR IGNORE INTO cameras (camera_id) VALUES (?)", (camera_id,))
    for name in zone_names:
        found = conn.execute(
            "SELECT 1 FROM zones WHERE camera_id=? AND zone_name=?", (camera_id, name)
        ).fetchone()
        if not found:
            conn.execute(
                "INSERT INTO zones (camera_id, zone_name) VALUES (?, ?)", (camera_id, name)
            )
    conn.commit()


def _zone_id(conn, camera_id, zone_name):
    row = conn.execute(
        "SELECT zone_id FROM zones WHERE camera_id=? AND zone_name=?", (camera_id, zone_name)
    ).fetchone()
    return row["zone_id"] if row else None


def record_sighting(conn, asset_id, asset_name, category, camera_id, zone_name):
    """Store 'this asset was seen in this zone right now' (the visual memory)."""
    zone_id = _zone_id(conn, camera_id, zone_name)
    now = now_str()
    existing = conn.execute(
        "SELECT zone_id FROM assets WHERE asset_id=?", (asset_id,)
    ).fetchone()

    if existing is None:
        conn.execute(
            """INSERT INTO assets (asset_id, asset_name, category, camera_id, zone_id,
                                   last_seen_time, status)
               VALUES (?, ?, ?, ?, ?, ?, 'Available')""",
            (asset_id, asset_name, category, camera_id, zone_id, now),
        )
        moved = True
    else:
        conn.execute(
            """UPDATE assets SET camera_id=?, zone_id=?, last_seen_time=?, status='Available'
               WHERE asset_id=?""",
            (camera_id, zone_id, now, asset_id),
        )
        moved = existing["zone_id"] != zone_id

    if moved:  # history only when new or when it changed zone
        conn.execute(
            "INSERT INTO asset_history (asset_id, camera_id, zone_id, seen_time) VALUES (?,?,?,?)",
            (asset_id, camera_id, zone_id, now),
        )
    # seen again -> close any open "Missing" alert
    conn.execute(
        "UPDATE alerts SET resolved=1 WHERE asset_id=? AND alert_type='Missing' AND resolved=0",
        (asset_id,),
    )
    conn.commit()


def refresh_missing(conn):
    """Mark assets not seen for a while as Missing and raise one alert each."""
    cutoff = (datetime.now() - timedelta(minutes=MISSING_AFTER_MINUTES)).strftime(TIME_FMT)
    rows = conn.execute(
        """SELECT asset_id FROM assets
           WHERE status != 'Missing' AND last_seen_time IS NOT NULL AND last_seen_time < ?""",
        (cutoff,),
    ).fetchall()
    for r in rows:
        conn.execute("UPDATE assets SET status='Missing' WHERE asset_id=?", (r["asset_id"],))
        conn.execute(
            "INSERT INTO alerts (asset_id, alert_type) VALUES (?, 'Missing')", (r["asset_id"],)
        )
    conn.commit()
