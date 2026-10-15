from pathlib import Path
from typing import TypedDict

from src.database import ReadOnlyDatabase
from src.sql_generator import SQLGenerator


class AgentState(TypedDict):
    question: str
    schema: str
    sql: str
    result: list
    error: str
    attempts: int


class SQLAgent:
    """Autonomous Text-to-SQL agent with bounded self-correction."""

    MAX_RETRIES = 3

    def __init__(self, db_path: str = "database/chinook.db"):
        self.db = ReadOnlyDatabase(Path(db_path))
        self.generator = SQLGenerator()

    def run(self, question: str) -> AgentState:
        schema = self.db.get_full_schema()

        state: AgentState = {
            "question": question,
            "schema": schema,
            "sql": "",
            "result": [],
            "error": "",
            "attempts": 0,
        }

        while state["attempts"] < self.MAX_RETRIES:

            state["attempts"] += 1

            try:
                # First attempt: generate SQL from the question.
                if state["attempts"] == 1:
                    sql = self.generator.generate_sql(
                        question=state["question"],
                        schema=state["schema"],
                    )

                # Retry: correct the previous SQL using the database error.
                else:
                    sql = self.generator.correct_sql(
                        question=state["question"],
                        schema=state["schema"],
                        previous_sql=state["sql"],
                        error=state["error"],
                    )

                state["sql"] = sql

                # Execute through the read-only database layer.
                state["result"] = self.db.execute_read_only(sql)

                # Success.
                state["error"] = ""

                return state

            except Exception as exc:
                state["error"] = str(exc)

                print(
                    f"⚠ Attempt {state['attempts']} failed: "
                    f"{state['error']}"
                )

        raise RuntimeError(
            f"SQL Agent failed after {self.MAX_RETRIES} attempts. "
            f"Last error: {state['error']}"
        )