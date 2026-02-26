import sqlite3
from typing import Any, List
from entities import User, MemberStats

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
                user_id INTEGER,
                commits INTEGER NOT NULL DEFAULT 0,
                closed_issues INTEGER NOT NULL DEFAULT 0,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        )
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                github_login TEXT NOT NULL,
                telegram_id TEXT NOT NULL  
            )
            """
        )
        self.conn.commit()
    
    def insert_member_stats(self, user_id, commits, issues, updated_time):
        self.conn.execute(
            """
            INSERT INTO member_stats (user_id, commits, closed_issues, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(login) DO UPDATE SET
                commits = excluded.commits,
                closed_issues = excluded.closed_issues,
                updated_at = excluded.updated_at
            """,
            (user_id, commits, issues, updated_time),
        )
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
        self.conn.commit()

    def get_members_stats(self) -> List[MemberStats]:
        rows = self.conn.execute(
            """
            SELECT user_id, commits, closed_issues, updated_at
            FROM member_stats
            """
        ).fetchall()

        return rows

    def get_member_stats_by_user_id(self, id: int) -> MemberStats:
        row = self.conn.execute(
            """
            SELECT user_id, commits, closed_issues, updated_at
            FROM member_stats
            WHERE user_id = ?
            """,
            (id,)
        ).fetchone()

        return row

    def get_user_by_id(self, user_id: int) -> User:
        row = self.conn.execute(
            """
            SELECT id, github_login, telegram_id
            FROM users
            WHERE id = ?
            """,
            (user_id,)
        ).fetchone()

        return row

    def get_user_by_login(self, login: str) -> User:
        row = self.conn.execute(
            """
            SELECT id, github_login, telegram_id
            FROM users
            WHERE github_login = ?
            """,
            (login,)
        ).fetchone()

        return row
        