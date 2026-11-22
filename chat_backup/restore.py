import os
import zipfile
import sqlite3
import shutil

conv_id = "dfaefe40-f699-4276-8717-cb4f8030016c"
target_dir = os.path.expandvars(r"%USERPROFILE%\.gemini\antigravity")
script_dir = os.path.dirname(os.path.abspath(__file__))
zip_file = os.path.join(script_dir, "antigravity_chat_session.zip")

print("====================================================================")
print("🚀 ANTIGRAVITY SESSION RESTORE (FULL 3-COMPONENT RESTORATION)")
print("====================================================================")

if not os.path.exists(zip_file):
    print(f"[ERROR] Berkas {zip_file} tidak ditemukan!")
    exit(1)

temp_dir = os.path.join(script_dir, "temp_restore")
if os.path.exists(temp_dir):
    shutil.rmtree(temp_dir)
os.makedirs(temp_dir, exist_ok=True)

print("Mengekstrak paket arsip sesi...")
with zipfile.ZipFile(zip_file, "r") as z:
    z.extractall(temp_dir)

# 1. Restore Brain
brain_src = os.path.join(temp_dir, "brain", conv_id)
brain_dst = os.path.join(target_dir, "brain", conv_id)
if os.path.exists(brain_src):
    print("Memulihkan folder brain (transcript, memory, artefak)...")
    os.makedirs(os.path.dirname(brain_dst), exist_ok=True)
    if os.path.exists(brain_dst):
        shutil.rmtree(brain_dst, ignore_errors=True)
    shutil.copytree(brain_src, brain_dst)

# 2. Restore Conversations DB
conv_db_src = os.path.join(temp_dir, "conversations", f"{conv_id}.db")
conv_db_dst = os.path.join(target_dir, "conversations", f"{conv_id}.db")
if os.path.exists(conv_db_src):
    print("Memulihkan database percakapan aktif...")
    os.makedirs(os.path.dirname(conv_db_dst), exist_ok=True)
    shutil.copy2(conv_db_src, conv_db_dst)

# 3. Restore Conversation Summary Row (Sidebar UI Index)
row_db = os.path.join(temp_dir, "conversation_row.db")
sum_db = os.path.join(target_dir, "conversation_summaries.db")
if os.path.exists(row_db):
    print("Mendaftarkan riwayat percakapan ke menu sidebar UI...")
    os.makedirs(target_dir, exist_ok=True)
    r_conn = sqlite3.connect(row_db)
    r_c = r_conn.cursor()
    r_c.execute("SELECT * FROM conversation_summary;")
    row = r_c.fetchone()
    cols = [d[0] for d in r_c.description]
    r_conn.close()

    s_conn = sqlite3.connect(sum_db)
    s_c = s_conn.cursor()
    s_c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='conversation_summaries';")
    if not s_c.fetchone():
        col_defs = ", ".join([f'"{name}"' for name in cols])
        s_c.execute(f"CREATE TABLE conversation_summaries ({col_defs});")

    s_c.execute("DELETE FROM conversation_summaries WHERE conversation_id = ?;", (conv_id,))
    placeholders = ", ".join(["?" for _ in cols])
    s_c.execute(f"INSERT INTO conversation_summaries VALUES ({placeholders});", row)
    s_conn.commit()
    s_conn.close()

shutil.rmtree(temp_dir, ignore_errors=True)

print("\n====================================================================")
print("✅ SUKSES! 3 Komponen Antigravity telah 100% dipulihkan.")
print("📌 Silakan buka / restart Antigravity, sesi ini akan langsung aktif!")
print("====================================================================")
