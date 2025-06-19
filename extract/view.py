import sqlite3
import pandas as pd

# Connect
conn = sqlite3.connect("fundamentals.db")

# uncomment to delete past data
# cursor = conn.cursor()
# cursor.execute("DROP TABLE IF EXISTS Filing")
# # cursor.execute("DELETE FROM Filing")
# conn.commit()

# List tables
tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn)
print("Tables:\n", tables)

# View Filing Table
# df = pd.read_sql("SELECT * FROM Filing;", conn)
# df.to_csv("filing.csv", index=False)
# print(df.head())

# View IncomeStatement Table
# df = pd.read_sql("SELECT * FROM IncomeStatement;", conn)
# df.to_csv("income_statement.csv", index=False)
# print(df.head())

# View BalanceSheet Table
df = pd.read_sql("SELECT * FROM BalanceSheet;", conn)
df.to_csv("balance_sheet.csv", index=False)
print(df.head())

conn.close()
