
from pathlib import Path
from src.database import ReadOnlyDatabase
from src.sql_generator import SQLGenerator

db = ReadOnlyDatabase(Path("database/chinook.db"))

schema = db.get_full_schema()

generator = SQLGenerator()

question = "How many customers are there?"

print("User question:")
print(question)

sql = generator.generate_sql(question, schema)

print("\nGenerated SQL:")
print(sql)

print("\nExecuting SQL...")

result = db.execute_read_only(sql)

print("\nResult:")
print(result)

print("\n✓ SQL GENERATION TEST PASSED!")