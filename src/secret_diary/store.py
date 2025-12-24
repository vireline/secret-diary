from __future__ import annotations

import sqlite3
from pathlib import Path
from dataclasses import dataclass

DB_NAME = "secret_diary.db"

SCHEMA = '''
CREATE TABLE IF NOT EXISTS meta (
  k TEXT PRIMARY KEY,
  v BLOB NOT NULL
);

CREATE TABLE IF NOT EXISTS notes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title BLOB NOT NULL,
  tags BLOB NOT NULL,
  body BLOB NOT NULL,
  created_at TEXT NOT NULL
);
'''

def db_path(home: Path) -> Path:
    return home / DB_NAME

def connect(home: Path) -> sqlite3.Connection:
    p = db_path(home)
    con = sqlite3.connect(p)
    con.execute("PRAGMA journal_mode=WAL;")
    con.executescript(SCHEMA)
    con.commit()
    return con
