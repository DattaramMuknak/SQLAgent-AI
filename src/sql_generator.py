import os

import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq


load_dotenv()


class SQLGenerator:
    """Generate and correct safe read-only SQL queries."""

    def __init__(self, provider: str | None = None):
        provider = (
            provider
            or os.getenv("LLM_PROVIDER", "groq")
        ).lower().strip()

        if provider not in {"gemini", "groq"}:
            raise ValueError(
                "Unsupported LLM provider. Choose 'gemini' or 'groq'."
            )

        self.provider = provider
        self.primary_provider = provider
        self.fallback_provider = (
            "gemini" if provider == "groq" else "groq"
        )
        self.active_provider = provider

        self.llm = self._create_llm(provider)

    def _get_api_key(self, provider: str):
        if provider == "groq":
            env_key = "GROQ_API_KEY"
        else:
            env_key = "GOOGLE_API_KEY"

        api_key = os.getenv(env_key)

        if not api_key:
            try:
                api_key = st.secrets.get(env_key)
            except Exception:
                api_key = None

        if not api_key:
            raise ValueError(
                f"{env_key} was not found in environment variables "
                "or Streamlit Secrets."
            )

        return api_key

    def _create_llm(self, provider: str):
        if provider == "groq":
            api_key = self._get_api_key("groq")

            return ChatGroq(
                model="openai/gpt-oss-120b",
                temperature=0,
                groq_api_key=api_key,
            )

        api_key = self._get_api_key("gemini")

        return ChatGoogleGenerativeAI(
            model="gemini-3.7-flash",
            temperature=0,
            google_api_key=api_key,
        )

    def _invoke_with_fallback(self, prompt: str):
        try:
            self.active_provider = self.primary_provider
            return self.llm.invoke(prompt)

        except Exception as primary_error:
            fallback_provider = self.fallback_provider

            try:
                fallback_llm = self._create_llm(fallback_provider)

                self.active_provider = fallback_provider

                return fallback_llm.invoke(prompt)

            except Exception as fallback_error:
                raise RuntimeError(
                    f"Primary provider '{self.primary_provider}' failed: "
                    f"{primary_error}. "
                    f"Fallback provider '{fallback_provider}' also failed: "
                    f"{fallback_error}"
                ) from fallback_error

    def _extract_text(self, response) -> str:
        content = response.content

        if isinstance(content, list):
            text_parts = []

            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text_parts.append(item.get("text", ""))

            return "".join(text_parts).strip()

        return str(content).strip()

    def _clean_sql(self, sql: str) -> str:
        sql = sql.strip()

        if sql.startswith("```sql"):
            sql = sql[len("```sql"):].strip()

        if sql.startswith("```"):
            sql = sql[len("```"):].strip()

        if sql.endswith("```"):
            sql = sql[:-3].strip()

        return sql

    def generate_sql(self, question: str, schema: str) -> str:
        prompt = f"""
You are an expert SQLite Text-to-SQL system.

Convert the user's natural language question into ONE valid SQLite query.

DATABASE SCHEMA:
{schema}

USER QUESTION:
{question}

STRICT RULES:
1. Generate ONLY a SELECT or WITH query.
2. Never generate INSERT, UPDATE, DELETE, DROP, ALTER,
   CREATE, REPLACE, TRUNCATE, ATTACH, or DETACH.
3. Use only tables and columns that exist in the schema.
4. Do not invent tables or columns.
5. Return ONLY the SQL query.
6. Do not use markdown code fences.
7. Do not include explanations.
"""

        response = self._invoke_with_fallback(prompt)

        return self._clean_sql(
            self._extract_text(response)
        )

    def correct_sql(
        self,
        question: str,
        schema: str,
        previous_sql: str,
        error: str,
    ) -> str:
        prompt = f"""
You are an expert SQLite SQL debugging agent.

The previous SQL query failed during execution.

DATABASE SCHEMA:
{schema}

USER QUESTION:
{question}

PREVIOUS SQL:
{previous_sql}

DATABASE ERROR:
{error}

Your task is to fix the SQL query.

STRICT RULES:
1. Return ONE valid SQLite query.
2. The query MUST be SELECT or WITH.
3. Never use INSERT, UPDATE, DELETE, DROP, ALTER,
   CREATE, REPLACE, TRUNCATE, ATTACH, or DETACH.
4. Use only tables and columns that exist in the schema.
5. Correct the query based on the database error.
6. Return ONLY the corrected SQL.
7. Do not use markdown code fences.
8. Do not include explanations.
"""

        response = self._invoke_with_fallback(prompt)

        return self._clean_sql(
            self._extract_text(response)
        )
