"""Tiny SQLite layer using only the standard library. One table: every health check is saved."""
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_DB = Path(__file__).resolve().parent.parent / "fincortex.db"


def _path() -> str:
    return os.environ.get("FINCORTEX_DB", str(DEFAULT_DB))   # tests point this at a temp file


@contextmanager
def connect():
    conn = sqlite3.connect(_path())
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with connect() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            score INTEGER NOT NULL,
            salary REAL NOT NULL,
            savings_rate_pct REAL NOT NULL,
            risk_appetite TEXT NOT NULL)""")


def save_check(score: int, salary: float, savings_rate_pct: float, risk: str) -> tuple[int, str]:
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with connect() as c:
        cur = c.execute(
            "INSERT INTO checks (created_at, score, salary, savings_rate_pct, risk_appetite) VALUES (?, ?, ?, ?, ?)",
            (now, score, salary, savings_rate_pct, risk),
        )
        return cur.lastrowid, now


def list_checks(limit: int = 50) -> list[dict]:
    with connect() as c:
        rows = c.execute("SELECT * FROM checks ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return [dict(r) for r in rows]


def delete_check(check_id: int) -> bool:
    with connect() as c:
        return c.execute("DELETE FROM checks WHERE id = ?", (check_id,)).rowcount > 0
