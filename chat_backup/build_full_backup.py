import os
import zipfile
import sqlite3

conv_id = 'dfaefe40-f699-4276-8717-cb4f8030016c'
appdata_dir = r'C:\Users\yoga\.gemini\antigravity'
backup_folder = r'E:\antigravity-novel-engine\chat_backup'

zip_path = os.path.join(backup_folder, 'antigravity_chat_session.zip')
brain_dir = os.path.join(appdata_dir, 'brain', conv_id)
conv_db = os.path.join(appdata_dir, 'conversations', f'{conv_id}.db')
sum_db_path = os.path.join(appdata_dir, 'conversation_summaries.db')

conn = sqlite3.connect(sum_db_path)
c = conn.cursor()
c.execute('SELECT * FROM conversation_summaries WHERE conversation_id = ?;', (conv_id,))
row = c.fetchone()
col_names = [d[0] for d in c.description]
conn.close()

row_db_temp = os.path.join(backup_folder, 'conversation_row.db')
if os.path.exists(row_db_temp):
    os.remove(row_db_temp)
m_conn = sqlite3.connect(row_db_temp)
m_c = m_conn.cursor()
col_defs = ', '.join([f'"{name}"' for name in col_names])
placeholders = ', '.join(['?' for _ in col_names])
m_c.execute(f'CREATE TABLE conversation_summary ({col_defs});')
m_c.execute(f'INSERT INTO conversation_summary VALUES ({placeholders});', row)
m_conn.commit()
m_conn.close()

print('Adding all 3 components into antigravity_chat_session.zip...')
with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for root, dirs, files in os.walk(brain_dir):
        for f in files:
            full_path = os.path.join(root, f)
            rel = os.path.relpath(full_path, brain_dir)
            z.write(full_path, arcname=os.path.join('brain', conv_id, rel))
    z.write(conv_db, arcname=os.path.join('conversations', f'{conv_id}.db'))
    z.write(row_db_temp, arcname='conversation_row.db')

if os.path.exists(row_db_temp):
    os.remove(row_db_temp)

print('Updated zip size:', f'{os.path.getsize(zip_path):,} bytes ({os.path.getsize(zip_path)/(1024*1024):.2f} MB)')
