import sqlite3

db_path = r"C:\Users\Eevyx\.gemini\antigravity\conversation_summaries.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute("SELECT conversation_id, title, step_count, last_modified_time FROM conversation_summaries WHERE conversation_id = 'dfaefe40-f699-4276-8717-cb4f8030016c';")
row = c.fetchone()
print("Current row for our conversation:")
print(row)
