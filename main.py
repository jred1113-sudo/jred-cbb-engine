from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import os
import time
import requests
from datetime import datetime

# =====================
# ENVIRONMENT VARIABLES
# =====================
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ODDS_API_KEY = os.getenv("ODDS_API_KEY")

# =====================
# SETTINGS
# =====================
POLL_INTERVAL = 60  # seconds

ODDS_ENDPOINT = "https://api.the-odds-api.com/v4/sports/basketball_ncaab/odds"

HEADERS = {
    "Accept": "application/json"
}

# =====================
# TELEGRAM
# =====================
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

    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print("Telegram error:", e)

# =====================
# ODDS API
# =====================
def get_games():
    if not ODDS_API_KEY:
        print("ODDS_API_KEY not set")
        return None

    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "us",
        "markets": "spreads",
        "oddsFormat": "american"
    }

    try:
        r = requests.get(ODDS_ENDPOINT, headers=HEADERS, params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print("Fetch error:", e)
        return None

# =====================
# PARSE & ALERT
# =====================
def parse_games(data):
    alerts = []

    if not data:
        return alerts

    for game in data:
        try:
            home = game["home_team"]
            away = game["away_team"]
            commence = game.get("commence_time", "")

            bookmakers = game.get("bookmakers", [])
            if not bookmakers:
                continue

            markets = bookmakers[0].get("markets", [])
            if not markets:
                continue

            outcomes = markets[0].get("outcomes", [])

            msg = f"<b>{away} vs {home}</b>\n"
            msg += f"Start: {commence}\n\n"

            for team in outcomes:
                msg += f"{team['name']}: {team['point']} ({team['price']})\n"

            alerts.append(msg)

        except Exception as e:
            print("Parse error:", e)

    return alerts

# =====================
# MAIN LOOP
# =====================
def main():
    print("CBP Edge Engine Running")
    send_telegram("🟢 CBP Edge Engine is LIVE")

    while True:
        data = get_games()
        alerts = parse_games(data)

        for alert in alerts:
            send_telegram(alert)

        time.sleep(POLL_INTERVAL)

# =====================
# FLY.IO HEALTH SERVER
# =====================
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"CBB Edge Engine Running")

def start_server():
    server = HTTPServer(("0.0.0.0", 8080), HealthHandler)
    server.serve_forever()

# =====================
# START EVERYTHING
# =====================
if __name__ == "__main__":
    threading.Thread(target=start_server, daemon=True).start()
    main()
