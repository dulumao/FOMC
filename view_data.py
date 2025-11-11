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

# Get economic indicators
print("Economic Indicators:")
print("-" * 50)
cursor.execute("SELECT id, name, code, description, frequency, units, seasonal_adjustment FROM economic_indicators;")
indicators = cursor.fetchall()

for indicator in indicators:
    print(f"ID: {indicator[0]}")
    print(f"Name: {indicator[1]}")
    print(f"Code: {indicator[2]}")
    print(f"Description: {indicator[3]}")
    print(f"Frequency: {indicator[4]}")
    print(f"Units: {indicator[5]}")
    print(f"Seasonal Adjustment: {indicator[6]}")
    print("-" * 30)

# Get some economic data points
print("\nSample Economic Data Points:")
print("-" * 50)
cursor.execute("SELECT indicator_id, date, value FROM economic_data_points ORDER BY date DESC LIMIT 10;")
data_points = cursor.fetchall()

for point in data_points:
    print(f"Indicator ID: {point[0]}, Date: {point[1]}, Value: {point[2]}")

conn.close()