import sqlite3
import csv

conn = sqlite3.connect("/Users/imran/Desktop/Scred/data.db")
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id ANY UNIQUE,
        name TEXT,
        social_credit INTEGER
    )
''')

with open('/Users/imran/Desktop/Scred/new.csv', 'r') as file:
    for line in file:
        row = line.strip().split(',')

        cursor.execute('''
            INSERT INTO users (id, name, social_credit)
            VALUES (?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                social_credit = users.social_credit + excluded.social_credit;
        ''', (row[0], row[1], row[2]))

conn.commit()

cursor.execute("SELECT * FROM users")

rows = cursor.fetchall()

print("ID       | Name       | Social Credit")
print("-" * 35)

for row in rows:
    print(f"{row[0]:<2} | {row[1]:<10} | {row[2]}")

with open("/Users/imran/Desktop/Scred/new.csv", mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerows([])

conn.close()
