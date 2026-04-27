#!/usr/bin/env bash
# ----------------------------------------------------------------------------
# deploy.sh — One-shot deploy for the Instant Heating and Air website.
#
# Usage:
#   bash deploy.sh "commit message"
#
# What it does:
#   1. Auto-discovers the newest site-updated*.zip anywhere under your user
#      folder — Downloads, OneDrive (any path), Desktop, Documents, etc.
#   2. Extracts it into the current directory (your git repo)
#   3. Stages all changes, commits with your message, pushes to GitHub
#   4. Sevalla auto-deploys ~30-60s after the push lands
#
# Save this file in the root of your git repo (~/instantheatingandair/).
# Run from the repo root.
# ----------------------------------------------------------------------------
set -e

# Commit message — required so commits stay descriptive
if [[ -z "$1" ]]; then
  echo "❌ Missing commit message."
  echo ""
  echo "   Usage: bash deploy.sh \"What you changed\""
  echo "   Example: bash deploy.sh \"Update homepage hero copy\""
  exit 1
fi
COMMIT_MSG="$1"

# Sanity check — must be inside a git repo
if [[ ! -d ".git" ]]; then
  echo "❌ This folder isn't a git repo. cd into ~/instantheatingandair first."
  exit 1
fi

# ---------------------------------------------------------------------------
# Auto-discover the newest site-updated*.zip anywhere under the user's home.
# Searches OneDrive (any path), Downloads, Desktop, Documents — wherever the
# zip might be — and picks the one with the most recent modification time.
# ---------------------------------------------------------------------------

# Determine user's Windows-side home (Git Bash maps it under /c/Users/...)
USER_HOME="$HOME"
[[ -d "$USER_HOME" ]] || USER_HOME="/c/Users/$(whoami)"

echo "🔎 Searching $USER_HOME for the newest site-updated*.zip..."

# Find every site-updated*.zip under USER_HOME, capped at 7 directories deep
# (covers OneDrive\Claude\Projects\<folder>\file with room to spare).
ZIP_PATH=""
NEWEST_MTIME=0
while IFS= read -r f; do
  [[ -f "$f" ]] || continue
  mtime=$(stat -c %Y "$f" 2>/dev/null || stat -f %m "$f" 2>/dev/null)
  if [[ -n "$mtime" && "$mtime" -gt "$NEWEST_MTIME" ]]; then
    NEWEST_MTIME="$mtime"
    ZIP_PATH="$f"
  fi
done < <(find "$USER_HOME" -maxdepth 7 -type f -name "site-updated*.zip" 2>/dev/null)

if [[ -z "$ZIP_PATH" ]]; then
  echo "❌ No site-updated*.zip found anywhere under $USER_HOME"
  echo ""
  echo "   Make sure Cowork has built the zip and try again."
  exit 1
fi

# Convert mtime to a friendly timestamp for the user
ZIP_TS=$(date -d "@$NEWEST_MTIME" '+%Y-%m-%d %H:%M' 2>/dev/null \
  || date -r "$NEWEST_MTIME" '+%Y-%m-%d %H:%M' 2>/dev/null \
  || echo "")

echo "📦 Using zip: $ZIP_PATH"
[[ -n "$ZIP_TS" ]] && echo "   (built $ZIP_TS)"
echo "📂 Extracting into $(pwd)..."
unzip -oq "$ZIP_PATH" -d .

# Show what changed
CHANGE_COUNT=$(git status --porcelain | wc -l | tr -d ' ')
if [[ "$CHANGE_COUNT" -eq 0 ]]; then
  echo ""
  echo "✅ No changes detected. Repo is already up to date."
  exit 0
fi

echo ""
echo "🔍 $CHANGE_COUNT file(s) changed:"
git status --short | head -25
if [[ "$CHANGE_COUNT" -gt 25 ]]; then
  echo "   ...and $((CHANGE_COUNT - 25)) more"
fi

echo ""
echo "💾 Committing: $COMMIT_MSG"
git add -A
git commit -m "$COMMIT_MSG"

echo ""
echo "⬆️  Pushing to GitHub..."
git push

echo ""
echo "✅ Deploy complete!"
echo "   Sevalla will redeploy in ~30-60 seconds."
echo "   Verify: https://instantheatingandair.com/?bust=$(date +%s)"
