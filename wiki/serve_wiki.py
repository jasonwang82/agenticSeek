#!/usr/bin/env python3
"""
AgenticSeek Wiki Server

A simple HTTP server to serve the wiki web application.

Usage:
    python serve_wiki.py [--port PORT] [--host HOST]

Examples:
    python serve_wiki.py                    # Serve on http://localhost:8888
    python serve_wiki.py --port 3001        # Serve on http://localhost:3001
    python serve_wiki.py --host 0.0.0.0     # Serve on all interfaces
"""

import argparse
import http.server
import os
import sys
import webbrowser
from functools import partial
from pathlib import Path


class WikiHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler with proper MIME types and SPA fallback."""

    MIME_TYPES = {
        '.html': 'text/html',
        '.css': 'text/css',
        '.js': 'application/javascript',
        '.md': 'text/markdown; charset=utf-8',
        '.json': 'application/json',
        '.svg': 'image/svg+xml',
        '.png': 'image/png',
        '.ico': 'image/x-icon',
    }

    def guess_type(self, path):
        ext = Path(path).suffix.lower()
        return self.MIME_TYPES.get(ext, 'application/octet-stream')

    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

    def log_message(self, format, *args):
        status = args[1] if len(args) > 1 else ''
        path = args[0] if args else ''
        if '200' in str(status) or '304' in str(status):
            color = '\033[32m'
        elif '404' in str(status):
            color = '\033[33m'
        else:
            color = '\033[0m'
        reset = '\033[0m'
        print(f"  {color}{path}{reset}")


def main():
    parser = argparse.ArgumentParser(description='Serve AgenticSeek Wiki')
    parser.add_argument('--port', type=int, default=8888, help='Port (default: 8888)')
    parser.add_argument('--host', type=str, default='localhost', help='Host (default: localhost)')
    parser.add_argument('--no-open', action='store_true', help='Do not open browser')
    args = parser.parse_args()

    wiki_dir = Path(__file__).parent
    os.chdir(wiki_dir)

    handler = partial(WikiHandler, directory=str(wiki_dir))
    server = http.server.HTTPServer((args.host, args.port), handler)

    url = f"http://{args.host}:{args.port}"
    print(f"\n  AgenticSeek Wiki")
    print(f"  {'─' * 40}")
    print(f"  Server running at: \033[36m{url}\033[0m")
    print(f"  Serving from:      {wiki_dir}")
    print(f"  {'─' * 40}")
    print(f"  Press Ctrl+C to stop\n")

    if not args.no_open:
        webbrowser.open(url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")
        server.server_close()
        sys.exit(0)


if __name__ == '__main__':
    main()
