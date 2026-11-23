import os
import sys
import json
import http.server
import socketserver
import urllib.parse
from typing import Dict, Any

# Add current path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ENGINE_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
sys.path.append(ENGINE_ROOT)

from src.database.db import NovelDatabase

DB_PATH = os.path.join(ENGINE_ROOT, "novel_pipeline.db")
db = NovelDatabase(DB_PATH)

PORT = 3000

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        
        # API Routes
        if path == "/api/projects":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            projects = db.list_all_projects()
            self.wfile.write(json.dumps(projects).encode("utf-8"))
            return
            
        elif path.startswith("/api/project/"):
            pid = path.replace("/api/project/", "").strip()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            stats = db.get_project_stats(pid)
            self.wfile.write(json.dumps(stats).encode("utf-8"))
            return

        elif path == "/api/profiles":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            profile_dir = os.path.join(ENGINE_ROOT, "config", "profiles")
            profiles = [f.replace(".yaml", "") for f in os.listdir(profile_dir) if f.endswith(".yaml")]
            self.wfile.write(json.dumps(profiles).encode("utf-8"))
            return

        # Serve static HTML/dashboard
        if path == "/" or path == "/index.html":
            html_file = os.path.join(ENGINE_ROOT, "web", "public", "index.html")
            if os.path.exists(html_file):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                with open(html_file, "rb") as f:
                    self.wfile.write(f.read())
                return
                
        # Default file handler
        return super().do_GET()

def run_server():
    os.chdir(os.path.join(ENGINE_ROOT, "web", "public"))
    with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
        print(f"🚀 Novel Engine Web Dashboard running at http://localhost:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()
