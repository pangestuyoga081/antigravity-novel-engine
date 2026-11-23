import sqlite3
import os
import json
from typing import Optional, Dict, Any, List

class NovelDatabase:
    def __init__(self, db_path: str):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_tables()

    def _init_tables(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    source_path TEXT NOT NULL,
                    profile_name TEXT NOT NULL,
                    total_chapters INTEGER DEFAULT 0,
                    completed_chapters INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS chapters (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    chapter_index INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    source_text TEXT NOT NULL,
                    translated_text TEXT,
                    char_count INTEGER NOT NULL,
                    status TEXT DEFAULT 'pending', -- pending, in_progress, completed, failed
                    validation_errors TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS chunks (
                    id TEXT PRIMARY KEY,
                    chapter_id TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    source_chunk TEXT NOT NULL,
                    translated_chunk TEXT,
                    status TEXT DEFAULT 'pending',
                    retry_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE CASCADE
                )
            """)
            self.conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_chapters_project ON chapters(project_id);
            """)
            self.conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_chunks_chapter ON chunks(chapter_id);
            """)

    def create_or_get_project(self, project_id: str, title: str, source_path: str, profile_name: str) -> Dict[str, Any]:
        with self.conn:
            row = self.conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
            if row:
                return dict(row)
            self.conn.execute(
                "INSERT INTO projects (id, title, source_path, profile_name) VALUES (?, ?, ?, ?)",
                (project_id, title, source_path, profile_name)
            )
            return dict(self.conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone())

    def update_chapter_status(self, chapter_id: str, status: str, translated_text: Optional[str] = None, validation_errors: Optional[str] = None):
        with self.conn:
            self.conn.execute("""
                UPDATE chapters 
                SET status = ?, translated_text = COALESCE(?, translated_text), 
                    validation_errors = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status, translated_text, validation_errors, chapter_id))
            
            # Update project completed chapters count
            ch = self.conn.execute("SELECT project_id FROM chapters WHERE id = ?", (chapter_id,)).fetchone()
            if ch:
                pid = ch["project_id"]
                completed = self.conn.execute("SELECT COUNT(*) as c FROM chapters WHERE project_id = ? AND status = 'completed'", (pid,)).fetchone()["c"]
                total = self.conn.execute("SELECT COUNT(*) as c FROM chapters WHERE project_id = ?", (pid,)).fetchone()["c"]
                status_proj = 'completed' if completed == total and total > 0 else 'in_progress'
                self.conn.execute("""
                    UPDATE projects 
                    SET completed_chapters = ?, total_chapters = ?, status = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, (completed, total, status_proj, pid))

    def get_project_stats(self, project_id: str) -> Dict[str, Any]:
        with self.conn:
            proj = self.conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
            if not proj:
                return {}
            chapters = self.conn.execute("SELECT id, chapter_index, title, char_count, status, validation_errors FROM chapters WHERE project_id = ? ORDER BY chapter_index", (project_id,)).fetchall()
            return {
                "project": dict(proj),
                "chapters": [dict(c) for c in chapters]
            }

    def list_all_projects(self) -> List[Dict[str, Any]]:
        with self.conn:
            rows = self.conn.execute("SELECT * FROM projects ORDER BY updated_at DESC").fetchall()
            return [dict(r) for r in rows]
