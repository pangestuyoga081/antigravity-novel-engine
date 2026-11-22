import os
import shutil
import sqlite3

repo_dir = r"D:\JV\novel yoga"
backup_root = os.path.join(repo_dir, "antigravity_complete_backup")
os.makedirs(backup_root, exist_ok=True)

conv_id = "dfaefe40-f699-4276-8717-cb4f8030016c"
appdata_dir = r"C:\Users\Eevyx\.gemini\antigravity"

# 1. Copy brain folder
brain_src = os.path.join(appdata_dir, "brain", conv_id)
brain_dst = os.path.join(backup_root, "brain", conv_id)
if os.path.exists(brain_dst):
    shutil.rmtree(brain_dst, ignore_errors=True)
os.makedirs(os.path.dirname(brain_dst), exist_ok=True)

print("Copying brain folder...")
for root, dirs, files in os.walk(brain_src):
    rel = os.path.relpath(root, brain_src)
    target_dir = os.path.join(brain_dst, rel)
    os.makedirs(target_dir, exist_ok=True)
    for f in files:
        if f.endswith('.html') and os.path.getsize(os.path.join(root, f)) > 2*1024*1024:
            continue
        try:
            shutil.copy2(os.path.join(root, f), os.path.join(target_dir, f))
        except Exception:
            pass

# 2. Copy conversations sqlite db file
conv_db_src = os.path.join(appdata_dir, "conversations", f"{conv_id}.db")
conv_db_dst_dir = os.path.join(backup_root, "conversations")
os.makedirs(conv_db_dst_dir, exist_ok=True)
if os.path.exists(conv_db_src):
    print("Copying conversations db...")
    shutil.copy2(conv_db_src, os.path.join(conv_db_dst_dir, f"{conv_id}.db"))

# 3. Export row from conversation_summaries.db
print("Exporting summary row...")
sum_db_path = os.path.join(appdata_dir, "conversation_summaries.db")
conn = sqlite3.connect(sum_db_path)
c = conn.cursor()
c.execute("SELECT * FROM conversation_summaries WHERE conversation_id = ?;", (conv_id,))
row = c.fetchone()
col_names = [d[0] for d in c.description]
conn.close()

# Save export summary row as a standalone sqlite db in backup
mini_db_path = os.path.join(backup_root, "conversation_row.db")
if os.path.exists(mini_db_path):
    os.remove(mini_db_path)
m_conn = sqlite3.connect(mini_db_path)
m_c = m_conn.cursor()
col_defs = ", ".join([f'"{name}"' for name in col_names])
placeholders = ", ".join(["?" for _ in col_names])
m_c.execute(f"CREATE TABLE conversation_summary ({col_defs});")
m_c.execute(f"INSERT INTO conversation_summary VALUES ({placeholders});", row)
m_conn.commit()
m_conn.close()

print("Backup complete!")
