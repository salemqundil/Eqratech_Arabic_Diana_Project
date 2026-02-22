"""Helper launcher for the FastAPI web app.

Usage:
  python run_server.py [--host 127.0.0.1] [--port 8000]

Falls back to defaults if args omitted.
This avoids shell issues where typing `uvicorn` directly fails.
"""
from __future__ import annotations

import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description="Run Arabic grammar web classifier server")
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload (dev mode)')
    args = parser.parse_args()
    try:
        import uvicorn  # type: ignore
    except ImportError:
        print("uvicorn not installed. Install dependencies: pip install -r requirements.txt", file=sys.stderr)
        sys.exit(1)
    uvicorn.run("web_app.main:app", host=args.host, port=args.port, reload=args.reload)

if __name__ == '__main__':
    main()
