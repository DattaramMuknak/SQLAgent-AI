from pathlib import Path
from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from src.database import ReadOnlyDatabase
from src.sql_generator import SQLGenerator
from src.summarizer import ResultSummarizer
from src.chart_tool import ChartTool


class SQLAgentState(TypedDict):
    question: str
    schema: str
    sql: str
    result: list
    error: str
    attempts: int
    answer: str
    should_chart: bool
    chart: object


class SQLAgentGraph:
    """Autonomous LangGraph Text-to-SQL analytics agent."""

    MAX_RETRIES = 2

    def __init__(
        self,
        db_path: str = "database/chinook.db",
        provider: str | None = None,
    ):
        self.db = ReadOnlyDatabase(Path(db_path))
        self.generator = SQLGenerator(provider=provider)
        self.summarizer = ResultSummarizer(provider=provider)
        self.chart_tool = ChartTool()

        graph = StateGraph(SQLAgentState)

        graph.add_node("generate_sql", self.generate_sql)
        graph.add_node("execute_sql", self.execute_sql)
        graph.add_node("correct_sql", self.correct_sql)
        graph.add_node("summarize_result", self.summarize_result)
        graph.add_node("prepare_chart", self.prepare_chart)

        graph.add_edge(START, "generate_sql")
        graph.add_edge("generate_sql", "execute_sql")

        graph.add_conditional_edges(
            "execute_sql",
            self.check_result,
            {
                "success": "summarize_result",
                "retry": "correct_sql",
                "failed": END,
            },
        )

        graph.add_edge("correct_sql", "execute_sql")
        graph.add_edge("summarize_result", "prepare_chart")
        graph.add_edge("prepare_chart", END)

        self.graph = graph.compile()

    def generate_sql(self, state):
        schema = self.db.get_full_schema()

        sql = self.generator.generate_sql(
            question=state["question"],
            schema=schema,
        )

        return {
            "schema": schema,
            "sql": sql,
            "error": "",
            "attempts": 1,
        }

    def execute_sql(self, state):
        try:
            result = self.db.execute_read_only(state["sql"])

            return {
                "result": result,
                "error": "",
            }

        except Exception as exc:
            error_message = str(exc)

            return {
                "result": [],
                "error": error_message,
            }

    def check_result(self, state):
        if not state["error"]:
            return "success"

        if state["attempts"] >= self.MAX_RETRIES:
            return "failed"

        return "retry"

    def correct_sql(self, state):
        print(
            f"SQL attempt {state['attempts']} failed: "
            f"{state['error']}"
        )

        sql = self.generator.correct_sql(
            question=state["question"],
            schema=state["schema"],
            previous_sql=state["sql"],
            error=state["error"],
        )

        return {
            "sql": sql,
            "attempts": state["attempts"] + 1,
        }

    def summarize_result(self, state):
        answer = self.summarizer.summarize(
            question=state["question"],
            sql=state["sql"],
            result=state["result"],
        )

        return {
            "answer": answer,
        }

    def prepare_chart(self, state):
        df = self.chart_tool.result_to_dataframe(state["result"])

        should_chart = self.chart_tool.should_chart(df)

        chart = None

        if should_chart:
            chart = self.chart_tool.create_chart(df)

        return {
            "should_chart": should_chart,
            "chart": chart,
        }

    def run(self, question: str):
        initial_state: SQLAgentState = {
            "question": question,
            "schema": "",
            "sql": "",
            "result": [],
            "error": "",
            "attempts": 0,
            "answer": "",
            "should_chart": False,
            "chart": None,
        }

        return self.graph.invoke(initial_state)
