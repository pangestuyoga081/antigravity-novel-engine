import os
import sys
import shutil
import sqlite3
import datetime

def sync_latest_backup():
    print("="*60)
    print("   SINKRONISASI BACKUP CHAT TERBARU (UP-TO-DATE)")
    print("="*60)
    
    appdata_dir = os.path.expandvars(r"%USERPROFILE%\.gemini\antigravity")
    repo_dir = r"D:\JV\novel yoga"
    backup_root = os.path.join(repo_dir, "antigravity_complete_backup")
    conv_id = "dfaefe40-f699-4276-8717-cb4f8030016c"

    # 1. Update Brain directory
    src_brain = os.path.join(appdata_dir, "brain", conv_id)
    dst_brain = os.path.join(backup_root, "brain", conv_id)
    print(f"1. Menyinkronkan brain dari:\n   {src_brain}\n   -> {dst_brain}")
    os.makedirs(dst_brain, exist_ok=True)
    
    copied_count = 0
    for root, dirs, files in os.walk(src_brain):
        rel = os.path.relpath(root, src_brain)
        target = os.path.join(dst_brain, rel)
        os.makedirs(target, exist_ok=True)
        for f in files:
            # skip oversized scratch dumps (>5MB) if any
            src_file = os.path.join(root, f)
            dst_file = os.path.join(target, f)
            try:
                if f.endswith('.html') and os.path.getsize(src_file) > 2*1024*1024:
                    continue
                shutil.copy2(src_file, dst_file)
                copied_count += 1
            except Exception as e:
                pass
    print(f"   -> {copied_count} file brain tersinkronkan.")

    # 2. Update Conversations SQLite DB
    src_conv_db = os.path.join(appdata_dir, "conversations", f"{conv_id}.db")
    dst_conv_dir = os.path.join(backup_root, "conversations")
    os.makedirs(dst_conv_dir, exist_ok=True)
    dst_conv_db = os.path.join(dst_conv_dir, f"{conv_id}.db")
    print(f"2. Menyalin SQLite DB live conversation ke:\n   -> {dst_conv_db}")
    if os.path.exists(src_conv_db):
        shutil.copy2(src_conv_db, dst_conv_db)
        print(f"   -> Ukuran DB: {os.path.getsize(dst_conv_db) / (1024*1024):.2f} MB")

    # 3. Update Conversation Summary Row (Sidebar Index)
    src_sum_db = os.path.join(appdata_dir, "conversation_summaries.db")
    dst_row_db = os.path.join(backup_root, "conversation_row.db")
    print(f"3. Menyimpan snapshot row index sidebar ke:\n   -> {dst_row_db}")
    if os.path.exists(src_sum_db):
        s_conn = sqlite3.connect(src_sum_db)
        s_c = s_conn.cursor()
        s_c.execute("SELECT * FROM conversation_summaries WHERE conversation_id=?", (conv_id,))
        row = s_c.fetchone()
        col_names = [d[0] for d in s_c.description]
        s_conn.close()

        if row:
            if os.path.exists(dst_row_db):
                os.remove(dst_row_db)
            r_conn = sqlite3.connect(dst_row_db)
            r_c = r_conn.cursor()
            cols_decl = ", ".join([f'"{name}" TEXT' for name in col_names])
            r_c.execute(f"CREATE TABLE conversation_summary ({cols_decl});")
            placeholders = ", ".join(["?" for _ in col_names])
            r_c.execute(f"INSERT INTO conversation_summary VALUES ({placeholders});", row)
            r_conn.commit()
            r_conn.close()
            print("   -> Snapshot UI sidebar tersimpan.")

    print("\n" + "="*60)
    print("✅ SINKRONISASI LENGKAP SELESAI HINGGA CHAT DETIK INI!")
    print("="*60)

if __name__ == "__main__":
    sync_latest_backup()
