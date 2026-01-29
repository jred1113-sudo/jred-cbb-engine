from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import os
import time
import requests
from datetime import datetime

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

POLL_INTERVAL = 60  # seconds

ODDS_API_KEY = os.getenv("ODDS_API_KEY")
ODDS_ENDPOINT = "https://api.the-odds-api.com/v4/sports/basketball_ncaab/odds"

def send_telegram(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram not configured")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    requests.post(url, json=payload)

def get_games():
    if not ODDS_API_KEY:
        print("ODDS_API_KEY not set")
        return None

    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "us",
        "markets": "h2h,spreads",
        "oddsFormat": "american"
    }

    try:
        r = requests.get(ODDS_ENDPOINT, params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print("Odds API fetch error:", e)
        return None

def parse_games(data):
    alerts = []

    if not data:
        return alerts

    events = data.get("events", [])
    for game in events:
        name = game["name"]
        status = game["status"]["type"]["description"]

        competitions = game.get("competitions", [])
        if not competitions:
            continue

        competitors = competitions[0].get("competitors", [])
        if len(competitors) != 2:
            continue

        team1 = competitors[0]["team"]["shortDisplayName"]
        team2 = competitors[1]["team"]["shortDisplayName"]

        score1 = competitors[0].get("score", "0")
        score2 = competitors[1].get("score", "0")

        headline = f"🏀 {team1} {score1} — {team2} {score2}\nStatus: {status}"
        alerts.append(headline)

    return alerts

def main():
    send_telegram("🚀 CBB Engine Online — Live monitoring started")

    while True:
        data = get_games()
        games = parse_games(data)

        if games:
            msg = "📊 Live Games Update:\n\n" + "\n\n".join(games)
            send_telegram(msg)
        else:
            print("No games found")

        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    if __name__ == "__main__":
    threading.Thread(target=start_server, daemon=True).start()
    main()# --- Fly.io Keep-Alive Server ---
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"CBB Edge Engine Running")

def start_server():
    server = HTTPServer(("0.0.0.0", 8080), HealthHandler)
    server.serve_forever()

threading.Thread(target=start_server, daemon=True).start()
