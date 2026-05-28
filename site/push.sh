#!/usr/bin/env bash
# push.sh — stage everything, commit with a message, push to GitHub.
# Usage: bash push.sh "what changed"
#        (default message: "Site update")

set -e
cd "$(dirname "$0")"

msg="${1:-Site update}"

git add -A

if git diff --staged --quiet; then
  echo "Nothing to commit. Local files match what's already on GitHub."
  exit 0
fi

git commit -m "$msg"
git push

echo ""
echo "Pushed. GitHub Pages will redeploy in about 60 seconds."
echo "Preview: https://marklopez1-cyber.github.io/instantheatingandair/"
