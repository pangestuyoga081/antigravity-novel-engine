import os
import sys
import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ENGINE_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
sys.path.append(ENGINE_ROOT)

from src.database.db import NovelDatabase

DB_PATH = os.path.join(ENGINE_ROOT, "novel_pipeline.db")
db = NovelDatabase(DB_PATH)

PORT = 3000

class TelemetryServer(BaseHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/projects":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            projects = db.list_all_projects()
            self.wfile.write(json.dumps(projects).encode("utf-8"))
            return

        elif path.startswith("/api/project/"):
            pid = path.replace("/api/project/", "").strip()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            stats = db.get_project_stats(pid)
            self.wfile.write(json.dumps(stats).encode("utf-8"))
            return

        elif path.startswith("/api/chapter/"):
            cid = path.replace("/api/chapter/", "").strip()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            chap = db.get_chapter(cid)
            self.wfile.write(json.dumps(chap or {}).encode("utf-8"))
            return

        elif path == "/api/profiles":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            profile_dir = os.path.join(ENGINE_ROOT, "config", "profiles")
            profiles = []
            if os.path.exists(profile_dir):
                profiles = [f.replace(".yaml", "") for f in os.listdir(profile_dir) if f.endswith(".yaml")]
            self.wfile.write(json.dumps(profiles).encode("utf-8"))
            return

        # Serve index.html
        if path in ["/", "/index.html"]:
            html_file = os.path.join(ENGINE_ROOT, "web", "public", "index.html")
            if os.path.exists(html_file):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                with open(html_file, "rb") as f:
                    self.wfile.write(f.read())
                return

        self.send_response(404)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"404 Not Found")

    def log_message(self, format, *args):
        # Clean logging
        sys.stdout.write("%s - - [%s] %s\n" % (self.address_string(), self.log_date_time_string(), format % args))
        sys.stdout.flush()

def main():
    server_address = ("127.0.0.1", PORT)
    httpd = HTTPServer(server_address, TelemetryServer)
    print(f"🚀 Telemetry Dashboard active at http://localhost:{PORT}", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        httpd.server_close()

if __name__ == "__main__":
    main()
