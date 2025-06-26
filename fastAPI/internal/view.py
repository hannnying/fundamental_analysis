import sqlite3
import pandas as pd
from database import db_path

# Connect
conn = sqlite3.connect(f"{db_path}")
cursor = conn.cursor()
df = pd.read_sql("SELECT * FROM income_statements;", conn)
df.to_csv("view.csv", index=False)

conn.close()
