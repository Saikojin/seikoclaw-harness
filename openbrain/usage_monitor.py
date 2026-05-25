import sqlite3
from datetime import date

class UsageMonitor:
    def __init__(self, db_path="openbrain.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Ensures the usage_stats table exists."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS usage_stats (
                stat_date DATE DEFAULT (DATE('now')),
                provider TEXT NOT NULL,
                tokens_used INTEGER DEFAULT 0,
                requests_count INTEGER DEFAULT 0,
                PRIMARY KEY (stat_date, provider)
            )
        """)
        conn.commit()
        conn.close()

    def track_usage(self, provider: str, tokens: int = 0, requests: int = 1):
        """Records API usage for the current day."""
        today = date.today().isoformat()
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        # Upsert usage record
        cur.execute("""
            INSERT INTO usage_stats (stat_date, provider, tokens_used, requests_count)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(stat_date, provider) DO UPDATE SET
                tokens_used = tokens_used + EXCLUDED.tokens_used,
                requests_count = requests_count + EXCLUDED.requests_count
        """, (today, provider, tokens, requests))
        
        conn.commit()
        conn.close()

    def get_todays_usage(self, provider: str):
        today = date.today().isoformat()
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT tokens_used, requests_count FROM usage_stats WHERE stat_date = ? AND provider = ?", (today, provider))
        row = cur.fetchone()
        conn.close()
        
        if row:
            return {"tokens": row[0], "requests": row[1]}
        return {"tokens": 0, "requests": 0}

    def check_limits(self, provider: str, token_limit: int, request_limit: int):
        usage = self.get_todays_usage(provider)
        if usage["tokens"] >= token_limit or usage["requests"] >= request_limit:
            return True, f"Limit reached for {provider}: {usage}"
        return False, None

if __name__ == "__main__":
    um = UsageMonitor("openbrain.db")
    um.track_usage("anthropic", tokens=1500)
    print(um.get_todays_usage("anthropic"))
