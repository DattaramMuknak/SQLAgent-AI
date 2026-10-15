import sqlite3
from pathlib import Path
from typing import Any

import sqlglot
from sqlglot import exp


DB_PATH = Path(__file__).resolve().parent.parent / "database" / "chinook.db"


class ReadOnlyDatabase:
    """Safe read-only interface for the Chinook SQLite database."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path

        if not self.db_path.exists():
            raise FileNotFoundError(
                f"Database not found: {self.db_path}"
            )

    def _connect(self):
        """Create a read-only SQLite connection."""
        uri = f"file:{self.db_path.resolve()}?mode=ro"

        return sqlite3.connect(
            uri,
            uri=True
        )

    def list_tables(self) -> list[str]:
        """Return all database tables."""

        with self._connect() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                ORDER BY name;
            """)

            return [row[0] for row in cursor.fetchall()]

    def get_schema(self, table_name: str) -> list[dict[str, Any]]:
        """Return column information for a table."""

        tables = self.list_tables()

        if table_name not in tables:
            raise ValueError(
                f"Unknown table: {table_name}"
            )

        with self._connect() as conn:
            cursor = conn.cursor()

            cursor.execute(
                f'PRAGMA table_info("{table_name}")'
            )

            rows = cursor.fetchall()

            return [
                {
                    "cid": row[0],
                    "name": row[1],
                    "type": row[2],
                    "not_null": bool(row[3]),
                    "default": row[4],
                    "primary_key": bool(row[5]),
                }
                for row in rows
            ]

    def get_full_schema(self) -> dict[str, list[dict[str, Any]]]:
        """Return the schema of the entire database."""

        return {
            table: self.get_schema(table)
            for table in self.list_tables()
        }

    def execute_read_only(self, query: str) -> list[dict[str, Any]]:
        """
        Execute exactly one read-only SQL statement.

        Only SELECT and WITH queries are allowed.
        SQL is parsed with sqlglot before execution.
        """

        cleaned_query = query.strip()

        if not cleaned_query:
            raise ValueError("SQL query cannot be empty.")

        # ---------------------------------------------------------
        # 1. Parse SQL and require exactly one statement
        # ---------------------------------------------------------
        try:
            statements = sqlglot.parse(
                cleaned_query,
                read="sqlite"
            )
        except sqlglot.errors.ParseError as exc:
            raise PermissionError(
                f"Invalid SQL query: {exc}"
            ) from exc

        if len(statements) != 1:
            raise PermissionError(
                "Only one SQL statement is allowed."
            )

        statement = statements[0]

        # ---------------------------------------------------------
        # 2. Allow only SELECT / WITH queries
        # ---------------------------------------------------------
        if not isinstance(statement, exp.Query):
            raise PermissionError(
                "Only SELECT and WITH queries are allowed."
            )

        # ---------------------------------------------------------
        # 3. Reject dangerous SQL operations
        # ---------------------------------------------------------
        forbidden_expressions = (
            exp.Insert,
            exp.Update,
            exp.Delete,
            exp.Drop,
            exp.Create,
            exp.Alter,
            exp.Command,
            exp.Attach,
            exp.Transaction,
        )

        for expression_type in forbidden_expressions:
            if statement.find(expression_type):
                raise PermissionError(
                    "Forbidden SQL operation detected."
                )

        # ---------------------------------------------------------
        # 4. Reject PRAGMA
        # ---------------------------------------------------------
        if statement.find(exp.Pragma):
            raise PermissionError(
                "PRAGMA statements are not allowed."
            )

        # ---------------------------------------------------------
        # 5. Execute only after successful validation
        # ---------------------------------------------------------
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row

            cursor = conn.cursor()
            cursor.execute(cleaned_query)

            rows = cursor.fetchall()

            return [dict(row) for row in rows]