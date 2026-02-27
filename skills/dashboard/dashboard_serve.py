#!/usr/bin/env python3
"""
Research Dashboard Server
Serves the task root directory so that dashboard/ and output dirs are all accessible.
Uses ThreadingHTTPServer for concurrent requests.

Usage:
  python dashboard_serve.py                          # serve task root (parent of script dir)
  python dashboard_serve.py --root /path/to/task     # explicit task root
  python dashboard_serve.py --port 7788              # specify port
"""

import http.server
import os
import sys
import socket
import argparse
import threading


def find_free_port(start=7788):
    for port in range(start, start + 20):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("localhost", port)) != 0:
                return port
    return start


class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()


class DashboardServer(http.server.ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True


def main():
    parser = argparse.ArgumentParser(description="Research Dashboard Server")
    parser.add_argument("--root", default=None, help="Task root directory to serve")
    parser.add_argument("--dir", default=None, help="(Legacy) alias for --root")
    parser.add_argument("--port", type=int, default=0, help="Port (default: auto from 7788)")
    args = parser.parse_args()

    if args.root:
        task_root = os.path.abspath(args.root)
    elif args.dir:
        d = os.path.abspath(args.dir)
        if os.path.basename(d) == "dashboard" and os.path.isdir(os.path.dirname(d)):
            task_root = os.path.dirname(d)
        else:
            task_root = d
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        task_root = os.path.dirname(script_dir)

    if not os.path.isdir(task_root):
        print(f"  Error: directory not found: {task_root}", file=sys.stderr)
        sys.exit(1)

    os.chdir(task_root)
    port = args.port if args.port > 0 else find_free_port()

    httpd = DashboardServer(("", port), DashboardHandler)
    url = f"http://localhost:{port}/dashboard/dashboard.html"
    print(f"\n  Dashboard ready → {url}", flush=True)
    print(f"  Serving: {task_root}\n", flush=True)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n  Dashboard server stopped.")
        httpd.shutdown()
        sys.exit(0)


if __name__ == "__main__":
    main()
