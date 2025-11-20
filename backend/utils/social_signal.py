import json
import os
from textblob import TextBlob

def get_team_mentions(team_name, sport):
    """
    Pull authenticated Bluesky posts mentioning a team (with fallback to neutral context).
    """
    try:
        # Load Bluesky credentials
        cfg_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
        if not os.path.exists(cfg_path):
            return {"social_mentions": 0, "social_sentiment": "neutral", "error": "no config file"}

        with open(cfg_path, "r") as f:
            config = json.load(f)
        creds = config.get("bluesky", {})
        handle = creds.get("handle")
        password = creds.get("password")

        # Skip if missing
        if not (handle and password):
            return {"social_mentions": 0, "social_sentiment": "neutral", "error": "missing credentials"}

        try:
            from atproto import Client
        except Exception as e:
            return {"social_mentions": 0, "social_sentiment": "neutral", "error": f"missing atproto: {e}"}

        client = Client()
        client.login(handle, password)

        # Search for posts related to this team
        feed = client.app.bsky.feed.search_posts(params={
            "q": f'"{team_name}" OR "#{team_name}" injury OR questionable OR probable OR out',
            "limit": 25
        })

        posts = []
        for item in getattr(feed, "posts", []) or []:
            record = getattr(item, "record", None)
            text = getattr(record, "text", "") if record else ""
            if text and any(k in text.lower() for k in ["injury", "out", "won't play", "questionable", "probable"]):
                posts.append({
                    "text": text[:200],
                    "author": getattr(item.author, "handle", "unknown"),
                    "time": getattr(record, "created_at", ""),
                    "sentiment": TextBlob(text).sentiment.polarity
                })

        avg_sent = sum(p["sentiment"] for p in posts) / len(posts) if posts else 0
        tone = "bullish" if avg_sent > 0.1 else "bearish" if avg_sent < -0.1 else "neutral"

        return {
            "social_mentions": len(posts),
            "social_sentiment": tone,
            "posts": posts[:10]
        }

    except Exception as e:
        return {
            "social_mentions": 0,
            "social_sentiment": "neutral",
            "error": str(e)
        }
