#!/usr/bin/env python3
import sqlite3
import os

# Check if database file exists
db_path = './fomc_data.db'
if not os.path.exists(db_path):
    print("Database file does not exist")
    exit(1)

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get table schemas
print("Database Tables and Their Schemas:")
print("=" * 50)

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

for table in tables:
    table_name = table[0]
    print(f"\nTable: {table_name}")
    print("-" * 30)
    
    # Get table info
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    
    for col in columns:
        print(f"Column: {col[1]} ({col[2]}) - Not Null: {bool(col[3])} - Default: {col[4]} - PK: {bool(col[5])}")

# Get some sample data
print("\n\nSample Data from economic_indicators:")
print("-" * 50)
try:
    cursor.execute("SELECT * FROM economic_indicators LIMIT 5;")
    indicators = cursor.fetchall()
    for indicator in indicators:
        print(indicator)
except Exception as e:
    print(f"Error fetching data: {e}")

print("\n\nSample Data from economic_data_points:")
print("-" * 50)
try:
    cursor.execute("SELECT * FROM economic_data_points LIMIT 5;")
    data_points = cursor.fetchall()
    for point in data_points:
        print(point)
except Exception as e:
    print(f"Error fetching data: {e}")

conn.close()