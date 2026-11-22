import sqlite3
import os

db_path = os.path.expandvars(r'%APPDATA%\9router\db\data.sqlite')
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [r[0] for r in cur.fetchall()]
print('Tables:', tables)

for t in tables:
    if any(k in t.lower() for k in ['key', 'auth', 'token', 'user', 'setting']):
        print('=== Table:', t, '===')
        cur.execute(f"PRAGMA table_info('{t}');")
        cols = [c[1] for c in cur.fetchall()]
        print('Cols:', cols)
        cur.execute(f"SELECT * FROM '{t}' LIMIT 5;")
        for row in cur.fetchall():
            print('  Row:', row)
