#!/usr/bin/env bash
# ----------------------------------------------------------------------------
# fetch-reviews.sh — Refresh the live Google reviews snapshot.
#
# Usage:
#   bash fetch-reviews.sh
#
# What it does:
#   1. Reads your Google Places API key + Place ID from ~/.iha-env
#      (a one-line-each plain text file you create once — see below).
#   2. Calls Google Places API → Place Details endpoint
#   3. Saves the JSON response to build/data/google_reviews.json
#   4. Tells you what the new total review count + average rating is
#
# After running this, push to GitHub and Cowork will pick up the fresh
# JSON on the next site rebuild.
#
# ONE-TIME SETUP — create ~/.iha-env with these two lines:
#   GOOGLE_PLACES_API_KEY=AIzaSy...your-key-here
#   GOOGLE_PLACE_ID=ChIJ...your-place-id
#
# Then: chmod 600 ~/.iha-env (so only you can read it)
# ----------------------------------------------------------------------------
set -e

ENV_FILE="$HOME/.iha-env"
OUT_FILE="build/data/google_reviews.json"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "❌ Config file not found: $ENV_FILE"
  echo ""
  echo "   Create it with these two lines:"
  echo "   GOOGLE_PLACES_API_KEY=AIzaSy...your-key"
  echo "   GOOGLE_PLACE_ID=ChIJ...your-place-id"
  echo ""
  echo "   Then run: chmod 600 ~/.iha-env"
  exit 1
fi

# Load env vars (shell-style: VAR=value per line)
set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

if [[ -z "$GOOGLE_PLACES_API_KEY" || -z "$GOOGLE_PLACE_ID" ]]; then
  echo "❌ Missing GOOGLE_PLACES_API_KEY or GOOGLE_PLACE_ID in $ENV_FILE"
  exit 1
fi

if [[ ! -d "build/data" ]]; then
  echo "❌ build/data/ not found. Run this from the repo root."
  exit 1
fi

echo "🔎 Fetching latest reviews from Google Places API..."
curl -s "https://maps.googleapis.com/maps/api/place/details/json?place_id=${GOOGLE_PLACE_ID}&fields=name,rating,user_ratings_total,reviews,url&key=${GOOGLE_PLACES_API_KEY}" \
  -o "$OUT_FILE"

# Verify status: "OK"
STATUS=$(grep -o '"status"[[:space:]]*:[[:space:]]*"[A-Z_]*"' "$OUT_FILE" | head -1 | grep -o '"[A-Z_]*"$' | tr -d '"')
if [[ "$STATUS" != "OK" ]]; then
  echo "❌ Google returned status: $STATUS"
  echo "   Check the file for the full error: $OUT_FILE"
  exit 1
fi

# Pull the headline numbers for the user
RATING=$(grep -o '"rating"[[:space:]]*:[[:space:]]*[0-9.]*' "$OUT_FILE" | head -1 | grep -o '[0-9.]*$')
TOTAL=$(grep -o '"user_ratings_total"[[:space:]]*:[[:space:]]*[0-9]*' "$OUT_FILE" | head -1 | grep -o '[0-9]*$')

echo ""
echo "✅ Refreshed $OUT_FILE"
echo "   Average rating: ${RATING}★"
echo "   Total reviews:  ${TOTAL}"
echo ""
echo "   Next: commit + push so Cowork picks up the new snapshot on rebuild."
