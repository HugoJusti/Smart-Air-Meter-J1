import sqlite3
import time
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "air_meter.db")


def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    with _conn() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS rooms (
                id     INTEGER PRIMARY KEY AUTOINCREMENT,
                name   TEXT    UNIQUE NOT NULL,
                active INTEGER NOT NULL DEFAULT 0
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS readings (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                room_id     INTEGER NOT NULL,
                ts          REAL    NOT NULL,
                co2         REAL,
                tvoc        REAL,
                temperature REAL,
                humidity    REAL,
                FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
            )
        """)
        c.execute(
            "CREATE INDEX IF NOT EXISTS idx_readings_room_ts "
            "ON readings(room_id, ts)"
        )


# ── Rooms ──────────────────────────────────────────────────────────────────────

def get_rooms():
    with _conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM rooms ORDER BY name")]


def add_room(name):
    with _conn() as c:
        c.execute("INSERT INTO rooms (name) VALUES (?)", (name,))


def delete_room(room_id):
    with _conn() as c:
        c.execute("DELETE FROM rooms WHERE id = ?", (room_id,))


def get_active_room():
    with _conn() as c:
        row = c.execute(
            "SELECT * FROM rooms WHERE active = 1 LIMIT 1"
        ).fetchone()
        return dict(row) if row else None


def set_active_room(room_id):
    with _conn() as c:
        c.execute("UPDATE rooms SET active = 0")
        if room_id is not None:
            c.execute("UPDATE rooms SET active = 1 WHERE id = ?", (room_id,))


# ── Readings ───────────────────────────────────────────────────────────────────

def log_reading(room_id, co2, tvoc, temperature, humidity):
    with _conn() as c:
        c.execute(
            "INSERT INTO readings (room_id, ts, co2, tvoc, temperature, humidity) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (room_id, time.time(), co2, tvoc, temperature, humidity),
        )


def get_readings(room_id, since_ts=None):
    with _conn() as c:
        if since_ts:
            rows = c.execute(
                "SELECT ts, co2, tvoc, temperature, humidity "
                "FROM readings WHERE room_id=? AND ts>=? ORDER BY ts",
                (room_id, since_ts),
            ).fetchall()
        else:
            rows = c.execute(
                "SELECT ts, co2, tvoc, temperature, humidity "
                "FROM readings WHERE room_id=? ORDER BY ts",
                (room_id,),
            ).fetchall()
        return [dict(r) for r in rows]


def get_stats(room_id, since_ts=None):
    with _conn() as c:
        if since_ts:
            row = c.execute(
                "SELECT AVG(co2) co2, AVG(tvoc) tvoc, "
                "       AVG(temperature) temperature, AVG(humidity) humidity, "
                "       COUNT(*) n "
                "FROM readings WHERE room_id=? AND ts>=?",
                (room_id, since_ts),
            ).fetchone()
        else:
            row = c.execute(
                "SELECT AVG(co2) co2, AVG(tvoc) tvoc, "
                "       AVG(temperature) temperature, AVG(humidity) humidity, "
                "       COUNT(*) n "
                "FROM readings WHERE room_id=?",
                (room_id,),
            ).fetchone()
        return dict(row) if row else {}
