import os

import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq


load_dotenv()


class ResultSummarizer:
    """Convert SQL results into concise natural-language answers."""

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

    def summarize(
        self,
        question: str,
        sql: str,
        result: list,
    ) -> str:
        prompt = f"""
You are an analytics assistant.

Answer the user's question using the SQL result.

USER QUESTION:
{question}

SQL QUERY:
{sql}

SQL RESULT:
{result}

RULES:
1. Answer directly and clearly.
2. Use only information present in the SQL result.
3. Do not invent facts.
4. Do not mention internal implementation details.
5. Keep the answer concise.
6. If the result contains a single number, explain what that number represents.
"""

        response = self._invoke_with_fallback(prompt)

        return self._extract_text(response)
