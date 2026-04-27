#!/usr/bin/env bash
# ----------------------------------------------------------------------------
# deploy.sh — One-shot deploy for the Instant Heating and Air website.
#
# Usage:
#   bash deploy.sh "commit message"
#
# What it does:
#   1. Finds the newest site-updated*.zip in your Downloads folder
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

# Find newest site-updated*.zip in Downloads (handles "site-updated (1).zip" etc.)
DOWNLOADS="$HOME/Downloads"
ZIP_PATH=$(ls -t "$DOWNLOADS"/site-updated*.zip 2>/dev/null | head -n1)

if [[ -z "$ZIP_PATH" ]]; then
  echo "❌ No site-updated*.zip found in $DOWNLOADS"
  echo ""
  echo "   Save the zip from Cowork to Downloads first, then re-run."
  exit 1
fi

echo "📦 Using zip: $ZIP_PATH"
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
git status --short | head -20
if [[ "$CHANGE_COUNT" -gt 20 ]]; then
  echo "   ...and $((CHANGE_COUNT - 20)) more"
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
