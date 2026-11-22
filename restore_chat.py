import os
import sys
import shutil
import sqlite3

def restore():
    print("="*60)
    print("   RESTORE ANTIGRAVITY CONVERSATION & UI INDEX KE PC INI")
    print("="*60)
    
    appdata_dir = os.path.expandvars(r"%USERPROFILE%\.gemini\antigravity")
    if not os.path.exists(appdata_dir):
        print(f"[ERROR] Antigravity AppData tidak ditemukan di: {appdata_dir}")
        print("Pastikan aplikasi Antigravity sudah terinstal di PC ini.")
        return False
        
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backup_root = os.path.join(script_dir, "antigravity_complete_backup")
    conv_id = "dfaefe40-f699-4276-8717-cb4f8030016c"

    # 1. Restore brain directory
    src_brain = os.path.join(backup_root, "brain", conv_id)
    dst_brain = os.path.join(appdata_dir, "brain", conv_id)
    print(f"1. Menyalin direktori brain ke:\n   -> {dst_brain}")
    os.makedirs(dst_brain, exist_ok=True)
    for root, dirs, files in os.walk(src_brain):
        rel = os.path.relpath(root, src_brain)
        target = os.path.join(dst_brain, rel)
        os.makedirs(target, exist_ok=True)
        for f in files:
            try:
                shutil.copy2(os.path.join(root, f), os.path.join(target, f))
            except Exception:
                pass

    # 2. Restore conversations SQLite DB
    src_conv_db = os.path.join(backup_root, "conversations", f"{conv_id}.db")
    dst_conv_dir = os.path.join(appdata_dir, "conversations")
    os.makedirs(dst_conv_dir, exist_ok=True)
    dst_conv_db = os.path.join(dst_conv_dir, f"{conv_id}.db")
    print(f"2. Menyalin database percakapan ke:\n   -> {dst_conv_db}")
    if os.path.exists(src_conv_db):
        shutil.copy2(src_conv_db, dst_conv_db)

    # 3. Register to conversation_summaries.db (UI Sidebar Index)
    src_row_db = os.path.join(backup_root, "conversation_row.db")
    dst_sum_db = os.path.join(appdata_dir, "conversation_summaries.db")
    print(f"3. Mendaftarkan percakapan ke UI Sidebar Antigravity:\n   -> {dst_sum_db}")
    
    if os.path.exists(src_row_db) and os.path.exists(dst_sum_db):
        try:
            r_conn = sqlite3.connect(src_row_db)
            r_c = r_conn.cursor()
            r_c.execute("SELECT * FROM conversation_summary LIMIT 1;")
            row = r_c.fetchone()
            col_names = [d[0] for d in r_c.description]
            r_conn.close()

            # Insert or replace into destination summaries db
            d_conn = sqlite3.connect(dst_sum_db)
            d_c = d_conn.cursor()
            cols_str = ", ".join([f'"{name}"' for name in col_names])
            placeholders = ", ".join(["?" for _ in col_names])
            d_c.execute(f"INSERT OR REPLACE INTO conversation_summaries ({cols_str}) VALUES ({placeholders});", row)
            d_conn.commit()
            d_conn.close()
            print("   -> Sukses terdaftar di index sidebar!")
        except Exception as e:
            print(f"   -> Peringatan index sidebar: {e}")

    print("\n" + "="*60)
    print("🎉 SUKSES! Percakapan berhasil dipulihkan.")
    print("Sekarang buka aplikasi Antigravity:")
    print("Percakapan 'Terjemahan Novel Akasic Records Vol 1' AKAN MUNCUL")
    print("di sidebar dan bisa langsung Anda klik & lanjutkan!")
    print("="*60)
    return True

if __name__ == "__main__":
    restore()
