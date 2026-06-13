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

# ---------------------------------------------------------------------------
# Push with auto-rebase-on-rejection.
#
# The GitHub Action (.github/workflows/refresh-reviews.yml) auto-commits the
# refreshed Google reviews JSON to main on its weekly schedule. Those commits
# never touch your laptop, so the next time you deploy, your local main can
# be one (or more) commits behind. A naive `git push` would be rejected with
# "Updates were rejected because the remote contains work you don't have."
#
# This block tries up to 3 times: if push is rejected, it rebases your one
# new commit onto whatever has landed on origin/main, then retries. If the
# rebase pauses on a conflict in build/data/google_reviews.json (the only
# file the workflow modifies), it auto-resolves by keeping the remote's copy
# — that file is the workflow's responsibility, not the deploy zip's.
# ---------------------------------------------------------------------------
echo ""
echo "⬆️  Pushing to GitHub..."

push_ok=0
for attempt in 1 2 3; do
  if git push 2>&1; then
    push_ok=1
    echo "✓ Pushed on attempt ${attempt}."
    break
  fi
  echo ""
  echo "⚠ Push rejected (remote moved). Rebasing on latest origin/main…"

  if ! git pull --rebase origin main; then
    # Rebase paused — check whether it's just the reviews JSON
    if git diff --name-only --diff-filter=U | grep -q "build/data/google_reviews.json"; then
      echo "  · Conflict on build/data/google_reviews.json — auto-resolving with remote version (workflow owns this file)"
      git checkout --theirs build/data/google_reviews.json
      git add build/data/google_reviews.json
      git rebase --continue
    else
      echo ""
      echo "❌ Rebase paused on an unexpected conflict. Aborting auto-recovery."
      echo "   Resolve manually with:"
      echo "     git status                  # see which files conflict"
      echo "     # edit them, then:"
      echo "     git add <file>"
      echo "     git rebase --continue"
      echo "     git push"
      exit 1
    fi
  fi
done

if [[ "$push_ok" != "1" ]]; then
  echo ""
  echo "❌ Push still failing after 3 attempts."
  echo "   Investigate with: git status && git log --oneline -5"
  exit 1
fi

echo ""
echo "✅ Deploy complete!"
echo "   Sevalla will redeploy in ~30-60 seconds."
echo "   Verify: https://instantheatingandair.com/?bust=$(date +%s)"
