import sys
import os
import json

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ENGINE_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
sys.path.append(ENGINE_ROOT)

from src.database.db import NovelDatabase

DB_PATH = os.path.join(ENGINE_ROOT, "novel_pipeline.db")
db = NovelDatabase(DB_PATH)

def main():
    if len(sys.argv) < 2:
        print("Usage: python db_bridge.py <command> [args...]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "init_project":
        # python db_bridge.py init_project <id> <title> <source_path> <profile_name> <total_chapters>
        pid, title, src, prof, total = sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], int(sys.argv[6])
        db.upsert_project_progress(pid, title, src, prof, total, 0, "in_progress")
        print(f"Project '{pid}' initialized with {total} chapters.")

    elif cmd == "update_chapter":
        # python db_bridge.py update_chapter <pid> <chap_id> <idx> <title> <char_count> <status> [translated_file]
        pid, cid, idx, title, chars, status = sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5], int(sys.argv[6]), sys.argv[7]
        trans_text = None
        if len(sys.argv) > 8 and os.path.exists(sys.argv[8]):
            with open(sys.argv[8], "r", encoding="utf-8", errors="ignore") as f:
                trans_text = f.read()

        db.record_chapter_snapshot(pid, cid, idx, title, chars, status, trans_text)
        
        # Count completed chapters for project
        with db.conn:
            completed = db.conn.execute("SELECT COUNT(*) as c FROM chapters WHERE project_id = ? AND status = 'completed'", (pid,)).fetchone()["c"]
            total_row = db.conn.execute("SELECT total_chapters FROM projects WHERE id = ?", (pid,)).fetchone()
            total = total_row["total_chapters"] if total_row else idx
            new_status = "completed" if completed >= total and total > 0 else "in_progress"
            db.conn.execute("UPDATE projects SET completed_chapters = ?, status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (completed, new_status, pid))

        print(f"Chapter '{cid}' recorded. Project '{pid}' progress: {completed}/{total}")

    elif cmd == "finish_project":
        # python db_bridge.py finish_project <pid>
        pid = sys.argv[2]
        with db.conn:
            db.conn.execute("UPDATE projects SET status = 'completed', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (pid,))
        print(f"Project '{pid}' marked as completed.")

if __name__ == "__main__":
    main()
