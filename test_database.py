import sqlite3
from pathlib import Path

DB_PATH = Path("database/chinook.db")

if not DB_PATH.exists():
    raise FileNotFoundError(f"Database not found: {DB_PATH}")

conn = sqlite3.connect(DB_PATH)

cursor = conn.cursor()

cursor.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type='table'
    ORDER BY name;
""")

tables = cursor.fetchall()

print("=" * 60)
print("Chinook Database Test")
print("=" * 60)

print("\nTables:")

for table in tables:
    print(f"✓ {table[0]}")

conn.close()

print("\n✓ Database connection successful!")