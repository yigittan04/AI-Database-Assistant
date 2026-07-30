import redis, json, os
from dotenv import load_dotenv

load_dotenv()

r = redis.from_url(
    os.getenv("REDIS_URL"),
    decode_responses=True,
    protocol=2
)

def get_history(session_id: str) -> list:
    data = r.get(f"history:{session_id}")
    return json.loads(data) if data else []

def save_history(session_id: str, history: list):
    r.setex(f"history:{session_id}", 3600, json.dumps(history))

def clear_history(session_id: str):
    r.delete(f"history:{session_id}")

def get_cached_query(sql: str):
    data = r.get(f"cache:{sql}")
    return json.loads(data) if data else None

def cache_query(sql: str, results: list, ttl: int = 60):
    r.setex(f"cache:{sql}", ttl, json.dumps(results))

def invalidate_cache():
    """Call this after any write operation to clear stale cache."""
    for key in r.scan_iter("cache:*"):
        r.delete(key)

import secrets

def create_session(user_id: str, is_admin: bool) -> str:
    token = secrets.token_hex(32)
    r.setex(f"session:{token}", 86400, json.dumps({
        "user_id": user_id,
        "is_admin": is_admin
    }))
    return token

def get_session(token: str) -> dict | None:
    data = r.get(f"session:{token}")
    return json.loads(data) if data else None

def delete_session(token: str):
    r.delete(f"session:{token}")