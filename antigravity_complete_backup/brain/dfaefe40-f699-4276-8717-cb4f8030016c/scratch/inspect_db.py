import sqlite3

db_path = r"C:\Users\Eevyx\.gemini\antigravity\conversation_summaries.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = c.fetchall()
print("Tables:", tables)

for t in tables:
    t_name = t[0]
    print(f"\nSchema for {t_name}:")
    c.execute(f"PRAGMA table_info({t_name});")
    print(c.fetchall())
    c.execute(f"SELECT * FROM {t_name} WHERE id LIKE '%dfaefe40%' OR conversation_id LIKE '%dfaefe40%' LIMIT 5;")
    rows = c.fetchall()
    print(f"Rows matching dfaefe40 in {t_name}:", len(rows))
    for r in rows:
        print(" ", r)
