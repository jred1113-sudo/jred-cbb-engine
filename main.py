import os
import time
import requests
from datetime import datetime

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

POLL_INTERVAL = 60  # seconds

ESPN_SCOREBOARD = "https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard"

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
    try:
        r = requests.get(ESPN_SCOREBOARD, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print("Fetch error:", e)
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
    main()
