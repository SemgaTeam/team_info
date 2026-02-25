import sqlite3
from typing import Any, List

class DB:
    def __init__(self, db_path: str):
        self.DB_PATH = db_path
        self.conn = sqlite3.connect(db_path)

    def __del__(self):
        self.conn.close()
        
    def init_db(self) -> None:
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS webhook_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                sender_login TEXT,
                repository_name TEXT,
                payload_json TEXT NOT NULL,
                received_at TEXT NOT NULL
            )
            """
        )
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS member_stats (
                login TEXT PRIMARY KEY,
                commits INTEGER NOT NULL DEFAULT 0,
                closed_issues INTEGER NOT NULL DEFAULT 0,
                updated_at TEXT NOT NULL
            )
            """
        )
        self.conn.commit()
    
    def insert_member_stats(self, member, commits, issues, updated_time):
        self.conn.execute(
            """
            INSERT INTO member_stats (login, commits, closed_issues, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(login) DO UPDATE SET
                commits = excluded.commits,
                closed_issues = excluded.closed_issues,
                updated_at = excluded.updated_at
            """,
            (member, commits, issues, updated_time),
        )
        print("insert member stats", member, commits, issues)
        self.conn.commit()

    def insert_webhook_event(self, event_type, sender_login, repository_name, payload_json, received_at):
        self.conn.execute(
            """
            INSERT INTO webhook_events (event_type, sender_login, repository_name, payload_json, received_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                event_type,
                sender_login,
                repository_name,
                payload_json,
                received_at,
            ),
        )

    def get_members_stats(self) -> List[Any]:
        rows = self.conn.execute(
            """
            SELECT login, commits, closed_issues, updated_at
            FROM member_stats
            """
        ).fetchall()

        print(rows)
        return rows

    def get_member_stats_by_login(self, login: str):
        row = self.conn.execute(
            """
            SELECT commits, closed_issues, updated_at
            FROM member_stats
            WHERE login = ?
            """,
            (login)
        ).fetchone()

        print(row)
        return row