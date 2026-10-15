import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI


load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError(
        "GOOGLE_API_KEY was not found in the .env file."
    )

print("✓ API key loaded successfully.")

llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    temperature=0,
    google_api_key=api_key,
)

response = llm.invoke(
    "Reply with exactly: Gemini connection successful."
)

print("\nGemini response:")
print(response.content)

print("\n✓ Gemini test passed!")