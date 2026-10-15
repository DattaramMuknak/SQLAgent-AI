from src.graph import SQLAgentGraph

agent = SQLAgentGraph()

questions = [
    "How many customers are there?",
    "How many invoices are there?",
    "What is the total revenue?",
    "What is the average invoice total?",
    "How many tracks are there in each genre?",
    "Show me the top 10 customers by total spending",
    "How many invoices were made by customers from Brazil?",
    "Show me the top 10 genres by number of tracks",
]

print("=" * 70)
print("SQLAgent AI - COMPREHENSIVE AGENT EVALUATION")
print("=" * 70)

for i, question in enumerate(questions, 1):
    print(f"\nTEST {i}: {question}")
    print("-" * 70)

    try:
        result = agent.run(question)

        print("SQL:", result["sql"])
        print("Answer:", result["answer"])
        print("Attempts:", result["attempts"])
        print("Chart:", result["chart"] is not None)

        if result["chart"]:
            print("Chart title:", result["chart"].layout.title.text)

    except Exception as e:
        print("ERROR:", type(e).__name__)
        print("MESSAGE:", str(e))

print("\n" + "=" * 70)
print("EVALUATION COMPLETED")
print("=" * 70)
