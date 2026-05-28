"""Live Google Reviews loaded from the Google Places API.

This module reads `google_reviews.json` (a cached snapshot of the Places API
response) and exposes the data the site needs:

  LIVE_REVIEWS       — list of dicts in the same shape as data/reviews.py
                       (text/author/city/source/date) so existing render code
                       can use either source interchangeably.
  TOTAL_REVIEWS      — live integer (e.g. 56). Replaces the old hardcoded 48
                       so review counts site-wide stay current.
  AVG_RATING         — live float (e.g. 5.0).
  GOOGLE_PROFILE_URL — link to the business's Google reviews page so visitors
                       can click through to read everything / leave their own.
  LAST_FETCHED       — ISO timestamp of when the JSON was last refreshed.

How to refresh
--------------
Run `bash fetch-reviews.sh` from the repo root (requires GOOGLE_PLACES_API_KEY
and GOOGLE_PLACE_ID env vars set, or in ~/.env). That re-pulls from Google and
overwrites google_reviews.json. Then rebuild + deploy as normal.
"""

import json
import os
from datetime import datetime

_HERE = os.path.dirname(os.path.abspath(__file__))
_JSON_PATH = os.path.join(_HERE, "google_reviews.json")


def _load():
    try:
        with open(_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"result": {"reviews": [], "rating": 5.0, "user_ratings_total": 0,
                           "url": "https://maps.google.com/"},
                "status": "MISSING"}


_DATA = _load()
_RESULT = _DATA.get("result", {})


def _transform(api_review):
    """Convert a Places API review dict into the shape used by reviews.py."""
    # API gives Unix timestamp; convert to YYYY-MM-DD for compatibility with
    # the curated REVIEWS schema (used by rev_card()).
    ts = api_review.get("time", 0)
    date_str = datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d") if ts else ""
    return {
        "text": api_review.get("text", ""),
        "author": api_review.get("author_name", "Google User"),
        "city": "phoenix",  # API doesn't tag city; safest default for HQ market
        "service": "general",
        "source": "Google",
        "date": date_str,
        # Extras (only the live Google strip uses these — not the curated card)
        "rating": api_review.get("rating", 5),
        "relative_time": api_review.get("relative_time_description", ""),
        "profile_photo_url": api_review.get("profile_photo_url", ""),
        "author_url": api_review.get("author_url", ""),
    }


LIVE_REVIEWS = [_transform(r) for r in _RESULT.get("reviews", [])]
TOTAL_REVIEWS = _RESULT.get("user_ratings_total", 0)
AVG_RATING = _RESULT.get("rating", 5.0)
GOOGLE_PROFILE_URL = _RESULT.get("url", "https://maps.google.com/")
LAST_FETCHED = datetime.utcfromtimestamp(
    os.path.getmtime(_JSON_PATH)
).strftime("%Y-%m-%d") if os.path.exists(_JSON_PATH) else ""
