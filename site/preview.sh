#!/usr/bin/env bash
# preview.sh — start a local web server in this folder and open the browser.
# Run from inside the extracted zip folder:  bash preview.sh
# Stop the server with Ctrl+C when you're done.

set -e
cd "$(dirname "$0")"

PORT=8000
URL="http://localhost:$PORT"

# Try to open the browser cross-platform (best effort — server runs either way)
open_browser() {
  if command -v xdg-open >/dev/null 2>&1; then xdg-open "$URL" >/dev/null 2>&1 || true
  elif command -v open >/dev/null 2>&1; then open "$URL" >/dev/null 2>&1 || true
  elif command -v start >/dev/null 2>&1; then start "$URL" >/dev/null 2>&1 || true
  elif command -v cmd.exe >/dev/null 2>&1; then cmd.exe /c start "" "$URL" >/dev/null 2>&1 || true
  fi
}

# Open browser after a short delay so the server is ready first
( sleep 1 && open_browser ) &

echo ""
echo "  Preview running at $URL"
echo "  Press Ctrl+C to stop."
echo ""

# Use python's built-in http.server (works in Git Bash on Windows + macOS + Linux)
if command -v python3 >/dev/null 2>&1; then
  python3 -m http.server $PORT
elif command -v python >/dev/null 2>&1; then
  python -m http.server $PORT
else
  echo "Python is not installed. Install Python 3 from https://www.python.org/downloads/"
  exit 1
fi
