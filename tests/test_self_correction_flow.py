from src.graph import SQLAgentGraph

agent = SQLAgentGraph()

state = {
    "question": "How many customers are there?",
    "schema": agent.db.get_full_schema(),
    "sql": "SELECT COUNT(*) FROM Customers;",
    "result": [],
    "error": "no such table: Customers",
    "attempts": 1,
    "answer": "",
    "should_chart": False,
    "chart": None,
}

print("=" * 70)
print("SQLAgent AI - SELF-CORRECTION FLOW CHECK")
print("=" * 70)

print("\n1. check_result()")
print("Decision:", agent.check_result(state))

print("\n2. execute_sql() with intentionally invalid SQL")
result = agent.execute_sql(state)
print("Error:", result["error"])
print("Result:", result["result"])

print("\n3. Retry condition")
print("Attempts:", state["attempts"])
print("MAX_RETRIES:", agent.MAX_RETRIES)
print("Expected decision: retry")

print("\n" + "=" * 70)
print("OFFLINE SELF-CORRECTION FLOW CHECK COMPLETED")
print("=" * 70)
