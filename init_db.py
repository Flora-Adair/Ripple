import sqlite3

# Connects to the database file (creates it if it doesn't exist)
conn = sqlite3.connect('database.db')

# Opens and reads schema.sql
with open('schema.sql') as f:
    conn.executescript(f.read())

# Closes the connection
conn.close()

print("Database initialized!")
