import json
import mysql.connector

# MySQL connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="admin@123",   
    database="chatbot_db"
)

cursor = conn.cursor()

# JSON load
with open("data.json", encoding="utf-8") as f:
    data = json.load(f)

count = 0

# ✅ CORRECT LOOP (intents format)
for intent in data["intents"]:
    patterns = intent.get("patterns", [])
    responses = intent.get("responses", [])

    for pattern in patterns:
        for response in responses:
            cursor.execute(
                "INSERT INTO data (question, answer) VALUES (%s, %s)",
                (pattern, response)
            )
            count += 1

conn.commit()
conn.close()

print(f"✅ {count} records inserted successfully!")